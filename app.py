import streamlit as st
import gspread
import pandas as pd
import os

# -----------------------------------------------------------------------------
# --- CONFIGURAÇÃO ---
# Edite os valores abaixo para corresponder à sua configuração.
# -----------------------------------------------------------------------------

CONFIG = {
    # !!! AÇÃO NECESSÁRIA: Cole a URL completa da sua MasterSheet aqui !!!
    "URL_PLANILHA": "https://docs.google.com/spreadsheets/d/1Y3mhS5BoB-0H6VQWOZcOq13NgQmQq8qeD3pqR5fMCyE/edit?gid=1697416463#gid=1697416463",

    # !!! AÇÃO NECESSÁRIA: Verifique se os nomes abaixo são IDÊNTICOS aos da sua planilha !!!
    "ABAS": {
        "EMISSOES": "emissoes",
        "ALUNOS": "cadastros",
        "EVENTOS": "cursos_eventos"
    },
    "CABEÇALHOS": {
        "CODIGO_VALIDACAO": "codigo_validacao", # Na aba 'emissoes'
        "ID_ALUNO": "id_aluno",                 # Em 'emissoes' e 'cadastros'
        "ID_EVENTO": "id_evento",               # Em 'emissoes' e 'cursos_eventos'
        "DATA_EMISSAO": "data_emissao",         # Na aba 'emissoes'
        "URL_PDF": "url_pdf",                   # Na aba 'emissoes'
        "NOME_COMPLETO": "nome_completo",       # Na aba 'cadastros'
        "NOME_EVENTO": "nome_evento"            # Na aba 'cursos_eventos'
    }
}

# -----------------------------------------------------------------------------
# --- FUNÇÕES AUXILIARES ---
# -----------------------------------------------------------------------------

def load_custom_css():
    """ Injeta CSS para aplicar as fontes e cores da marca. """
    st.markdown("""
        <style>
            /* 1. Importa as fontes DM Sans e DM Mono do Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;700&display=swap');

            /* 2. Aplica as fontes aos elementos */
            html, body, [class*="css"], .stTextInput, .stButton {
                font-family: 'DM Sans', sans-serif;
            }
            code, pre {
                font-family: 'DM Mono', monospace;
            }

            /* 3. Estilos customizados com as cores da marca */
            .stButton>button {
                background-color: #000000;
                color: #F74406;
                border: 1px solid #F74406;
                transition: all 0.2s ease-in-out;
            }
            .stButton>button:hover {
                background-color: #F74406;
                color: #FFFFFF;
                border-color: #F74406;
            }
            .stButton>button:focus {
                box-shadow: 0 0 0 0.2rem rgba(247, 68, 6, 0.5) !important;
            }
        </style>
    """, unsafe_allow_html=True)

def connect_to_google_sheets():
    """ Estabelece conexão com o Google Sheets de forma segura (local vs. nuvem). """
    if os.path.exists('credentials.json'):
        return gspread.service_account(filename='credentials.json')
    else:
        return gspread.service_account_from_dict(st.secrets)

# -----------------------------------------------------------------------------
# --- INÍCIO DA APLICAÇÃO STREAMLIT ---
# -----------------------------------------------------------------------------

# Configuração da página e carregamento do CSS
st.set_page_config(page_title="Validação de Certificado", page_icon="✅", layout="centered")
load_custom_css()

# Logo na barra lateral (usando o parâmetro correto)
st.sidebar.image("assets/logo.png", use_container_width=True)

# Título principal
st.title("Verificação de Autenticidade")

# Conexão com a planilha
try:
    gc = connect_to_google_sheets()
    sh = gc.open_by_url(CONFIG["URL_PLANILHA"])
except Exception as e:
    st.error("Ocorreu um erro de configuração ou conexão. Contate o administrador.")
    st.stop()

# --- Interface principal e lógica de validação ---

# Lê o código de validação do parâmetro 'c' na URL
params = st.query_params
codigo_url = params.get('c', [None])[0]

codigo_validacao = st.text_input(
    label="Código de Validação",
    value=codigo_url if codigo_url else "",
    placeholder="Cole o código de validação aqui...",
    label_visibility="collapsed"
)

verificar_btn = st.button("Verificar Certificado", use_container_width=True)

# Executa a busca se o botão for clicado ou se um código vier da URL
if verificar_btn or codigo_url:
    if not codigo_validacao:
        st.warning("Por favor, insira um código de validação.")
    else:
        with st.spinner("Buscando em nossos registros..."):
            try:
                # Carrega as abas como DataFrames do Pandas
                emissoes_df = pd.DataFrame(sh.worksheet(CONFIG["ABAS"]["EMISSOES"]).get_all_records())
                alunos_df = pd.DataFrame(sh.worksheet(CONFIG["ABAS"]["ALUNOS"]).get_all_records())
                eventos_df = pd.DataFrame(sh.worksheet(CONFIG["ABAS"]["EVENTOS"]).get_all_records())

                # Busca o registro da emissão
                registro = emissoes_df[emissoes_df[CONFIG["CABEÇALHOS"]["CODIGO_VALIDACAO"]].astype(str) == str(codigo_validacao)]

                if not registro.empty:
                    dados = registro.iloc[0]
                    id_aluno = dados[CONFIG["CABEÇALHOS"]["ID_ALUNO"]]
                    id_evento = dados[CONFIG["CABEÇALHOS"]["ID_EVENTO"]]

                    info_aluno = alunos_df[alunos_df[CONFIG["CABEÇALHOS"]["ID_ALUNO"]].astype(str) == str(id_aluno)].iloc[0]
                    info_evento = eventos_df[eventos_df[CONFIG["CABEÇALHOS"]["ID_EVENTO"]].astype(str) == str(id_evento)].iloc[0]

                    # Bloco de resultado totalmente customizado
                    st.markdown(f"""
                        <div style="
                            border: 1px solid #F74406; 
                            border-radius: 10px; 
                            padding: 25px; 
                            text-align: center;
                            background-color: #1C1C1E;
                        ">
                            <h2 style="color: #FFFFFF; margin-bottom: 25px;">✅ Certificado Válido e Autêntico!</h2>
                            <p style="color: #FFFFFF; font-size: 18px; margin: 5px;"><strong>Nome:</strong> {info_aluno[CONFIG['CABEÇALHOS']['NOME_COMPLETO']]}</p>
                            <p style="color: #FFFFFF; font-size: 18px; margin: 5px;"><strong>Evento:</strong> {info_evento[CONFIG['CABEÇALHOS']['NOME_EVENTO']]}</p>
                            <p style="color: #FFFFFF; font-size: 18px; margin: 5px;"><strong>Data de Emissão:</strong> {dados[CONFIG['CABEÇALHOS']['DATA_EMISSAO']]}</p>
                        </div>
                    """, unsafe_allow_html=True)

                    st.write("") # Adiciona um espaço vertical
                    st.link_button("Visualizar Certificado em PDF", dados[CONFIG['CABEÇALHOS']['URL_PDF']], use_container_width=True)
                    st.toast('Validação concluída!', icon='🎉')
                else:
                    st.error("Certificado não encontrado. Por favor, verifique se o código de validação está correto.")
            
            except Exception as e:
                st.error("Ocorreu um erro durante a busca. Verifique se os nomes dos cabeçalhos na planilha e no script estão alinhados.")