import cv2
import numpy as np
from typing import Optional, Dict, Any
from .base import BaseEffect

class BlurFaceEffect(BaseEffect):
    """
    Aplica desenfoque (Blur) selectivo sobre el rostro detectado o el fondo.
    """
    def __init__(self, name: str = "blur_face", blur_amount: int = 35, blur_background: bool = False, enabled: bool = True):
        super().__init__(name=name, enabled=enabled)
        self.blur_amount = blur_amount if blur_amount % 2 == 1 else blur_amount + 1
        self.blur_background = blur_background

    def apply(self, frame: np.ndarray, face_data: Optional[Dict[str, Any]], progress: float) -> np.ndarray:
        if not face_data or "bbox" not in face_data:
            return frame

        x, y, w, h = face_data["bbox"]
        h_frame, w_frame, _ = frame.shape

        # Asegurar límites dentro de la imagen
        x1, y1 = max(0, x), max(0, y)
        x2, y2 = min(w_frame, x + w), min(h_frame, y + h)

        if x2 <= x1 or y2 <= y1:
            return frame

        k = int(self.blur_amount * max(0.2, progress))
        if k % 2 == 0:
            k += 1
        if k < 3:
            return frame

        out = frame.copy()
        if not self.blur_background:
            # Desenfocar solo el rostro
            roi = out[y1:y2, x1:x2]
            blurred_roi = cv2.GaussianBlur(roi, (k, k), 0)
            out[y1:y2, x1:x2] = blurred_roi
        else:
            # Desenfocar el fondo y dejar nítido el rostro
            blurred_full = cv2.GaussianBlur(frame, (k, k), 0)
            blurred_full[y1:y2, x1:x2] = frame[y1:y2, x1:x2]
            out = blurred_full

        return out
