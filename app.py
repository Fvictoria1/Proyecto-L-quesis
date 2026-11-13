import streamlit as st
from auth import MoiranAuth
from menu import MoiranMenu
from laquesis import MoiranLaquesis

# ---------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Moiran SCPS - Supply Chain Planning System",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------
# ESTILOS GLOBALES UI KIT MOIRAN SCPS
# ---------------------------------------------------------------------
def aplicar_ui_kit():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;800;900&display=swap');

/* Ajuste de márgenes superiores del área principal para la Top Navbar */
.block-container {
    padding-top: 2.2rem !important;
    padding-bottom: 2rem !important;
}

/* Posicionamiento de Toasts en Esquina Superior Izquierda */
[data-testid="stToastContainer"] {
    top: 20px !important;
    left: 20px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 999999 !important;
}

[data-testid="stToast"] {
    background-color: #1A1F26 !important;
    color: #F1F5F9 !important;
    border: 1px solid #00E5FF !important;
    border-radius: 10px !important;
    box-shadow: 0 8px 20px rgba(0, 229, 255, 0.25) !important;
    padding: 12px 18px !important;
}

/* Fondo general con gradientes oscuros y textura SVG */
.stApp {
    background-color: #121519 !important;
    background-image: 
        radial-gradient(circle at 50% 20%, rgba(0, 229, 255, 0.08) 0%, transparent 50%),
        radial-gradient(circle at 85% 85%, rgba(123, 44, 191, 0.06) 0%, transparent 45%),
        url("data:image/svg+xml,%3Csvg width='120' height='120' viewBox='0 0 120 120' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 90 Q 30 30, 60 70 T 120 40' stroke='rgba(0,229,255,0.035)' stroke-width='1.5' fill='none'/%3E%3Cpath d='M0 100 Q 40 50, 80 80 T 120 20' stroke='rgba(123,44,191,0.025)' stroke-width='1.5' fill='none'/%3E%3Ccircle cx='60' cy='70' r='2.5' fill='rgba(0,229,255,0.05)'/%3E%3Ccircle cx='120' cy='40' r='3.5' fill='rgba(0,229,255,0.08)'/%3E%3C/svg%3E") !important;
}

/* Barra Superior Horizontal (Top Navbar) */
.top-navbar-container {
    background-color: #161A20;
    border: 1px solid #232A34;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 18px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
}

/* Estilo de la Barra Lateral (Sidebar exclusiva para Guía de Operación) */
[data-testid="stSidebar"] {
    background-color: #161A20 !important;
    border-right: 1px solid #232A34 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem !important;
}

/* Estilo de Inputs de Texto */
.stTextInput input {
    background-color: #1A1F26 !important;
    color: #F1F5F9 !important;
    border: 1px solid #2D3748 !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    font-size: 14px !important;
    transition: all 0.3s ease !important;
}
.stTextInput input:focus {
    border-color: #00E5FF !important;
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.3) !important;
}
.stTextInput label {
    color: #94A3B8 !important;
    font-weight: 600 !important;
}

