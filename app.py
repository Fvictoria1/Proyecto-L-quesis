import streamlit as st
from auth import MoiranAuth
from menu import MoiranMenu

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

/* Estilo de la Barra Lateral (Sidebar) */
[data-testid="stSidebar"] {
    background-color: #161A20 !important;
    border-right: 1px solid #232A34 !important;
}

/* Estilo de Inputs de Texto */
.stTextInput input {
    background-color: #1A1F26 !important;
    color: #F1F5F9 !important;
    border: 1px solid #2D3748 !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    font-size: 15px !important;
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

/* Botones Principales (Gradiente Ciano / Glow) */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #00E5FF 0%, #0088FF 100%) !important;
    color: #090B0E !important;
    font-weight: 800 !important;
    letter-spacing: 1.2px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    box-shadow: 0 4px 15px rgba(0, 229, 255, 0.2) !important;
    transition: all 0.3s ease !important;
}
div.stButton > button:first-child:hover {
    background: linear-gradient(135deg, #33EBFF 0%, #1A94FF 100%) !important;
    box-shadow: 0 6px 20px rgba(0, 229, 255, 0.4) !important;
    transform: translateY(-1px);
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
</style>
""", unsafe_allow_html=True)

aplicar_ui_kit()

# ---------------------------------------------------------------------
# LIMPIEZA DE ESTADO GLOBAL AL CERRAR SESIÓN
# ---------------------------------------------------------------------
def limpiar_sesion_global():
    keys_a_borrar = [
        "df_resultados", "df_input", "detalle_competencia",
        "df_resultados_v1_1", "df_input_v1_1", "detalle_competencia_v1_1",
        "ultimo_guardado_msg", "toast_pendiente", "modulo_activo"
    ]
    for key in keys_a_borrar:
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
# FLUJO PRINCIPAL AUTENTICADO -> MENÚ PRINCIPAL (MOIRAN MENU)
# ---------------------------------------------------------------------
if "toast_pendiente" in st.session_state and st.session_state["toast_pendiente"]:
    st.toast(st.session_state["toast_pendiente"])
    del st.session_state["toast_pendiente"]

menu_principal = MoiranMenu(auth=auth, callback_limpieza=limpiar_sesion_global)
menu_principal.renderizar()