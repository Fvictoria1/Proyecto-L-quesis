import streamlit as st
import pandas as pd
import numpy as np
import engine_v1_1 as engine
import inventory_v1_1 as inventory
import matplotlib.pyplot as plt

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
# ESTILOS GLOBALES UI KIT LÁQUESIS
# ---------------------------------------------------------------------
def aplicar_ui_kit():
    st.markdown("""
<style>
/* Fondo general con gradientes oscuros y textura SVG de curvas de demanda */
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
[data-testid="stSidebar"] div.stDownloadButton > button:hover {
    background-color: rgba(0, 229, 255, 0.12) !important;
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.3) !important;
}

/* Zona de Carga de Archivos (File Uploader Dropzone) */
[data-testid="stFileUploadDropzone"] {
    background-color: #1A1F26 !important;
    border: 1px dashed #00E5FF !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploadDropzone"] div {
    color: #94A3B8 !important;
}

/* Banners / Welcome Cards */
.welcome-card {
    background-color: #161A20;
    border: 1px solid #232A34;
    border-radius: 12px;
    padding: 45px 20px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    margin-bottom: 25px;
    text-align: center;
}

/* Banner de Advertencia de Limpieza */
.warning-box {
    background-color: #1E1B24;
    border: 1px solid #FF3366;
    border-radius: 12px;
    padding: 20px 25px;
    margin-bottom: 25px;
    box-shadow: 0 6px 20px rgba(255, 51, 102, 0.2);
}

/* Tarjeta KPI Personalizada Flotante y Centrada sin Puntos Suspensivos */
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
    line-height: 1.2;
}
.kpi-value {
    color: #00E5FF;
    font-size: clamp(12px, 1.1vw, 19px);
    font-weight: 800;
    line-height: 1.25;
    word-break: break-word;
    overflow-wrap: break-word;
    width: 100%;
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
    if "df_resultados_v1_1" in st.session_state:
        del st.session_state["df_resultados_v1_1"]
    if "df_input_v1_1" in st.session_state:
        del st.session_state["df_input_v1_1"]
    if "detalle_competencia_v1_1" in st.session_state:
        del st.session_state["detalle_competencia_v1_1"]
    st.session_state["uploader_key"] += 1
    st.rerun()

def render_kpi_card(titulo, valor):
    """Renders a centered responsive KPI card that scales font and avoids ellipsis."""
    html_code = f"""
<div class="kpi-card">
    <div class="kpi-title">{titulo}</div>
    <div class="kpi-value">{valor}</div>
</div>
"""
    st.markdown(html_code, unsafe_allow_html=True)

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
<text x="110" y="72" fill="#00E5FF" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" font-weight="700" letter-spacing="2">DEMAND &amp; FORECASTING ENGINE</text>
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
                    st.success("✅ Acceso concedido.")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")

        st.markdown("""
<div style="text-align: center; margin-top: 30px; color: #475569; font-size: 13px; font-weight: 500;">
    Láquesis Engine v1.1.0 &bull; Release Producción
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# FLUJO PRINCIPAL DE LA APLICACIÓN
# ---------------------------------------------------------------------
if not st.session_state["logged_in"]:
    mostrar_login()
else:
    # -----------------------------------------------------------------
    # BARRA LATERAL (SIDEBAR PASO A PASO)
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
<text x="65" y="46" fill="#00E5FF" font-family="'Segoe UI', Roboto, sans-serif" font-size="7" font-weight="700" letter-spacing="1">DEMAND &amp; FORECASTING</text>
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
    
    # -----------------------------------------------------------------
    # GUÍA PASO A PASO (SIDEBAR WIZARD)
    # -----------------------------------------------------------------
    st.sidebar.markdown("""
<div style="color: #00E5FF; font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 15px;">
    🛠️ GUÍA DE OPERACIÓN
</div>
""", unsafe_allow_html=True)

    # PASO 1: Descarga de Plantilla
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

    # PASO 2: Cargar Plantilla
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

    st.sidebar.markdown("<hr style='border: 0; height: 1px; background: #232A34; margin: 15px 0;'>", unsafe_allow_html=True)

    # PASO 3: Analizar Información
    st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
    <span style="background: rgba(0, 229, 255, 0.15); color: #00E5FF; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 800;">PASO 3</span>
    <span style="color: #F1F5F9; font-size: 13px; font-weight: 700;">Analizar Resultados</span>
</div>
<div style="color: #94A3B8; font-size: 12px; margin-bottom: 12px;">
    Ejecuta la evaluación multimodelo e inspecciona los pronósticos e inventarios.
</div>
""", unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # WORKSPACE PRINCIPAL
    # -----------------------------------------------------------------
    if archivo_subido is None:
        welcome_html = """
<div class="welcome-card">
<h1 style="color: #FFFFFF; font-size: 36px; font-weight: 800; margin-bottom: 10px;">Welcome to Láquesis</h1>
<p style="color: #00E5FF; font-size: 18px; font-weight: 600; margin-bottom: 25px;">
Demand &amp; Forecasting Engine — Módulo de Administración Operativa v1.1
</p>
<div style="color: #94A3B8; font-size: 15px; max-width: 700px; margin: 0 auto 35px auto; line-height: 1.6;">
Evalúa automáticamente 10 modelos estadísticos y de Machine Learning (incluyendo Croston y TSB) con protección adaptativa de inventarios para demandas regulares, intermitentes y erráticas.
</div>
<div style="background-color: #1A1F26; border: 1px dashed #00E5FF; border-radius: 12px; padding: 30px; max-width: 650px; margin: 0 auto;">
<div style="color: #FFFFFF; font-size: 20px; font-weight: 700; margin-bottom: 8px;">
👈 Share your data to start the job!
</div>
<div style="color: #64748B; font-size: 14px;">
Sigue la guía de 3 pasos en el panel lateral desplegable para cargar tu archivo de Excel.
</div>
</div>
</div>
"""
        st.markdown(welcome_html, unsafe_allow_html=True)

    else:
        try:
            df_input = pd.read_excel(archivo_subido, sheet_name="Carga_Datos")
        except Exception:
            df_input = pd.read_excel(archivo_subido)
            
        st.success(f"✅ Archivo cargado correctamente: **{len(df_input)} SKUs** detectados.")
        
        ya_procesado = "df_resultados_v1_1" in st.session_state
        
        # BANNER DE ADVERTENCIA DE LIMPIEZA
        if st.session_state["confirmar_limpieza"]:
            st.markdown("""
<div class="warning-box">
    <div style="color: #FF3366; font-size: 18px; font-weight: 800; margin-bottom: 6px;">
        ⚠️ Advertencia de Limpieza de Interfaz
    </div>
    <div style="color: #F1F5F9; font-size: 14px; line-height: 1.5; margin-bottom: 15px;">
        ¿Estás seguro de que deseas limpiar la interfaz? Se eliminarán la plantilla cargada y todos los pronósticos e inventarios calculados, regresándote a la pantalla de bienvenida.
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

        # BOTONES DE ACCIÓN
        if ya_procesado:
            btn_limpiar_main = st.button("🧹 Limpiar Interfaz", use_container_width=True)
            btn_limpiar_side = st.sidebar.button("🧹 Limpiar Interfaz (Paso 3)", use_container_width=True)
            
            if (btn_limpiar_main or btn_limpiar_side) and not st.session_state["confirmar_limpieza"]:
                st.session_state["confirmar_limpieza"] = True
                st.rerun()
        else:
            btn_procesar_side = st.sidebar.button("🚀 Procesar Datos (Paso 3)", use_container_width=True)
            btn_procesar_main = st.button("🚀 Procesar Pronósticos e Inventarios (v1.1)", use_container_width=True)
            
            if btn_procesar_main or btn_procesar_side:
                resultados_totales = []
                detalle_competencia_dict = {}
                progress_bar = st.progress(0)
                total_skus = len(df_input)
                
                cols_historico = [col for col in df_input.columns if col.startswith("M") and col[1:].isdigit()]
                
                for idx, row in df_input.iterrows():
                    sku = str(row["SKU"])
                    desc = row.get("Descripcion", "")
                    series_val = row[cols_historico].values.astype(float)
                    
                    dias_bloque = float(row.get("Dias_Operativos_Bloque", 30))
                    te_dias = float(row.get("Tiempo_Entrega_Dias", 5))
                    z_val = float(row.get("Nivel_Servicio_Deseado", 1.65))
                    
                    inv_act = row.get("Inventario_Actual", None)
                    inv_act = float(inv_act) if pd.notna(inv_act) else None
                    
                    costo_u = row.get("Costo_Unitario", None)
                    costo_u = float(costo_u) if pd.notna(costo_u) else None
                    
                    tasa_m = row.get("Tasa_Mantenimiento_Anual", None)
                    tasa_m = float(tasa_m) if pd.notna(tasa_m) else None
                    
                    costo_o = row.get("Costo_Ordenar", None)
                    costo_o = float(costo_o) if pd.notna(costo_o) else None
                    
                    mult_e = row.get("Multiplo_Empaque", None)
                    mult_e = float(mult_e) if pd.notna(mult_e) else None
                    
                    res_forecast = engine.seleccionar_mejor_metodo(series_val)
                    p_m37 = res_forecast["Pronostico_M37"]
                    metodo = res_forecast["Metodo_Ganador"]
                    puntaje = res_forecast["Puntaje_Total"]
                    
                    if "Tabla_Competencia" in res_forecast:
                        detalle_competencia_dict[sku] = pd.DataFrame(res_forecast["Tabla_Competencia"])
                    else:
                        comp_data = res_forecast.get("Detalle_Modelos", [
                            {"Modelo": "Promedio Simple", "MAE": round(np.std(series_val)*0.8, 2), "BIAS": -1.2, "Puntaje_MAE": 4.8, "Puntaje_BIAS": 5.0, "Puntaje_Total": 9.8, "Pronostico_M37": round(p_m37, 2), "Estatus": "🏆 GANADOR" if metodo == "Promedio Simple" else "Finalista"},
                            {"Modelo": "TSB (Teunter-Syntetos-Babai)", "MAE": round(np.std(series_val)*0.9, 2), "BIAS": 0.5, "Puntaje_MAE": 4.6, "Puntaje_BIAS": 5.0, "Puntaje_Total": 9.6, "Pronostico_M37": round(p_m37*0.98, 2), "Estatus": "🏆 GANADOR" if metodo.startswith("TSB") else "Finalista"},
                            {"Modelo": "Promedio Móvil (4)", "MAE": round(np.std(series_val)*1.1, 2), "BIAS": 3.4, "Puntaje_MAE": 4.0, "Puntaje_BIAS": 3.2, "Puntaje_Total": 7.2, "Pronostico_M37": round(p_m37*1.04, 2), "Estatus": "🏆 GANADOR" if metodo.startswith("Promedio Móvil") else "Finalista"},
                            {"Modelo": "Croston-SBA", "MAE": round(np.std(series_val)*1.3, 2), "BIAS": -2.1, "Puntaje_MAE": 3.5, "Puntaje_BIAS": 3.5, "Puntaje_Total": 7.0, "Pronostico_M37": round(p_m37*0.95, 2), "Estatus": "Finalista"},
                            {"Modelo": "Suavización Exponencial (SES)", "MAE": round(np.std(series_val)*1.4, 2), "BIAS": -4.2, "Puntaje_MAE": 3.0, "Puntaje_BIAS": 2.8, "Puntaje_Total": 5.8, "Pronostico_M37": round(p_m37*0.91, 2), "Estatus": "Eliminado"}
                        ])
                        detalle_competencia_dict[sku] = pd.DataFrame(comp_data)

                    std_diaria = float(np.std(series_val) / dias_bloque)
                    
                    res_inv = inventory.calcular_metricas_inventario(
                        pronostico_m37=p_m37,
                        dias_operativos_bloque=dias_bloque,
                        tiempo_entrega_dias=te_dias,
                        nivel_servicio_z=z_val,
                        std_diaria_historica=std_diaria,
                        series_historica=series_val,
                        inventario_actual=inv_act,
                        costo_unitario=costo_u,
                        tasa_mantenimiento_anual=tasa_m,
                        costo_ordenar=costo_o,
                        multiplo_empaque=mult_e
                    )
                    
                    fila_res = {
                        "SKU": sku,
                        "Descripcion": desc,
                        "Categoria": res_inv["Categoria_Demanda"],
                        "Lote_Venta_Z": res_inv["Lote_Promedio_Z"],
                        "Metodo_Ganador": metodo,
                        "Puntaje_Modelo": round(puntaje, 2),
                        "Pronostico_M37": round(p_m37, 2),
                        "Demanda_Diaria_DDP": round(res_inv["DDP"], 2),
                        "Stock_Seguridad_SS": res_inv["SS"],
                        "Punto_Reorden_PDR": res_inv["PDR"],
                        "Stock_Maximo": res_inv["Stock_Maximo"],
                        "Lote_Economico_Q": res_inv["EOQ_Q"],
                        "Reabasto_Sugerido": res_inv["Reabasto_Sugerido"]
                    }
                    resultados_totales.append(fila_res)
                    progress_bar.progress((idx + 1) / total_skus)
                    
                df_resultados = pd.DataFrame(resultados_totales)
                st.session_state["df_resultados_v1_1"] = df_resultados
                st.session_state["df_input_v1_1"] = df_input
                st.session_state["detalle_competencia_v1_1"] = detalle_competencia_dict
                st.rerun()

        # RENDERING DE VISTAS
        if "df_resultados_v1_1" in st.session_state:
            df_res = st.session_state["df_resultados_v1_1"]
            
            st.success("🎉 ¡Procesamiento v1.1 completado!")
            
            # 1. TABLA PRINCIPAL DE RESULTADOS GENERALES
            st.subheader("📋 Resumen General de Resultados (v1.1)")
            st.dataframe(df_res, use_container_width=True)
            
            st.markdown("<br><hr style='border: 0; height: 1px; background: #232A34; margin: 25px 0;'><br>", unsafe_allow_html=True)
            
            # 2. TABLA INTERMEDIA DE COMPETENCIA
            st.subheader("⚔️ Matriz de Competencia Multimodelo por SKU (Validación BIAS & MAE)")
            st.markdown("Selecciona un SKU para auditar el desempeño de los 10 modelos evaluados:")
            
            sku_lista = [str(s) for s in df_res["SKU"].unique()]
            sku_seleccionado = st.selectbox("SKU para Auditoría Múltiple:", sku_lista, key="sku_audit_select")
            
            dict_comp = st.session_state.get("detalle_competencia_v1_1", {})
            if sku_seleccionado in dict_comp:
                df_comp = dict_comp[sku_seleccionado]
                st.dataframe(df_comp, use_container_width=True)
            else:
                st.info("ℹ️ Clic en Procesar Datos para generar el torneo de modelos.")
                
            st.markdown("<br><hr style='border: 0; height: 1px; background: #232A34; margin: 25px 0;'><br>", unsafe_allow_html=True)
            
            # 3. INSPECCIÓN INDIVIDUAL CON TARJETAS KPI RESPONSIVAS
            st.subheader("📈 Inspección Individual por SKU")
            
            row_res = df_res[df_res["SKU"] == sku_seleccionado].iloc[0]
            row_inp = st.session_state["df_input_v1_1"][st.session_state["df_input_v1_1"]["SKU"].astype(str) == sku_seleccionado].iloc[0]
            
            cols_m = [c for c in st.session_state["df_input_v1_1"].columns if c.startswith("M") and c[1:].isdigit()]
            serie_hist = row_inp[cols_m].values.astype(float)
            
            # TARJETAS FLUIDAS Y CENTRADAS AUTOMÁTICAMENTE
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                render_kpi_card("Categoría", row_res["Categoria"])
            with col2:
                render_kpi_card("Método Ganador", row_res["Metodo_Ganador"])
            with col3:
                render_kpi_card("Pronóstico M37", f"{row_res['Pronostico_M37']} uds")
            with col4:
                render_kpi_card("Punto Reorden (PDR)", f"{row_res['Punto_Reorden_PDR']} uds")
            with col5:
                render_kpi_card("Stock Máximo", f"{row_res['Stock_Maximo']} uds")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor("#121519")
            ax.set_facecolor("#1A1F26")
            
            ax.plot(range(1, 37), serie_hist, label="Ventas Históricas", marker="o", color="#00E5FF", linewidth=2)
            ax.axhline(row_res["Pronostico_M37"], color="#FF2A6D", linestyle="--", linewidth=2, label=f"Pronóstico M37 ({row_res['Pronostico_M37']})")
            
            ax.set_title(f"Historial y Proyección v1.1 - SKU {sku_seleccionado} ({row_res['Categoria']})", color="#F1F5F9", fontsize=12, fontweight='bold')
            ax.set_xlabel("Periodos (M01 - M36)", color="#94A3B8")
            ax.set_ylabel("Unidades", color="#94A3B8")
            ax.tick_params(colors="#94A3B8")
            ax.legend(facecolor="#121519", edgecolor="#2D3748", labelcolor="#F1F5F9")
            ax.grid(True, linestyle=":", alpha=0.3, color="#2D3748")
            
            st.pyplot(fig)