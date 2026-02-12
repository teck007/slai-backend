import requests
from bs4 import BeautifulSoup, FeatureNotFound

def url_content(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; url_content/1.0)"
        }
        response = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
        # response.raise_for_status()
        if response.status_code != 200:
            return None
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            texto = soup.get_text().replace("\n", "")
            return texto[:500]
        except FeatureNotFound as fe:
            print(f"Error BeautifulSoup: parser not found: {str(fe)}")
            return None
        except Exception as pe:
            print(f"Error HTML analyse: {str(pe)}")
            return None
    except requests.exceptions.RequestException as re:
        print(f"Network error: {str(re)}")
        return None
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return None