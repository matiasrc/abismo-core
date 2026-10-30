import os
import platform
from pathlib import Path

# --- DETECCIÓN DE ENTORNO ---
# Detecta si se ejecuta en Raspberry Pi (Linux ARM) o en PC/Mac
IS_RASPBERRY_PI = platform.machine() in ("aarch64", "armv7l") and "Linux" in platform.system()

# --- RUTAS DE DIRECTORIO ---
BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR / "repositorio"
CAPTURES_DIR = REPO_DIR / "capturas"
FACCIONES_DIR = REPO_DIR / "facciones"

# Asegurar directorios
CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
FACCIONES_DIR.mkdir(parents=True, exist_ok=True)

# --- VIDEO Y PANTALLA ---
# En Raspberry Pi usamos resolución interna optimizada; en PC/Mac podemos usar mayor definición.
CAMERA_INDEX = 1
CAPTURE_WIDTH = 640 if IS_RASPBERRY_PI else 1280
CAPTURE_HEIGHT = 480 if IS_RASPBERRY_PI else 720
TARGET_FPS = 25 if IS_RASPBERRY_PI else 30

# Proporción de aspecto vertical tipo celular (4:5)
ASPECT_RATIO_4_5 = True
MIRROR_HORIZONTAL = True  # Modo selfie (efecto espejo)

# Modo de pantalla: En Mac para pruebas conviene False (ventana), en la Pi True (fullscreen)
FULLSCREEN = IS_RASPBERRY_PI
WINDOW_SIZE = (640, 800) if not FULLSCREEN else (0, 0)

# --- BOTÓN FÍSICO / ENTRADA ---
GPIO_PIN_BUTTON = 17  # Pin GPIO físico en Raspberry Pi
JOYSTICK_BUTTON_INDEX = 0  # Botón en encoder Arcade USB

# --- TIEMPOS DE LA INSTALACIÓN (Segundos) ---
COUNTDOWN_SECONDS = 5
RESULT_DISPLAY_SECONDS = 5
IDLE_TIMEOUT_SECONDS = 30  # Tiempo sin interacción antes de pasar a modo Galería/Salvapantallas

# --- RED (OSC & NDI) ---
ENABLE_NDI = True
NDI_STREAM_NAME = "abismoCam_Python"

ENABLE_OSC = True
# IP o hostname de la PC Central receptora (puede ser IP o nombre .local ej. "pc3.local")
OSC_RECEIVER_IP = os.getenv("OSC_RECEIVER_IP", "192.168.0.30")
OSC_RECEIVER_PORT = int(os.getenv("OSC_RECEIVER_PORT", "9000"))
OSC_ADDRESS_TRIGGER = "/camara/disparo"
