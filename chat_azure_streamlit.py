import streamlit as st
import PyPDF2
import requests
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()


# Función para extraer texto del PDF usando PyPDF2
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Interfaz de Streamlit
st.title("Chat con tu PDF usando herramientas de Microsoft")

# Subir el archivo PDF
pdf_file = st.file_uploader("Sube un archivo PDF", type=["pdf"])

if pdf_file is not None:
    # Mostrar el texto extraído
    extracted_text = extract_text_from_pdf(pdf_file)
    st.write("Texto extraído del PDF:")
    st.text_area("Texto PDF", extracted_text)

    # Mover el input de la pregunta fuera del botón
    user_question = st.text_input("Haz una pregunta sobre el PDF:")

    # Proceso de pregunta-respuesta con Azure OpenAI
    if st.button("Preguntar sobre el PDF"):
        if user_question:
            with st.spinner("Procesando la respuesta..."):
                try:
                    # Configuración del cliente de Azure OpenAI
                    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
                    api_key = os.getenv("AZURE_OPENAI_API_KEY")
                    

                    headers = {
                            "Content-Type": "application/json",
                            "api-key": api_key,
                        }

                    data = {
                        "model": "gpt-4o-mini", 
                        "messages": [
                            {"role": "system", "content": "Eres un asistente que responde preguntas basadas en contenido de PDF."},
                            {"role": "user", "content": f"El siguiente es un texto extraído de un PDF:\n\n{extracted_text}\n\nPregunta: {user_question}"}
                        ]
                    }

                    response = requests.post(
                        f"{endpoint}",
                        headers=headers,
                        json=data
                    )

                    response.raise_for_status()  # Lanza un error para respuestas HTTP 4xx/5xx

                    # Mostrar la respuesta en Streamlit
                    response_json = response.json()
                    response_text = response_json['choices'][0]['message']['content']
                    st.write("Respuesta:")
                    st.write(response_text.strip())

                except Exception as e:
                    # Manejo de errores si algo falla
                    st.error(f"Ocurrió un error al procesar la pregunta: {e}")
        else:
            st.warning("Por favor, ingresa una pregunta antes de presionar el botón.")
