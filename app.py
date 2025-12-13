import streamlit as st
import bcrypt
import random
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# ================= CONFIG =================
st.set_page_config(page_title="⚽ Plataforma Profissional de Bilhetes", layout="wide")

# ================= BANCO SIMPLES =================
USUARIOS = {
    "nando": {
        "senha": bcrypt.hashpw("didoge17".encode(), bcrypt.gensalt()),
        "plano": "VIP",
        "role": "user"
    },
    "admin": {
        "senha": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()),
        "plano": "ADMIN",
        "role": "admin"
    }
}

# ================= SESSION =================
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.user = None

# ================= LOGIN =================
def login():
    st.title("🔐 Login Seguro")

    u = st.text_input("Usuário")
    s = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if u in USUARIOS and bcrypt.checkpw(s.encode(), USUARIOS[u]["senha"]):
            st.session_state.logado = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Credenciais inválidas")

if not st.session_state.logado:
    login()
    st.stop()

user = USUARIOS[st.session_state.user]

# ================= TOPO =================
st.title("⚽ Plataforma Profissional de Bilhetes")
st.caption(f"Usuário: **{st.session_state.user}** | Plano: **{user['plano']}**")

# ================= ADMIN PANEL =================
if user["role"] == "admin":
    with st.expander("📊 Painel Admin"):
        st.write("Usuários cadastrados:")
        for k, v in USUARIOS.items():
            st.write(f"- {k} | Plano: {v['plano']} | Role: {v['role']}")

# ================= PLANOS =================
if user["plano"] != "VIP" and user["role"] != "admin":
    st.warning("Plano FREE ativo. Faça upgrade para VIP.")
    if st.button("💳 Simular pagamento VIP"):
        USUARIOS[st.session_state.user]["plano"] = "VIP"
        st.success("Plano VIP ativado (simulado)")
        st.rerun()

# ================= IA DE APOSTAS =================
st.subheader("🤖 IA de Sugestão de Apostas")

modo = st.selectbox("Perfil de Risco", ["Ultra Conservador", "Normal", "Agressivo"])

PESO = {
    "Ultra Conservador": {"1X": 0.65, "X2": 0.25, "12": 0.10},
    "Normal": {"1X": 0.4, "X2": 0.35, "12": 0.25},
    "Agressivo": {"1X": 0.25, "X2": 0.30, "12": 0.45},
}

MAPA = {"1X": "Casa ou Empate", "X2": "Empate ou Fora", "12": "Casa ou Fora"}

def ia_opcao():
    return random.choices(list(PESO[modo].keys()), list(PESO[modo].values()))[0]

# ================= ENTRADA JOGOS =================
st.subheader("📋 Jogos (12 seguros)")

jogos = []
for i in range(12):
    c1, c2 = st.columns(2)
    casa = c1.text_input(f"Casa {i+1}", key=f"c{i}")
    fora = c2.text_input(f"Fora {i+1}", key=f"f{i}")
    if casa and fora:
        jogos.append(f"{casa} vs {fora}")

# ================= GERAR =================
if st.button("✨ Gerar Bilhetes"):
    if len(jogos) != 12:
        st.error("Preencha todos os 12 jogos")
    else:
        bilhetes = {}
        ranking = {}

        for b in range(4):
            escolhas = [ia_opcao() for _ in range(12)]
            bilhetes[f"Bilhete {b+1}"] = escolhas

            for j, op in zip(jogos, escolhas):
                ranking[j] = ranking.get(j, 0) + {"1X": 1, "X2": 2, "12": 3}[op]

        for nome, esc in bilhetes.items():
            risco = sum({"1X": 5, "X2": 10, "12": 18}[o] for o in esc)
            st.subheader(nome)
            st.progress(min(risco, 100) / 100)
            st.write(f"Risco estimado: **{risco}%**")

            for j, o in zip(jogos, esc):
                st.write(f"{j} | {MAPA[o]} ({o})")

        st.subheader("🏆 Ranking de Jogos Mais Seguros")
        for j, s in sorted(ranking.items(), key=lambda x: x[1]):
            st.write(f"{j} — Segurança: **{max(0,100-s*4)}%**")

        # ================= PDF =================
        if st.button("🖨️ Gerar PDF"):
            pdf = "bilhetes_12_jogos.pdf"
            c = canvas.Canvas(pdf, pagesize=A4)
            y = 800
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, "BILHETES PROFISSIONAIS - 12 JOGOS")
            y -= 30

            for nome, esc in bilhetes.items():
                c.setFont("Helvetica-Bold", 10)
                c.drawString(40, y, nome)
                y -= 15
                c.setFont("Helvetica", 8)
                for j, o in zip(jogos, esc):
                    c.drawString(40, y, f"{j} | {o}")
                    y -= 12
            c.save()
            st.success("PDF gerado com sucesso")

# ================= LOGOUT =================
st.divider()
if st.button("🚪 Sair"):
    st.session_state.logado = False
    st.session_state.user = None
    st.rerun()
