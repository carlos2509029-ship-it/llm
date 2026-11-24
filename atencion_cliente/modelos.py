from dotenv import load_dotenv
from google import genai

load_dotenv("atencion_cliente/.env")
client = genai.Client()

for m in client.models.list():
    print(m.name)