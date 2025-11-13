from graphs.states import EvaluateLevelTestState
from utils import safe, ask_exaone
from .prompts import answer_check_prompt


async def node_answer_check(state: EvaluateLevelTestState) -> EvaluateLevelTestState:
    """정답 체크 노드"""
    question_text=safe(state.get("question_text"))
    student_ocr=safe(state.get("student_ocr"))
    answer_text=safe(state.get("answer_text"))
    answer=safe(state.get("answer"))

    prompt = answer_check_prompt.format(
        question_text=question_text,
        student_ocr=student_ocr,
        answer_text=answer_text,
        answer=answer
    )
    out = await ask_exaone(prompt)
    print("answer_check_result", out)
    return {"answer_check_result": out}