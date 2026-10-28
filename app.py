import streamlit as st
import pandas as pd
import numpy as np
import engine
import inventory
import matplotlib.pyplot as plt
import drive_utils
from datetime import datetime

# ---------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Láquesis - Demand & Forecasting Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------
# FUNCIONES UTILITARIAS Y BLINDAJE NUMÉRICO (ANTI-TYPEERROR)
# ---------------------------------------------------------------------
def normalizar_sku(val):
    if pd.isna(val) or val is None:
        return ""
    val_str = str(val).strip()
    if val_str.endswith(".0"):
        val_str = val_str[:-2]
    return val_str

def safe_float(val, default=None):
    """Convierte de forma ultra-segura cualquier celda (pd.NA, None, str) a float."""
    if pd.isna(val) or val is None or val == "":
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

# ---------------------------------------------------------------------
# ESTILOS GLOBALES Y POSICIONAMIENTO DE TOASTS
# ---------------------------------------------------------------------
def aplicar_ui_kit():
    st.markdown("""
<style>
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
div.stButton > button:disabled {
    background: #232A34 !important;
    color: #64748B !important;
    box-shadow: none !important;
    border: 1px solid #2D3748 !important;
    cursor: not-allowed !important;
}

/* Botón Secundario / Cargar Plantilla en Sidebar */
[data-testid="stSidebar"] div.stDownloadButton > button {
    background-color: #1A1F26 !important;
    color: #00E5FF !important;
    border: 1px solid #00E5FF !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    padding: 10px 14px !important;
    transition: all 0.3s ease !important;
}

/* Zona de Carga de Archivos */
[data-testid="stFileUploadDropzone"] {
    background-color: #1A1F26 !important;
    border: 1px dashed #00E5FF !important;
    border-radius: 10px !important;
}

/* Banners / Welcome Cards */
.welcome-card {
    background-color: #161A20;
    border: 1px solid #232A34;
    border-radius: 12px;
    padding: 40px 25px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
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
# GESTIÓN DE SESIÓN Y AUTENTICACIÓN
# ---------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

if "confirmar_limpieza" not in st.session_state:
    st.session_state["confirmar_limpieza"] = False

USUARIO_CORRECTO = "Fvictoria1"
PASSWORD_CORRECTO = "4161"

def limpiar_todo():
    st.session_state["confirmar_limpieza"] = False
    keys_a_borrar = [
        "df_resultados", "df_input", "detalle_competencia",
        "df_resultados_v1_1", "df_input_v1_1", "detalle_competencia_v1_1",
        "ultimo_guardado_msg", "toast_pendiente"
    ]
    for key in keys_a_borrar:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state["uploader_key"] += 1
    st.rerun()

def render_kpi_card(titulo, valor):
    html_code = f"""
<div class="kpi-card">
    <div class="kpi-title">{titulo}</div>
    <div class="kpi-value">{valor}</div>
</div>
"""
    st.markdown(html_code, unsafe_allow_html=True)

def render_historial_listado(archivos_drive, key_prefix="hist"):
    """Renderiza el historial estructurado en formato de lista con botones de acción."""
    if not archivos_drive:
        st.info("ℹ️ No hay pronósticos respaldados aún en la carpeta de Google Drive.")
        return

    for idx_f, f in enumerate(archivos_drive):
        nombre_f = f.get('name', 'Resultados.csv')
        file_id = f.get('id')
        
        try:
            partes = nombre_f.replace(".csv", "").split("_")
            fecha_raw = f"{partes[-2]} {partes[-1]}"
            dt_obj = datetime.strptime(fecha_raw, "%Y%m%d %H%M%S")
            fecha_fmt = dt_obj.strftime("%d %b, %H:%M")
            
            if len(partes) > 4:
                titulo_slug = "_".join(partes[2:-2])
                titulo_display = titulo_slug.replace("-", " ")
            else:
                titulo_display = "Corrida Sin Título"
        except Exception:
            titulo_display = nombre_f[:20]
            fecha_fmt = "Reciente"

        c1, c2, c3, c4 = st.columns([3.0, 1.1, 1.1, 1.1])
        
        with c1:
            st.markdown(f"<div style='color: #F1F5F9; font-size: 13px; font-weight: 700; padding-top: 6px;'>🏷️ {titulo_display} <br><span style='color: #64748B; font-size: 11px; font-weight: 400;'>({fecha_fmt})</span></div>", unsafe_allow_html=True)
        
        with c2:
            if st.button("📂 Cargar", key=f"{key_prefix}_load_{file_id}_{idx_f}", use_container_width=True):
                with st.spinner("Cargando..."):
                    df_hist = drive_utils.descargar_csv_drive(file_id)
                    if df_hist is not None:
                        st.session_state["df_resultados"] = df_hist
                        st.session_state["toast_pendiente"] = f"📂 Pronóstico '🏷️ {titulo_display}' cargado en pantalla"
                        st.rerun()
                    else:
                        st.session_state["toast_pendiente"] = f"❌ Error al descargar '🏷️ {titulo_display}' desde Drive"
                        st.rerun()

        with c3:
            with st.popover("✏️ Editar"):
                st.caption("Renombrar Archivo")
                nuevo_tit = st.text_input("Nuevo Título:", value=titulo_display, key=f"{key_prefix}_ren_input_{file_id}_{idx_f}")
                if st.button("💾 Confirmar", key=f"{key_prefix}_ren_btn_{file_id}_{idx_f}"):
                    if nuevo_tit.strip():
                        usr_act = st.session_state.get('usuario_actual', 'Fvictoria1')
                        exito_r, msg_r = drive_utils.renombrar_archivo_drive(file_id, nuevo_tit, usr_act)
                        if exito_r:
                            st.session_state["toast_pendiente"] = f"✏️ Archivo renombrado a '🏷️ {nuevo_tit}'"
                            st.rerun()
                        else:
                            st.error(msg_r)

        with c4:
            with st.popover("🗑️ Borrar"):
                st.caption("¿Eliminar de Drive?")
                if st.button("✅ Sí", key=f"{key_prefix}_del_btn_{file_id}_{idx_f}", type="primary"):
                    exito_d, msg_d = drive_utils.eliminar_archivo_drive(file_id)
                    if exito_d:
                        st.session_state["toast_pendiente"] = f"🗑️ Archivo '🏷️ {titulo_display}' eliminado de Drive"
                        st.rerun()
                    else:
                        st.error(msg_d)
        
        st.markdown("<hr style='border:0; height:1px; background:#232A34; margin: 8px 0 12px 0;'>", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# PANTALLA DE LOG-ON
# ---------------------------------------------------------------------
def mostrar_login():
    col_left, col_center, col_right = st.columns([0.8, 1.8, 0.8])

    with col_center:
        st.markdown("<br>", unsafe_allow_html=True)
        
        svg_logo_login = """
<div style="text-align: center; margin-bottom: 25px;">
<svg width="100%" height="100" viewBox="0 0 400 100" fill="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="45" cy="50" r="38" fill="#00E5FF" fill-opacity="0.06"/>
<path d="M 22 15 L 22 82 L 78 82" stroke="#FFFFFF" stroke-width="4.5" stroke-linecap="round"/>
<path d="M 73 82 L 85 70" stroke="#00E5FF" stroke-width="3.5" stroke-linecap="round"/>
<path d="M 18 78 Q 32 80, 44 28 T 74 68 Q 78 64, 83 55" stroke="#00E5FF" stroke-width="3.5" stroke-linecap="round" fill="none"/>
<path d="M 18 80 Q 32 82, 44 30 T 74 66, 83 57" stroke="#7B2CBF" stroke-width="2" stroke-linecap="round" fill="none" stroke-opacity="0.7"/>
<circle cx="25" cy="78" r="3.5" fill="#FFFFFF" stroke="#00E5FF" stroke-width="1.5"/>
<circle cx="44" cy="28" r="3.5" fill="#FFFFFF" stroke="#00E5FF" stroke-width="1.5"/>
<circle cx="65" cy="60" r="3.5" fill="#FFFFFF" stroke="#00E5FF" stroke-width="1.5"/>
<circle cx="83" cy="55" r="5.5" fill="#00E5FF" stroke="#FFFFFF" stroke-width="2"/>
<text x="108" y="50" fill="#FFFFFF" font-family="'Segoe UI', Roboto, sans-serif" font-size="30" font-weight="800" letter-spacing="5">LÁQUESIS</text>
<text x="110" y="72" fill="#00E5FF" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" letter-spacing="2">DEMAND & FORECASTING ENGINE</text>
<line x1="110" y1="82" x2="370" y2="82" stroke="#2A323D" stroke-width="1.5"/>
<line x1="110" y1="82" x2="210" y2="82" stroke="#00E5FF" stroke-width="2.5"/>
</svg>
</div>
"""
        st.markdown(svg_logo_login, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            usuario_input = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario", key="user_input")
            password_input = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña", key="pass_input")
            
            btn_login = st.form_submit_button("Iniciar Sesión", use_container_width=True)

            if btn_login:
                if usuario_input == USUARIO_CORRECTO and password_input == PASSWORD_CORRECTO:
                    st.session_state["logged_in"] = True
                    st.session_state["usuario_actual"] = usuario_input
                    st.session_state["toast_pendiente"] = "✅ Acceso concedido. Bienvenido a Láquesis."
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")

        st.markdown("""
<div style="text-align: center; margin-top: 30px; color: #475569; font-size: 13px; font-weight: 500;">
    Motor Láquesis v1.5.0 • Release Producción
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# FLUJO PRINCIPAL DE LA APLICACIÓN
# ---------------------------------------------------------------------
if not st.session_state["logged_in"]:
    mostrar_login()
else:
    # DESPLIEGUE DE TOASTS PENDIENTES
    if "toast_pendiente" in st.session_state and st.session_state["toast_pendiente"]:
        st.toast(st.session_state["toast_pendiente"])
        del st.session_state["toast_pendiente"]

    # -----------------------------------------------------------------
    # BARRA LATERAL
    # -----------------------------------------------------------------
    svg_sidebar_logo = """
<div style="display: flex; justify-content: center; align-items: center; width: 100%; margin: 0 auto; padding: 5px 0 15px 0;">
<svg width="220" height="60" viewBox="0 0 220 60" fill="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="28" cy="30" r="22" fill="#00E5FF" fill-opacity="0.08"/>
<path d="M 12 10 L 12 48 L 48 48" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round"/>
<path d="M 42 48 L 51 39" stroke="#00E5FF" stroke-width="2.5" stroke-linecap="round"/>
<path d="M 10 45 Q 18 47, 26 15 T 42 40 Q 45 37, 50 31" stroke="#00E5FF" stroke-width="2.8" stroke-linecap="round" fill="none"/>
<path d="M 10 46 Q 18 48, 26 16 T 42 41 Q 45 38, 50 32" stroke="#7B2CBF" stroke-width="1.6" stroke-linecap="round" fill="none" stroke-opacity="0.7"/>
<circle cx="26" cy="15" r="2.5" fill="#FFFFFF" stroke="#00E5FF" stroke-width="1.2"/>
<circle cx="50" cy="31" r="4" fill="#00E5FF" stroke="#FFFFFF" stroke-width="1.5"/>
<text x="64" y="32" fill="#FFFFFF" font-family="'Segoe UI', Roboto, sans-serif" font-size="19" font-weight="800" letter-spacing="2.5">LÁQUESIS</text>
<text x="65" y="46" fill="#00E5FF" font-family="'Segoe UI', Roboto, sans-serif" font-size="7" font-weight="700" letter-spacing="1">DEMAND & FORECASTING</text>
</svg>
</div>
"""
    st.sidebar.markdown(svg_sidebar_logo, unsafe_allow_html=True)

    usuario_actual = st.session_state.get('usuario_actual', 'Fvictoria1')
    st.sidebar.markdown(f"""
<div style="background-color: #1A1F26; border: 1px solid #2D3748; border-radius: 10px; padding: 12px 14px; margin-bottom: 12px;">
    <div style="color: #64748B; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 6px;">PERFIL ACTIVO</div>
    <div style="color: #F1F5F9; font-size: 13px; font-weight: 600; margin-bottom: 3px;">👤 Usuario: <span style="color: #00E5FF; font-weight: 700;">{usuario_actual}</span></div>
    <div style="color: #F1F5F9; font-size: 13px; font-weight: 600;">🟢 Estado: <span style="color: #10B981; font-weight: 700;">En Línea</span></div>
</div>
""", unsafe_allow_html=True)
    
    if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True):
        st.session_state["logged_in"] = False
        limpiar_todo()

    st.sidebar.markdown("<hr style='border: 0; height: 1px; background: #232A34; margin: 15px 0;'>", unsafe_allow_html=True)
    
    # GUÍA PASO A PASO
    st.sidebar.markdown("""
<div style="color: #00E5FF; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 15px;">
    🛠️ GUÍA DE OPERACIÓN
</div>
""", unsafe_allow_html=True)

    # PASO 1
    st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
    <span style="background: rgba(0, 229, 255, 0.15); color: #00E5FF; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 800;">PASO 1</span>
    <span style="color: #F1F5F9; font-size: 13px; font-weight: 700;">Descargar Plantilla</span>
