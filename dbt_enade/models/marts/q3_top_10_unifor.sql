{{ config(materialized='view') }}

select
    c.nome_area,
    c.desc_modalidade,
    f.nt_ger_media,
    f.qtd_alunos
from {{ ref('dim_cursos') }} c
join {{ ref('fato_performance_cursos') }} f on c.co_curso = f.co_curso
where c.co_ies = 555
order by f.nt_ger_media desc
limit 10