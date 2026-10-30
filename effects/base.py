from abc import ABC, abstractmethod
import numpy as np
from typing import Optional, Dict, Any

class BaseEffect(ABC):
    """
    Clase base para todos los efectos visuales.
    Cualquier efecto nuevo debe heredar de esta clase e implementar `apply()`.
    Permite encadenar, activar, desactivar o modificar efectos sin tocar el resto del programa.
    """
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    @abstractmethod
    def apply(self, frame: np.ndarray, face_data: Optional[Dict[str, Any]], progress: float) -> np.ndarray:
        """
        Aplica la transformación sobre el fotograma.

        :param frame: Imagen BGR de OpenCV (NumPy array).
        :param face_data: Diccionario con información del rostro (bounding box, landmarks, etc.) o None.
        :param progress: Número de 0.0 (inicio de la cuenta) a 1.0 (momento exacto del disparo).
                         Permite hacer que los efectos aumenten su intensidad con el tiempo.
        :return: Fotograma resultante transformado (NumPy array).
        """
        pass

    def __repr__(self) -> str:
        return f"<Effect: {self.name} (enabled={self.enabled})>"
