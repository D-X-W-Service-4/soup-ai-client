import re
from langgraph.graph import START, END, StateGraph
from graphs.states.level_test_state import EvaluateLevelTestState
from graphs.nodes.prompts import generate_level_test_prompt, simple_eval_prompt
from utils import ask_llm, normalize_text, ensure_json, get_question_by_difficulty_unit
from graphs.nodes import (
    node_image_ocr,
    node_answer_check,
    node_calculate_check,
    node_step234,
    node_evaluate_essay_question
)


def evaluate_level_test_graph():
    graph = StateGraph(EvaluateLevelTestState)
    '''
    1. input으로 image url을 받아서, b64코드로 변환 후, ocr 텍스트를 가져온다.
    2. 가져온 결과를 병렬로 계산/대입/수치,  논리(F2)·적합성(F3)·결과 작성 여부(F4), 정답 비교 전용 동시 진행
    3. final evaluate 실행
    '''
    graph.add_node("image_ocr", node_image_ocr)
    graph.add_node("answer_check", node_answer_check)
    graph.add_node("step234", node_step234)
    graph.add_node("calculate_check", node_calculate_check)
    graph.add_node("evaluate_essay_question", node_evaluate_essay_question)

    graph.add_edge(START, "image_ocr")
    graph.add_edge("image_ocr", "answer_check")
    graph.add_edge("image_ocr", "step234")
    graph.add_edge("image_ocr", "calculate_check")

    graph.add_edge("answer_check", "evaluate_essay_question")
    graph.add_edge("step234", "evaluate_essay_question")
    graph.add_edge("calculate_check", "evaluate_essay_question")

    graph.add_edge("evaluate_essay_question", END)

    return graph.compile()



async def eval_simple_level_test(question_text, user_answer, answer): 
    prompt = simple_eval_prompt.format(
        question_text=question_text,
        user_answer=user_answer,
        answer=answer, 
    )
    out = await ask_llm(prompt)
    out_clean = re.sub(r"[^A-Za-z]", "", out)
    out_clean = out_clean.lower()

    return {
        "eval_result": {
            "is_correct": out_clean == "true",
            "essay_type_score": None,
            "essay_type_score_text": None,
            "user_answer": user_answer
        }
    }

async def generate_level_test(soup_level: str, workbooks: str, unit_list: dict):
    # unit_id_list = unit_list.keys()
    unit_list = list(unit_list.values())

    soup_score_map = {
        "CORN": "1",
        "MUSHROOM": "2",
        "PUMPKIN": "3",
        "SWEET_POTATO": "4",
        "TOMATO": "5"
    }
    workbook_score_map = {
        "체크체크": 1,
        "수력충전": 1,
        "쎈 연산": 1,
        "교과서": 1,
        "개념원리": 2,
        "RPM": 2,
        "개념 쎈": 2,
        "우공비": 2,
        "자이스토리": 3,
        "쎈수학": 3,
        "최상위 라이트": 3,
        "원리해설": 3,
        "최고수준": 4,
        "일품": 4,
        "최상위 수학": 4,
        "최고득점": 4,
        "에이급수학": 5,
        "블랙라벨": 5,
        "최강 TOT": 5,
    }
    workbooks = workbooks.split(',')
    workbooks = [workbook_score_map.get(normalize_text(workbook), 1) for workbook in workbooks]
    workbook_score = sum(workbooks) / len(workbooks)

    prompt = generate_level_test_prompt.format(
        soup_level_to_score=soup_score_map.get(normalize_text(soup_level), "기록 없음"), 
        workbook_to_score=workbook_score, 
        unit_list=unit_list, 
    )
        # unit_checked_rate= )
    out = await ask_llm(prompt)
    out = ensure_json(out)
    print("out", out)
    time_map = {"1": 8, "2": 4, "3":2}
    
    for i, row in enumerate(out["level_test"]):
        row["question_num"] = i+1
        row["time"] = time_map[str(row["difficulty"])]
        questions = get_question_by_difficulty_unit(difficulty=row["difficulty"],
                                        subject_unit=row["subject_unit"]
                                        )
        row["topic"] = questions.get("topic", "")
        row["question_id"] = questions.get("question_id", "")
        row["question_text"] = questions.get("text", "")
        row["question_format"] = questions.get("question_format", "")
    return out["level_test"]

'''
{
    "level_test": [
            {"question_id": int "실제 db의 PK값",
                "question_number": int, #1~10
                "question_text": str, 
                "topic": str,
                "time": float, # 임의 부여한 값
                "difficulty": str, 
                "question_format": str "객or선"},
                
            {"question_id": int "실제 db의 PK값", 
                "question_number": int, #1~10
                "question_text": str, 
                "topic": str,
                "time": float, # 임의 부여한 값
                "difficulty": str, 
                "question_format": str "객or선"},
                ...
    ]
}
'''

