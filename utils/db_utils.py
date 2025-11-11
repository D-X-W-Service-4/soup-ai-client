import os
from typing import Dict, Any
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()
DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL, pool_pre_ping=True)


def get_user_info(student_id: int) -> Dict[str, Any]:
    """users 테이블에서 학년, 레벨, 학습시간 등 가져오기"""
    query = text("""
        SELECT grade, study_hours, soup, last_subject_unit_id
        FROM users
        WHERE user_id = :uid
    """)
    with engine.connect() as conn:
        res = conn.execute(query, {"uid": student_id}).fetchone()
    if not res:
        raise HTTPException(status_code=404, detail=f"User {student_id} not found.")
    soup_score_map = {
        "CORN": "1",
        "MUSHROOM": "2",
        "PUMPKIN": "3",
        "SWEET_POTATO": "4",
        "TOMATO": "5"
    }
    grade_map = {"M1":"중학교 1학년", "M2": "중학교 3학년", "M3": "중학교 3학년"}
    result = dict(res._mapping)
    result["grade"] = grade_map[result["grade"]]
    result["soup"] = soup_score_map[result["soup"]]
    query = text("""
        SELECT name
        FROM subject_units
        WHERE subject_unit_id = :unit_id
    """)
    
    # 현재 단원
    with engine.connect() as conn:
        res = conn.execute(query, {"unit_id": result["last_subject_unit_id"]}).fetchone()
    if not res:
        raise HTTPException(status_code=404, detail=f"Name for {result["last_subject_unit_id"]} not found.")
    
    result["current_unit"] = dict(res._mapping)["name"]
    
    # 관련 단원 
    query = text("""
        SELECT name
        FROM subject_units
        WHERE subject_unit_id BETWEEN :start_id AND :end_id
        ORDER BY subject_unit_id
    """)

    unit_id = result["last_subject_unit_id"]

    with engine.connect() as conn:
        rows = conn.execute(
            query,
            {"start_id": unit_id - 1, "end_id": unit_id + 3}
        ).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No nearby units found for id {unit_id}")

    related_units = [r._mapping["name"] for r in rows]

    return result, related_units



def _compute_accuracy_by(items, key):
    counts = defaultdict(lambda: {"correct": 0, "total": 0})
    for r in items:
        k = r[key]
        counts[k]["total"] += 1
        if r["is_correct"]:
            counts[k]["correct"] += 1

    return {
        k: v["correct"] / v["total"]
        for k, v in counts.items()
        if v["total"] > 0
    }

def get_recent_quiz_info(student_id: int) -> Dict[str, Any]:
    # 최근 quiz_id 두개 조회
    level_test_query = text("""
        SELECT level_test_id
        FROM level_tests
        WHERE user_id = :uid
        ORDER BY created_at DESC
        LIMIT 2
    """)

    with engine.connect() as conn:
        level_test_row = conn.execute(level_test_query, {"uid": student_id}).fetchall()

        if not level_test_row:
            # 해당 유저의 레벨테스트 기록 없음
            return {}

        level_test_id = level_test_row[0]._mapping["level_test_id"]
        prev_level_test_id = level_test_row[1]._mapping["question_set_id"] if len(level_test_row) > 1 else None
        item_query = text("""
            SELECT 
                lti.is_correct,
                lti.is_timeout,
                lti.essay_type_score,
                q.difficulty,
                q.subject_unit_id,  ## 이것도 해당 question_id에 있음
                q.question_type ## 이것도
            FROM level_test_questions lti
            JOIN questions q ON lti.question_id = q.question_id
            WHERE lti.level_test_id = :level_test_id
        """)
        rows = conn.execute(item_query, {"level_test_id": level_test_id}).fetchall()
        if prev_level_test_id: #이전 퀴즈
            prev_rows = conn.execute(item_query, {"level_test_id": prev_level_test_id}).fetchall()
        else:
            prev_rows = []

    quiz_items = [
        {
            "question_num": idx + 1,
            "essay_type_score": r._mapping["essay_type_score"],
            "difficulty": r._mapping["difficulty"], 
            "is_correct": bool(r._mapping["is_correct"]),
            "is_timeout": bool(r._mapping["is_timeout"]), 
        }
        for idx, r in enumerate(rows)
    ]

    total_score = sum(1 for q in quiz_items if q["is_correct"]) * 10
    prev_score = (
        sum(1 for r in prev_rows if r._mapping["is_correct"]) * 10
        if prev_rows else None
    )
    if prev_score is None:
        score_trend = None
    elif total_score > prev_score:
        score_trend = "상승"
    elif total_score < prev_score:
        score_trend = "하락"
    else:
        score_trend = "유지"

    accuracy_by_unit = _compute_accuracy_by(
        [{**r._mapping, "is_correct": bool(r._mapping["is_correct"])} for r in rows],
        "subject_unit_id"
    )

    # subject_unit_id → name 매핑 조회
    unit_name_query = text("""
        SELECT subject_unit_id, name
        FROM subject_units
        WHERE subject_unit_id IN :ids
    """)

    unit_ids = tuple(accuracy_by_unit.keys())

    with engine.connect() as conn:
        unit_name_rows = conn.execute(unit_name_query, {"ids": unit_ids}).fetchall()

    unit_name_map = {
        r._mapping["subject_unit_id"]: r._mapping["name"]
        for r in unit_name_rows
    }

    accuracy_by_unit = {
        unit_name_map.get(k, f"단원_{k}"): v
        for k, v in accuracy_by_unit.items()
    }

    accuracy_by_topic = _compute_accuracy_by(
        [{**r._mapping, "is_correct": bool(r._mapping["is_correct"])} for r in rows],
        "question_type"
    )
    accuracy_by_difficulty_raw = _compute_accuracy_by(
        [{**r._mapping, "is_correct": bool(r._mapping["is_correct"])} for r in rows],
        "difficulty"
    )
    difficulty_map = {1: "상", 2: "중", 3: "하"}
    accuracy_by_difficulty = {}

    for k, v in accuracy_by_difficulty_raw.items():
        try:
            k_int = int(k)
        except (ValueError, TypeError):
            k_int = k
        accuracy_by_difficulty[difficulty_map.get(k_int, str(k))] = v

    for row in quiz_items:
        row["difficulty"] = difficulty_map[int(row['difficulty'])]
    timeout_rate = sum(1 for q in quiz_items if q["is_timeout"]) / len(quiz_items)
    if prev_rows:
        prev_timeout_rate = sum(1 for r in prev_rows if r._mapping["is_timeout"]) / len(prev_rows)
        if timeout_rate < prev_timeout_rate:
            time_efficiency = "상승"
        elif timeout_rate > prev_timeout_rate:
            time_efficiency = "하락"
        else:
            time_efficiency = "유지"
    else:
        time_efficiency = None

    return {
        "quiz_id": str(level_test_id),
        "quizes": quiz_items,
        "total_score": sum(1 for q in quiz_items if q["is_correct"]) * 10,
        "previous_quiz_score": prev_score,
        "score_trend": score_trend,  # 상승/하락/유지
        "accuracy_by_unit": accuracy_by_unit,
        "accuracy_by_topic": accuracy_by_topic,
        "accuracy_by_difficulty": accuracy_by_difficulty,
        "time_efficiency": time_efficiency, # 상승/하락/유지
    }


