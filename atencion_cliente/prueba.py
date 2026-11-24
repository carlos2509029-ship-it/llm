from dotenv import load_dotenv
from google import genai

load_dotenv("atencion_cliente/.env")
client = genai.Client()   # lee GEMINI_API_KEY automáticamente

respuesta = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Explica en dos líneas qué es un centro de carga eléctrico."
)
print(respuesta.text)