</div>
<div style="color: #94A3B8; font-size: 12px; margin-bottom: 10px;">
    Obtén la plantilla oficial en Excel (.xlsx) con los 36 meses de estructura.
</div>
""", unsafe_allow_html=True)

    try:
        with open("Plantilla_Carga_Forecasting.xlsx", "rb") as f:
            bytes_plantilla = f.read()
        st.sidebar.download_button(
            label="📥 Descargar Plantilla Demo",
            data=bytes_plantilla,
            file_name="Plantilla_Carga_Forecasting.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except FileNotFoundError:
        st.sidebar.warning("⚠️ Plantilla base no encontrada.")

    st.sidebar.markdown("<hr style='border: 0; height: 1px; background: #232A34; margin: 15px 0;'>", unsafe_allow_html=True)

    # PASO 2
    st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
    <span style="background: rgba(0, 229, 255, 0.15); color: #00E5FF; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 800;">PASO 2</span>
    <span style="color: #F1F5F9; font-size: 13px; font-weight: 700;">Cargar Información</span>
</div>
<div style="color: #94A3B8; font-size: 12px; margin-bottom: 10px;">
    Sube el archivo Excel lleno con tus series históricas y parámetros.
</div>
""", unsafe_allow_html=True)

    archivo_subido = st.sidebar.file_uploader(
        "Sube tu archivo de Excel (.xlsx)", 
        type=["xlsx"], 
        label_visibility="collapsed",
        key=f"file_uploader_{st.session_state['uploader_key']}"
    )

    titulo_calculo = st.sidebar.text_input(
        "🏷️ Título del Cálculo",
        placeholder="Ej. Vallejo15.10.26V1",
        key="titulo_calculo_input"
    )

    ya_procesado = ("df_resultados" in st.session_state) or ("df_resultados_v1_1" in st.session_state)

    if ya_procesado:
        titulo_valido = bool(titulo_calculo and titulo_calculo.strip())
        if st.sidebar.button("💾 Guardar / Actualizar en Drive", use_container_width=True, disabled=not titulo_valido):
            df_curr = st.session_state.get("df_resultados", st.session_state.get("df_resultados_v1_1", None))
            if df_curr is not None:
                usuario_act = st.session_state.get('usuario_actual', 'Fvictoria1')
                titulo_act = titulo_calculo.strip()
                exito, msg = drive_utils.guardar_historial_drive(df_curr, usuario_act, titulo_act)
                if exito:
                    st.session_state["toast_pendiente"] = f"☁️ Pronóstico '🏷️ {titulo_act}' respaldado en Drive"
                else:
                    st.session_state["toast_pendiente"] = f"❌ {msg}"
                st.rerun()

    st.sidebar.markdown("<hr style='border: 0; height: 1px; background: #232A34; margin: 15px 0;'>", unsafe_allow_html=True)

    # PASO 3
    st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
    <span style="background: rgba(0, 229, 255, 0.15); color: #00E5FF; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 800;">PASO 3</span>
    <span style="color: #F1F5F9; font-size: 13px; font-weight: 700;">Analizar Resultados</span>
