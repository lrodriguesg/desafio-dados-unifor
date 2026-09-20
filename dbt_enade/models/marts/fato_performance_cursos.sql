{{ config(materialized='table') }}

with notas as (
    select * from {{ source('silver', 'silver_notas') }}
)

select
    co_curso,
    nt_ger_media,
    qtd_imputados,
    qtd_alunos
from notas