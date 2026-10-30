# Guía de Contribución: Creación de Nuevos Efectos Visuales

¡Bienvenido/a! Esta guía está pensada para que artistas visuales y desarrolladores puedan crear, probar y sumar nuevos efectos, filtros y transformaciones a **`abismo-core`** de forma rápida, aislada y colaborativa.

---

## 💡 El Concepto: Efectos 100% Desacoplados

No necesitas entender cómo funciona la red NDI, los pines de la Raspberry Pi ni la máquina de estados. 

Cada efecto es una clase independiente dentro de la carpeta `effects/` que recibe un fotograma de video (`np.ndarray`) y devuelve el fotograma transformado.

---

## 🛠️ Paso a Paso: Flujo de Trabajo con Git

### 1. Clona el repositorio y crea tu propia rama (Branch)
Nunca trabajes directamente sobre `main`. Crea una rama con el nombre del efecto que vas a crear:

```bash
git clone https://github.com/matiasrc/abismo-core.git
cd abismo-core
git checkout -b feature/efecto-espejo-liquido
```

### 2. Crea tu archivo de efecto en `effects/`
Copia la plantilla base o crea un nuevo archivo en `effects/` (ejemplo: `effects/mi_efecto.py`):

```python
# effects/mi_efecto.py
import cv2
import numpy as np
from typing import Optional, Dict, Any
from .base import BaseEffect

class MiEfecto(BaseEffect):
    """
    Descripción de lo que hace el efecto (ej. deformación, pixelado, glitch).
    """
    def __init__(self, name: str = "mi_efecto", enabled: bool = True, parametro_propio: int = 10):
        super().__init__(name=name, enabled=enabled)
        self.parametro_propio = parametro_propio

    def apply(self, frame: np.ndarray, face_data: Optional[Dict[str, Any]], progress: float) -> np.ndarray:
        """
        :param frame: Fotograma BGR de OpenCV (imagen de NumPy).
        :param face_data: Diccionario con la posición del rostro:
                          - face_data["bbox"] = (x, y, w, h)
                          - face_data["center"] = (cx, cy)
                          - face_data["landmarks"] = lista de puntos si MediaPipe está activo.
                          Puede ser None si no se detectó ningún rostro.
        :param progress: Número de 0.0 (inicio del conteo) a 1.0 (disparo final).
                         Úsalo para hacer que el efecto aumente de intensidad con el tiempo.
        :return: Fotograma transformado (NumPy array con la misma dimensión que frame).
        """
        h, w, c = frame.shape
        out = frame.copy()

        # Ejemplo 1: Efecto global (pixelación proporcional al progreso)
        if progress > 0.1:
            pixel_size = max(1, int(self.parametro_propio * progress))
            temp = cv2.resize(out, (w // pixel_size, h // pixel_size), interpolation=cv2.INTER_LINEAR)
            out = cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)

        # Ejemplo 2: Usar datos del rostro si están disponibles
        if face_data and "bbox" in face_data:
            x, y, bw, bh = face_data["bbox"]
            # Aplicar algo específico solo en el área del rostro...

        return out
```

### 3. Exponer el efecto en `effects/__init__.py`
Agrega tu clase para que sea visible desde afuera:

```python
# effects/__init__.py
from .base import BaseEffect
from .pipeline import EffectPipeline
from .glitch import GlitchEffect
from .blur_face import BlurFaceEffect
from .frankenstein import FrankensteinEffect
from .mi_efecto import MiEfecto  # 👈 Agregar tu efecto

__all__ = [
    "BaseEffect",
    "EffectPipeline",
    "GlitchEffect",
    "BlurFaceEffect",
    "FrankensteinEffect",
    "MiEfecto"                   # 👈 Y aquí
]
```

### 4. Probar tu efecto en tu computadora
En `main.py` registra tu efecto dentro del `EffectPipeline`:

```python
pipeline = EffectPipeline()
pipeline.register(MiEfecto(name="mi_efecto", enabled=True))
```

Ejecuta la app con tu webcam:
```bash
python3 main.py
```
Pulsa la barra espaciadora y verifica que el efecto se intensifique suavemente durante los 5 segundos de cuenta regresiva.

---

## 💡 Consejos para Desarrolladores de Efectos

1. **Rendimiento:** El código debe correr rápido (más de 25 FPS). Prefiere operaciones vectorizadas con **NumPy** o funciones nativas de **OpenCV** (`cv2`) en lugar de recorrer píxeles con bucles `for` de Python.
2. **Uso de `progress`:** El parámetro `progress` va de `0.0` a `1.0`. Es muy gratificante cuando un efecto arranca sutil en el segundo 5 y se vuelve extremo o monstruoso al llegar al segundo 0 (disparo).
3. **Robustez:** Siempre verifica que `face_data` no sea `None` antes de acceder a sus claves, ya que si la persona se mueve o sale del cuadro, el efecto debe seguir corriendo sin crashear.

---

## 🚀 Enviar tu Pull Request (PR)

Una vez que tu efecto funcione y se vea increíble:

1. Agrega tus cambios a Git:
   ```bash
   git add effects/mi_efecto.py effects/__init__.py
   git commit -m "feat(effects): agrega efecto de distorsión líquida"
   ```
2. Sube tu rama a GitHub:
   ```bash
   git push origin feature/efecto-espejo-liquido
   ```
3. Abre un **Pull Request** en GitHub describiendo:
   - Nombre del efecto.
   - Breve descripción visual de la transformación.
   - Parámetros que acepta para calibrarlo.
