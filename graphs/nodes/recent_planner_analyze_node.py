from graphs.states import PlannerState
from utils import safe, ask_llm
from .prompts import recent_planner_analyze_prompt

async def node_recent_planner_analyze(state: PlannerState) -> PlannerState:
    """직전 플래너 분석 텍스트 생성."""
    print("직전 플래너 분석 텍스트 생성")
    rp = state.get("recent_planner")
    print(rp)
    planned = rp["meta"]["planned_time_min"] if (rp and rp.get("meta")) else None
    # 실제 학습 시간은 별도 수집값이 없으므로 없으면 planned로 대체(0으로 두기보다 안전)
    actual = [plan["time"] for plan in rp["content"]] if (rp and rp.get("content")) else []
    actual = sum(actual) if actual else None
    plan_completion_rate = [plan["checked"] for plan in rp["content"]] if (rp and rp.get("content")) else []
    plan_completion_rate = (sum(plan_completion_rate)/len(plan_completion_rate))*100 if plan_completion_rate else None

    prompt = recent_planner_analyze_prompt.format(
        plan_completion_rate=safe(plan_completion_rate),
        planned_time_min=safe(planned),
        actual_time_min=safe(actual),
        quiz_score=safe(state.get("recent_quiz_info", {}).get("total_score")),
        recent_quiz_analyze_result=safe(state.get("recent_quiz_analyze_result"))
    )
    out = await ask_llm(prompt)
    print("Recent Planner Analyze Result:", out)
    return {**state, "recent_planner_analyze_result": out}
