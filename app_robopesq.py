import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import hashlib
import requests  # para enviar mensagem ao Telegram

# ==========================
# CONFIG STREAMLIT (GERAL)
# ==========================

st.set_page_config(
    page_title="RGP - Deferimento CPF",
    layout="wide",
)

# ==========================
# ESTILO GLOBAL (CSS)
# ==========================

def aplicar_estilo_global():
    st.markdown(
        """
        <style>
        /* Fonte moderna */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        html, body, [class*="css"] {
            font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        /* Fundo geral com gradiente moderno */
        .stApp {
            background: radial-gradient(circle at top left, #0f766e29, transparent 55%),
                        radial-gradient(circle at bottom right, #1d4ed829, #020617);
            color: #e5e7eb;
        }

        /* Container principal */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1100px;
        }

        /* Sidebar moderna */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #020617, #020617);
            border-right: 1px solid rgba(148, 163, 184, 0.35);
        }

        [data-testid="stSidebar"] * {
            color: #e5e7eb !important;
        }

        [data-testid="stSidebar"] .stRadio > label {
            font-weight: 600;
            letter-spacing: 0.02em;
        }

        /* Títulos */
        h1, h2, h3, h4 {
            color: #e5e7eb;
        }

        /* Métricas (cards) */
        div[data-testid="stMetric"] {
            background: rgba(15, 23, 42, 0.90);
            padding: 18px;
            border-radius: 18px;
            box-shadow: 0 20px 40px rgba(15, 23, 42, 0.70);
            border: 1px solid rgba(148, 163, 184, 0.45);
        }

        /* Botões */
        button[kind="primary"] {
            border-radius: 999px !important;
            font-weight: 600 !important;
        }

        /* DataFrame */
        .stDataFrame {
            background: rgba(15, 23, 42, 0.92);
            border-radius: 18px;
            padding: 6px;
            box-shadow: 0 16px 36px rgba(15,23,42,0.80);
            border: 1px solid rgba(148, 163, 184, 0.45);
        }
        .stDataFrame table {
            font-size: 0.9rem;
        }

        /* Caixas tipo cartão de vidro */
        .caixa-bloco {
            background: rgba(15, 23, 42, 0.92);
            padding: 18px 20px;
            border-radius: 20px;
            box-shadow: 0 18px 45px rgba(15,23,42,0.95);
            margin-bottom: 18px;
            border: 1px solid rgba(148, 163, 184, 0.40);
            backdrop-filter: blur(10px);
        }

        /* Card de login */
        .login-card {
            max-width: 520px;
            margin: 40px auto 10px auto;
            background: rgba(15, 23, 42, 0.96);
            padding: 24px 26px;
            border-radius: 22px;
            box-shadow: 0 28px 65px rgba(15,23,42,0.98);
            border: 1px solid rgba(148, 163, 184, 0.55);
        }

        .login-title {
            font-size: 24px;
            font-weight: 800;
            margin-bottom: 4px;
            letter-spacing: 0.03em;
        }

        .login-subtitle {
            font-size: 13px;
            color: #cbd5f5;
            margin-bottom: 16px;
        }

        .login-pill {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            background: rgba(37, 99, 235, 0.15);
            border: 1px solid rgba(96, 165, 250, 0.6);
            font-size: 11px;
            color: #bfdbfe;
            margin-bottom: 10px;
        }

        /* Tabs de login */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 999px;
            padding-top: 4px;
            padding-bottom: 4px;
        }

        /* Chips de info no cabeçalho */
        .chip {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11px;
            background: rgba(15, 23, 42, 0.25);
            border: 1px solid rgba(226, 232, 240, 0.35);
            margin-right: 6px;
        }

        /* Rodapé */
        .rodape-rgp {
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
            margin-top: 32px;
            margin-bottom: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

aplicar_estilo_global()

# ==========================
# ARQUIVOS LOCAIS
# ==========================

ARQUIVO_DADOS = Path("pescadores_robopesq.csv")
ARQUIVO_USUARIOS = Path("usuarios_robopesq.csv")

# ==========================
# CONFIG ADMINISTRADOR
# ==========================

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Didoge17"

# ==========================
# CONFIG TELEGRAM (ALERTA)
# ==========================

ATIVAR_TELEGRAM = True

TELEGRAM_BOT_TOKEN = "8177978199:AAFemguhf7LXucKKZMqg4dZRzpAF8ZEF8Z0"
TELEGRAM_CHAT_ID = 6247567864

# ==========================
# COLUNAS DAS TABELAS
# ==========================

COLUNAS_DADOS = [
    "id",
    "data_cadastro",
    "responsavel",
    "municipio",
    "nome_pescador",
    "cpf",
    "selecionado_deferimento",
    "observacoes"
]

COLUNAS_USUARIOS = [
    "username",
    "nome",
    "municipio",
    "senha_hash",
    "role"
]

# ==========================
# FUNÇÕES AUXILIARES - USUÁRIOS
# ==========================

def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def inicializar_usuarios():
    if not ARQUIVO_USUARIOS.exists():
        df = pd.DataFrame(columns=COLUNAS_USUARIOS)
        df.to_csv(ARQUIVO_USUARIOS, index=False, encoding="utf-8")


def carregar_usuarios() -> pd.DataFrame:
    inicializar_usuarios()
    df = pd.read_csv(ARQUIVO_USUARIOS, dtype=str)
    for col in COLUNAS_USUARIOS:
        if col not in df.columns:
            df[col] = ""
    return df


def salvar_usuarios(df: pd.DataFrame):
    df = df[COLUNAS_USUARIOS]
    df.to_csv(ARQUIVO_USUARIOS, index=False, encoding="utf-8")

# ==========================
# FUNÇÕES AUXILIARES - DADOS CPF
# ==========================

def inicializar_base_dados():
    if not ARQUIVO_DADOS.exists():
        df = pd.DataFrame(columns=COLUNAS_DADOS)
        df.to_csv(ARQUIVO_DADOS, index=False, encoding="utf-8")


def carregar_dados() -> pd.DataFrame:
    inicializar_base_dados()
    df = pd.read_csv(ARQUIVO_DADOS, dtype=str)
    for col in COLUNAS_DADOS:
        if col not in df.columns:
            df[col] = ""
    df["selecionado_deferimento"] = df["selecionado_deferimento"].fillna("").astype(str)
    df["selecionado_deferimento"] = df["selecionado_deferimento"].apply(
        lambda x: True if str(x).lower() in ["true", "1", "sim"] else False
    )
    return df


def salvar_dados(df: pd.DataFrame):
    df = df[COLUNAS_DADOS]
    df["selecionado_deferimento"] = df["selecionado_deferimento"].astype(str)
    df.to_csv(ARQUIVO_DADOS, index=False, encoding="utf-8")


def limpar_cpf(cpf: str) -> str:
    if not cpf:
        return ""
    return "".join([c for c in str(cpf) if c.isdigit()])


def gerar_novo_id(df: pd.DataFrame) -> int:
    if df.empty:
        return 1
    try:
        return int(df["id"].astype(int).max()) + 1
    except Exception:
        return 1

# ==========================
# TELEGRAM - NOTIFICAÇÃO
# ==========================

def enviar_telegram_novo_cadastro(cpf: str, nome_pescador: str, responsavel: str, municipio: str):
    if not ATIVAR_TELEGRAM:
        return

    try:
        texto = (
            "🟢 *Novo CPF cadastrado no RGP*\n"
            f"*CPF:* `{cpf}`\n"
            f"*Pescador:* {nome_pescador if nome_pescador else '_não informado_'}\n"
            f"*Responsável:* {responsavel}\n"
            f"*Município:* {municipio}"
        )

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": texto,
            "parse_mode": "Markdown"
        }

        resp = requests.post(url, json=payload, timeout=10)
        if not resp.ok:
            st.warning(f"Não foi possível enviar mensagem no Telegram: {resp.text}")

    except Exception as e:
        st.warning(f"Erro ao enviar mensagem no Telegram: {e}")

# ==========================
# LOGIN / SESSÃO
# ==========================

def inicializar_sessao():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.nome = None
        st.session_state.municipio = None
        st.session_state.role = None


def fazer_logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.nome = None
    st.session_state.municipio = None
    st.session_state.role = None


def tela_login():
    st.markdown(
        """
        <div class="login-card">
            <div class="login-pill">Acesso restrito a colônias e associações de pescadores</div>
            <div class="login-title">🐟 RGP - Deferimento CPF</div>
            <div class="login-subtitle">
                Plataforma segura para cadastro e gestão de CPFs de pescadores,
                com foco em listas para deferimento e controle por município.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        tab_login, tab_cadastro = st.tabs(["Já tenho acesso", "Criar novo acesso"])

        # ------------------ ABA LOGIN ------------------
        with tab_login:
            st.subheader("Entrar no sistema")

            usuario = st.text_input("Login")
            senha = st.text_input("Senha", type="password")

            if st.button("Entrar", key="btn_login"):
                if usuario == ADMIN_USERNAME and senha == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.username = ADMIN_USERNAME
                    st.session_state.nome = "Administrador"
                    st.session_state.municipio = "(todos)"
                    st.session_state.role = "admin"
                    st.success("Login de administrador efetuado com sucesso!")
                    st.rerun()

                df_users = carregar_usuarios()
                linha = df_users[df_users["username"] == usuario]

                if linha.empty:
                    st.error("Login não encontrado. Se ainda não tem acesso, use a aba 'Criar novo acesso'.")
                    return

                senha_hash = linha.iloc[0]["senha_hash"]
                if senha_hash != hash_senha(senha):
                    st.error("Senha incorreta.")
                    return

                st.session_state.logged_in = True
                st.session_state.username = usuario
                st.session_state.nome = linha.iloc[0]["nome"]
                st.session_state.municipio = linha.iloc[0]["municipio"]
                st.session_state.role = linha.iloc[0]["role"] or "user"

                st.success("Login realizado com sucesso!")
                st.rerun()

        # ------------------ ABA CADASTRO ------------------
        with tab_cadastro:
            st.subheader("Criar novo acesso")

            df_users = carregar_usuarios()

            col1, col2 = st.columns(2)
            with col1:
                nome_user = st.text_input("Nome completo", key="cad_nome")
                username = st.text_input("Login desejado (sem espaços)", key="cad_username")
            with col2:
                municipio_user = st.text_input("Município", key="cad_municipio")
                senha_user = st.text_input("Senha", type="password", key="cad_senha")
                senha_conf = st.text_input("Confirmar senha", type="password", key="cad_senha_conf")

            if st.button("Criar conta", key="btn_criar_conta"):
                if not nome_user or not username or not municipio_user or not senha_user or not senha_conf:
                    st.error("Preencha todos os campos para criar o acesso.")
                    return

                if " " in username:
                    st.error("O login não pode conter espaços. Use algo como: joao_sbrp.")
                    return

                if senha_user != senha_conf:
                    st.error("As senhas não conferem. Digite a mesma senha nos dois campos.")
                    return

                if (df_users["username"] == username).any() or username == ADMIN_USERNAME:
                    st.error("Já existe um usuário com esse login. Escolha outro.")
                    return

                novo = {
                    "username": username,
                    "nome": nome_user,
                    "municipio": municipio_user,
                    "senha_hash": hash_senha(senha_user),
                    "role": "user"
                }
                df_users = pd.concat([df_users, pd.DataFrame([novo])], ignore_index=True)
                salvar_usuarios(df_users)

                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.nome = nome_user
                st.session_state.municipio = municipio_user
                st.session_state.role = "user"

                st.success("Conta criada com sucesso! Você já está logado no sistema.")
                st.rerun()

# ==========================
# INÍCIO DO APP
# ==========================

inicializar_sessao()

if not st.session_state.logged_in:
    tela_login()
    st.stop()

# Cabeçalho moderno
st.markdown(
    """
    <div style="
        background: linear-gradient(120deg, #0f766e, #0891b2, #22c55e);
        padding: 16px 20px;
        border-radius: 22px;
        color: white;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 28px 70px rgba(15,23,42,0.95);
        border: 1px solid rgba(148, 163, 184, 0.60);
    ">
        <div>
            <div style="font-size: 22px; font-weight: 800; letter-spacing: 0.03em;">
                RGP · Registro Geral de Pescadores
            </div>
            <div style="margin-top: 6px;">
                <span class="chip">📍 Gestão por município</span>
                <span class="chip">📤 Exportação de CPFs para deferimento</span>
                <span class="chip">📲 Alerta automático via Telegram</span>
            </div>
        </div>
        <div style="font-size: 13px; text-align: right; opacity: 0.92;">
            Usuário: <b>{nome}</b><br>
            Perfil: <b>{role}</b>
        </div>
    </div>
    """.format(
        nome=st.session_state.nome or "",
        role="Administrador" if st.session_state.role == "admin" else "Responsável"
    ),
    unsafe_allow_html=True
)

st.caption(
    f"Usuário logado: **{st.session_state.nome}** "
    f"({st.session_state.username}) – Papel: **{st.session_state.role}**"
)

if st.sidebar.button("🔓 Sair"):
    fazer_logout()
    st.rerun()

# ==========================
# MENU LATERAL
# ==========================

if st.session_state.role == "admin":
    opcoes_menu = ["🛠️ Administração"]
else:
    opcoes_menu = ["📋 Cadastro de CPFs", "✅ Lista para Deferimento"]

menu = st.sidebar.radio("Navegação", opcoes_menu, index=0)

st.sidebar.info(
    "Responsáveis dos municípios:\n"
    "- Criam seu próprio acesso.\n"
    "- Fazem cadastro de CPFs e deferimento.\n\n"
    "Administrador:\n"
    "- Usa login 'admin' e acompanha visão geral, relatórios e exclusões."
)

# ==========================
# PÁGINA: CADASTRO DE CPFs
# ==========================

if "Cadastro" in menu:
    st.subheader("📋 Cadastro de CPFs de Pescadores")

    df = carregar_dados()

    st.markdown(
        """
        <div class="caixa-bloco">
            <h4 style="margin-bottom: 10px;">Dados do Responsável</h4>
            <p style="font-size: 13px; color: #cbd5f5; margin-bottom: 4px;">
                Informe quem está preenchendo e o município correspondente.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        responsavel = st.text_input(
            "Nome do responsável*",
            value=st.session_state.nome or "",
            placeholder="Nome de quem está preenchendo"
        )
    with col2:
        municipio = st.text_input(
            "Município*",
            value=st.session_state.municipio if st.session_state.municipio not in [None, "(todos)"] else "",
            placeholder="Ex: São Benedito do Rio Preto - MA"
        )

    st.markdown(
        """
        <div class="caixa-bloco">
            <h4 style="margin-bottom: 10px;">Dados do Pescador</h4>
            <p style="font-size: 13px; color: #cbd5f5; margin-bottom: 4px;">
                Informe o CPF do pescador (e, se desejar, o nome para controle interno).
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:
        nome_pescador = st.text_input("Nome do pescador (opcional)")
    with c2:
        cpf = st.text_input("CPF do pescador*", placeholder="Apenas números ou com pontos/traços")

    selecionado_deferimento = st.checkbox("Já marcar este CPF para lista de deferimento?")
    observacoes = st.text_area("Observações (opcional)", height=80)

    st.markdown("---")

    if st.button("✅ Salvar CPF"):
        if not responsavel or not municipio or not cpf:
            st.error("Preencha os campos obrigatórios: responsável, município e CPF.")
        else:
            cpf_limpo = limpar_cpf(cpf)
            df = carregar_dados()
            ja_existe = df[df["cpf"].astype(str) == cpf_limpo]

            if not ja_existe.empty:
                st.warning("⚠️ Já existe um cadastro com esse CPF.")
            else:
                novo_id = gerar_novo_id(df)
                novo_registro = {
                    "id": novo_id,
                    "data_cadastro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "responsavel": responsavel,
                    "municipio": municipio,
                    "nome_pescador": nome_pescador,
                    "cpf": cpf_limpo,
                    "selecionado_deferimento": selecionado_deferimento,
                    "observacoes": observacoes
                }

                df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
                salvar_dados(df)
                enviar_telegram_novo_cadastro(cpf_limpo, nome_pescador, responsavel, municipio)

                st.success("CPF cadastrado com sucesso! 🎣")
                st.info(f"CPF cadastrado: **{cpf_limpo}**")

    st.markdown("### Cadastros Recentes")
    df = carregar_dados()
    if not df.empty:
        muni_filtro = st.text_input("Filtrar por município (opcional)", value="")
        df_visu = df.copy()
        if muni_filtro:
            df_visu = df_visu[df_visu["municipio"].str.contains(muni_filtro, case=False, na=False)]

        st.dataframe(
            df_visu.sort_values("data_cadastro", ascending=False)[
                ["id", "data_cadastro", "responsavel", "municipio", "nome_pescador", "cpf", "selecionado_deferimento"]
            ],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Ainda não há CPFs cadastrados.")

# ==========================
# PÁGINA: LISTA PARA DEFERIMENTO
# ==========================

elif "Lista" in menu:
    st.subheader("✅ Lista de CPF para Deferimento")

    df = carregar_dados()

    if df.empty:
        st.info("Ainda não há dados cadastrados.")
    else:
        col_filtros = st.columns(2)
        with col_filtros[0]:
            municipio_escolhido = st.selectbox(
                "Filtrar por município",
                options=["(Todos)"] + sorted(df["municipio"].dropna().unique().tolist())
            )
        with col_filtros[1]:
            somente_marcados = st.checkbox("Mostrar apenas já selecionados para deferimento", value=False)

        df_filtrado = df.copy()

        if municipio_escolhido != "(Todos)":
            df_filtrado = df_filtrado[df_filtrado["municipio"] == municipio_escolhido]

        if somente_marcados:
            df_filtrado = df_filtrado[df_filtrado["selecionado_deferimento"] == True]

        if df_filtrado.empty:
            st.warning("Nenhum registro encontrado com esses filtros.")
        else:
            st.markdown("### Marcar/Desmarcar para Deferimento")

            df_editavel_view = df_filtrado[[
                "id",
                "responsavel",
                "municipio",
                "nome_pescador",
                "cpf",
                "selecionado_deferimento"
            ]].copy()

            df_editado = st.data_editor(
                df_editavel_view,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "selecionado_deferimento": st.column_config.CheckboxColumn(
                        "Selecionar para deferimento?",
                        help="Marque se este CPF deve entrar na lista de deferimento."
                    )
                }
            )

            if st.button("💾 Salvar Marcações de Deferimento"):
                df_base = carregar_dados()
                for _, row in df_editado.iterrows():
                    idx = df_base.index[df_base["id"].astype(str) == str(row["id"])]
                    if len(idx) == 1:
                        df_base.loc[idx, "selecionado_deferimento"] = bool(row["selecionado_deferimento"])
                salvar_dados(df_base)
                st.success("Marcações atualizadas com sucesso! ✅")

            st.markdown("---")
            st.markdown("### Gerar Arquivo COM APENAS OS CPFs Deferidos")

            df_deferidos = carregar_dados()
            df_deferidos = df_deferidos[df_deferidos["selecionado_deferimento"] == True]

            if municipio_escolhido != "(Todos)":
                df_deferidos = df_deferidos[df_deferidos["municipio"] == municipio_escolhido]

            if df_deferidos.empty:
                st.info("Nenhum CPF marcado para deferimento com esses filtros.")
            else:
                st.success(f"Total de CPFs marcados para deferimento: **{len(df_deferidos)}**")

                df_exportar = df_deferidos[["cpf"]].copy()

                csv_bytes = df_exportar.to_csv(index=False, encoding="utf-8").encode("utf-8")

                nome_arquivo = "lista_deferimento_cpfs.csv"
                if municipio_escolhido != "(Todos)":
                    nome_arquivo = f"lista_deferimento_cpfs_{municipio_escolhido}.csv".replace(" ", "_")

                st.download_button(
                    "⬇️ Baixar lista de deferimento (somente CPF) (CSV)",
                    data=csv_bytes,
                    file_name=nome_arquivo,
                    mime="text/csv"
                )

                st.markdown("Pré-visualização (apenas CPF):")
                st.dataframe(df_exportar, use_container_width=True, hide_index=True)

# ==========================
# PÁGINA: ADMINISTRAÇÃO
# ==========================

elif "Administração" in menu:
    if st.session_state.role != "admin":
        st.error("Acesso restrito ao administrador.")
        st.stop()

    st.subheader("🛠️ Administração / Visão Geral")

    df = carregar_dados()

    if df.empty:
        st.info("Ainda não há dados cadastrados.")
    else:
        total_registros = len(df)
        total_municipios = df["municipio"].nunique()
        total_deferidos = df[df["selecionado_deferimento"] == True].shape[0]

        st.markdown("#### Visão geral dos cadastros")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total de cadastros", total_registros)
        c2.metric("Municípios cadastrados", total_municipios)
        c3.metric("CPFs marcados para deferimento", total_deferidos)

        st.markdown("---")
        st.markdown("### Tabela completa de CPFs (apenas para administração)")

        df_view = df.copy()
        df_view["Excluir"] = False

        df_edit = st.data_editor(
            df_view[[
                "id",
                "data_cadastro",
                "responsavel",
                "municipio",
                "nome_pescador",
                "cpf",
                "selecionado_deferimento",
                "observacoes",
                "Excluir"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "selecionado_deferimento": st.column_config.CheckboxColumn(
                    "Deferido?",
                    help="Indica se o CPF está marcado para lista de deferimento."
                ),
                "Excluir": st.column_config.CheckboxColumn(
                    "Excluir?",
                    help="Marque os registros que deseja apagar DEFINITIVAMENTE."
                )
            }
        )

        if st.button("🗑️ Excluir registros marcados"):
            ids_excluir = (
                df_edit.loc[df_edit["Excluir"] == True, "id"]
                .astype(str)
                .tolist()
            )

            if not ids_excluir:
                st.warning("Nenhum registro marcado para exclusão.")
            else:
                df_base = carregar_dados()
                antes = len(df_base)
                df_base = df_base[~df_base["id"].astype(str).isin(ids_excluir)]
                salvar_dados(df_base)
                apagados = antes - len(df_base)
                st.success(f"{apagados} registro(s) excluído(s) com sucesso.")
                st.info("A tabela foi atualizada.")
                st.rerun()

    st.markdown("---")
    st.markdown("### Teste de envio para Telegram")

    if st.button("📲 Enviar mensagem de TESTE para meu Telegram"):
        enviar_telegram_novo_cadastro(
            cpf="00000000000",
            nome_pescador="TESTE TELEGRAM",
            responsavel=st.session_state.nome or "ADMIN",
            municipio=st.session_state.municipio or "TESTE"
        )
        st.success("Se estiver tudo certo, a mensagem de teste deve chegar no seu Telegram em alguns segundos.")

    st.markdown("---")
    st.subheader("Usuários cadastrados")

    df_users = carregar_usuarios()
    if df_users.empty:
        st.info("Ainda não há usuários cadastrados (apenas o admin fixo).")
    else:
        st.dataframe(
            df_users[["username", "nome", "municipio", "role"]],
            use_container_width=True,
            hide_index=True
        )

    st.warning(
        "⚠ Os responsáveis criam o próprio acesso pela tela de login.\n"
        "Você continua usando o login 'admin' para acompanhar a visão geral, Telegram e excluir registros, se necessário."
    )

# ==========================
# RODAPÉ
# ==========================

st.markdown(
    """
    <div class="rodape-rgp">
        Sistema RGP • PesqBrasil · Desenvolvido com apoio de IA<br>
        Versão inicial para uso em colônias e associações de pescadores.
    </div>
    """,
    unsafe_allow_html=True
)
