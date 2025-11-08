from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
from schema.ocr_schema import OCRResponse
from utils.ocr_utils import imagefile_to_b64_png, call_kanana_generate

router = APIRouter()

@router.post("/transcribe", response_model=OCRResponse, summary="손글씨 수학 풀이 OCR 변환")
def ocr_transcribe(
    image_url: Optional[str] = None,
    file: Optional[UploadFile] = File(None),
):
    """
    로컬 파일 또는 원격 URL 기반 Kanana OCR 호출
    - file (multipart) 또는 image_url 중 하나 필수
    """
    if not file and not image_url:
        raise HTTPException(status_code=400, detail="file 또는 image_url 중 하나는 필요합니다.")

    # 업로드 파일 → base64 변환
    image_b64 = imagefile_to_b64_png(file) if file else None

    payload = {
        "image_url": image_url,
        "image_b64": image_b64,
    }

    data = call_kanana_generate(payload=payload)
    return OCRResponse(text=data.get("text", ""), tokens=int(data.get("tokens", 0)))
