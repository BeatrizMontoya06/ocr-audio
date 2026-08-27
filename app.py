import streamlit as st
import os
import cv2
import numpy as np
import pytesseract
from gtts import gTTS


# -----------------------------------
# CONFIGURACIÓN
# -----------------------------------

st.set_page_config(
    page_title="Imagen a Audio",
    page_icon="🔊"
)


# -----------------------------------
# TÍTULO
# -----------------------------------

st.title("🖼️ Transcripción de Imagen a Audio")
st.write("Toma una foto o carga una imagen para convertir su texto en audio.")


# -----------------------------------
# SELECCIONAR FUENTE DE IMAGEN
# -----------------------------------

st.subheader("1. Selecciona una imagen")

opcion = st.radio(
    "¿De dónde quieres obtener la imagen?",
    ("Cámara", "Cargar imagen")
)


# -----------------------------------
# CÁMARA
# -----------------------------------

img_file_buffer = None

if opcion == "Cámara":

    img_file_buffer = st.camera_input("Toma una foto")


# -----------------------------------
# CARGAR IMAGEN
# -----------------------------------

else:

    img_file_buffer = st.file_uploader(
        "Selecciona una imagen",
        type=["png", "jpg", "jpeg"]
    )


# -----------------------------------
# PROCESAR IMAGEN
# -----------------------------------

if img_file_buffer is not None:

    bytes_data = img_file_buffer.getvalue()

    cv2_img = cv2.imdecode(
        np.frombuffer(bytes_data, np.uint8),
        cv2.IMREAD_COLOR
    )

    # Convertir la imagen a RGB
    img_rgb = cv2.cvtColor(
        cv2_img,
        cv2.COLOR_BGR2RGB
    )

    # Mostrar imagen
    st.subheader("2. Imagen seleccionada")

    st.image(
        img_rgb,
        caption="Imagen",
        use_container_width=True
    )


    # -----------------------------------
    # RECONOCIMIENTO DEL TEXTO
    # -----------------------------------

    st.subheader("3. Texto transcrito")

    text = pytesseract.image_to_string(img_rgb)

    if text.strip():

        st.text_area(
            "Texto encontrado:",
            text,
            height=150
        )


        # -----------------------------------
        # CONVERTIR TEXTO A AUDIO
        # -----------------------------------

        st.subheader("4. Escuchar texto")

        if st.button("🔊 Reproducir texto"):

            tts = gTTS(
                text=text,
                lang="es"
            )

            audio_file = "texto.mp3"

            tts.save(audio_file)

            with open(audio_file, "rb") as audio:
                audio_bytes = audio.read()

            st.audio(
                audio_bytes,
                format="audio/mp3"
            )

            st.success("Texto convertido a audio.")


    else:

        st.warning(
            "No se encontró texto en la imagen. "
            "Intenta con una imagen más clara."
        )


# -----------------------------------
# INFORMACIÓN LATERAL
# -----------------------------------

with st.sidebar:

    st.header("¿Cómo funciona?")

    st.write(
        "Esta aplicación utiliza OCR para "
        "reconocer el texto de una imagen."
    )

    st.write(
        "Después, convierte el texto reconocido "
        "en audio para poder escucharlo."
    )
