import os
import requests
import zipfile
import urllib3

# Desabilita avisos de certificado SSL inseguro (comum em sites gov.br)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://download.inep.gov.br/microdados/microdados_enade_2023.zip"
BRONZE_DIR = "data/bronze/enade"
ZIP_PATH = os.path.join(BRONZE_DIR, "microdados_enade_2023.zip")

def download_and_extract():
    os.makedirs(BRONZE_DIR, exist_ok=True)
    
    # Etapa 1: Download do arquivo
    if not os.path.exists(ZIP_PATH):
        print(f"Iniciando download dos dados do INEP: {URL}...")
        response = requests.get(URL, stream=True, verify=False)
        response.raise_for_status() # Garante que erro 404/500 levante uma exceção
        
        with open(ZIP_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download concluído com sucesso.")
    else:
        print("Arquivo ZIP já existe. Pulando etapa de download.")
    
    # Etapa 2: Extração dos dados
    print("Extraindo arquivos...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(BRONZE_DIR)
    print(f"Arquivos brutos extraídos em: {BRONZE_DIR}")

if __name__ == "__main__":
    download_and_extract()