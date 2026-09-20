import streamlit as st
import duckdb
import pandas as pd
import altair as alt

st.set_page_config(page_title="Painel Executivo ENADE 2023", page_icon="🎓", layout="wide")
st.title("🎓 Desempenho ENADE 2023 - Unifor")
st.markdown("Painel executivo focado em gerar *insights* acionáveis para a Coordenação Acadêmica com base nos microdados oficiais do INEP.")

@st.cache_resource
def get_connection():
    return duckdb.connect("data/gold/enade_gold.duckdb", read_only=True)

con = get_connection()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📍 Panorama", "⚖️ Presencial x EaD (Benchmark)", "🏆 Top 10 Cursos", "📊 Melhor IES Brasil", "💰 Renda vs Nota"
])

# ---------------------------------------------------------
# ABA 1: Panorama
# ---------------------------------------------------------
with tab1:
    st.header("A Unifor está no ENADE 2023?")
    st.success("**Sim.** O código da instituição (555) foi validado e cruzado utilizando o Censo da Educação Superior para garantir a integridade da identificação oficial.")
    
    df_q1 = con.execute("SELECT * FROM q1_unifor_overview").df()
    df_q1.columns = df_q1.columns.str.lower()
    
    if not df_q1.empty:
        total_cursos = df_q1['qtd_cursos'].sum()
        
        col_kpi, col_insight = st.columns([1, 3])
        col_kpi.metric("Cursos Avaliados", total_cursos)
        
        with col_insight:
            st.info(f"**Visão Estratégica:** Todos os {total_cursos} cursos avaliados da instituição concentram-se na modalidade Presencial. Isso indica que a fotografia do desempenho da Unifor no ciclo 2023 reflete puramente as suas operações de ensino físico.")
            
        st.dataframe(df_q1, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# ABA 2: Benchmark Presencial x EaD
# ---------------------------------------------------------
with tab2:
    st.header("Benchmark: Nota Geral (NT_GER) vs Cenário Nacional")
    
    with st.expander("📝 Entenda o Cálculo (Decisão Metodológica)"):
        st.write("""
        **Problema:** Calcular a média simples das notas dos cursos distorce a realidade analítica, pois dá o mesmo peso a um curso com 200 alunos e outro com 10. Além disso, a Unifor possui apenas cursos Presenciais neste ciclo avaliativo, impossibilitando uma comparação interna.
        
        **Solução Implementada:** 
        1. Apliquei o cálculo estatístico de **Média Ponderada** (`Σ(Nota × Alunos) / Σ(Alunos)`) na camada Gold.
        2. Expandi a análise: como não há base interna de EaD para comparação, cruzei a nota da Unifor com a **Média Nacional de todo o Brasil** (isolando estritamente as áreas concorrentes), trazendo uma visão clara de mercado para a coordenação.
        """)
        
    df_q2 = con.execute("SELECT * FROM q2_presencial_vs_ead").df()
    df_q2.columns = df_q2.columns.str.lower()
    
    if not df_q2.empty:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(df_q2, use_container_width=True, hide_index=True)
        with col2:
            chart = alt.Chart(df_q2).mark_bar().encode(
                x=alt.X('desc_modalidade:N', title='Modalidade'),
                y=alt.Y('media_ponderada_nt_ger:Q', title='Nota Média Ponderada'),
                color=alt.Color('escopo:N', title='Escopo de Análise'),
                column=alt.Column('escopo:N', title='')
            ).properties(width=150)
            st.altair_chart(chart, use_container_width=False)

# ---------------------------------------------------------
# ABA 3: Top 10 Cursos
# ---------------------------------------------------------
with tab3:
    st.header("Top 10 Cursos com Maior Nota Geral Média")
    
    df_q3 = con.execute("SELECT * FROM q3_top_10_unifor").df()
    df_q3.columns = df_q3.columns.str.lower()
    
    if not df_q3.empty:
        top_1 = df_q3.iloc[0]['nome_area']
        top_1_nota = df_q3.iloc[0]['nt_ger_media']
        top_2 = df_q3.iloc[1]['nome_area']
        top_2_nota = df_q3.iloc[1]['nt_ger_media']
        
        st.success(f"**Liderança na Saúde:** O ranking é liderado por **{top_1}** (Nota: {top_1_nota}) e **{top_2}** (Nota: {top_2_nota}). Estes dados confirmam empiricamente a força e a tradição dos programas de saúde da instituição, que conseguem manter alta performance mesmo avaliando volumes expressivos de alunos.")
        
        st.dataframe(df_q3, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# ABA 4: Melhor IES Brasil
# ---------------------------------------------------------
with tab4:
    st.header("Ranking de Mercado: Unifor vs Melhor IES do Brasil por Área")
    
    with st.expander("📝 Entenda o Cálculo (Decisão Metodológica)"):
        st.write("Para descobrir as instituições líderes sem degradar a performance do painel, utilizei *Window Functions* diretamente na modelagem da camada de dados. O algoritmo escaneia todas as instituições do país, isola os cursos com os mesmos códigos de área (`CO_GRUPO`) da Unifor e subtrai a nota da líder nacional da nota obtida pela nossa instituição, revelando o *Gap* (distância) exato em pontos.")

    df_q4 = con.execute("SELECT * FROM q4_bonus_melhor_ies").df()
    df_q4.columns = df_q4.columns.str.lower()
    
    if not df_q4.empty:
        st.dataframe(df_q4, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# ABA 5: Perfil Socioeconômico
# ---------------------------------------------------------
with tab5:
    st.header("Impacto: Renda Predominante vs Desempenho do Curso")
    
    with st.expander("📝 Cuidado Metodológico (LGPD e Regra do INEP)"):
        st.write("O manual do INEP proíbe terminantemente o cruzamento de notas e questionários ao nível do estudante individual para evitar reidentificação. Para respeitar a legislação e garantir a integridade da análise, estruturei o pipeline para calcular a **Moda Estatística** (a faixa de renda mais comum) de cada curso na camada Silver, antes de realizar o cruzamento com as notas na camada Gold.")

    df_q5 = con.execute("SELECT * FROM q5_bonus_renda").df()
    df_q5.columns = df_q5.columns.str.lower()
    
    if not df_q5.empty:
        st.info("""
        **Quebra de Paradigma Acadêmico:** 
        A análise estatística da base revela que a maior performance não está atrelada ao topo da pirâmide financeira. O melhor desempenho médio (Nota: 56.46) foi alcançado pelo grupo predominantemente classificado na faixa **B (De 1,5 a 3 salários mínimos)**. Por outro lado, observo uma forte concentração do corpo discente na faixa **F (De 10 a 30 salários mínimos)**, que concentra 7 cursos com uma média geral sólida de 51.33.
        """)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(df_q5, use_container_width=True, hide_index=True)
        with col2:
            chart = alt.Chart(df_q5).mark_bar(color='#ff7f0e').encode(
                x=alt.X('faixa_renda:N', title='Faixa de Renda', sort=None),
                y=alt.Y('media_geral_cursos:Q', title='Nota Média')
            )
            st.altair_chart(chart, use_container_width=True)