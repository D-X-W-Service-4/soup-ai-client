from graphs.states import PlannerState


def node_data_check(state: PlannerState) -> PlannerState:
    recent_quiz_info = state.get("recent_quiz_info") or {}
    recent_planner = state.get("recent_planner") or []

    has_quiz = len(recent_quiz_info) > 0
    has_planner = not (len(recent_planner) == 1 and recent_planner.get("message", "최근 플래너 없음") == "최근 플래너 없음")

    return {
        **state,
        "has_quiz": has_quiz,
        "has_planner": has_planner,
    }
