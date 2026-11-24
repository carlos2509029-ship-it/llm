# Asistente de atención al cliente para un servicio de mantenimiento eléctrico
# Autor: Carlos Eduardo Lozoya López
# Modelo de lenguaje: Google Gemini (librería google-genai)

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------
CARPETA = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CARPETA, ".env"))

EMPRESA = "ElectroServicio Confiable"
TELEFONO = "(656) 555-0100"   # teléfono ficticio

# Si un modelo está saturado o no disponible, se intenta con el siguiente
MODELOS = ["gemini-3.5-flash-lite", "gemini-3.7-flash", "gemini-3.8-flash"]

# Catálogo real de servicios: el modelo SOLO puede usar estos precios
CATALOGO = {
    1: {"servicio": "Revisión general de instalación eléctrica", "precio": 650},
    2: {"servicio": "Cambio o instalación de contactos y apagadores", "precio": 180},
    3: {"servicio": "Instalación o reemplazo de centro de carga", "precio": 2500},
    4: {"servicio": "Termografía de tableros eléctricos", "precio": 1800},
    5: {"servicio": "Servicio de emergencia (24 horas)", "precio": 950},
}

PALABRAS_EMERGENCIA = ["humo", "chispa", "quemado", "fuego", "incendio",
                       "descarga", "electrocut", "explot"]

AVISO_EMERGENCIA = f"""
🚨 POSIBLE EMERGENCIA
   1. Si es seguro hacerlo, corte la energía desde el interruptor principal.
   2. Aléjese del área y no toque cables ni equipos.
   3. Llame al 911.
   Nuestro servicio de emergencia 24 horas: {TELEFONO}
"""

CITAS = []   # citas registradas en esta sesión (simulación de base de datos)


def crear_instrucciones():
    """Arma las instrucciones de sistema, incluyendo el catálogo real."""
    lista = "\n".join(
        f"- {d['servicio']}: ${d['precio']} MXN" for d in CATALOGO.values()
    )
    return f"""
Eres el asistente virtual de atención al cliente de "{EMPRESA}",
una empresa de mantenimiento eléctrico residencial e industrial.

Catálogo oficial de servicios y precios (los ÚNICOS que existen):
{lista}

Reglas:
- Usa SOLO los precios del catálogo. Si preguntan por algo que no está, di que
  un técnico lo cotizará en la visita. Nunca inventes precios.
- Tú no puedes registrar citas ni consultar sistemas. Para agendar, indica al
  cliente que escriba 'salir' para volver al menú de este programa y elija la
  opción 3 "Agendar una visita".
- NUNCA des instrucciones para trabajar con la electricidad conectada.
- Ante cualquier riesgo, recomienda cortar la energía y llamar a un técnico calificado.
- Solo hablas de temas eléctricos y de la empresa.
- Sé amable, claro y breve (máximo 5 líneas).
"""


def es_emergencia(texto):
    """Filtro de reglas: detecta palabras de emergencia sin usar el modelo."""
    texto = texto.lower()
    return any(palabra in texto for palabra in PALABRAS_EMERGENCIA)


def preguntar_al_modelo(client, contenidos, instrucciones):
    """Envía la conversación al modelo. Si uno falla, prueba con el siguiente.
    Devuelve el texto de la respuesta, o None si ningún modelo respondió."""
    for modelo in MODELOS:
        try:
            respuesta = client.models.generate_content(
                model=modelo,
                contents=contenidos,
                config=types.GenerateContentConfig(system_instruction=instrucciones),
            )
            return respuesta.text
        except Exception:
            # Modelo saturado (503), no disponible (404) o sin conexión: probar el siguiente
            continue
    return None


