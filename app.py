import streamlit as st
import gspread
import pandas as pd
import os # Importamos a biblioteca 'os' para verificar a existência de arquivos

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Validação de Certificado",
    page_icon="✅",
    layout="centered"
)

# --- CONEXÃO SEGURA E INTELIGENTE COM O GOOGLE SHEETS ---
def connect_to_google_sheets():
    # Se o arquivo credentials.json existir, estamos rodando LOCALMENTE
    if os.path.exists('credentials.json'):
        return gspread.service_account(filename='credentials.json')
    # Senão, estamos na nuvem (Streamlit Cloud) e usamos os Segredos
    else:
        return gspread.service_account_from_dict(st.secrets)

try:
    gc = connect_to_google_sheets()
    # !!! AÇÃO NECESSÁRIA !!!
    # Substitua pela URL completa da sua MasterSheet
    URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1Y3mhS5BoB-0H6VQWOZcOq13NgQmQq8qeD3pqR5fMCyE/edit?gid=1697416463#gid=1697416463"
    sh = gc.open_by_url(URL_PLANILHA)
except Exception as e:
    st.error("Ocorreu um erro de configuração ou conexão. Contate o administrador.")
    st.stop()

# --- INTERFACE DO USUÁRIO ---
st.title("Verificação de Autenticidade de Certificado")
st.write("Insira o código de validação encontrado no seu certificado ou acesse a URL do QR Code.")

# Lê o código diretamente do parâmetro 'c' na URL
params = st.query_params
codigo_url = params.get('c', [None])[0]

codigo_validacao = st.text_input(
    "Código de Validação",
    value=codigo_url if codigo_url else "",
    placeholder="Cole o código aqui..."
)

verificar_btn = st.button("Verificar Certificado")

# Lógica de execução: Roda se o botão for clicado OU se um código veio da URL
if verificar_btn or codigo_url:
    if not codigo_validacao:
        st.warning("Por favor, insira um código de validação.")
    else:
        with st.spinner("Buscando nos nossos registros..."):
            try:
                aba_emissoes = sh.worksheet('emissoes')
                aba_alunos = sh.worksheet('cadastros')
                aba_eventos = sh.worksheet('cursos_eventos')

                # Cabeçalhos Corretos (ajuste se necessário)
                CABEÇALHO_CODIGO = 'codigo_validacao' # Ajuste se o seu for diferente
                CABEÇALHO_ID_ALUNO_EMISSOES = 'id_aluno'
                CABEÇALHO_ID_EVENTO_EMISSOES = 'id_evento'
                CABEÇALHO_DATA_EMISSAO = 'data_emissao'
                CABEÇALHO_URL_PDF = 'url_pdf'
                CABEÇALHO_ID_ALUNO_CADASTROS = 'id_aluno'
                CABEÇALHO_NOME_COMPLETO = 'nome_completo'
                CABEÇALHO_ID_EVENTO_CURSOS = 'id_evento'
                CABEÇALHO_NOME_EVENTO = 'nome_evento'
                
                df_emissoes = pd.DataFrame(aba_emissoes.get_all_records())
                registro = df_emissoes[df_emissoes[CABEÇALHO_CODIGO] == codigo_validacao]

                if not registro.empty:
                    id_aluno = registro.iloc[0][CABEÇALHO_ID_ALUNO_EMISSOES]
                    id_evento = registro.iloc[0][CABEÇALHO_ID_EVENTO_EMISSOES]
                    data_emissao = registro.iloc[0][CABEÇALHO_DATA_EMISSAO]
                    url_pdf = registro.iloc[0][CABEÇALHO_URL_PDF]
                    
                    df_alunos = pd.DataFrame(aba_alunos.get_all_records())
                    info_aluno = df_alunos[df_alunos[CABEÇALHO_ID_ALUNO_CADASTROS] == id_aluno].iloc[0]
                    
                    df_eventos = pd.DataFrame(aba_eventos.get_all_records())
                    info_evento = df_eventos[df_eventos[CABEÇALHO_ID_EVENTO_CURSOS] == id_evento].iloc[0]

                    st.success("Certificado Válido e Autêntico!")
                    st.balloons()
                    
                    st.markdown(f"**Nome:** `{info_aluno[CABEÇALHO_NOME_COMPLETO]}`")
                    st.markdown(f"**Evento:** `{info_evento[CABEÇALHO_NOME_EVENTO]}`")
                    st.markdown(f"**Data de Emissão:** `{data_emissao}`")
                    st.markdown(f"---")
                    st.link_button("Visualizar Certificado em PDF", url_pdf)
                else:
                    st.error("Certificado não encontrado. Por favor, verifique se o código de validação está correto.")
            except Exception as e:
                st.error(f"Ocorreu um erro durante a busca. Verifique se os nomes dos cabeçalhos na planilha e no script estão alinhados. Detalhe: {e}")
