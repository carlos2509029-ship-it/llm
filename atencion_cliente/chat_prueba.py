from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv("atencion_cliente/.env")
client = genai.Client()

MODELO = "gemini-3.5-flash-lite"

INSTRUCCIONES = """
Eres el asistente virtual de atención al cliente de "ElectroServicio Confiable",
una empresa de mantenimiento eléctrico residencial e industrial.

Tu trabajo:
- Responder dudas sobre los servicios y precios de la empresa.
- Ayudar a identificar qué servicio necesita el cliente según su problema.
- Ser amable, claro y breve (máximo 5 líneas por respuesta).

Reglas de seguridad (obligatorias):
- NUNCA des instrucciones para trabajar con la electricidad conectada.
- Ante cualquier riesgo, recomienda cortar la energía y llamar a un técnico calificado.
- Si el cliente menciona humo, chispas u olor a quemado, indícale que corte la energía
  si es seguro hacerlo, se aleje y llame al 911.

Alcance:
- Solo hablas de temas eléctricos y de la empresa. Si te preguntan otra cosa,
  explica amablemente que solo puedes ayudar con servicios eléctricos.
"""

chat = client.chats.create(
    model=MODELO,
    config=types.GenerateContentConfig(system_instruction=INSTRUCCIONES),
)

print("Asistente de ElectroServicio Confiable (escribe 'salir' para terminar)\n")

while True:
    mensaje = input("Tú: ")
    if mensaje.lower() == "salir":
        print("Asistente: ¡Gracias por contactarnos! Que tenga buen día.")
        break
    respuesta = chat.send_message(mensaje)
    print(f"Asistente: {respuesta.text}\n")