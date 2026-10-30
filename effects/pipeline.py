from typing import List, Dict, Optional, Any
import numpy as np
from .base import BaseEffect

class EffectPipeline:
    """
    Gestor del flujo de efectos visuales.
    Permite registrar efectos, prenderlos, apagarlos o reordenarlos en caliente.
    """
    def __init__(self):
        self._effects: List[BaseEffect] = []
        self._effects_map: Dict[str, BaseEffect] = {}

    def register(self, effect: BaseEffect) -> "EffectPipeline":
        """Registra un nuevo efecto al final de la cadena de procesamiento."""
        if effect.name in self._effects_map:
            # Reemplaza si ya existía con ese nombre
            idx = self._effects.index(self._effects_map[effect.name])
            self._effects[idx] = effect
        else:
            self._effects.append(effect)
        self._effects_map[effect.name] = effect
        return self

    def set_enabled(self, name: str, enabled: bool):
        """Activa o desactiva un efecto por su nombre."""
        if name in self._effects_map:
            self._effects_map[name].enabled = enabled

    def get_effect(self, name: str) -> Optional[BaseEffect]:
        """Obtiene una referencia a un efecto registrado."""
        return self._effects_map.get(name)

    def process(self, frame: np.ndarray, face_data: Optional[Dict[str, Any]] = None, progress: float = 0.0) -> np.ndarray:
        """
        Ejecuta todos los efectos habilitados en orden secuencial.
        """
        current_frame = frame
        for effect in self._effects:
            if effect.enabled:
                try:
                    current_frame = effect.apply(current_frame, face_data, progress)
                except Exception as e:
                    print(f"[EffectPipeline] Error aplicando efecto '{effect.name}': {e}")
        return current_frame

    def list_effects(self) -> List[str]:
        return [f"{e.name} (enabled={e.enabled})" for e in self._effects]
