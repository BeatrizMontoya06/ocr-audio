import streamlit as st
import cv2
import numpy as np
import pytesseract
from gtts import gTTS
import base64
import io

# Configuración de página
st.set_page_config(
    page_title="Bee's Vision OCR v1.0 - Retro Y2K",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar estado del audio
if "audio_b64" not in st.session_state:
    st.session_state.audio_b64 = None

# Inyección CSS Global para la estética Y2K
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

    .stApp {
        background-color: #008080 !important;
        background-image: 
            radial-gradient(#40e0d0 15%, transparent 16%),
            radial-gradient(#004040 15%, transparent 16%) !important;
        background-size: 16px 16px !important;
        font-family: 'MS Sans Serif', Tahoma, sans-serif !important;
    }

    div[data-testid="stVerticalBlock"] > div {
        background: #c0c0c0;
        border: 3px solid;
        border-color: #ffffff #808080 #808080 #ffffff;
        padding: 12px;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.5);
    }

    label, p, h1, h2, h3, span {
        color: #000000 !important;
        font-family: 'MS Sans Serif', Tahoma, sans-serif !important;
    }

    textarea, div[data-baseweb="select"], div[data-testid="stFileUploader"], div[data-testid="stCameraInput"] {
        background-color: #ffffff !important;
        border: 2px inset #808080 !important;
        font-family: monospace !important;
        color: #000000 !important;
    }

    .stButton > button {
        background: #c0c0c0 !important;
        color: #000000 !important;
        border: 2px solid !important;
        border-color: #ffffff #808080 #808080 #ffffff !important;
        font-weight: bold !important;
        font-size: 13px !important;
        border-radius: 0px !important;
        box-shadow: 2px 2px 0px #000000 !important;
    }

    .stButton > button:active {
        border-color: #808080 #ffffff #ffffff #808080 !important;
        box-shadow: inset 1px 1px 0px #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado Ventana Y2K
y2k_header = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
        body { font-family: Tahoma, sans-serif; margin: 0; background: transparent; }
        .title-bar {
            background: linear-gradient(90deg, #000080, #1084d0);
            color: white; padding: 4px 8px; font-weight: bold; font-size: 14px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .win-btn {
            width: 16px; height: 14px; background: #c0c0c0; border: 1px solid;
            border-color: #ffffff #808080 #808080 #ffffff; font-size: 9px;
            text-align: center; font-weight: bold; color: #000; display: inline-block;
        }
        marquee {
            background: #000; color: #00ff00; font-family: 'VT323', monospace;
            font-size: 20px; padding: 4px; border: 2px inset #808080; margin: 8px 0;
        }
        .retro-info {
            border: 2px inset #ffffff; background: #e0e0e0; padding: 8px; margin-bottom: 8px;
        }
        .retro-info h2 {
            margin: 0 0 4px 0; font-size: 13px; background: #000080; color: #fff; padding: 2px 6px;
        }
    </style>
</head>
<body>
    <div class="title-bar">
        <span>🐝 C:\\BEES_VISION\\v1.0\\OCR_TO_SPEECH.EXE</span>
        <div>
            <div class="win-btn">_</div>
            <div class="win-btn">□</div>
            <div class="win-btn">✕</div>
        </div>
    </div>
    <marquee scrollamount="5">
        *** BEE'S VISION OCR Y2K *** ESCANEO INTELIGENTE DE IMÁGENES Y LECTURA EN VOZ ALTA ***
    </marquee>
    <div class="retro-info">
        <h2>🎯 PROPÓSITO DEL SISTEMA (ACCESIBILIDAD DIGITAL)</h2>
        <p style="font-size: 12px; margin: 2px 0;">
            Herramienta diseñada para asistir a personas con visibilidad reducida o dificultades lectoras. Captura cualquier texto impreso (documentos, carteles, libros) con tu cámara o archivo y escúchalo al instante en audio.
        </p>
    </div>
</body>
</html>
"""
st.components.v1.html(y2k_header, height=195)

# Selección de Origen de Imagen
st.markdown("### 📷 1. Captura u Obtención de Imagen")
opcion = st.radio(
    "Selecciona el método de entrada:",
    ("Subir Archivo de Imagen", "Usar Cámara en Vivo"),
    horizontal=True
)

img_file_buffer = None

if opcion == "Usar Cámara en Vivo":
    img_file_buffer = st.camera_input("Toma una fotografía al texto")
else:
    img_file_buffer = st.file_uploader(
        "Selecciona un archivo de imagen (PNG, JPG, JPEG):",
        type=["png", "jpg", "jpeg"]
    )

if img_file_buffer is not None:
    # Decodificar imagen
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

    st.markdown("### 🖼️ 2. Vista Previa de la Imagen")
    st.image(img_rgb, caption="Imagen cargada", use_container_width=True)

    # Procesar OCR con Tesseract
    st.markdown("### 🔍 3. Escaneo y Extracción OCR")
    with st.spinner("Procesando la imagen con motor Tesseract..."):
        text = pytesseract.image_to_string(img_rgb)

    if text.strip():
        st.text_area(
            "Texto detectado:",
            value=text,
            height=140
        )

        st.markdown("### 🔊 4. Generación de Audio")
        if st.button("▶️ ESCUCHAR TEXTO EN LA PÁGINA"):
            with st.spinner("Sintetizando voz..."):
                try:
                    tts = gTTS(text=text, lang="es", slow=False)
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    
                    audio_bytes = fp.read()
                    b64 = base64.b64encode(audio_bytes).decode()
                    st.session_state.audio_b64 = b64

                except Exception as e:
                    st.error(f"Error generando el audio: {e}")

        # Reproductor Autoplay Y2K
        if st.session_state.audio_b64 is not None:
            player_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    .player-card {{
                        background: #e0e0e0;
                        border: 2px inset #ffffff;
                        padding: 10px;
                        text-align: center;
                        font-family: Tahoma, sans-serif;
                        margin-top: 10px;
                    }}
                    audio {{ width: 100%; margin-top: 6px; }}
                    .status {{
                        color: #008000; font-weight: bold; font-size: 12px;
                        background: #000; padding: 4px; border: 1px inset #808080;
                    }}
                </style>
            </head>
            <body>
                <div class="player-card">
                    <div class="status">🔊 REPRODUCIENDO TEXTO ESCANEADO...</div>
                    <audio controls autoplay>
                        <source src="data:audio/mp3;base64,{st.session_state.audio_b64}" type="audio/mp3">
                    </audio>
                </div>
            </body>
            </html>
            """
            st.components.v1.html(player_html, height=120)

    else:
        st.warning("⚠️ No se encontró texto inteligible en la imagen. Intenta tomar una fotografía con mayor iluminación o enfoque.")
