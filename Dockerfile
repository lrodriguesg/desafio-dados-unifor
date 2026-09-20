# Usa uma imagem oficial e leve do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema operacional necessárias para compilação (se houver)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copia os requisitos e instala as bibliotecas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do projeto para o container
COPY . .

# Define variável de ambiente para o dbt não pedir confirmações interativas
ENV DBT_PROFILES_DIR=/app/dbt_enade