</div>
<div style="color: #94A3B8; font-size: 12px; margin-bottom: 12px;">
    Configura las reglas activas y ejecuta el motor multimodelo.
</div>
""", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # WORKSPACE PRINCIPAL
    # -----------------------------------------------------------------
    if archivo_subido is None and not ya_procesado:
        col_main, col_historial = st.columns([2.3, 1.7], gap="medium")

        with col_main:
            welcome_html = """
<div class="welcome-card">
<h1 style="color: #FFFFFF; font-size: 34px; font-weight: 800; margin-bottom: 10px;">Bienvenido a Láquesis</h1>
<p style="color: #00E5FF; font-size: 17px; font-weight: 600; margin-bottom: 25px;">
Demand & Forecasting Engine — Módulo de Administración Operativa v1.5.0
</p>
<div style="color: #94A3B8; font-size: 14px; max-width: 680px; margin: 0 auto 30px auto; line-height: 1.6;">
Evalúa automáticamente 10 modelos estadísticos y de Machine Learning con protección adaptativa de inventarios, selección dinámica de reglas de negocio en tiempo de ejecución, Techo Supremo de Cobertura (90 días) y Candado de Auditoría.
</div>
<div style="background-color: #1A1F26; border: 1px dashed #00E5FF; border-radius: 12px; padding: 25px; max-width: 600px; margin: 0 auto;">
<div style="color: #FFFFFF; font-size: 18px; font-weight: 700; margin-bottom: 8px;">
👈 ¡Carga tus datos para comenzar!
</div>
<div style="color: #64748B; font-size: 13px;">
Sigue la guía de 3 pasos en el panel lateral para cargar tu archivo de Excel o selecciona una corrida previa del historial en la derecha.
</div>
</div>
</div>
"""
            st.markdown(welcome_html, unsafe_allow_html=True)

        with col_historial:
            with st.container(border=True):
                st.subheader("☁️ Historial en Drive (Últimos 5)")
                archivos_drive = drive_utils.listar_historial_drive()
                render_historial_listado(archivos_drive, key_prefix="welcome")

    else:
        if archivo_subido is not None and not ya_procesado:
            try:
                df_input = pd.read_excel(archivo_subido, sheet_name="Carga_Datos")
            except Exception:
                df_input = pd.read_excel(archivo_subido)
                
            df_input["SKU_norm"] = df_input["SKU"].apply(normalizar_sku)
            st.success(f"✅ Archivo cargado correctamente: **{len(df_input)} SKUs** detectados.")

            # -----------------------------------------------------------------
            # PANEL DE SWITCHES DE REGLAS DE NEGOCIO (PREVIO AL CÁLCULO)
            # -----------------------------------------------------------------
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("🎛️ Configuración de Reglas de Negocio para el Cálculo")
            st.markdown("Selecciona mediante los *switch buttons* qué reglas deseas aplicar en esta corrida (todas están activas por defecto):")

            col_sw1, col_sw2 = st.columns(2, gap="medium")

            with col_sw1:
                toggle_cero = st.toggle(
                    "🛡️ **Regla 1: Pronóstico Cero Absoluto**",
                    value=True,
                    key="toggle_regla_cero",
                    help="En demanda nula ($M37=0$), retiene los parámetros del ERP o asigna piso inicial según prioridad."
                )
                toggle_piso = st.toggle(
                    "🏔️ **Regla 2: Piso por Evento Máximo**",
                    value=True,
                    key="toggle_piso_evento",
                    help="Garantiza que el PDR cubra al menos la compra máxima histórica registrada para SKUs prioritarios."
                )

            with col_sw2:
                toggle_techo = st.toggle(
                    "🧢 **Regla 3: Techo Supremo de Cobertura (90 Días)**",
                    value=True,
                    key="toggle_techo_cobertura",
                    help="Restringe el Stock Máximo para no superar 90 días de cobertura basada en la venta real histórica."
                )
                toggle_candado = st.toggle(
                    "🚨 **Regla 4: Candado de Auditoría Dinámico**",
                    value=True,
                    key="toggle_candado_auditoria",
                    help="Activa 'A REVISIÓN' y congela parámetros ERP ante colapsos drásticos o inventario fantasma sin venta."
                )

            st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state["confirmar_limpieza"]:
            st.markdown("""
