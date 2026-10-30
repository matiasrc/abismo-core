import cv2
import numpy as np
from typing import Optional, Dict, Any
from .base import BaseEffect

class FrankensteinEffect(BaseEffect):
    """
    Efecto Frankenstein / Collage:
    Recorta regiones del rostro (ej. franja de los ojos o la boca)
    y las desplaza, invierte o distorsiona de posición.
    Más adelante permite mezclar con facciones guardadas en repositorio.
    """
    def __init__(self, name: str = "frankenstein", enabled: bool = True):
        super().__init__(name=name, enabled=enabled)

    def apply(self, frame: np.ndarray, face_data: Optional[Dict[str, Any]], progress: float) -> np.ndarray:
        if not face_data or "bbox" not in face_data:
            return frame

        x, y, w, h = face_data["bbox"]
        h_frame, w_frame, _ = frame.shape

        out = frame.copy()

        # Franja de los ojos aproximada: tercio superior-medio de la cara
        eyes_y1 = int(y + h * 0.20)
        eyes_y2 = int(y + h * 0.45)
        eyes_x1 = max(0, x)
        eyes_x2 = min(w_frame, x + w)

        if eyes_y2 > eyes_y1 and eyes_x2 > eyes_x1:
            eyes_roi = out[eyes_y1:eyes_y2, eyes_x1:eyes_x2].copy()
            
            # Desplazamiento proporcional al progreso
            offset_y = int(h * 0.25 * progress)
            target_y1 = min(h_frame - (eyes_y2 - eyes_y1), eyes_y1 + offset_y)
            target_y2 = target_y1 + (eyes_y2 - eyes_y1)

            # Invertir horizontalmente los ojos o mezclarlos
            if progress > 0.4:
                eyes_roi = cv2.flip(eyes_roi, 1)

            # Pega la franja de ojos desplazada
            out[target_y1:target_y2, eyes_x1:eyes_x2] = eyes_roi

        return out
