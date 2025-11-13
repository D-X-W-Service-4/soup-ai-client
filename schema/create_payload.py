from utils import get_user_info, get_recent_quiz_info, get_recent_planner


def create_planner_input_payload(student_id: str, date: str):
    '''create planner about per day.'''
    user_info, related_units = get_user_info(student_id) # grade, study_hours, soup
    quiz_info = get_recent_quiz_info(student_id) # quiz_id, quizes, total_score
    print("quiz_info: ", quiz_info)
    planner = get_recent_planner(student_id)

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

'''
class EvaluateLevelTestState(TypedDict):
    image_url: Optional[str]
    question_text: Optional[str]
    answer_text: Optional[str]
    question_topic: Optional[str]
    max_score: Optional[int]

    # 각 node 결과 저장
    student_ocr: Optional[str]
    student_check_result: Optional[str]
    answer_check_result: Optional[str]
    step234_result: Optional[str]
    final_eval_result: Optional[dict]
'''

def create_eval_quiz_input_payload(
          num_questions, 
          user_answer_image, 
          question_text, 
          answer,
          answer_text,
          topic):
    
    max_score = 100 // num_questions
    return {
        "image_url": user_answer_image,
        "question_text": question_text,
        "answer_text": answer_text,
        "answer": answer,
        "question_topic": topic,
        "max_score": max_score,
    }