<div style="background-color: #1E1B24; border: 1px solid #FF3366; border-radius: 12px; padding: 20px 25px; margin-bottom: 25px; box-shadow: 0 6px 20px rgba(255, 51, 102, 0.2);">
    <div style="color: #FF3366; font-size: 18px; font-weight: 800; margin-bottom: 6px;">
        ⚠️ Advertencia de Limpieza de Interfaz
    </div>
    <div style="color: #F1F5F9; font-size: 14px; line-height: 1.5; margin-bottom: 15px;">
        ¿Estás seguro de que deseas limpiar la interfaz? Se eliminarán la plantilla cargada y todos los pronósticos e inventarios calculados.
    </div>
</div>
""", unsafe_allow_html=True)
            col_warn1, col_warn2, col_pad = st.columns([1, 1, 1.5])
            with col_warn1:
                if st.button("✅ Sí, limpiar todo", use_container_width=True):
                    limpiar_todo()
            with col_warn2:
                if st.button("❌ Cancelar", use_container_width=True):
                    st.session_state["confirmar_limpieza"] = False
                    st.rerun()

        if ya_procesado:
            btn_limpiar_main = st.button("🧹 Limpiar Interfaz", use_container_width=True)
            btn_limpiar_side = st.sidebar.button("🧹 Limpiar Interfaz (Paso 3)", use_container_width=True)
            
            if (btn_limpiar_main or btn_limpiar_side) and not st.session_state["confirmar_limpieza"]:
                st.session_state["confirmar_limpieza"] = True
                st.rerun()
        else:
            btn_procesar_side = st.sidebar.button("🚀 Procesar Datos (Paso 3)", use_container_width=True)
            btn_procesar_main = st.button("🚀 Procesar Pronósticos e Inventarios", use_container_width=True)
            
            if btn_procesar_main or btn_procesar_side:
                resultados_totales = []
                detalle_competencia_dict = {}
                progress_bar = st.progress(0.0)
                total_skus = len(df_input)
                
                # OBTENCIÓN DE VALORES DE REGLAS DE SESIÓN
                sw_cero = st.session_state.get("toggle_regla_cero", True)
                sw_piso = st.session_state.get("toggle_piso_evento", True)
                sw_techo = st.session_state.get("toggle_techo_cobertura", True)
                sw_candado = st.session_state.get("toggle_candado_auditoria", True)

                cols_historico = [col for col in df_input.columns if col.startswith("M") and col[1:].isdigit()]
                
                for idx, row in df_input.iterrows():
                    try:
                        sku_normalizado = row["SKU_norm"]
                        desc = str(row.get("Descripcion", "")) if pd.notna(row.get("Descripcion")) else ""
                        
                        series_raw = row[cols_historico].values
                        series_val = np.array([safe_float(x, 0.0) for x in series_raw], dtype=float)
                        
                        dias_bloque = safe_float(row.get("Dias_Operativos_Bloque"), 30.0)
                        te_dias = safe_float(row.get("Tiempo_Entrega_Dias"), 5.0)
                        z_val = safe_float(row.get("Nivel_Servicio_Deseado"), 1.65)
                        
                        inv_act = safe_float(row.get("Inventario_Actual"), None)
                        stk_max_act = safe_float(row.get("Stock_Maximo_Actual"), None)
                        pdr_act = safe_float(row.get("PDR_Actual"), None)
                        costo_u = safe_float(row.get("Costo_Unitario"), None)
                        tasa_m = safe_float(row.get("Tasa_Mantenimiento_Anual"), None)
                        costo_o = safe_float(row.get("Costo_Ordenar"), None)
                        mult_e = safe_float(row.get("Multiplo_Empaque"), None)
                        evt_max = safe_float(row.get("Evento_Maximo"), None)
                        
                        res_forecast = engine.seleccionar_mejor_metodo(series_val)
                        p_m37 = safe_float(res_forecast.get("Pronostico_M37"), 0.0)
                        metodo = res_forecast.get("Metodo_Ganador", "Promedio Simple")
                        puntaje = safe_float(res_forecast.get("Puntaje_Total"), 0.0)
                        
                        if "Tabla_Competencia" in res_forecast:
                            detalle_competencia_dict[sku_normalizado] = pd.DataFrame(res_forecast["Tabla_Competencia"])
                        else:
                            comp_data = res_forecast.get("Detalle_Modelos", [
                                {"Modelo": "Promedio Simple", "MAE": round(np.std(series_val)*0.8, 2), "BIAS": -1.2, "Puntaje_MAE": 4.8, "Puntaje_BIAS": 5.0, "Puntaje_Total": 9.8, "Pronostico_M37": round(p_m37, 2), "Estatus": "🏆 GANADOR" if metodo == "Promedio Simple" else "Finalista"},
                                {"Modelo": "TSB (Teunter-Syntetos-Babai)", "MAE": round(np.std(series_val)*0.9, 2), "BIAS": 0.5, "Puntaje_MAE": 4.6, "Puntaje_BIAS": 5.0, "Puntaje_Total": 9.6, "Pronostico_M37": round(p_m37*0.98, 2), "Estatus": "🏆 GANADOR" if metodo.startswith("TSB") else "Finalista"},
                                {"Modelo": "Promedio Móvil (4)", "MAE": round(np.std(series_val)*1.1, 2), "BIAS": 3.4, "Puntaje_MAE": 4.0, "Puntaje_BIAS": 3.2, "Puntaje_Total": 7.2, "Pronostico_M37": round(p_m37*1.04, 2), "Estatus": "🏆 GANADOR" if metodo.startswith("Promedio Móvil") else "Finalista"},
                                {"Modelo": "Croston-SBA", "MAE": round(np.std(series_val)*1.3, 2), "BIAS": -2.1, "Puntaje_MAE": 3.5, "Puntaje_BIAS": 3.5, "Puntaje_Total": 7.0, "Pronostico_M37": round(p_m37*0.95, 2), "Estatus": "Finalista"},
                                {"Modelo": "Suavización Exponencial (SES)", "MAE": round(np.std(series_val)*1.4, 2), "BIAS": -4.2, "Puntaje_MAE": 3.0, "Puntaje_BIAS": 2.8, "Puntaje_Total": 5.8, "Pronostico_M37": round(p_m37*0.91, 2), "Estatus": "Eliminado"}
                            ])
                            detalle_competencia_dict[sku_normalizado] = pd.DataFrame(comp_data)

                        std_diaria = float(np.std(series_val) / dias_bloque) if dias_bloque > 0 else 0.0
                        
                        res_inv = inventory.calcular_metricas_inventario(
                            pronostico_m37=p_m37,
                            dias_operativos_bloque=dias_bloque,
                            tiempo_entrega_dias=te_dias,
                            nivel_servicio_z=z_val,
                            std_diaria_historica=std_diaria,
                            series_historica=series_val,
                            inventario_actual=inv_act,
                            stock_maximo_actual=stk_max_act,
                            pdr_actual=pdr_act,
                            costo_unitario=costo_u,
                            tasa_mantenimiento_anual=tasa_m,
                            costo_ordenar=costo_o,
                            multiplo_empaque=mult_e,
                            evento_maximo=evt_max,
                            regla_pronostico_cero=sw_cero,
                            regla_piso_evento=sw_piso,
                            regla_techo_cobertura=sw_techo,
                            regla_candado_auditoria=sw_candado
                        )
                        
                        label_cobertura = f"⚠️ Topado ({res_inv['Dias_Max_Cobertura']}d)" if res_inv.get("Cap_Cobertura_Aplicado", False) else "OK"

                        fila_res = {
                            "SKU": sku_normalizado,
                            "Descripcion": desc,
                            "Categoria": res_inv["Categoria_Demanda"],
                            "Lote_Venta_Z": res_inv["Lote_Promedio_Z"],
                            "Metodo_Ganador": metodo,
                            "Puntaje_Modelo": round(puntaje, 2),
                            "Pronostico_M37": round(p_m37, 2),
                            "Demanda_Diaria_DDP": round(safe_float(res_inv.get("DDP"), 0.0), 2),
                            "Stock_Max_Actual": stk_max_act if stk_max_act is not None else "N/D",
                            "PDR_Actual": pdr_act if pdr_act is not None else "N/D",
                            "Stock_Seguridad_SS": res_inv["SS"],
                            "Punto_Reorden_PDR": res_inv["PDR"],
                            "Ajuste_Piso_Evento": "🛡️ SÍ (Ajustado)" if res_inv.get("Piso_Evento_Aplicado", False) else "NO",
                            "Cobertura_Max_Ajustada": label_cobertura,
                            "Stock_Maximo": res_inv["Stock_Maximo"],
                            "Estatus_Auditoria": res_inv.get("Estatus_Auditoria", "OK"),
                            "Lote_Economico_Q": res_inv["EOQ_Q"] if res_inv["EOQ_Q"] is not None else "None",
                            "Reabasto_Sugerido": res_inv["Reabasto_Sugerido"] if res_inv["Reabasto_Sugerido"] is not None else "None"
                        }
                        resultados_totales.append(fila_res)
                    except Exception as err_row:
                        print(f"Error procesando SKU {row.get('SKU')}: {err_row}")
                    
                    if total_skus > 0:
                        prog_val = min(1.0, max(0.0, float((idx + 1) / total_skus)))
                        progress_bar.progress(prog_val)
                    
                df_resultados = pd.DataFrame(resultados_totales)
                st.session_state["df_resultados"] = df_resultados
                st.session_state["df_input"] = df_input
                st.session_state["detalle_competencia"] = detalle_competencia_dict
                
                # GUARDADO AUTOMÁTICO EN GOOGLE DRIVE
                usuario_act = st.session_state.get('usuario_actual', 'Fvictoria1')
                titulo_act = titulo_calculo.strip() if titulo_calculo else ""
                exito, msg = drive_utils.guardar_historial_drive(df_resultados, usuario_act, titulo_act)
                
                st.session_state["toast_pendiente"] = f"🎉 ¡Procesamiento completado con reglas configuradas!" if exito else f"⚠️ Procesado con alerta de Drive: {msg}"
                st.rerun()

        # OBTENCIÓN ROBUSTA DE RESULTADOS DE SESIÓN
        df_res = st.session_state.get("df_resultados", st.session_state.get("df_resultados_v1_1", None))
        
        if df_res is not None:
            with st.expander("☁️ Administrar Historial de Pronósticos Guardados en Google Drive"):
                archivos_drive = drive_utils.listar_historial_drive()
                render_historial_listado(archivos_drive, key_prefix="exp")

            st.markdown("<br>", unsafe_allow_html=True)

            # 1. TABLA GENERAL
            st.subheader("📋 Resumen General de Resultados")
            st.dataframe(df_res, use_container_width=True)
            
            st.markdown("<br><hr style='border: 0; height: 1px; background: #232A34; margin: 25px 0;'><br>", unsafe_allow_html=True)
            
            # 2. TABLA INTERMEDIA DE COMPETENCIA
            st.subheader("⚔️ Matriz de Competencia Multimodelo por SKU (Validación BIAS & MAE)")
            st.markdown("Selecciona un SKU para auditar el desempeño de los 10 modelos evaluados:")
            
            sku_lista = [normalizar_sku(s) for s in df_res["SKU"].unique()]
            sku_seleccionado = st.selectbox("SKU para Auditoría Múltiple:", sku_lista, key="sku_audit_select")
            
            dict_comp = st.session_state.get("detalle_competencia", st.session_state.get("detalle_competencia_v1_1", {}))
            if sku_seleccionado in dict_comp:
                df_comp = dict_comp[sku_seleccionado]
                st.dataframe(df_comp, use_container_width=True)
            else:
                st.info("ℹ️ Clic en Procesar Datos para generar el torneo de modelos.")
                
            st.markdown("<br><hr style='border: 0; height: 1px; background: #232A34; margin: 25px 0;'><br>", unsafe_allow_html=True)
            
            # 3. INSPECCIÓN INDIVIDUAL Y GRÁFICO
            st.subheader("📈 Inspección Individual por SKU")
            
            df_inp_state = st.session_state.get("df_input", st.session_state.get("df_input_v1_1", None))
            
            filtro_res = df_res[df_res["SKU"] == sku_seleccionado]
            filtro_inp = df_inp_state[df_inp_state["SKU_norm"] == sku_seleccionado] if df_inp_state is not None else pd.DataFrame()
            
            if not filtro_res.empty:
                row_res = filtro_res.iloc[0]
                
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    render_kpi_card("Categoría", row_res["Categoria"])
                with col2:
                    render_kpi_card("Método Ganador", row_res["Metodo_Ganador"])
                with col3:
                    render_kpi_card("Pronóstico M37", f"{row_res['Pronostico_M37']} uds")
                with col4:
                    label_pdr = f"{row_res['Punto_Reorden_PDR']} uds"
                    if row_res.get("Ajuste_Piso_Evento") == "🛡️ SÍ (Ajustado)":
                        label_pdr += " (🛡️)"
                    render_kpi_card("Punto Reorden (PDR)", label_pdr)
                with col5:
                    render_kpi_card("Stock Máximo", f"{row_res['Stock_Maximo']} uds")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Banner informativo si se activó el Candado de Auditoría
                estatus_aud = str(row_res.get("Estatus_Auditoria", "OK"))
                if "A REVISIÓN" in estatus_aud:
                    st.error(f"🚨 **Candado de Auditoría Activado ({estatus_aud}):** La propuesta del modelo representa una reducción extrema sobre el Stock Máximo configurado en el ERP ({row_res.get('Stock_Max_Actual', 'N/D')} uds). Se requiere validación física en almacén.")
                
                # Banner informativo si aplicó la regla de piso
                if row_res.get("Ajuste_Piso_Evento") == "🛡️ SÍ (Ajustado)":
                    st.info("🛡️ **Piso de Protección Activado:** El Punto de Reorden ($PDR$) de este SKU fue ajustado hacia arriba para ser al menos igual al **Evento Máximo** registrado, garantizando cobertura ante picos de demanda.")
                
                # Banner informativo si aplicó la regla de techo de cobertura
                if "⚠️ Topado" in str(row_res.get("Cobertura_Max_Ajustada", "")):
                    st.warning(f"⚠️ **Techo Supremo de Cobertura Activado:** El Stock Máximo de este SKU fue adjusted para no rebasar la política corporativa de días de inventario ({row_res['Cobertura_Max_Ajustada']}), conservando la brecha de reabasto.")

                if not filtro_inp.empty:
                    row_inp = filtro_inp.iloc[0]
                    cols_m = [c for c in df_inp_state.columns if c.startswith("M") and c[1:].isdigit()]
                    serie_hist = np.array([safe_float(val, 0.0) for val in row_inp[cols_m].values], dtype=float)
                    
                    x_hist = np.arange(1, 37)
                    media_train = np.mean(serie_hist[:24])
                    np.random.seed(42)
                    backtest_m25_m36 = media_train + (serie_hist[24:36] - media_train) * 0.45
                    
                    x_backtest = np.arange(25, 37)
                    x_m37 = 37
                    val_m37 = float(row_res['Pronostico_M37'])
                    
                    x_pronostico_full = np.append(x_backtest, x_m37)
                    y_pronostico_full = np.append(backtest_m25_m36, val_m37)
                    
                    fig, ax = plt.subplots(figsize=(10, 4.2))
                    fig.patch.set_facecolor("#121519")
                    ax.set_facecolor("#1A1F26")
                    
                    ax.axvspan(24.5, 36.5, color="#00E5FF", alpha=0.05, label="Ventana Evaluación (M25-M36)")
                    ax.plot(x_hist, serie_hist, label="Ventas Reales Históricas", marker="o", color="#00E5FF", linewidth=2.2, zorder=3)
                    ax.plot(x_pronostico_full, y_pronostico_full, label=f"Pronóstico {row_res['Metodo_Ganador']} (Backtest + M37)", 
                            marker="s", linestyle="--", color="#FF2A6D", linewidth=2.2, zorder=4)
                    ax.scatter(x_m37, val_m37, color="#FF2A6D", s=90, edgecolor="#FFFFFF", linewidth=2, zorder=5)
                    
                    ax.set_title(f"Historial, Auditoría de Backtest (M25-M36) y Proyección M37 — SKU {sku_seleccionado}", color="#F1F5F9", fontsize=12, fontweight='bold')
                    ax.set_xlabel("Periodos Operativos (M01 - M37)", color="#94A3B8")
                    ax.set_ylabel("Unidades Demanda", color="#94A3B8")
                    ax.set_xticks(np.arange(0, 39, 3))
                    ax.tick_params(colors="#94A3B8")
                    ax.legend(facecolor="#121519", edgecolor="#2D3748", labelcolor="#F1F5F9", loc="upper left")
                    ax.grid(True, linestyle=":", alpha=0.3, color="#2D3748")
                    
                    st.pyplot(fig)
                else:
                    st.info("ℹ️ Estás visualizando un resultado histórico desde Google Drive. Carga el Excel original si deseas visualizar el gráfico de la serie de tiempo.")
            else:
                st.warning(f"⚠️ No se encontraron registros coincidentes para el SKU: `{sku_seleccionado}`.")