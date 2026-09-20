import os
import pandas as pd

BRONZE_DIR = "data/bronze/emec"

def generate_ies_mapping():
    """
    Gera o arquivo bruto de mapeamento da Unifor.
    A descoberta do código 1214 foi feita via consulta pública ao portal Cadastro e-MEC (emec.mec.gov.br).
    """
    os.makedirs(BRONZE_DIR, exist_ok=True)
    
    # Criação do dataframe com o código descoberto
    data = {
        "CO_IES": [1214],
        "NO_IES": ["UNIVERSIDADE DE FORTALEZA (UNIFOR)"],
        "SG_IES": ["UNIFOR"]
    }
    
    df = pd.DataFrame(data)
    output_path = os.path.join(BRONZE_DIR, "mapeamento_ies.csv")
    
    df.to_csv(output_path, index=False, sep=";")
    print(f"Arquivo de mapeamento e-MEC gerado com sucesso em: {output_path}")

if __name__ == "__main__":
    generate_ies_mapping()