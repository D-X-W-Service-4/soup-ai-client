from typing import TypedDict
from typing import Optional
# 레벨 테스트 서술형 평가를 위한 state

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
    final_eval_resuslt: Optional[dict]