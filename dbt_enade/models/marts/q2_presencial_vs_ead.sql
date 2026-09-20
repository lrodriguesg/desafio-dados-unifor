{{ config(materialized='view') }}

with unifor_areas as (
    -- Isola as áreas (CO_GRUPO) em que a Unifor possui cursos
    select distinct co_grupo 
    from {{ ref('dim_cursos') }} 
    where co_ies = 555
),
unifor_stats as (
    -- Calcula a média ponderada apenas da Unifor
    select
        'Unifor' as escopo,
        c.desc_modalidade,
        count(distinct c.co_curso) as qtd_cursos_avaliados,
        sum(f.qtd_alunos) as total_alunos,
        round(sum(f.nt_ger_media * f.qtd_alunos) / sum(f.qtd_alunos), 2) as media_ponderada_nt_ger
    from {{ ref('dim_cursos') }} c
    join {{ ref('fato_performance_cursos') }} f on c.co_curso = f.co_curso
    where c.co_ies = 555
    group by 1, 2
),
brasil_stats as (
    -- Calcula a média ponderada nacional (apenas para as áreas concorrentes da Unifor)
    select
        'Média Nacional (Mesmas Áreas)' as escopo,
        c.desc_modalidade,
        count(distinct c.co_curso) as qtd_cursos_avaliados,
        sum(f.qtd_alunos) as total_alunos,
        round(sum(f.nt_ger_media * f.qtd_alunos) / sum(f.qtd_alunos), 2) as media_ponderada_nt_ger
    from {{ ref('dim_cursos') }} c
    join {{ ref('fato_performance_cursos') }} f on c.co_curso = f.co_curso
    where c.co_grupo in (select co_grupo from unifor_areas)
    group by 1, 2
)
-- Une as duas visões
select * from unifor_stats
union all
select * from brasil_stats
order by escopo desc, desc_modalidade