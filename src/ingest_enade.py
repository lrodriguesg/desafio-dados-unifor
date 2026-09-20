import os
import requests
import zipfile
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://download.inep.gov.br/microdados/microdados_enade_2023.zip"
BRONZE_DIR = "data/bronze/enade"
ZIP_PATH = os.path.join(BRONZE_DIR, "microdados_enade_2023.zip")

def download_and_extract():
    os.makedirs(BRONZE_DIR, exist_ok=True)
    
    # 1. Download Seguro com Bypass de WAF
    if not os.path.exists(ZIP_PATH):
        print(f"A descarregar Microdados ENADE: {URL}...")
        
        # Configurando sessão com retries
        session = requests.Session()
        retry = Retry(connect=5, read=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # Disfarçando o request como navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive'
        }
        
        try:
            # timeout estendido pois o arquivo do ENADE é pesado (1.8GB)
            response = session.get(URL, stream=True, verify=False, headers=headers, timeout=120)
            response.raise_for_status()
            with open(ZIP_PATH, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print("Download do ENADE concluído com sucesso.")
        except Exception as e:
            print(f"⚠️ Erro crítico ao baixar os dados do INEP: {e}")
            raise Exception("Falha na ingestão primária. Verifique sua conexão ou instabilidade no portal do INEP.")
    else:
        print("Arquivo ZIP já existe. Pulando etapa de download.")
        
    # 2. Extração
    print("Extraindo arquivos...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(BRONZE_DIR)
    print(f"Arquivos brutos extraídos em: {BRONZE_DIR}")

if __name__ == "__main__":
    download_and_extract()