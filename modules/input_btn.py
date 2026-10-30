import pygame
import config
from typing import Callable, Optional

class InputManager:
    """
    Gestor unificado de entrada / botón de disparo:
    - Escucha la tecla ESPACIO / ENTER / Clic de mouse en Pygame.
    - Escucha botones de Joystick / Arcade USB Encoder.
    - Escucha el pin GPIO físico (Pin 17) en Raspberry Pi mediante `gpiozero`.
    """
    def __init__(self, on_trigger: Optional[Callable[[], None]] = None):
        self.on_trigger = on_trigger
        self.gpio_button = None
        self.joystick = None

        self._init_gpio()
        self._init_joystick()

    def _init_gpio(self):
        if config.IS_RASPBERRY_PI:
            try:
                from gpiozero import Button
                self.gpio_button = Button(config.GPIO_PIN_BUTTON, bounce_time=0.1)
                if self.on_trigger:
                    self.gpio_button.when_pressed = self.on_trigger
                print(f"[InputManager] Botón físico GPIO configurado en el pin {config.GPIO_PIN_BUTTON}.")
            except Exception as e:
                print(f"[InputManager] No se pudo inicializar GPIO ({e}).")

    def _init_joystick(self):
        if pygame.joystick.get_count() > 0:
            try:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print(f"[InputManager] Joystick/Arcade USB detectado: {self.joystick.get_name()}")
            except Exception as e:
                print(f"[InputManager] Error al inicializar joystick ({e}).")

    def handle_pygame_event(self, event: pygame.event.Event) -> bool:
        """
        Procesa eventos de Pygame. Retorna True si se detectó una orden de disparo.
        """
        triggered = False

        # 1. Teclado (ESPACIO o ENTER)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                triggered = True

        # 2. Pantalla táctil o clic de mouse
        elif event.type == pygame.MOUSEBUTTONDOWN:
            triggered = True

        # 3. Botón de Joystick Arcade USB
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == config.JOYSTICK_BUTTON_INDEX:
                triggered = True

        if triggered and self.on_trigger:
            self.on_trigger()

        return triggered

    def is_gpio_pressed(self) -> bool:
        if self.gpio_button:
            return self.gpio_button.is_pressed
        return False
