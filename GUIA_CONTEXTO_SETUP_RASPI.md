# PROMPT DE CONTEXTO PARA CONFIGURAR LA RASPBERRY PI 4
> **Instrucciones para el usuario:** Copia y pega todo el texto de este documento en tu nueva conversación con Gemini o ChatGPT para que tenga todo el contexto exacto del proyecto y te guíe paso a paso.

---

```markdown
Hola. Necesito que me guíes paso a paso para configurar una Raspberry Pi 4 (4GB) desde cero, para un proyecto de arte interactivo ("El abismo de la visibilidad"). 

Quiero configurar la Raspberry Pi sin monitor físico (modo headless) desde mi computadora de desarrollo que es una Mac.

Aquí tienes el contexto técnico exacto del proyecto y los componentes que tengo:

### 1. El Proyecto
Es una estación interactiva de captura (estilo fotocabina / selfie inteligente):
- Una cámara toma a la persona.
- Una pantalla muestra la vista en espejo de la cámara en orientación vertical (formato 4:5 tipo celular).
- Un botón físico (tipo arcade conectado a los pines GPIO de la Pi) inicia una cuenta regresiva de 5 segundos.
- Durante y al final de los 5 segundos, la aplicación aplica efectos y transformaciones faciales (glitch, desenfoque, deformaciones, mezclas de partes de caras).
- Guarda la foto/clip procesado en una carpeta local y la muestra en pantalla.
- Si no hay nadie por un tiempo (modo IDLE), la pantalla proyecta una galería aleatoria de capturas anteriores.
- La aplicación está siendo programada en **Python** (usando `picamera2`, `opencv`, `pygame`, `gpiozero`, `python-osc` y streaming de video `NDI`).
- En la sala de exposición aún no está definido si habrá un router con DHCP o simplemente un **switch de red cerrado**. Por lo tanto, la configuración debe ser flexible (resolución por nombre de red local `raspberrypi.local` vía mDNS/Bonjour o IPs configurables). Para la etapa de configuración inicial en mi taller/casa, la conectaré a mi red local para instalar paquetes.

### 2. El Hardware que tengo a mano
- **Raspberry Pi 4 Model B (4 GB de RAM)**.
- **Tarjeta MicroSD** y lector de tarjetas para conectarla a mi Mac.
- **Cámara:** Raspberry Pi Camera Module con cable plano ribbon CSI (y/o webcam USB).
- **Alimentación:** Cargador original Apple USB-C (de mi MacBook Air de 30W/35W o MacBook Pro de 61W con salida 5V 3A).
- **Red:** Conexión por cable de red Ethernet RJ45 y también Wi-Fi.
- **Botón:** Botón pulsador arcade para conectar entre el pin GPIO 17 y GND.
- **Computadora principal de control y desarrollo:** Una Mac con macOS y terminal/VS Code.

### 3. Lo que necesito que hagamos juntos, paso a paso:
1. Grabar la tarjeta MicroSD con **Raspberry Pi Imager** en mi Mac:
   - Necesito saber exactamente qué versión de sistema operativo elegir (debe ser Raspberry Pi OS Bookworm de 64 bits con Desktop).
   - Configurar los ajustes ocultos de Raspberry Pi Imager (activar SSH, usuario y contraseña, Wi-Fi y nombre de host `raspberrypi.local`).
2. Primer encendido y conexión por **SSH** desde la terminal de mi Mac para verificar que la Pi esté viva.
3. Configurar **acceso visual remoto (VNC o WayVNC / RDP)** para poder ver la pantalla gráfica de la Raspberry Pi en una ventana dentro de mi Mac (usando RealVNC Viewer u otra app).
4. Probar que la cámara ribbon CSI sea reconocida por el sistema mediante comandos de `libcamera` / `picam2`.
5. Instalar el entorno de dependencias necesarias en Python:
   - `python3-picamera2`
   - `python3-opencv`
   - `python3-pygame`
   - `python3-gpiozero`
   - `python-osc`
   - Soporte para NDI en Linux ARM64.
6. Dejar la Pi lista para recibir el código Python que estamos desarrollando en la Mac (vía Git o VS Code Remote SSH).

Por favor, no me des todos los pasos juntos en una sola respuesta gigante. Llévame paso a paso, esperando mi confirmación antes de avanzar al siguiente. Empecemos por el Paso 1 (grabar la tarjeta con Raspberry Pi Imager).
```