def _get_korean_day(weekday_idx: int) -> str:
    days = ["월", "화", "수", "목", "금", "토", "일"]
    return days[weekday_idx % 7]



def get_recent_planner(student_id: int) -> Dict[str, Any]:
    """해당 학생의 가장 최근 플래너 1개와 그에 속한 모든 planner_items 조회"""

    # 1. 가장 최근 planner_id 1개 조회
    recent_planner_query = text("""
        SELECT planner_id, date
        FROM planners
        WHERE user_id = :uid
        ORDER BY date DESC
        LIMIT 1
    """)

    with engine.connect() as conn:
        planner_row = conn.execute(recent_planner_query, {"uid": student_id}).fetchone()
        if not planner_row:
            return {"message": "최근 플래너 없음"}

        planner_id = planner_row._mapping["planner_id"]
        planner_date = planner_row._mapping["date"]

        # 2. 해당 planner_id의 planner_items 전부 조회
        item_query = text("""
            SELECT content, duration
            FROM planner_items
            WHERE planner_id = :pid
        """)
        item_rows = conn.execute(item_query, {"pid": planner_id}).fetchall()

    # 아이템이 없을 수도 있음
    contents = [
        {"text": r._mapping["content"], "time": r._mapping["duration"] or 0}
        for r in item_rows
    ]

    total_time = sum(c["time"] for c in contents)
    return {
        "planner_id": planner_id,
        "meta": {
            "date": str(planner_date),
            "day_of_week": _get_korean_day(planner_date.weekday()),
            "planned_time_min": total_time,
        },
        "content": contents,
        "content_total_min": total_time,
    }


def get_question_by_difficulty_unit(difficulty: int, subject_unit: str):
    with engine.connect() as conn:
        # 먼저 (difficulty, subject_unit) 조건으로 랜덤 1개 시도
        query = text("""
            SELECT q.question_id, q.text, q.question_format, q.topic
            FROM questions q
            JOIN subject_units su ON q.subject_unit_id = su.subject_unit_id
            WHERE q.difficulty = :difficulty
            AND su.name = :subject_unit
            ORDER BY RAND()
            LIMIT 1
        """)
        result = conn.execute(query, {
            "difficulty": difficulty,
            "subject_unit": subject_unit
        }).fetchone()

        # 없으면 subject_unit 내에서 랜덤 1개로 fallback
        if not result:
            print(f"[INFO] '{subject_unit}' 단원에서 해당 난이도 문제 없음 → 다른 난이도로 대체합니다.")
            fallback_query = text("""
                SELECT q.question_id, q.text, q.question_format, q.topic
                FROM questions q
                JOIN subject_units su ON q.subject_unit_id = su.subject_unit_id
                WHERE su.name = :subject_unit
                ORDER BY RAND()
                LIMIT 1
            """)
            result = conn.execute(fallback_query, {"subject_unit": subject_unit}).fetchone()

        if not result:
            print(f"[WARN] '{subject_unit}' 단원 문제 자체가 존재하지 않습니다.")
            return None

        return dict(result._mapping)
