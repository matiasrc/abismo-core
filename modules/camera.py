import cv2
import numpy as np
from typing import Optional, Tuple
import config

class CameraManager:
    """
    Gestor agnóstico de cámara:
    - En Raspberry Pi intenta usar `picamera2`.
    - Si falla o corre en Mac/PC, usa `cv2.VideoCapture` de OpenCV.
    - Aplica efecto espejo y recorte 4:5 vertical si está configurado.
    """
    def __init__(self):
        self.cap = None
        self.is_picam = False
        self._init_camera()

    def _init_camera(self):
        if config.IS_RASPBERRY_PI:
            try:
                from picamera2 import Picamera2
                self.picam2 = Picamera2()
                camera_config = self.picam2.create_preview_configuration(
                    main={"size": (config.CAPTURE_WIDTH, config.CAPTURE_HEIGHT), "format": "RGB888"}
                )
                self.picam2.configure(camera_config)
                self.picam2.start()
                self.is_picam = True
                print("[CameraManager] Iniciado con Picamera2 nativo de Raspberry Pi.")
                return
            except Exception as e:
                print(f"[CameraManager] No se pudo iniciar Picamera2 ({e}). Intentando OpenCV...")

        # Fallback estándar para PC, Mac o webcam USB
        # En macOS usamos CAP_AVFOUNDATION explícitamente para mayor compatibilidad
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_AVFOUNDATION)
        if not self.cap.isOpened():
            # Reintentar con backend predeterminado
            self.cap = cv2.VideoCapture(config.CAMERA_INDEX)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAPTURE_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAPTURE_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.TARGET_FPS)
        
        self._black_frame_warned = False

        if not self.cap.isOpened():
            print(f"[CameraManager] ¡ADVERTENCIA! No se pudo abrir la cámara {config.CAMERA_INDEX}.")
        else:
            print(f"[CameraManager] Iniciado con OpenCV VideoCapture({config.CAMERA_INDEX}).")

    def read_frame(self) -> Optional[np.ndarray]:
        """Obtiene un fotograma en formato BGR de OpenCV."""
        frame = None
        if self.is_picam:
            frame_rgb = self.picam2.capture_array()
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        elif self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                return None

        if frame is None:
            return None

        # Si el fotograma es 100% negro en macOS, suele ser por falta de permisos de cámara en Terminal
        if not self._black_frame_warned and frame.mean() == 0.0:
            print("\n[CameraManager] ⚠️  ATENCIÓN: La cámara está devolviendo fotogramas completamente negros.")
            print("[CameraManager] 👉 En macOS esto ocurre cuando 'Terminal' no tiene permiso de acceso a la Cámara.")
            print("[CameraManager]    Ve a: Ajustes del Sistema -> Privacidad y Seguridad -> Cámara -> Activa 'Terminal'.")
            print("[CameraManager] 👉 O si tienes iPhone/Continuity, prueba cambiar CAMERA_INDEX = 1 en config.py.\n")
            self._black_frame_warned = True

        # 1. Efecto espejo (selfie frontal)
        if config.MIRROR_HORIZONTAL:
            frame = cv2.flip(frame, 1)

        # 2. Recorte a proporción 4:5 vertical (tipo abismoCam de celular)
        if config.ASPECT_RATIO_4_5:
            frame = self._crop_to_4_5(frame)

        return frame

    def _crop_to_4_5(self, frame: np.ndarray) -> np.ndarray:
        """Recorta el centro de la imagen para que coincida con una proporción 4:5 vertical."""
        h, w, _ = frame.shape
        target_aspect = 4.0 / 5.0
        current_aspect = w / h

        if current_aspect > target_aspect:
            # La imagen es más ancha de lo deseado; recortar laterales
            new_w = int(h * target_aspect)
            start_x = (w - new_w) // 2
            return frame[:, start_x:start_x + new_w]
        elif current_aspect < target_aspect:
            # La imagen es más alta de lo deseado; recortar arriba/abajo
            new_h = int(w / target_aspect)
            start_y = (h - new_h) // 2
            return frame[start_y:start_y + new_h, :]
        return frame

    def release(self):
        if self.is_picam:
            self.picam2.stop()
        elif self.cap:
            self.cap.release()
        print("[CameraManager] Cámara liberada.")
