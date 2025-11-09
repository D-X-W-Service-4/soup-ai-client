from graphs.states import EvaluateLevelTestState
from utils import safe, ask_exaone
from .prompts import step234_prompt


async def node_step234(state: EvaluateLevelTestState) -> EvaluateLevelTestState:
    """step234 체크 노드"""
    question_text=safe(state.get("question_text"))
    student_ocr=safe(state.get("student_ocr"))
    question_topic=safe(state.get("question_topic"))
    
    prompt = step234_prompt.format(
        question_text=question_text,
        student_ocr=student_ocr,
        question_topic=question_topic
    )
    out = await ask_exaone(prompt)
    print("step234_result", out)
    return {"step234_result": out}