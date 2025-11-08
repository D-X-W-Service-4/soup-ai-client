import os, base64
from typing import Optional
from pydantic import BaseModel, Field, model_validator

# 환경 변수
class Settings(BaseModel):
    REMOTE_BASE: str = Field(default=os.getenv("REMOTE_BASE", "http://193.69.10.2:26973"))
    REMOTE_API_KEY: str = Field(default=os.getenv("REMOTE_API_KEY", "Soup"))
    REMOTE_TIMEOUT_S: int = Field(default=int(os.getenv("REMOTE_TIMEOUT_S", "120")))

settings = Settings()

# 허용 MIME 타입과 최대 크기
ALLOWED_MIME = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
MAX_B64_BYTES = 10 * 1024 * 1024  # 10MB

# 요청 모델: image_url / image_b64만
class OCRRequest(BaseModel):
    image_url: Optional[str] = Field(default=None, description="원격 이미지 URL (선택)")
    image_b64: Optional[str] = Field(default=None, description="data URL 또는 순수 base64(권장)")

    @model_validator(mode="after")
    def require_image_input(cls, values: "OCRRequest"):
        if not values.image_b64 and not values.image_url:
            raise ValueError("image_b64 또는 image_url 중 하나는 반드시 제공해야 합니다.")
        return values

    @model_validator(mode="after")
    def normalize_and_check_b64(cls, values: "OCRRequest"):
        b64 = values.image_b64
        if not b64:
            return values

        # data URL 허용
        if "," in b64 and b64.strip().lower().startswith("data:"):
            header, payload = b64.split(",", 1)
            mime = header[5:].split(";")[0].strip().lower()
            if mime not in ALLOWED_MIME:
                raise ValueError(f"허용되지 않은 이미지 MIME 타입: {mime}")
            raw = payload
        else:
            raw = b64
            values.image_b64 = f"data:image/png;base64,{b64}"

        # base64 유효성 검증
        try:
            raw_bytes = base64.b64decode(raw, validate=True)
        except Exception:
            raise ValueError("image_b64가 올바른 base64가 아닙니다.")
        if len(raw_bytes) > MAX_B64_BYTES:
            raise ValueError(f"image_b64 용량이 너무 큽니다(최대 {MAX_B64_BYTES//(1024*1024)}MB).")
        return values

# 응답 모델
class OCRResponse(BaseModel):
    text: str = Field(..., description="OCR 결과 텍스트")
    tokens: int = Field(..., description="생성된 토큰 수")
