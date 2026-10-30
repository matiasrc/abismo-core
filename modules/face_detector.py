import cv2
import numpy as np
from typing import Optional, Dict, Any

class FaceDetector:
    """
    Detector de rostros modular y tolerante a fallos:
    - Intenta usar MediaPipe si está instalado.
    - Intenta usar OpenCV CascadeClassifier si la versión de OpenCV lo soporta (OpenCV 4).
    - Si no está disponible (ej. OpenCV 5 o paquetes mínimos), usa una estimación de encuadre
      facial central para selfie vertical 4:5, garantizando que el programa jamás crashee.
    """
    def __init__(self):
        self.use_mediapipe = False
        self.face_cascade = None

        # 1. Intentar cargar MediaPipe
        try:
            import mediapipe as mp
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.use_mediapipe = True
            print("[FaceDetector] MediaPipe Face Mesh cargado con éxito.")
            return
        except Exception:
            pass

        # 2. Intentar cargar OpenCV CascadeClassifier (disponible en OpenCV 4)
        if hasattr(cv2, "CascadeClassifier") and hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
            try:
                cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                if not self.face_cascade.empty():
                    print("[FaceDetector] OpenCV Haar Cascade cargado con éxito.")
                    return
            except Exception:
                self.face_cascade = None

        # 3. Fallback inteligente
        print("[FaceDetector] Modo selfie central activo (estimación de rostro para encuadre 4:5).")

    def detect(self, frame: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Retorna diccionario con datos del rostro principal:
        {
            "bbox": (x, y, w, h),
            "center": (cx, cy),
            "landmarks": [...] o None
        }
        """
        h, w, _ = frame.shape

        # 1. MediaPipe
        if self.use_mediapipe:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                xs = [int(p.x * w) for p in landmarks]
                ys = [int(p.y * h) for p in landmarks]
                min_x, max_x = max(0, min(xs)), min(w, max(xs))
                min_y, max_y = max(0, min(ys)), min(h, max(ys))
                bbox = (min_x, min_y, max_x - min_x, max_y - min_y)
                return {
                    "bbox": bbox,
                    "center": (min_x + (max_x - min_x) // 2, min_y + (max_y - min_y) // 2),
                    "landmarks": landmarks
                }

        # 2. OpenCV CascadeClassifier
        if self.face_cascade is not None and not self.face_cascade.empty():
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            small_gray = cv2.resize(gray, (0, 0), fx=0.5, fy=0.5)
            faces = self.face_cascade.detectMultiScale(small_gray, scaleFactor=1.2, minNeighbors=4, minSize=(30, 30))
            if len(faces) > 0:
                faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                fx, fy, fw, fh = faces[0]
                bbox = (fx * 2, fy * 2, fw * 2, fh * 2)
                return {
                    "bbox": bbox,
                    "center": (bbox[0] + bbox[2] // 2, bbox[1] + bbox[3] // 2),
                    "landmarks": None
                }

        # 3. Fallback estimado: En formato selfie vertical 4:5, la cara está en el centro superior
        box_w = int(w * 0.55)
        box_h = int(h * 0.45)
        box_x = int((w - box_w) // 2)
        box_y = int(h * 0.18)
        return {
            "bbox": (box_x, box_y, box_w, box_h),
            "center": (box_x + box_w // 2, box_y + box_h // 2),
            "landmarks": None
        }
