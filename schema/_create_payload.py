from utils import get_user_info, get_recent_quiz_info, get_recent_planner


def create_planner_input_payload(student_id: str, date: str):
    '''create planner about per day.'''
    # user_info = get_user_info(student_id) # grade, study_hours, soup
    user_info = {
        "grade": "중학교 1학년",
        "soup": "2",
        "study_hours": 2,
        "current_unit": "기본 도형 - 작도와 합동"
    }
    related_units = ["좌표평면과 그래프 - 정비례와 반비례", 
                     "기본 도형 - 작도와 합동", 
                     "기본 도형 - 기본 도형", 
                     "기본 도형 - 평행선",
                     "기본 도형 - 위치 관계"], 
    # quiz_info = get_recent_quiz_info(student_id) # quiz_id, quizes, total_score
    quiz_info = {
        "quiz_id": "1",
        "quizes": [
            {"question_num": 1, "essay_type_score": None, "difficulty_level": "상", "is_correct": True, "timeout": False},
            {"question_num": 2, "essay_type_score": None, "difficulty_level": "중", "is_correct": False, "timeout": False},
            {"question_num": 3, "essay_type_score": None, "difficulty_level": "중", "is_correct": True, "timeout": False},
            {"question_num": 4, "essay_type_score": None, "difficulty_level": "하", "is_correct": False, "timeout": True},
            {"question_num": 5, "essay_type_score": None, "difficulty_level": "상", "is_correct": True, "timeout": False},
        ],
        "total_score": 60.0,  # (3/5)*100
        "previous_quiz_score": 40.0,  # (2/5)*100
        "score_trend": "상승",
        "accuracy_by_unit": {
            "좌표평면과 그래프 - 좌표평면과 그래프": 1.0,
            "좌표평면과 그래프 - 정비례와 반비례": 0.5,
            "기본 도형 - 작도와 합동": 0.0
        },
        "accuracy_by_topic": {
            "계산": 1.0,
            "추론": 0.5,
            "이해": 0.7,
            "문제해결": 0.1
        },
        "accuracy_by_difficulty": {
            "상": 0.4,
            "중": 0.8,
            "하": 1.0
        },
        "time_efficiency": "상승"
    }

    # planner = get_recent_planner(student_id)
    planner =  {
        "planner_id": 1,
        "meta": {
            "date": "2025-11-01",
            "day_of_week": "토",
            "planned_time_min": 120
        },
        "content": [
            {"text": "1. 좌표평면과 그래프 - 좌표평면과 그래프 : 개념 학습하기", "time": 60},
            {"text": "2. 좌표평면과 그래프 - 좌표평면과 그래프 : 문제 풀기", "time": 40},
            {"text": "3. 좌표평면과 그래프 - 정비례와 반비례 : 개념 이해하기", "time": 20}
        ],
        "content_total_min": 120
    }
    return {
        "grade": user_info["grade"],
        "available_time_min": user_info["study_hours"]*60, # convert to minutes
        "initial_level": user_info["soup"],
        "recent_quiz_info": quiz_info,
        "recent_planner": planner,
        "recent_score":quiz_info["total_score"],
        "current_unit":user_info["current_unit"],
        "related_units": related_units
    }


def create_eval_quiz_input_payload(request):
    pass
#     all_quizzes = request.quizzes
#     for quiz in all_quizzes:
#         question = quiz["question"]
#         answer = quiz["answer"]
#         user_answer = quiz["user_answer"]
        

#         quiz_payload = {
#             "question": ["query"],
#             "answer": ["predicted_documents"],
#             "user_answer": cleanseddata["ground_truth_documents"], # List[List of text]
#             "ans_by_level": "",

#         }
#     final_payload = {
#         "retrieve_metrics": config["retrieve_metrics"],
#         "dataset": {
#             "Retrieval": retrieval_dataset,
#         },
#             "evaluation_mode": config["evaluation_mode"],
#     }

#     return final_payload
