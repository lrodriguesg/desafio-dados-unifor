import os
import duckdb
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check

def process_silver_layer():
    print("Iniciando processamento da Camada Silver com DuckDB...")
    os.makedirs("data/silver", exist_ok=True)
    
    # Conecta ao DuckDB em memória
    con = duckdb.connect(database=':memory:')
    
    # ---------------------------------------------------------
    # 1. Processamento de Cursos (arq1)
    # ---------------------------------------------------------
    print("Extraindo e tipando dados de Cursos (arq1)...")
    con.execute("""
        COPY (
            SELECT DISTINCT
                TRY_CAST(CO_CURSO AS INTEGER) AS CO_CURSO,
                TRY_CAST(CO_IES AS INTEGER) AS CO_IES,
                TRY_CAST(CO_GRUPO AS INTEGER) AS CO_GRUPO,
                TRY_CAST(CO_MODALIDADE AS INTEGER) AS CO_MODALIDADE
            FROM read_csv('data/bronze/enade/Microdados_Enade_2023/DADOS/microdados2023_arq1.txt', 
                          sep=';', header=True, null_padding=True)
        ) TO 'data/silver/silver_cursos.parquet' (FORMAT PARQUET);
    """)

    # ---------------------------------------------------------
    # 2. Processamento de Notas com Imputação (arq3)
    # ---------------------------------------------------------
    print("Tratando nulos e agregando Notas por Curso (arq3)...")
    # A CTE 'raw_notas' converte o ponto '.' em nulo conforme o manual e cria a flag.
    # A CTE 'medias_curso' calcula a média dos que fizeram a prova.
    # A CTE 'imputados' preenche o nulo do aluno com a média do seu curso (tratamento antes de agregar).
    # O SELECT final faz a agregação exigida pela LGPD.
    con.execute("""
        COPY (
            WITH raw_notas AS (
                SELECT
                    TRY_CAST(CO_CURSO AS INTEGER) AS CO_CURSO,
                    TRY_CAST(NT_GER AS DOUBLE) AS NT_GER_raw,
                    CASE WHEN NT_GER IS NULL THEN 1 ELSE 0 END AS is_null
                FROM read_csv('data/bronze/enade/Microdados_Enade_2023/DADOS/microdados2023_arq3.txt', 
                              sep=';', header=True, null_padding=True, nullstr='.')
            ),
            medias_curso AS (
                SELECT CO_CURSO, AVG(NT_GER_raw) AS media_imputacao
                FROM raw_notas
                GROUP BY CO_CURSO
            ),
            imputados AS (
                SELECT
                    r.CO_CURSO,
                    COALESCE(r.NT_GER_raw, m.media_imputacao, 0) AS NT_GER_tratado,
                    r.is_null
                FROM raw_notas r
                LEFT JOIN medias_curso m ON r.CO_CURSO = m.CO_CURSO
            )
            SELECT
                CO_CURSO,
                ROUND(AVG(NT_GER_tratado), 2) AS NT_GER_MEDIA,
                SUM(is_null) AS QTD_IMPUTADOS,
                COUNT(*) AS QTD_ALUNOS
            FROM imputados
            GROUP BY CO_CURSO
        ) TO 'data/silver/silver_notas.parquet' (FORMAT PARQUET);
    """)
    print("Arquivos Parquet gerados na Camada Silver.")

def run_data_quality_checks():
    print("Iniciando validação de Data Quality com Pandera...")
    
    # Lendo os parquets gerados para validação
    df_cursos = pd.read_parquet('data/silver/silver_cursos.parquet')
    df_notas = pd.read_parquet('data/silver/silver_notas.parquet')

    # Schema de Validação para Cursos
    schema_cursos = DataFrameSchema({
        "CO_CURSO": Column(int, Check.greater_than(0), unique=True),
        "CO_IES": Column(int, Check.greater_than(0)),
        "CO_MODALIDADE": Column(int, Check.isin([0, 1]))
    }, coerce=True) # <- Adicionado coerce=True para uniformizar int32/int64

    # Schema de Validação para Notas
    schema_notas = DataFrameSchema({
        "CO_CURSO": Column(int, Check.greater_than(0), unique=True),
        "NT_GER_MEDIA": Column(float, nullable=False),
        "QTD_ALUNOS": Column(int, Check.greater_than(0))
    }, coerce=True) # <- Adicionado coerce=True

    try:
        schema_cursos.validate(df_cursos)
        schema_notas.validate(df_notas)
        print("✅ Data Quality Checks: APROVADOS! Nenhuma anomalia estrutural ou nulos remanescentes.")
    except pa.errors.SchemaErrors as err:
        print("❌ Data Quality Checks: REPROVADOS!")
        print(err.failure_cases)
        raise

if __name__ == "__main__":
    process_silver_layer()
    run_data_quality_checks()