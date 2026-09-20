{{ config(materialized='table') }}

with renda as (
    select * from {{ source('silver', 'silver_renda') }}
),
cursos_unifor as (
    select co_curso, nome_area 
    from {{ ref('dim_cursos') }}
    where co_ies = 555
)

select
    r.cat_renda_predominante,
    case
        when r.cat_renda_predominante = 'A' then 'Até 1,5 salário mínimo'
        when r.cat_renda_predominante = 'B' then 'De 1,5 a 3 salários mínimos'
        when r.cat_renda_predominante = 'C' then 'De 3 a 4,5 salários mínimos'
        when r.cat_renda_predominante = 'D' then 'De 4,5 a 6 salários mínimos'
        when r.cat_renda_predominante = 'E' then 'De 6 a 10 salários mínimos'
        when r.cat_renda_predominante = 'F' then 'De 10 a 30 salários mínimos'
        when r.cat_renda_predominante = 'G' then 'Acima de 30 salários mínimos'
    end as faixa_renda,
    count(distinct c.co_curso) as qtd_cursos,
    round(avg(f.nt_ger_media), 2) as media_geral_cursos
from cursos_unifor c
join {{ ref('fato_performance_cursos') }} f on c.co_curso = f.co_curso
join renda r on c.co_curso = r.co_curso
group by 1, 2
order by 1