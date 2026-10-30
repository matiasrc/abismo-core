import cv2
import time
import random
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any
import config

class RepositoryManager:
    """
    Gestor del repositorio de imágenes:
    - Guarda fotos/clips capturados.
    - Extrae facciones para la memoria colectiva (Frankenstein).
    - Entrega imágenes aleatorias para la galería en modo de reposo (IDLE).
    """
    def __init__(self):
        self.captures_dir = config.CAPTURES_DIR
        self.facciones_dir = config.FACCIONES_DIR

    def save_capture(self, frame_bgr: np.ndarray, face_data: Optional[Dict[str, Any]] = None) -> Path:
        """Guarda la foto final procesada en el repositorio."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"abismo_{timestamp}.jpg"
        save_path = self.captures_dir / filename

        cv2.imwrite(str(save_path), frame_bgr)
        print(f"[RepositoryManager] Imagen guardada en: {save_path.name}")

        # Si hay rostro detectado, extraer facciones para la galería histórica
        if face_data and "bbox" in face_data:
            self._save_facial_features(frame_bgr, face_data["bbox"], timestamp)

        return save_path

    def _save_facial_features(self, frame_bgr: np.ndarray, bbox: tuple, timestamp: str):
        """Recorta y almacena ojos o boca para futuros collages."""
        x, y, w, h = bbox
        h_frame, w_frame, _ = frame_bgr.shape

        eyes_y1 = int(y + h * 0.20)
        eyes_y2 = int(y + h * 0.45)
        eyes_x1 = max(0, x)
        eyes_x2 = min(w_frame, x + w)

        if eyes_y2 > eyes_y1 and eyes_x2 > eyes_x1:
            eyes_crop = frame_bgr[eyes_y1:eyes_y2, eyes_x1:eyes_x2]
            crop_path = self.facciones_dir / f"ojos_{timestamp}.jpg"
            cv2.imwrite(str(crop_path), eyes_crop)

    def get_random_gallery_image(self) -> Optional[Path]:
        """Obtiene una foto al azar del repositorio para el modo IDLE."""
        all_images = list(self.captures_dir.glob("*.jpg"))
        if not all_images:
            return None
        return random.choice(all_images)
