import requests
from bs4 import BeautifulSoup
import openai

def url_content(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; url_content/1.0)"
        }
        response = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
        response.raise_for_status()  # Lanza excepción si el código de estado no es 2xx
        soup = BeautifulSoup(response.text, "html.parser")
        texto = soup.get_text().replace("\n", "")
        return texto[:500]
    except Exception as e:
        return f"Error al acceder a la URL: {str(e)}"