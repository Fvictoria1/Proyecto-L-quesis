import streamlit as st
from auth import MoiranAuth


class MoiranMenu:
    """
    Componente independiente encargado de renderizar el marco principal,
    la barra lateral con estatus de usuario y la vista de bienvenida
    del ecosistema Moiran SCPS.
    """

    def __init__(self, auth: MoiranAuth, callback_limpieza=None):
        self.auth = auth
        self.callback_limpieza = callback_limpieza

    def renderizar_sidebar_base(self):
        """Renderiza únicamente el logo, el perfil activo y el botón de cierre de sesión."""
        st.sidebar.markdown(MoiranAuth.obtener_logo_html(compacto=True), unsafe_allow_html=True)

        st.sidebar.markdown(f"""
<div style="background-color: #1A1F26; border: 1px solid #2D3748; border-radius: 10px; padding: 12px 14px; margin-bottom: 12px;">
    <div style="color: #64748B; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 6px;">PERFIL ACTIVO</div>
    <div style="color: #F1F5F9; font-size: 13px; font-weight: 600; margin-bottom: 3px;">👤 Usuario: <span style="color: #00E5FF; font-weight: 700;">{self.auth.usuario_actual}</span></div>
    <div style="color: #F1F5F9; font-size: 13px; font-weight: 600;">🟢 Estado: <span style="color: #10B981; font-weight: 700;">En Línea</span></div>
</div>
""", unsafe_allow_html=True)

        if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True, key="btn_logout_menu"):
            self.auth.cerrar_sesion(callback_limpieza=self.callback_limpieza)

        st.sidebar.markdown("<hr style='border: 0; height: 1px; background: #232A34; margin: 15px 0;'>", unsafe_allow_html=True)

    def renderizar_bienvenida_principal(self):
        """Renderiza el mensaje de bienvenida global centrado en el área principal."""
        _, col_centro, _ = st.columns([0.6, 2.8, 0.6])

        with col_centro:
            st.markdown("<br>", unsafe_allow_html=True)
            welcome_html = """
<div class="welcome-card" style="padding: 55px 40px;">
    <h1 style="color: #FFFFFF; font-size: 36px; font-weight: 800; margin-bottom: 12px; letter-spacing: 0.5px;">
        Bienvenido a Moiran SCPS
    </h1>
    <p style="color: #00E5FF; font-size: 18px; font-weight: 600; margin-bottom: 28px;">
        Supply Chain Planning System — Plataforma Integral de Planeación y Reabasto
    </p>
    <div style="color: #94A3B8; font-size: 15px; max-width: 680px; margin: 0 auto; line-height: 1.7;">
        Ecosistema analítico multi-escalón diseñado para gobernar de extremo a extremo el flujo de inventarios de la red: 
        planeación maestra y capacidad central en <strong style="color: #F1F5F9;">Cloto</strong>, 
        pronóstico estadístico y parametrización táctica de unidades de negocio en <strong style="color: #F1F5F9;">Láquesis</strong>, 
        y ejecución inteligente del reabasto en <strong style="color: #F1F5F9;">Átropo</strong>.
    </div>
</div>
"""
            st.markdown(welcome_html, unsafe_allow_html=True)

    def renderizar(self):
        """Punto de entrada único para desplegar el menú principal limpio."""
        self.renderizar_sidebar_base()
        self.renderizar_bienvenida_principal()