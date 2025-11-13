from graphs.states import EvaluateLevelTestState
from utils import safe, ask_llm, ensure_json
from .prompts import evaluate_essay_question_prompt


async def node_evaluate_essay_question(state: EvaluateLevelTestState) -> EvaluateLevelTestState:
    """최종 평가 결과 생성 노드"""
    question_text=safe(state.get("question_text"))
    student_ocr=safe(state.get("student_ocr"))
    answer_text=safe(state.get("answer_text"))
    question_topic=safe(state.get("question_topic"))
    student_check_result=safe(state.get("student_check_result"))
    step234_result=safe(state.get("step234_result"))
    answer_check_result=safe(state.get("answer_check_result"))
    max_score=safe(state.get("max_score"))
    print('max_score: ', max_score)
    prompt = evaluate_essay_question_prompt.format(
        question_text=question_text,
        student_ocr=student_ocr,
        answer_text=answer_text,
        question_topic=question_topic,
        student_check_result=student_check_result,
        step234_result=step234_result,
        answer_check_result=answer_check_result,
        max_score=max_score
    )
    out = await ask_llm(prompt)
    print("final out: ", out)
    out = ensure_json(out)
    score = out.get("score", 0)
    criteria = out.get("criteria", {})
    accuracy = criteria.get("accuracy", 0)
    feedback = out.get("feedback", "")

    result = {
        "essay_type_score": score,
        "user_answer": student_ocr,
        "is_correct": int(accuracy) == max_score, 
        "essay_type_score_text": feedback
    }

    # print("final_result", result)
    return {**state, "final_eval_result": result}

'''
{{
  "score": 0, (최종 score)
  "max_score": {max_score},
  "criteria": {{
    "accuracy": 0,
    "completeness": 0,
    "relevance": 0,
    "validity": 0,
    "presentation": 0
  }},
  "feedback": ""
}}

{
  "essay_type_score": int,
	"user_answer": str
	"is_correct": bool
  "essay_type_score_text": str
}
'''