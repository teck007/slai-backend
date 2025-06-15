import os
from dotenv import load_dotenv
from openai import OpenAI

# Carga las variables del archivo .env
load_dotenv()
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPENAI_API_KEY"),
)
def chat(mensaje_usuario: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1-nano", 
        messages=[
            {"role": "user", "content": mensaje_usuario}
        ]
    )
    # 3. Extrae y devuelve el texto
    return response.choices[0].message.content

def shorten(url: str, content: str) -> str:
    prompt = (
        f"Tengo esta URL: {url} y este contenido extraído de la URL: {content}. "
        "Quiero que resumas el contenido. Con este resumen genera un nombre corto de hasta 12 caracteres, solo en minúsculas."
        "Para el resumen no incluyas palabras relacionadas con partes del HTML como meta tags, meta description, meta keywords, etc. "
        "Si es necesario utiliza alguna palabra clave de la URL. Me debes responder con solo una opcion de frase, con dos palabras."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano", 
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.replace(" ", "-")
    except Exception as e:
        print(e)
