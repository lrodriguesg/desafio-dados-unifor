{{ config(materialized='view') }}

select
    c.desc_modalidade,
    count(distinct c.co_curso) as qtd_cursos_avaliados,
    sum(f.qtd_alunos) as total_alunos,
    round(sum(f.nt_ger_media * f.qtd_alunos) / sum(f.qtd_alunos), 2) as media_ponderada_nt_ger
from {{ ref('dim_cursos') }} c
join {{ ref('fato_performance_cursos') }} f on c.co_curso = f.co_curso
where c.co_ies = 555
group by 1