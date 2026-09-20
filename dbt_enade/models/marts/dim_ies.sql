{{ config(materialized='table') }}

with ies as (
    select * from {{ source('bronze', 'mapeamento_ies') }}
)

select
    try_cast(co_ies as integer) as co_ies,
    no_ies as nome_ies,
    sg_ies as sigla_ies
from ies