import sys
import time
import math
import pygame
from enum import Enum, auto

import config
from modules.camera import CameraManager
from modules.face_detector import FaceDetector
from modules.input_btn import InputManager
from modules.display import DisplayManager
from modules.network import NetworkManager
from modules.repository import RepositoryManager

# Importamos el pipeline y los efectos independientes
from effects import EffectPipeline, GlitchEffect, BlurFaceEffect, FrankensteinEffect

class AppState(Enum):
    PREVIEW = auto()        # Vista previa en vivo (esperando a que toquen el botón)
    COUNTDOWN = auto()      # Cuenta de 5 segundos con efectos progresivos
    FLASH_CAPTURE = auto()  # Destello de flash y guardado
    DISPLAY_RESULT = auto() # Exhibición del resultado en pantalla
    IDLE = auto()           # Salvapantallas / Galería cuando no hay nadie

def main():
    print("========================================")
    print("  Iniciando abismoCam (Python Core)     ")
    print(f"  Plataforma: {'Raspberry Pi' if config.IS_RASPBERRY_PI else 'PC/Mac'}")
    print("========================================")

    # 1. Inicialización de subsistemas
    camera = CameraManager()
    detector = FaceDetector()
    display = DisplayManager()
    network = NetworkManager()
    repository = RepositoryManager()

    # 2. Configuración del Pipeline de Efectos Modular e Independiente
    # ¡Aquí puedes agregar, quitar o cambiar cualquier efecto sin tocar nada más!
    pipeline = EffectPipeline()
    pipeline.register(GlitchEffect(name="glitch", max_shift=20, enabled=True))
    pipeline.register(FrankensteinEffect(name="frankenstein", enabled=True))
    pipeline.register(BlurFaceEffect(name="blur_face", blur_amount=25, enabled=False))

    print(f"[Main] Efectos cargados en pipeline: {pipeline.list_effects()}")

    # 3. Variables de Estado
    current_state = AppState.PREVIEW
    countdown_start_time = 0.0
    display_result_start_time = 0.0
    last_interaction_time = time.time()
    last_gallery_change_time = 0.0

    captured_result_frame = None
    last_face_data = None

    clock = pygame.time.Clock()
    running = True

    # Callback para cuando se presiona el botón físico o teclado
    def on_button_pressed():
        nonlocal current_state, countdown_start_time, last_interaction_time
        last_interaction_time = time.time()

        if current_state in (AppState.PREVIEW, AppState.IDLE):
            print("\n>>> ¡DISPARO DETECTADO! Iniciando cuenta regresiva...")
            current_state = AppState.COUNTDOWN
            countdown_start_time = time.time()
            network.send_osc_trigger(1)  # OSC 1 al iniciar conteo

    input_mgr = InputManager(on_trigger=on_button_pressed)

    try:
        while running:
            # Procesar eventos de Pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    input_mgr.handle_pygame_event(event)

            # Verificar botón GPIO en la Pi si aplica
            if input_mgr.is_gpio_pressed():
                on_button_pressed()

            now = time.time()

            # Capturar fotograma de la cámara
            frame = camera.read_frame()
            if frame is None:
                clock.tick(10)
                continue

            # Transmitir video puro a NDI (hacia TouchDesigner / OBS en la red)
            network.send_ndi_frame(frame)

            # ==========================================
            # MÁQUINA DE ESTADOS
            # ==========================================

            # --- ESTADO 1: PREVIEW (Cámara en vivo esperando interacción) ---
            if current_state == AppState.PREVIEW:
                # Comprobar si pasó a modo reposo (IDLE)
                if now - last_interaction_time > config.IDLE_TIMEOUT_SECONDS:
                    print("[Main] Tiempo de inactividad alcanzado. Pasando a modo IDLE (Galería)...")
                    current_state = AppState.IDLE
                else:
                    display.render_frame(frame, banner_text="Toca el botón para disparar")

            # --- ESTADO 2: COUNTDOWN (Cuenta regresiva de 5 segundos con efectos) ---
            elif current_state == AppState.COUNTDOWN:
                elapsed = now - countdown_start_time
                remaining = config.COUNTDOWN_SECONDS - elapsed

                if remaining > 0:
                    # Progreso de 0.0 a 1.0 para aumentar la intensidad de los efectos
                    progress = min(1.0, elapsed / config.COUNTDOWN_SECONDS)

                    # Detectar rostro
                    face_data = detector.detect(frame)
                    last_face_data = face_data

                    # Aplicar la cadena de efectos independiente
                    processed_frame = pipeline.process(frame, face_data=face_data, progress=progress)

                    # Mostrar fotograma con el número gigante en pantalla
                    display.render_frame(processed_frame, countdown_number=int(math.ceil(remaining)))
                else:
                    # Fin de la cuenta -> Disparo
                    current_state = AppState.FLASH_CAPTURE

            # --- ESTADO 3: FLASH_CAPTURE (Destello y guardado de imagen) ---
            elif current_state == AppState.FLASH_CAPTURE:
                print(">>> ¡FLASH Y CAPTURA!")
                display.trigger_flash()
                network.send_osc_trigger(0)  # OSC 0 al terminar

                # Aplicar efectos a máxima intensidad (1.0) para la foto final
                face_data = detector.detect(frame)
                final_frame = pipeline.process(frame, face_data=face_data, progress=1.0)

                # Guardar en repositorio
                repository.save_capture(final_frame, face_data=face_data)

                captured_result_frame = final_frame
                display_result_start_time = now
                current_state = AppState.DISPLAY_RESULT

            # --- ESTADO 4: DISPLAY_RESULT (Exhibición del resultado) ---
            elif current_state == AppState.DISPLAY_RESULT:
                if captured_result_frame is not None:
                    display.render_frame(captured_result_frame, banner_text="[ Captura procesada ]")

                # Mantener la foto congelada durante RESULT_DISPLAY_SECONDS
                if now - display_result_start_time > config.RESULT_DISPLAY_SECONDS:
                    print("[Main] Fin de exhibición. Volviendo a PREVIEW.")
                    last_interaction_time = now
                    current_state = AppState.PREVIEW

            # --- ESTADO 5: IDLE (Galería / Salvapantallas cuando no hay nadie) ---
            elif current_state == AppState.IDLE:
                if now - last_gallery_change_time > 4.0:
                    img_path = repository.get_random_gallery_image()
                    if img_path:
                        display.render_gallery_image(img_path)
                    else:
                        # Si aún no hay fotos guardadas, mostrar cámara en vivo
                        display.render_frame(frame, banner_text="Presiona el botón para comenzar")
                    last_gallery_change_time = now

            clock.tick(config.TARGET_FPS)

    except KeyboardInterrupt:
        print("\n[Main] Interrupción por teclado.")
    finally:
        print("[Main] Cerrando recursos...")
        camera.release()
        network.release()
        display.quit()
        print("[Main] Aplicación cerrada limpiamente.")

if __name__ == "__main__":
    main()
