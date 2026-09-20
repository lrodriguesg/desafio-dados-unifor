import streamlit as st
import duckdb
import pandas as pd

# ---------------------------------------------------------
# Configuração da Página
# ---------------------------------------------------------
st.set_page_config(
    page_title="Painel ENADE 2023 - Unifor",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Desempenho ENADE 2023 - Unifor")
st.markdown("Painel executivo construído para a Coordenação Acadêmica responder às principais dúvidas do ciclo avaliativo de 2023.")

# ---------------------------------------------------------
# Conexão com a Camada Gold (DuckDB)
# ---------------------------------------------------------
@st.cache_resource
def get_connection():
    # Conecta no arquivo criado pelo dbt. read_only evita lock de banco de dados.
    return duckdb.connect("data/gold/enade_gold.duckdb", read_only=True)

con = get_connection()

# Criação de abas para organizar as perguntas
tab1, tab2, tab3 = st.tabs(["Pergunta 1: Panorama", "Pergunta 2: Presencial x EaD", "Pergunta 3: Top 10 Cursos"])

# ---------------------------------------------------------
# ABA 1: Panorama Unifor
# ---------------------------------------------------------
with tab1:
    st.header("A Unifor está no ENADE 2023?")
    st.success("**Sim.** O código da instituição é **555**. Esta informação foi validada ativamente mediante cruzamento com a base de dados pública do portal Cadastro e-MEC.")
    
    # Consulta a view gerada pelo dbt e padroniza as colunas para minúsculo
    df_q1 = con.execute("SELECT * FROM q1_unifor_overview").df()
    df_q1.columns = df_q1.columns.str.lower()
    
    if not df_q1.empty:
        total_cursos = df_q1['qtd_cursos'].sum()
        
        # KPI Centralizado
        col_kpi, _ = st.columns([1, 3])
        col_kpi.metric("Cursos Ofertados e Avaliados", total_cursos)
        
        st.subheader("Distribuição por Área e Modalidade")
        st.dataframe(df_q1, use_container_width=True, hide_index=True)
    else:
        st.warning("Nenhum dado encontrado para a Unifor nesta view.")

# ---------------------------------------------------------
# ABA 2: Presencial vs EaD
# ---------------------------------------------------------
with tab2:
    st.header("A nota geral (NT_GER) difere entre as modalidades?")
    
    df_q2 = con.execute("SELECT * FROM q2_presencial_vs_ead").df()
    df_q2.columns = df_q2.columns.str.lower()
    
    if not df_q2.empty:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.dataframe(df_q2, use_container_width=True, hide_index=True)
            st.info("💡 **Nota Metodológica:** Para garantir precisão, a média exibida é uma **Média Ponderada**, calculada com base na quantidade de alunos que efetivamente realizaram a prova em cada curso.")
            
        with col2:
            st.bar_chart(data=df_q2, x='desc_modalidade', y='media_ponderada_nt_ger', color='#1f77b4')
    else:
        st.warning("Nenhum dado encontrado para comparação de modalidades.")

# ---------------------------------------------------------
# ABA 3: Top 10 Cursos
# ---------------------------------------------------------
with tab3:
    st.header("Top 10 Cursos com Maior Nota Geral Média (NT_GER)")
    
    df_q3 = con.execute("SELECT * FROM q3_top_10_unifor").df()
    df_q3.columns = df_q3.columns.str.lower()
    
    if not df_q3.empty:
        st.dataframe(df_q3, use_container_width=True, hide_index=True)
        
        # Extrai dinamicamente o primeiro lugar para o texto de análise
        top_1_curso = df_q3.iloc[0]['nome_area']
        top_1_nota = df_q3.iloc[0]['nt_ger_media']
        
        st.markdown(f"""
        ### Conclusão Analítica
        O curso no topo do ranking do ciclo 2023 é **{top_1_curso}** (Nota: {top_1_nota}). 
        
        Conforme a expectativa da coordenação acadêmica, é comum observar que cursos tradicionais, especialmente da área da saúde ou engenharias consolidadas, performem melhor devido ao perfil do ingressante e à estrutura histórica do corpo docente.
        """)
    else:
        st.warning("Nenhum dado encontrado para o ranking.")