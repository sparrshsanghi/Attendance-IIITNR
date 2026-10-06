import base64
import hashlib
import hmac
import io
import json
import os
import time

import cv2
import numpy as np
import segno
from PIL import Image


def _get_qr_secret():
    return os.getenv("QR_SIGNING_SECRET", "attendance-dev-secret")


def _b64_url_encode(raw_bytes):
    return base64.urlsafe_b64encode(raw_bytes).decode().rstrip("=")


def _b64_url_decode(raw_text):
    padding = "=" * (-len(raw_text) % 4)
    return base64.urlsafe_b64decode(raw_text + padding)


def _sign_payload(payload_b64, secret):
    digest = hmac.new(secret.encode(), payload_b64.encode(), hashlib.sha256).digest()
    return _b64_url_encode(digest)


def create_qr_token(subject_id, teacher_id, session_id, ttl_seconds=300):
    now_ts = int(time.time())
    payload = {
        "subject_id": int(subject_id),
        "teacher_id": int(teacher_id),
        "session_id": int(session_id),
        "iat": now_ts,
        "exp": now_ts + int(ttl_seconds),
        "kind": "attendance_qr_v1"
    }
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    payload_b64 = _b64_url_encode(payload_json.encode())
    signature = _sign_payload(payload_b64, _get_qr_secret())
    return f"{payload_b64}.{signature}"


def verify_qr_token(token):
    if not token or "." not in token:
        return False, "Invalid token format.", None

    try:
        payload_b64, signature = token.split(".", 1)
    except ValueError:
        return False, "Invalid token structure.", None

    expected = _sign_payload(payload_b64, _get_qr_secret())
    if not hmac.compare_digest(signature, expected):
        return False, "QR signature mismatch.", None

    try:
        payload_json = _b64_url_decode(payload_b64).decode()
        payload = json.loads(payload_json)
    except Exception:
        return False, "QR payload decode failed.", None

    now_ts = int(time.time())
    exp = int(payload.get("exp", 0))
    if exp <= now_ts:
        return False, "QR code expired.", payload

    if payload.get("kind") != "attendance_qr_v1":
        return False, "Unsupported QR payload type.", payload

    return True, "OK", payload


def qr_token_to_png_bytes(token, scale=8):
    qr = segno.make_qr(token, error="m")
    raw = io.BytesIO()
    qr.save(raw, kind="png", scale=scale, border=3)
    raw.seek(0)
    return raw.getvalue()


def decode_qr_from_image_file(image_file):
    if image_file is None:
        return None

    try:
        img = Image.open(image_file).convert("RGB")
        arr = np.array(img)
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        detector = cv2.QRCodeDetector()
        text, _, _ = detector.detectAndDecode(bgr)
        return text if text else None
    except Exception:
        return None
