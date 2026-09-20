{{ config(materialized='view') }}

-- Filtramos diretamente pelo CO_IES = 555 (Mapeado na Bronze via e-MEC)
select
    c.nome_area,
    c.desc_modalidade,
    count(distinct c.co_curso) as qtd_cursos
from {{ ref('dim_cursos') }} c
where c.co_ies = 555
group by 1, 2
order by 3 desc, 1 asc