/* Botones Primarios (Gradiente Ciano / Glow) */
div.stButton > button[kind="primary"],
div.stButton > button:first-child:not([kind="secondary"]) {
    background: linear-gradient(135deg, #00E5FF 0%, #0088FF 100%) !important;
    color: #090B0E !important;
    font-weight: 800 !important;
    letter-spacing: 1.1px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 14px !important;
    box-shadow: 0 4px 15px rgba(0, 229, 255, 0.22) !important;
    transition: all 0.25s ease !important;
}
div.stButton > button[kind="primary"]:hover,
div.stButton > button:first-child:not([kind="secondary"]):hover {
    background: linear-gradient(135deg, #33EBFF 0%, #1A94FF 100%) !important;
    box-shadow: 0 6px 20px rgba(0, 229, 255, 0.4) !important;
    transform: translateY(-1px);
}
div.stButton > button:disabled {
    background: #232A34 !important;
    color: #64748B !important;
    box-shadow: none !important;
    border: 1px solid #2D3748 !important;
    cursor: not-allowed !important;
}

/* Acoplamiento de botones secundarios en la Barra Superior Horizontal */
div[data-testid="column"] div.stButton > button[kind="secondary"] {
    background-color: #121519 !important;
    color: #CBD5E1 !important;
    border: 1px solid #2D3748 !important;
    border-radius: 0 0 10px 10px !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    padding: 8px 12px !important;
    margin-top: -16px !important;
    transition: all 0.25s ease !important;
}
div[data-testid="column"] div.stButton > button[kind="secondary"]:hover {
    border-color: #00E5FF !important;
    color: #00E5FF !important;
    background-color: rgba(0, 229, 255, 0.08) !important;
}

/* Acoplamiento del botón primario activo con su tarjeta superior en Top Navbar */
div[data-testid="column"] div.stButton > button[kind="primary"] {
    border-radius: 0 0 10px 10px !important;
    font-size: 12px !important;
    padding: 8px 12px !important;
    margin-top: -16px !important;
}

/* Botón Secundario / Descargar Plantilla en Sidebar */
[data-testid="stSidebar"] div.stDownloadButton > button {
    background-color: #1A1F26 !important;
    color: #00E5FF !important;
    border: 1px solid #00E5FF !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    padding: 10px 14px !important;
    transition: all 0.3s ease !important;
}
[data-testid="stSidebar"] div.stDownloadButton > button:hover {
    background-color: rgba(0, 229, 255, 0.12) !important;
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.3) !important;
}

/* Zona de Carga de Archivos */
[data-testid="stFileUploadDropzone"] {
    background-color: #1A1F26 !important;
    border: 1px dashed #00E5FF !important;
    border-radius: 10px !important;
}

/* Tarjeta Principal de Bienvenida */
.welcome-card {
    background-color: #161A20;
    border: 1px solid #232A34;
    border-radius: 12px;
    padding: 40px 25px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    margin-bottom: 25px;
    text-align: center;
}

/* Tarjeta KPI Personalizada Flotante y Centrada */
.kpi-card {
    background-color: #1A1F26;
    border: 1px solid #2D3748;
    border-radius: 10px;
    padding: 12px 10px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    min-height: 98px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    transition: all 0.3s ease;
}
.kpi-card:hover {
    border-color: #00E5FF;
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.2);
}
.kpi-title {
    color: #94A3B8;
    font-size: clamp(10px, 0.85vw, 12px);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
}
.kpi-value {
    color: #00E5FF;
    font-size: clamp(12px, 1.1vw, 19px);
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

aplicar_ui_kit()

# ---------------------------------------------------------------------
# LIMPIEZA DE ESTADO GLOBAL AL CERRAR SESIÓN
# ---------------------------------------------------------------------
def limpiar_sesion_global():
    MoiranLaquesis.limpiar_estado()
    for key in ["toast_pendiente", "modulo_activo"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ---------------------------------------------------------------------
# GUARDIA DE ACCESO (MOIRAN AUTH)
# ---------------------------------------------------------------------
auth = MoiranAuth()

if not auth.requerir_autenticacion():
    st.stop()

# ---------------------------------------------------------------------
# FLUJO PRINCIPAL AUTENTICADO -> BARRA SUPERIOR HORIZONTAL (MOIRAN MENU)
# ---------------------------------------------------------------------
if "toast_pendiente" in st.session_state and st.session_state["toast_pendiente"]:
    st.toast(st.session_state["toast_pendiente"])
    del st.session_state["toast_pendiente"]

menu_principal = MoiranMenu(auth=auth, callback_limpieza=limpiar_sesion_global)
modulo_actual = menu_principal.renderizar()

# ---------------------------------------------------------------------
# ENRUTADOR DE MÓDULOS INDEPENDIENTES (GUÍA EN SIDEBAR + WORKSPACE)
# ---------------------------------------------------------------------
if modulo_actual == "cloto":
    pass
elif modulo_actual == "laquesis":
    modulo_laquesis = MoiranLaquesis(usuario_actual=auth.usuario_actual)
    modulo_laquesis.renderizar()
elif modulo_actual == "atropo":
    pass