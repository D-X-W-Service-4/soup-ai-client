from graphs.states import EvaluateLevelTestState
from utils import safe, ask_exaone
from .prompts import calculate_check_prompt


async def node_calculate_check(state: EvaluateLevelTestState) -> EvaluateLevelTestState:
    """계산 체크 노드"""
    question_text=safe(state.get("question_text"))
    student_ocr=safe(state.get("student_ocr"))
    
    prompt = calculate_check_prompt.format(
        question_text=question_text,
        student_ocr=student_ocr
    )
    out = await ask_exaone(prompt)
    print("student_check_result", out)
    return {"student_check_result": out}