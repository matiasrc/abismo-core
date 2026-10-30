import pygame
import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import config

class DisplayManager:
    """
    Gestor de pantalla e interfaz gráfica usando Pygame:
    - Escala el video de la cámara para llenar la pantalla manteniendo proporción.
    - Dibuja la cuenta regresiva con números gigantes.
    - Aplica la animación de destello (flash blanco fotográfico).
    - Muestra la galería en modo de reposo (IDLE).
    """
    def __init__(self):
        pygame.init()
        pygame.font.init()

        if config.FULLSCREEN:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF)
            pygame.mouse.set_visible(False)
        else:
            self.screen = pygame.display.set_mode(config.WINDOW_SIZE, pygame.DOUBLEBUF)
            pygame.mouse.set_visible(True)

        pygame.display.set_caption("abismoCam - Python")
        self.screen_w, self.screen_h = self.screen.get_size()

        # Fuentes tipográficas
        self.font_countdown = pygame.font.SysFont("Arial", int(self.screen_h * 0.25), bold=True)
        self.font_small = pygame.font.SysFont("Arial", int(self.screen_h * 0.04), bold=False)

        # Superficie de Flash blanco para el disparo
        self.flash_alpha = 0
        self.flash_surface = pygame.Surface((self.screen_w, self.screen_h))
        self.flash_surface.fill((255, 255, 255))

    def trigger_flash(self):
        """Activa el destello de flash blanco al máximo."""
        self.flash_alpha = 255

    def render_frame(self, frame_bgr: np.ndarray, countdown_number: Optional[int] = None, banner_text: Optional[str] = None):
        """Dibuja un fotograma de OpenCV en la pantalla con los overlays correspondientes."""
        self.screen.fill((0, 0, 0))

        # 1. Convertir BGR de OpenCV a RGB de Pygame
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        fh, fw, _ = frame_rgb.shape

        # Escalar para encajar en la pantalla manteniendo la proporción
        scale = min(self.screen_w / fw, self.screen_h / fh)
        target_w, target_h = int(fw * scale), int(fh * scale)

        resized_rgb = cv2.resize(frame_rgb, (target_w, target_h))
        surface = pygame.image.frombuffer(resized_rgb.tobytes(), (target_w, target_h), "RGB")

        # Centrar en pantalla
        pos_x = (self.screen_w - target_w) // 2
        pos_y = (self.screen_h - target_h) // 2
        self.screen.blit(surface, (pos_x, pos_y))

        # 2. Dibujar número de cuenta regresiva (si está activo)
        if countdown_number is not None and countdown_number > 0:
            num_str = str(countdown_number)
            # Sombra negra
            shadow_txt = self.font_countdown.render(num_str, True, (0, 0, 0))
            shadow_rect = shadow_txt.get_rect(center=(self.screen_w // 2 + 4, self.screen_h // 2 + 4))
            self.screen.blit(shadow_txt, shadow_rect)
            # Texto blanco
            num_txt = self.font_countdown.render(num_str, True, (255, 255, 255))
            num_rect = num_txt.get_rect(center=(self.screen_w // 2, self.screen_h // 2))
            self.screen.blit(num_txt, num_rect)

        # 3. Dibujar texto opcional abajo
        if banner_text:
            txt = self.font_small.render(banner_text, True, (220, 220, 220))
            rect = txt.get_rect(center=(self.screen_w // 2, self.screen_h - 40))
            self.screen.blit(txt, rect)

        # 4. Dibujar desvanecimiento del Flash blanco
        if self.flash_alpha > 0:
            self.flash_surface.set_alpha(self.flash_alpha)
            self.screen.blit(self.flash_surface, (0, 0))
            self.flash_alpha = max(0, self.flash_alpha - 35)  # Se desvanece en ~7 cuadros

        pygame.display.flip()

    def render_gallery_image(self, image_path: Path):
        """Muestra una imagen estática del repositorio en pantalla completa."""
        if not image_path.exists():
            return

        img_bgr = cv2.imread(str(image_path))
        if img_bgr is not None:
            self.render_frame(img_bgr, banner_text="[ Memoria colectiva ]")

    def quit(self):
        pygame.quit()
