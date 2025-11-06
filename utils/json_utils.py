def _balanced_json_from(text: str) -> Optional[str]:
    if not text:
        return None
    i = text.find('{')
    if i == -1:
        return None
    depth = 0
    for j, ch in enumerate(text[i:], start=i):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return text[i:j+1]
    return None

def extract_json_from_text_strict(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    t = text.strip()

    m = re.search(r"<JSON>(.*)</JSON>", t, flags=re.DOTALL | re.IGNORECASE)
    if m:
        block = m.group(1).strip()
        candidate = _balanced_json_from(block)
        if candidate:
            try:
                return json.loads(candidate)
            except Exception:
                pass

    candidate = _balanced_json_from(t)
    if candidate:
        try:
            return json.loads(candidate)
        except Exception:
            return None
    return None

def _schema_guard(data: Optional[Dict[str, Any]], max_score: int) -> Dict[str, Any]:
    if data is None:
        data = {
            "score": 0,
            "max_score": max_score,
            "criteria": {
                "relevance": 0, "validity": 0, "accuracy": 0,
                "completeness": 0, "presentation": 0
            },
            "mistakes": ["FINAL_PARSE_FAIL"],
            "feedback": "채점 결과를 파싱하지 못했습니다."
        }
    # 누락 키 보정
    def _get(d, k, default):
        return d[k] if isinstance(d, dict) and k in d else default
    data = {
        "score": _get(data, "score", 0),
        "max_score": _get(data, "max_score", max_score),
        "criteria": {
            "relevance": _get(_get(data, "criteria", {}), "relevance", 0),
            "validity": _get(_get(data, "criteria", {}), "validity", 0),
            "accuracy": _get(_get(data, "criteria", {}), "accuracy", 0),
            "completeness": _get(_get(data, "criteria", {}), "completeness", 0),
            "presentation": _get(_get(data, "criteria", {}), "presentation", 0),
        },
        "mistakes": _get(data, "mistakes", []),
        "feedback": _get(data, "feedback", "")
    }
    return data