import os
from dotenv import load_dotenv
from openai import OpenAI

# Carga las variables del archivo .env
load_dotenv()
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

def resume_url(url: str, content: str) -> str:
    prompt = (
        f"""Tengo esta URL: {url} y este contenido extraído de la URL: {content}. 
        Quiero que resumas el contenido. Con este resumen genera un nombre corto de hasta 12 caracteres, solo en minúsculas.
        Para el resumen no incluyas palabras relacionadas con partes del HTML como meta tags, meta description, meta keywords, etc. 
        Si es necesario utiliza alguna palabra clave de la URL. Me debes responder con solo una opcion de frase, con dos palabras y sin tildes.
        Puedes abreviar palabras generadas para que sea la minima cantidad de caracteres posibles
        """
    )
    try:
        response = client.chat.completions.create(
            model="deepseek-chat", 
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.replace(" ", "-")
    except Exception as e:
        print(e)
