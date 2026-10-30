# abismo-core

Estación interactiva de captura, procesamiento visual en tiempo real, streaming NDI y control OSC para la instalación artística **"El abismo de la visibilidad"** (Lisandro Peralta / Colectivo Biopus).

Diseñado para ejecutarse de forma agnóstica tanto en **PC / Mac** como en una **Raspberry Pi 4**.

---

## 🎯 ¿Qué hace este sistema?

1. **Captura y Formato Espejo:** Toma la señal de cámara (webcam USB en PC/Mac o cámara ribbon CSI en Raspberry Pi), aplica efecto espejo y la recorta a proporción vertical **4:5** (formato teléfono / selfie).
2. **Streaming NDI:** Envía la imagen de video continuo a la red local mediante protocolo NDI High Bandwidth para que **TouchDesigner** y **OBS** la reciban en las computadoras de la sala.
3. **Interacción y Conteo:** Al presionar un botón (físico arcade vía GPIO/USB o tecla `ESPACIO`), inicia una cuenta regresiva de **5 segundos**.
4. **Cadena de Efectos Progresiva:** Durante los 5 segundos, una serie de efectos visuales independientes (glitch, aberración cromática, deformaciones faciales, efecto Frankenstein) van incrementando su intensidad.
5. **Disparo y Guardado:** Al llegar a cero, se produce un flash blanco, se envía un mensaje de disparo OSC (`/camara/disparo 0`) a las máquinas receptoras (PC Central / Mappings), se guarda la foto intervenida en `repositorio/capturas/` y se muestra en pantalla completa durante unos segundos.
6. **Modo Galería / Salvapantallas (IDLE):** Si transcurren `N` segundos sin que nadie toque el botón, la pantalla proyecta aleatoriamente las capturas de visitantes anteriores (memoria colectiva).

---

## 🚀 Instalación y Puesta en Marcha Rápida

### 1. Clonar el repositorio
```bash
git clone https://github.com/matiasrc/abismo-core.git
cd abismo-core
```

### 2. Instalar dependencias
Se recomienda Python 3.9 o posterior:
```bash
# En macOS / Linux:
python3 -m pip install -r requirements.txt
```

### 3. Ejecutar
```bash
python3 main.py
```
* **En Mac / PC:** Se abre en modo ventana vertical `640x800`. Pulsa la tecla **ESPACIO** o haz **clic** en la ventana para disparar la cuenta regresiva. Pulsa **ESC** para salir.
* **En Raspberry Pi:** Se ejecuta automáticamente a **pantalla completa** (HDMI) y escucha el botón físico en el pin **GPIO 17**.

---

## 🧩 Arquitectura Modular

```
abismo-core/
├── config.py                 # Ajustes globales y auto-detección (Pi vs Mac/PC)
├── main.py                   # Orquestador del ciclo de vida (Máquina de estados)
├── effects/                  # 👈 SUBSISTEMA DE EFECTOS DESACOPLADO
│   ├── base.py               # Clase abstracta BaseEffect
│   ├── pipeline.py           # Gestor de cadena de efectos (Pipeline)
│   ├── glitch.py             # Aberración cromática y corte de tiras (slice)
│   ├── blur_face.py          # Desenfoque selectivo
│   └── frankenstein.py       # Trasplante e inversión de regiones faciales
├── modules/                  # Subsistemas de hardware y plataforma
│   ├── camera.py             # Captura (Picamera2 en Pi / OpenCV en PC/Mac)
│   ├── display.py            # Motor gráfico Pygame (fullscreen, textos, flash)
│   ├── face_detector.py      # Detección facial tolerante a fallos
│   ├── input_btn.py          # Botón GPIO 17, Arcade USB o teclado
│   ├── network.py            # Emisor NDI y cliente OSC
│   └── repository.py         # Base de datos local de capturas y facciones
└── repositorio/              # Almacén de fotos y recortes históricos
    ├── capturas/
    └── facciones/
```

---

## 🎨 ¿Quieres crear o sumar nuevos efectos visuales?

¡El sistema fue diseñado específicamente para que cualquier artista o programador pueda crear sus propios filtros sin tocar el código central!

👉 Consulta la guía paso a paso en **[CONTRIBUTING_EFFECTS.md](CONTRIBUTING_EFFECTS.md)** para aprender a crear una rama, programar tu clase de efecto y enviar un Pull Request.

---

## ⚙️ Configuración (`config.py`)

Todos los parámetros se ajustan en un solo lugar sin modificar la lógica:

* `FULLSCREEN`: `True` para pantalla completa (por defecto activo en Raspberry Pi).
* `COUNTDOWN_SECONDS`: Duración del conteo regresivo (por defecto 5 segundos).
* `IDLE_TIMEOUT_SECONDS`: Segundos de inactividad antes de pasar a modo galería de fotos previas.
* `ENABLE_NDI`: Activa o desactiva la transmisión NDI.
* `OSC_RECEIVER_IP` / `OSC_RECEIVER_PORT`: Destino de los mensajes de disparo OSC.

---

## 📄 Licencia y Créditos
Desarrollado para la obra de arte interactivo **"El abismo de la visibilidad"** — Colectivo Biopus.
