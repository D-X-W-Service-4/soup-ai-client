import io
import boto3
import httpx
import base64
import os, requests
from PIL import Image
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()
KANANA_PORT=os.getenv("KANANA_PORT")
VASTAI_HOST=os.getenv("VASTAI_HOST")
KANANA_API_KEY = os.getenv("KANANA_API_KEY", "Soup")
BUCKET_NAME = os.getenv("BUCKET_NAME")
S3_DIR= os.getenv("S3_DIR")

def imagefile_to_b64_png(img_filename: str) -> str:
    """
    업로드된 이미지를 PNG로 변환 후 base64 인코딩합니다.
    Kanana API에 전달 가능한 형태: data:image/png;base64,<...>
    """
    # s3 = boto3.client("s3")

    # s3_key = f"{S3_DIR}/{img_filename}"

    # # S3에서 이미지 가져오기
    # response = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)
    # data = response['Body'].read()
    
    with open(img_filename, "rb") as f:
        data = f.read()  # bytes
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

async def call_kanana_generate(payload: dict) -> dict:
    """
    Kanana API로 요청을 전송하고 JSON 결과 반환
    payload: {"image_url": ..., "image_b64": ...}
    """
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"http://{VASTAI_HOST}:{KANANA_PORT}/kanana/generate",
                json=payload,
                headers={"Authorization": f"Bearer {KANANA_API_KEY}", "Content-Type": "application/json"}
            )
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()
    
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Kanana 서버 응답 시간 초과")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kanana 호출 실패: {e}")