{{ config(materialized='table') }}

with cursos as (
    select * from {{ source('silver', 'silver_cursos') }}
)

select
    co_curso,
    co_ies,
    co_grupo,
    case
        when co_grupo = 5 then 'Medicina Veterinária'
        when co_grupo = 6 then 'Odontologia'
        when co_grupo = 12 then 'Medicina'
        when co_grupo = 17 then 'Agronomia'
        when co_grupo = 19 then 'Farmácia'
        when co_grupo = 21 then 'Arquitetura e Urbanismo'
        when co_grupo = 23 then 'Enfermagem'
        when co_grupo = 27 then 'Fonoaudiologia'
        when co_grupo = 28 then 'Nutrição'
        when co_grupo = 36 then 'Fisioterapia'
        when co_grupo = 51 then 'Zootecnia'
        when co_grupo = 55 then 'Biomedicina'
        when co_grupo = 69 then 'Tecnologia em Radiologia'
        when co_grupo = 90 then 'Tecnologia em Agronegócios'
        when co_grupo = 91 then 'Tecnologia em Gestão Hospitalar'
        when co_grupo = 92 then 'Tecnologia em Gestão Ambiental'
        when co_grupo = 95 then 'Tecnologia em Estética e Cosmética'
        when co_grupo = 5710 then 'Engenharia Civil'
        when co_grupo = 5806 then 'Engenharia Elétrica'
        when co_grupo = 5814 then 'Engenharia de Controle e Automação'
        when co_grupo = 5902 then 'Engenharia Mecânica'
        when co_grupo = 6002 then 'Engenharia de Alimentos'
        when co_grupo = 6008 then 'Engenharia Química'
        when co_grupo = 6208 then 'Engenharia de Produção'
        when co_grupo = 6307 then 'Engenharia Ambiental'
        when co_grupo = 6405 then 'Engenharia Florestal'
        when co_grupo = 6410 then 'Tecnologia em Segurança no Trabalho'
        when co_grupo = 6411 then 'Engenharia de Computação'
        else 'Outros'
    end as nome_area,
    co_modalidade,
    case
        when co_modalidade = 0 then 'EaD'
        when co_modalidade = 1 then 'Presencial'
        else 'Não Identificado'
    end as desc_modalidade
from cursos