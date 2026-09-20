import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(page_title="Painel ENADE 2023 - Unifor", page_icon="📊", layout="wide")
st.title("📊 Desempenho ENADE 2023 - Unifor")
st.markdown("Painel executivo construído para a Coordenação Acadêmica responder às principais dúvidas do ciclo avaliativo de 2023.")

@st.cache_resource
def get_connection():
    return duckdb.connect("data/gold/enade_gold.duckdb", read_only=True)

con = get_connection()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Panorama", "Presencial x EaD", "Top 10 Cursos", "Bônus: Melhor IES Brasil", "Bônus: Renda vs Nota"
])

with tab1:
    st.header("A Unifor está no ENADE 2023?")
    st.success("**Sim.** O código 555 foi validado cruzando o Censo da Educação Superior.")
    df_q1 = con.execute("SELECT * FROM q1_unifor_overview").df()
    df_q1.columns = df_q1.columns.str.lower()
    if not df_q1.empty:
        col_kpi, _ = st.columns([1, 3])
        col_kpi.metric("Cursos Ofertados e Avaliados", df_q1['qtd_cursos'].sum())
        st.dataframe(df_q1, use_container_width=True, hide_index=True)

with tab2:
    st.header("A nota geral (NT_GER) difere entre as modalidades?")
    df_q2 = con.execute("SELECT * FROM q2_presencial_vs_ead").df()
    df_q2.columns = df_q2.columns.str.lower()
    if not df_q2.empty:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(df_q2, use_container_width=True, hide_index=True)
        with col2:
            st.bar_chart(data=df_q2, x='desc_modalidade', y='media_ponderada_nt_ger', color='#1f77b4')

with tab3:
    st.header("Top 10 Cursos com Maior Nota Geral Média")
    df_q3 = con.execute("SELECT * FROM q3_top_10_unifor").df()
    df_q3.columns = df_q3.columns.str.lower()
    if not df_q3.empty:
        st.dataframe(df_q3, use_container_width=True, hide_index=True)

with tab4:
    st.header("Ranking: Unifor vs Melhor IES do Brasil por Área")
    df_q4 = con.execute("SELECT * FROM q4_bonus_melhor_ies").df()
    df_q4.columns = df_q4.columns.str.lower()
    if not df_q4.empty:
        st.dataframe(df_q4, use_container_width=True, hide_index=True)
        st.info("💡 **Análise:** A coluna 'gap_pontos' mostra a distância da nota média da Unifor para a instituição líder nacional naquela área.")

with tab5:
    st.header("Perfil Socioeconômico Predominante vs Desempenho")
    df_q5 = con.execute("SELECT * FROM q5_bonus_renda").df()
    df_q5.columns = df_q5.columns.str.lower()
    if not df_q5.empty:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(df_q5, use_container_width=True, hide_index=True)
        with col2:
            st.bar_chart(data=df_q5, x='faixa_renda', y='media_geral_cursos', color='#ff7f0e')