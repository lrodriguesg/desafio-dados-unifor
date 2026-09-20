{{ config(materialized='view') }}

with unifor_areas as (
    -- Descobre as áreas em que a Unifor (555) possui cursos avaliados
    select distinct co_grupo
    from {{ ref('dim_cursos') }}
    where co_ies = 555
),
rank_ies_area as (
    -- Calcula a média geral de cada IES por área e cria um ranking
    select
        c.co_grupo,
        c.nome_area,
        c.co_ies,
        i.nome_ies,
        round(avg(f.nt_ger_media), 2) as media_ies_area,
        row_number() over (partition by c.co_grupo order by avg(f.nt_ger_media) desc) as rank_area
    from {{ ref('dim_cursos') }} c
    join {{ ref('fato_performance_cursos') }} f on c.co_curso = f.co_curso
    left join {{ ref('dim_ies') }} i on c.co_ies = i.co_ies
    where c.co_grupo in (select co_grupo from unifor_areas)
    group by 1, 2, 3, 4
),
unifor_notas as (
    -- Isola as notas da Unifor para fazer a comparação de distância
    select
        co_grupo,
        media_ies_area as nota_unifor
    from rank_ies_area
    where co_ies = 555
)
-- Cruza a IES #1 de cada área com a nota da Unifor
select
    r.nome_area,
    r.nome_ies as melhor_ies_brasil,
    r.media_ies_area as nota_melhor_ies,
    u.nota_unifor,
    round(r.media_ies_area - u.nota_unifor, 2) as gap_pontos
from rank_ies_area r
join unifor_notas u on r.co_grupo = u.co_grupo
where r.rank_area = 1
order by gap_pontos asc