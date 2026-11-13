import streamlit as st
from auth import MoiranAuth


class MoiranMenu:
    """
    Componente independiente encargado de renderizar la Barra Superior Horizontal
    (Top Navbar) con el logo, navegación entre módulos (Cloto, Láquesis, Átropo),
    estatus del usuario y la vista de bienvenida de Moiran SCPS.
    """

    MODULOS = [
        {
            "id": "cloto",
            "nombre": "CLOTO",
            "subtitulo": "Inventario Central (CD)",
            "svg": '<svg width="20" height="20" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="18" cy="18" r="13" stroke="#00E5FF" stroke-width="2.4"/><circle cx="18" cy="18" r="4" fill="#00E5FF" fill-opacity="0.25" stroke="#FFFFFF" stroke-width="1.8"/><line x1="18" y1="5" x2="18" y2="14" stroke="#00E5FF" stroke-width="2" stroke-linecap="round"/><line x1="18" y1="22" x2="18" y2="31" stroke="#00E5FF" stroke-width="2" stroke-linecap="round"/><line x1="5" y1="18" x2="14" y2="18" stroke="#00E5FF" stroke-width="2" stroke-linecap="round"/><line x1="22" y1="18" x2="31" y2="18" stroke="#00E5FF" stroke-width="2" stroke-linecap="round"/></svg>'
        },
        {
            "id": "laquesis",
            "nombre": "LÁQUESIS",
            "subtitulo": "Demanda & Pronósticos",
            "svg": '<svg width="20" height="20" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="6" y="11" width="24" height="14" rx="2.5" transform="rotate(-18 18 18)" stroke="#00E5FF" stroke-width="2.3" fill="#00E5FF" fill-opacity="0.08"/><line x1="11" y1="15.5" x2="12.5" y2="20" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round"/><line x1="15.5" y1="14" x2="16.5" y2="17" stroke="#00E5FF" stroke-width="1.6" stroke-linecap="round"/><line x1="19.5" y1="12.8" x2="21" y2="17.3" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round"/><line x1="23.5" y1="11.5" x2="24.5" y2="14.5" stroke="#00E5FF" stroke-width="1.6" stroke-linecap="round"/></svg>'
        },
        {
            "id": "atropo",
            "nombre": "ÁTROPO",
            "subtitulo": "Ejecución de Reabasto",
            "svg": '<svg width="20" height="20" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="10.5" cy="11.5" r="4.2" stroke="#00E5FF" stroke-width="2.2"/><circle cx="10.5" cy="24.5" r="4.2" stroke="#00E5FF" stroke-width="2.2"/><line x1="14.2" y1="13.5" x2="29" y2="24.5" stroke="#FFFFFF" stroke-width="2.3" stroke-linecap="round"/><line x1="14.2" y1="22.5" x2="29" y2="11.5" stroke="#00E5FF" stroke-width="2.3" stroke-linecap="round"/><circle cx="19.5" cy="18" r="1.6" fill="#7B2CBF" stroke="#FFFFFF" stroke-width="1"/></svg>'
        }
    ]

    def __init__(self, auth: MoiranAuth, callback_limpieza=None):
        self.auth = auth
        self.callback_limpieza = callback_limpieza
        if "modulo_activo" not in st.session_state:
            st.session_state["modulo_activo"] = None

    @property
    def modulo_activo(self):
        return st.session_state.get("modulo_activo", None)

    def seleccionar_modulo(self, modulo_id: str):
        """Cambia el módulo activo conservando intacto el estado de los demás."""
        st.session_state["modulo_activo"] = modulo_id

    def renderizar_top_navbar(self):
        """Renderiza la barra superior horizontal con logo, selector de módulos y perfil."""
        st.markdown('<div class="top-navbar-container">', unsafe_allow_html=True)

        col_logo, col_cloto, col_laq, col_atr, col_perfil = st.columns(
            [1.6, 1.35, 1.45, 1.35, 1.85],
            vertical_alignment="center"
        )

        # 1. Logo Compacto Moiran SCPS
        with col_logo:
            logo_top_html = (
                '<div style="display:flex;align-items:center;gap:10px;padding:4px 0;">'
                '<svg width="34" height="34" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">'
                '<circle cx="30" cy="30" r="25" fill="#00E5FF" fill-opacity="0.08"/>'
                '<circle cx="30" cy="18" r="7.5" stroke="#00E5FF" stroke-width="2.5"/>'
                '<circle cx="19.5" cy="36.5" r="7.5" stroke="#7B2CBF" stroke-width="2.5"/>'
                '<circle cx="40.5" cy="36.5" r="7.5" stroke="#10B981" stroke-width="2.5"/>'
                '<circle cx="30" cy="29" r="3" fill="#FFFFFF"/>'
                '</svg>'
                '<div>'
                '<div style="font-family:\'Cinzel\',serif;color:#FFFFFF;font-size:16px;font-weight:900;letter-spacing:1.5px;line-height:1.1;">MOIRAN SCPS</div>'
                '<div style="color:#00E5FF;font-size:9px;font-weight:700;letter-spacing:1px;">SUPPLY CHAIN PLANNING</div>'
                '</div>'
                '</div>'
            )
            st.markdown(logo_top_html, unsafe_allow_html=True)

        # 2. Botones de Módulos con Ícono SVG Superior
        cols_modulos = [col_cloto, col_laq, col_atr]
        activo_actual = self.modulo_activo

        for idx, mod in enumerate(self.MODULOS):
            with cols_modulos[idx]:
                es_activo = (activo_actual == mod["id"])
                borde = "1.5px solid #00E5FF" if es_activo else "1px solid #2D3748"
                fondo = "rgba(0, 229, 255, 0.12)" if es_activo else "#1A1F26"
                badge = (
                    '<span style="color:#00E5FF;font-size:9px;font-weight:800;">● ACTIVO</span>'
                    if es_activo else
                    '<span style="color:#64748B;font-size:9px;font-weight:600;">DISPONIBLE</span>'
                )

                header_mod_html = (
                    f'<div style="background-color:{fondo};border:{borde};border-bottom:none;border-radius:8px 8px 0 0;padding:6px 10px;display:flex;align-items:center;justify-content:space-between;">'
                    f'<div style="display:flex;align-items:center;gap:7px;">'
                    f'{mod["svg"]}'
                    f'<span style="color:#94A3B8;font-size:10px;font-weight:600;">{mod["subtitulo"]}</span>'
                    f'</div>'
                    f'{badge}'
                    f'</div>'
                )
                st.markdown(header_mod_html, unsafe_allow_html=True)

                etiqueta_btn = f"✓ {mod['nombre']}" if es_activo else mod["nombre"]
                if st.button(
                    etiqueta_btn,
                    key=f"topnav_btn_{mod['id']}",
                    use_container_width=True,
                    type="primary" if es_activo else "secondary"
                ):
                    if not es_activo:
                        self.seleccionar_modulo(mod["id"])
                        st.rerun()

        # 3. Estatus del Usuario y Cierre de Sesión
        with col_perfil:
            c_info, c_logout = st.columns([1.25, 0.95], vertical_alignment="center")
            with c_info:
                user_html = (
                    f'<div style="background-color:#1A1F26;border:1px solid #2D3748;border-radius:8px;padding:7px 10px;line-height:1.25;">'
                    f'<div style="color:#F1F5F9;font-size:12px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">👤 {self.auth.usuario_actual}</div>'
                    f'<div style="color:#10B981;font-size:10px;font-weight:700;">🟢 En Línea</div>'
                    f'</div>'
                )
                st.markdown(user_html, unsafe_allow_html=True)
            with c_logout:
                if st.button("🔒 Salir", key="topnav_btn_logout", type="secondary", use_container_width=True):
                    self.auth.cerrar_sesion(callback_limpieza=self.callback_limpieza)

        st.markdown('</div>', unsafe_allow_html=True)

    def renderizar_bienvenida_principal(self):
        """Renderiza el mensaje de bienvenida global centrado cuando aún no se elige módulo."""
        st.sidebar.markdown(
            '<div style="color:#00E5FF;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px;">🧭 NAVEGACIÓN</div>'
            '<div style="color:#94A3B8;font-size:12px;line-height:1.5;">Selecciona un módulo en la barra superior (<b>Cloto</b>, <b>Láquesis</b> o <b>Átropo</b>) para desplegar aquí su guía operativa y herramientas.</div>',
            unsafe_allow_html=True
        )

        _, col_centro, _ = st.columns([0.5, 3.0, 0.5])
        with col_centro:
            st.markdown("<br>", unsafe_allow_html=True)
            welcome_html = (
                '<div class="welcome-card" style="padding:55px 40px;">'
                '<h1 style="color:#FFFFFF;font-size:36px;font-weight:800;margin-bottom:12px;letter-spacing:0.5px;">Bienvenido a Moiran SCPS</h1>'
                '<p style="color:#00E5FF;font-size:18px;font-weight:600;margin-bottom:28px;">Supply Chain Planning System — Plataforma Integral de Planeación y Reabasto</p>'
                '<div style="color:#94A3B8;font-size:15px;max-width:680px;margin:0 auto;line-height:1.7;">'
                'Ecosistema analítico multi-escalón diseñado para gobernar de extremo a extremo el flujo de inventarios de la red: '
                'planeación maestra y capacidad central en <strong style="color:#F1F5F9;">Cloto</strong>, '
                'pronóstico estadístico y parametrización táctica de unidades de negocio en <strong style="color:#F1F5F9;">Láquesis</strong>, '
                'y ejecución inteligente del reabasto en <strong style="color:#F1F5F9;">Átropo</strong>.'
                '</div>'
                '</div>'
            )
            st.markdown(welcome_html, unsafe_allow_html=True)

    def renderizar(self) -> str | None:
        """
        Despliega la barra superior horizontal y devuelve el ID del módulo activo.
        Si no hay módulo seleccionado, muestra la pantalla de bienvenida general.
        """
        self.renderizar_top_navbar()

        if self.modulo_activo is None:
            self.renderizar_bienvenida_principal()

        return self.modulo_activo