import numpy as np
import config

class NetworkManager:
    """
    Gestor de red para OSC y streaming NDI:
    - Envía mensajes OSC `/camara/disparo 1` y `0`.
    - Transmite el video por NDI si la librería `ndi-python` está instalada.
    """
    def __init__(self):
        self.osc_client = None
        self.ndi_sender = None
        self.ndi_lib = None

        self._init_osc()
        self._init_ndi()

    def _init_osc(self):
        if not config.ENABLE_OSC:
            return
        try:
            from pythonosc import udp_client
            self.osc_client = udp_client.SimpleUDPClient(config.OSC_RECEIVER_IP, config.OSC_RECEIVER_PORT)
            print(f"[NetworkManager] OSC activo hacia {config.OSC_RECEIVER_IP}:{config.OSC_RECEIVER_PORT}")
        except Exception as e:
            print(f"[NetworkManager] Error inicializando OSC ({e}).")

    def _init_ndi(self):
        if not config.ENABLE_NDI:
            return
        try:
            import NDIlib as ndi
            self.ndi_lib = ndi
            if not ndi.initialize():
                print("[NetworkManager] No se pudo inicializar SDK NDI.")
                return

            send_settings = ndi.SendCreate()
            send_settings.ndi_name = config.NDI_STREAM_NAME
            self.ndi_sender = ndi.send_create(send_settings)
            print(f"[NetworkManager] NDI activo emitiendo como '{config.NDI_STREAM_NAME}'.")
        except ImportError:
            print("[NetworkManager] Librería 'ndi-python' no encontrada; modo NDI desactivado (Dry-run).")
        except Exception as e:
            print(f"[NetworkManager] Error al inicializar NDI ({e}).")

    def send_osc_trigger(self, state: int):
        """
        Envía `/camara/disparo` con entero 1 (comienza conteo) o 0 (termina conteo).
        """
        if self.osc_client:
            try:
                self.osc_client.send_message(config.OSC_ADDRESS_TRIGGER, int(state))
                print(f"[NetworkManager] OSC enviado: {config.OSC_ADDRESS_TRIGGER} -> {state}")
            except Exception as e:
                print(f"[NetworkManager] Error enviando OSC ({e})")

    def send_ndi_frame(self, frame_bgr: np.ndarray):
        """Envía un fotograma BGR a la red NDI."""
        if not self.ndi_sender or not self.ndi_lib:
            return

        try:
            ndi = self.ndi_lib
            video_frame = ndi.VideoFrameV2()
            video_frame.data = frame_bgr
            video_frame.FourCC = ndi.FOURCC_VIDEO_TYPE_BGRX  # o BGRA
            ndi.send_send_video_v2(self.ndi_sender, video_frame)
        except Exception as e:
            pass

    def release(self):
        if self.ndi_sender and self.ndi_lib:
            self.ndi_lib.send_destroy(self.ndi_sender)
            self.ndi_lib.destroy()
            print("[NetworkManager] NDI liberado.")
