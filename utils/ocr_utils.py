import io
import base64
import os, requests
from PIL import Image
from fastapi import UploadFile, HTTPException

REMOTE_BASE = os.getenv("REMOTE_BASE", "http://193.69.10.2:26973")
REMOTE_API_KEY = os.getenv("REMOTE_API_KEY", "Soup")
REMOTE_TIMEOUT_S = int(os.getenv("REMOTE_TIMEOUT_S", "120"))

def imagefile_to_b64_png(img_file: UploadFile) -> str:
    """
    업로드된 이미지를 PNG로 변환 후 base64 인코딩합니다.
    Kanana API에 전달 가능한 형태: data:image/png;base64,<...>
    """
    data = img_file.file.read()
    image = Image.open(io.BytesIO(data)).convert("RGB")

    # 과도한 해상도 방지 (긴 변 2048px 권장)
    max_side = max(image.size)
    if max_side > 2048:
        scale = 2048 / max_side
        new_w = int(image.size[0] * scale)
        new_h = int(image.size[1] * scale)
        image = image.resize((new_w, new_h))

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def call_kanana_generate(payload: dict) -> dict:
    """
    Kanana API로 요청을 전송하고 JSON 결과 반환
    payload: {"image_url": ..., "image_b64": ...}
    """
    try:
        resp = requests.post(
            f"{REMOTE_BASE}/kanana/generate",
            json=payload,
            headers={"Authorization": f"Bearer {REMOTE_API_KEY}", "Content-Type": "application/json"},
            timeout=REMOTE_TIMEOUT_S
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Kanana 서버 응답 시간 초과")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kanana 호출 실패: {e}")