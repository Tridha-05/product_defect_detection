"""Small helper functions."""
import base64
import io

from PIL import Image


def to_jpeg_bytes(img: Image.Image, max_side: int = 512, quality: int = 85) -> bytes:
    """Shrink an image and return JPEG bytes (keeps DB small)."""
    img = img.convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return buf.getvalue()


def to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")
