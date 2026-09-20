import os
import duckdb
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema, Check

def process_silver_layer():
    print("Iniciando o processamento da Camada Silver com DuckDB...")
    os.makedirs("data/silver", exist_ok=True)
    
    con = duckdb.connect(database=':memory:')
    
    # 1. Processamento de Cursos (arq1)
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

    # 2. Processamento de Notas com Imputação (arq3)
    print("Tratando nulos e agregando Notas por Curso (arq3)...")
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

    # 3. Processamento do Perfil Socioeconômico (arq14) - Garantia de Integridade LGPD
    print("Agregando perfil socioeconômico predominante por curso (arq14)...")
    con.execute("""
        COPY (
            WITH raw_renda AS (
                SELECT
                    TRY_CAST(CO_CURSO AS INTEGER) AS CO_CURSO,
                    QE_I08 -- Corrigido para a letra 'I' conforme o cabeçalho real do arquivo
                FROM read_csv('data/bronze/enade/Microdados_Enade_2023/DADOS/microdados2023_arq14.txt', 
                              sep=';', header=True, null_padding=True)
                WHERE QE_I08 IN ('A', 'B', 'C', 'D', 'E', 'F', 'G')
            )
            SELECT
                CO_CURSO,
                MODE(QE_I08) AS cat_renda_predominante
            FROM raw_renda
            GROUP BY CO_CURSO
        ) TO 'data/silver/silver_renda.parquet' (FORMAT PARQUET);
    """)
    print("Arquivos Parquet gerados na Camada Silver.")

def run_data_quality_checks():
    print("Iniciando validação de Data Quality com Pandera...")
    
    df_cursos = pd.read_parquet('data/silver/silver_cursos.parquet')
    df_notas = pd.read_parquet('data/silver/silver_notas.parquet')
    df_renda = pd.read_parquet('data/silver/silver_renda.parquet')

    schema_cursos = DataFrameSchema({
        "CO_CURSO": Column(int, Check.greater_than(0), unique=True),
        "CO_IES": Column(int, Check.greater_than(0)),
        "CO_MODALIDADE": Column(int, Check.isin([0, 1])) 
    }, coerce=True)

    schema_notas = DataFrameSchema({
        "CO_CURSO": Column(int, Check.greater_than(0), unique=True),
        "NT_GER_MEDIA": Column(float, nullable=False),
        "QTD_ALUNOS": Column(int, Check.greater_than(0))
    }, coerce=True)

    # Novo schema assegurando que não passaram caracteres inválidos ou nulos
    schema_renda = DataFrameSchema({
        "CO_CURSO": Column(int, Check.greater_than(0), unique=True),
        "cat_renda_predominante": Column(str, Check.isin(['A', 'B', 'C', 'D', 'E', 'F', 'G']))
    }, coerce=True)

    try:
        schema_cursos.validate(df_cursos)
        schema_notas.validate(df_notas)
        schema_renda.validate(df_renda)
        print("✅ Data Quality Checks: APROVADOS! Nenhuma anomalia estrutural ou nulos remanescentes.")
    except pa.errors.SchemaErrors as err:
        print("❌ Data Quality Checks: REPROVADOS!")
        print(err.failure_cases)
        raise

if __name__ == "__main__":
    process_silver_layer()
    run_data_quality_checks()