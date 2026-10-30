import numpy as np
import random
from typing import Optional, Dict, Any
from .base import BaseEffect

class GlitchEffect(BaseEffect):
    """
    Efecto de Glitch:
    - Aberración cromática (desfase horizontal de canales R, G, B).
    - Desplazamiento horizontal de bandas o tiras de píxeles aleatorias.
    La intensidad del efecto aumenta con el parámetro 'progress' (0.0 a 1.0).
    """
    def __init__(self, name: str = "glitch", max_shift: int = 15, max_slices: int = 6, enabled: bool = True):
        super().__init__(name=name, enabled=enabled)
        self.max_shift = max_shift
        self.max_slices = max_slices

    def apply(self, frame: np.ndarray, face_data: Optional[Dict[str, Any]], progress: float) -> np.ndarray:
        # Si progress es muy bajo o no está activo, no alterar
        intensity = max(0.1, progress)
        shift = int(self.max_shift * intensity)
        
        if shift <= 0:
            return frame

        h, w, c = frame.shape
        out = frame.copy()

        # 1. Aberración cromática (Desfase de canal Rojo y Azul)
        # B = 0, G = 1, R = 2
        r_shift = shift
        b_shift = -shift

        # Desplaza canal R hacia la derecha
        if r_shift > 0 and r_shift < w:
            out[:, r_shift:, 2] = frame[:, :-r_shift, 2]
        # Desplaza canal B hacia la izquierda
        if abs(b_shift) > 0 and abs(b_shift) < w:
            out[:, :b_shift, 0] = frame[:, -b_shift:, 0]

        # 2. Desplazamiento de tiras horizontales (Slice Glitch)
        num_slices = int(self.max_slices * intensity)
        for _ in range(num_slices):
            slice_h = random.randint(4, max(5, int(h * 0.08)))
            y_start = random.randint(0, h - slice_h)
            x_offset = random.randint(-shift * 2, shift * 2)

            if x_offset != 0:
                slice_data = out[y_start:y_start + slice_h, :]
                out[y_start:y_start + slice_h, :] = np.roll(slice_data, x_offset, axis=1)

        return out
