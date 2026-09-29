import streamlit as st
import cv2
import numpy as np
import pytesseract
from gtts import gTTS
import base64
import io

# Configuración inicial de la página
st.set_page_config(
    page_title="Bee's OCR v1.0 - Retro Y2K Edition",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estado para la persistencia del audio en la sesión
if "audio_b64" not in st.session_state:
    st.session_state.audio_b64 = None

# Estilos CSS con temática Retro Y2K / Windows 98
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

# Ventana con interfaz Y2K y contexto del proyecto
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
            border: 2px inset #ffffff; background: #e0e0e0; padding: 10px; margin-bottom: 8px;
        }
        .retro-info h2 {
            margin: 0 0 6px 0; font-size: 13px; background: #000080; color: #fff; padding: 3px 6px;
        }
    </style>
</head>
<body>
    <div class="title-bar">
        <span>🐝 C:\\BEES_OCR\\v1.0\\VISION_READER.EXE</span>
        <div>
            <div class="win-btn">_</div>
            <div class="win-btn">□</div>
            <div class="win-btn">✕</div>
        </div>
    </div>
    <marquee scrollamount="5">
        *** BEE'S OCR v1.0 *** RECONOCIMIENTO ÓPTICO DE CARACTERES Y SÍNTESIS DE VOZ ***
    </marquee>
    <div class="retro-info">
        <h2>📜 PROPÓSITO DEL SISTEMA Y CONTEXTO DE USO</h2>
        <p style="font-size: 12px; margin: 2px 0; line-height: 1.4;">
            <b>Bee's OCR</b> es una solución asistencial digital diseñada para la digitalización instantánea de material impreso. Su propósito principal es mejorar la <b>accesibilidad para personas con discapacidad visual, dislexia o dificultades de lectura</b>, permitiendo transformar libros, documentos, carteles o empaques en audio ejecutable en tiempo real mediante visión por computadora.
        </p>
    </div>
</body>
</html>
"""
st.components.v1.html(y2k_header, height=210)

# ---------------------------------------------------------
# 1. SELECCIÓN DE ENTRADA
# ---------------------------------------------------------
st.markdown("### 📷 1. Captura u Obtención de Imagen")
opcion = st.radio(
    "Selecciona el método de entrada para la captura:",
    ("Subir Archivo de Imagen", "Cámara Web en Vivo"),
    horizontal=True
)

img_file_buffer = None

if opcion == "Cámara Web en Vivo":
    img_file_buffer = st.camera_input("Capturar fotografía al texto impreso")
else:
    img_file_buffer = st.file_uploader(
        "Selecciona un archivo de imagen (Formatos admitidos: PNG, JPG, JPEG):",
        type=["png", "jpg", "jpeg"]
    )

# ---------------------------------------------------------
# 2. PROCESAMIENTO Y VISUALIZACIÓN
# ---------------------------------------------------------
if img_file_buffer is not None:
    # Decodificación de la imagen cargada con OpenCV
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

    st.markdown("### 🖼️ 2. Imagen en Inspección")
    st.image(img_rgb, caption="Muestra cargada correctamente", use_container_width=True)

    # ---------------------------------------------------------
    # 3. EXTRACCIÓN DE TEXTO (OCR CON TESSERACT)
    # ---------------------------------------------------------
    st.markdown("### 🔍 3. Escaneo OCR (Tesseract Engine)")
    with st.spinner("Procesando matriz de imagen y extrayendo caracteres..."):
        try:
            # Intento de lectura con soporte de idioma español e inglés
            extracted_text = pytesseract.image_to_string(img_rgb, lang="spa+eng")
        except Exception:
            # Fallback en caso de que solo esté disponible el paquete genérico
            extracted_text = pytesseract.image_to_string(img_rgb)

    if extracted_text.strip():
        st.text_area(
            "Texto detectado:",
            value=extracted_text,
            height=140
        )

        # ---------------------------------------------------------
        # 4. SÍNTESIS DE VOZ Y REPRODUCCIÓN
        # ---------------------------------------------------------
        st.markdown("### 🔊 4. Conversión a Audio Asistivo")
        if st.button("▶️ GENERAR Y ESCUCHAR AUDIO EN VIVO"):
            with st.spinner("Sintetizando voz en alta definición..."):
                try:
                    tts = gTTS(text=extracted_text, lang="es", slow=False)
                    fp = io.BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    
                    audio_bytes = fp.read()
                    b64 = base64.b64encode(audio_bytes).decode()
                    st.session_state.audio_b64 = b64

                except Exception as e:
                    st.error(f"Error durante el proceso de síntesis de voz: {e}")

        # Reproductor incrustado HTML5
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
                    <div class="status">🔊 REPRODUCIENDO TEXTO DETECTADO POR BEE'S OCR...</div>
                    <audio controls autoplay>
                        <source src="data:audio/mp3;base64,{st.session_state.audio_b64}" type="audio/mp3">
                    </audio>
                </div>
            </body>
            </html>
            """
            st.components.v1.html(player_html, height=120)

    else:
        st.warning("⚠️ No se logró identificar texto legible en la imagen. Asegúrate de enfocar bien el texto y contar con una iluminación adecuada.")