def opcion_chat(client):
    """Conversación con memoria: el historial se reenvía completo en cada mensaje."""
    instrucciones = crear_instrucciones()
    historial = []
    print("\n💬 Chat con el asistente (escribe 'salir' para volver al menú)\n")

    while True:
        mensaje = input("Tú: ").strip()
        if mensaje.lower() in ("salir", "adios", "adiós", "menu", "menú"):
            print("Asistente: ¡Con gusto! Regresando al menú.\n")
            break
        if not mensaje:
            continue

        # 1) Primero las reglas: una emergencia no depende del modelo
        if es_emergencia(mensaje):
            print(AVISO_EMERGENCIA)
            continue

        # 2) Después el modelo de lenguaje
        historial.append(types.Content(role="user", parts=[types.Part(text=mensaje)]))
        texto = preguntar_al_modelo(client, historial, instrucciones)

        if texto is None:
            historial.pop()   # se quita el mensaje que no obtuvo respuesta
            print(f"Asistente: En este momento no puedo conectarme. Intente en unos minutos "
                  f"o llame al {TELEFONO}.\n")
        else:
            historial.append(types.Content(role="model", parts=[types.Part(text=texto)]))
            print(f"Asistente: {texto}\n")


def mostrar_catalogo():
    print(f"\n📋 Servicios de {EMPRESA}")
    for numero, datos in CATALOGO.items():
        print(f"  {numero}. {datos['servicio']:<50} ${datos['precio']:>6,} MXN")
    print()


def pedir_texto(etiqueta):
    """Pide un dato obligatorio hasta que el usuario escriba algo."""
    while True:
        valor = input(f"  {etiqueta}: ").strip()
        if valor:
            return valor
        print("  Este dato es obligatorio.")


def agendar_visita(client):
    """Los datos los captura el código (exactos); el modelo solo redacta la cortesía."""
    print("\n📅 Agendar una visita")
    nombre = pedir_texto("Nombre")
    direccion = pedir_texto("Dirección")
    telefono = pedir_texto("Teléfono")

    mostrar_catalogo()
    while True:
        try:
            numero = int(input("  Número de servicio: "))
            if numero in CATALOGO:
                break
            print("  Elija un número del catálogo.")
        except ValueError:
            print("  Escriba solo el número.")
    fecha = pedir_texto("Fecha preferida (ej. 28/11/2026)")

    servicio = CATALOGO[numero]
    print("\n  Registrando cita en el sistema…")
    cita = {"folio": len(CITAS) + 1, "nombre": nombre, "direccion": direccion,
            "telefono": telefono, "servicio": servicio["servicio"],
            "precio": servicio["precio"], "fecha": fecha}
    CITAS.append(cita)

    # Ficha oficial: la imprime el código, con los datos tal cual
    print(f"""
  ✅ Cita registrada — Folio {cita['folio']:04d}
     Cliente:   {cita['nombre']}
     Dirección: {cita['direccion']}
     Teléfono:  {cita['telefono']}
     Servicio:  {cita['servicio']} (${cita['precio']:,} MXN)
     Fecha:     {cita['fecha']}
""")

    # El modelo solo redacta un mensaje amable, sin repetir datos
    peticion = (f"Escribe un mensaje breve y cordial (máximo 3 líneas) para {nombre}, "
                f"que agendó el servicio '{servicio['servicio']}'. Agradécele y dale una "
                f"recomendación práctica para preparar la visita. NO repitas dirección, "
                f"teléfono, fecha ni precio.")
    texto = preguntar_al_modelo(client, peticion, crear_instrucciones())
    if texto:
        print(f"  {texto}\n")


def main():
    if not os.getenv("GEMINI_API_KEY"):
        print("No se encontró GEMINI_API_KEY. Revise el archivo .env (ver README).")
        return
    client = genai.Client()

    print(f"=== {EMPRESA} · Asistente de atención al cliente ===")
    while True:
        print("1. Hablar con el asistente")
        print("2. Ver servicios y precios")
        print("3. Agendar una visita")
        print("4. Salir")
        opcion = input("Elija una opción: ").strip()

        if opcion == "1":
            opcion_chat(client)
        elif opcion == "2":
            mostrar_catalogo()
        elif opcion == "3":
            agendar_visita(client)
        elif opcion == "4":
            print(f"Gracias por contactar a {EMPRESA}. ¡Hasta pronto!")
            break
        else:
            print("Opción no válida. Escriba un número del 1 al 4.\n")


if __name__ == "__main__":
    main()