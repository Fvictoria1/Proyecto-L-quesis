import streamlit as st
from auth import MoiranAuth


class MoiranMenu:
    """
    Componente independiente encargado de renderizar el marco principal,
    la barra lateral con estatus de usuario, el selector de módulos
    (Cloto, Láquesis, Átropo) y la vista de bienvenida de Moiran SCPS.
    """

    MODULOS = [
        {
            "id": "cloto",
            "nombre": "CLOTO",
            "subtitulo": "Inventario Central (CD)",
            "svg": '<svg width="24" height="24" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="18" cy="18" r="13" stroke="#00E5FF" stroke-width="2.4"/><circle cx="18" cy="18" r="4" fill="#00E5FF" fill-opacity="0.25" stroke="#FFFFFF" stroke-width="1.8"/><line x1="18" y1="5" x2="18" y2="14" stroke="#00E5FF" stroke-width="2" stroke-linecap="round"/><line x1="18" y1="22" x2="18" y2="31" stroke="#00E5FF" stroke-width="2" stroke-linecap="round"/><line x1="5" y1="18" x2="14" y2="18" stroke="#00E5FF" stroke-width="2" stroke-linecap="round"/><line x1="22" y1="18" x2="31" y2="18" stroke="#00E5FF" stroke-width="2" stroke-linecap="round"/><line x1="8.8" y1="8.8" x2="15.1" y2="15.1" stroke="#7B2CBF" stroke-width="1.8" stroke-linecap="round"/><line x1="20.9" y1="20.9" x2="27.2" y2="27.2" stroke="#7B2CBF" stroke-width="1.8" stroke-linecap="round"/><line x1="27.2" y1="8.8" x2="20.9" y2="15.1" stroke="#7B2CBF" stroke-width="1.8" stroke-linecap="round"/><line x1="15.1" y1="20.9" x2="8.8" y2="27.2" stroke="#7B2CBF" stroke-width="1.8" stroke-linecap="round"/></svg>'
        },
        {
            "id": "laquesis",
            "nombre": "LÁQUESIS",
            "subtitulo": "Demanda & Pronósticos",
            "svg": '<svg width="24" height="24" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg"><rect x="6" y="11" width="24" height="14" rx="2.5" transform="rotate(-18 18 18)" stroke="#00E5FF" stroke-width="2.3" fill="#00E5FF" fill-opacity="0.08"/><line x1="11" y1="15.5" x2="12.5" y2="20" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round"/><line x1="15.5" y1="14" x2="16.5" y2="17" stroke="#00E5FF" stroke-width="1.6" stroke-linecap="round"/><line x1="19.5" y1="12.8" x2="21" y2="17.3" stroke="#FFFFFF" stroke-width="1.8" stroke-linecap="round"/><line x1="23.5" y1="11.5" x2="24.5" y2="14.5" stroke="#00E5FF" stroke-width="1.6" stroke-linecap="round"/></svg>'
        },
        {
            "id": "atropo",
            "nombre": "ÁTROPO",
            "subtitulo": "Ejecución de Reabasto",
            "svg": '<svg width="24" height="24" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg"><circle cx="10.5" cy="11.5" r="4.2" stroke="#00E5FF" stroke-width="2.2"/><circle cx="10.5" cy="24.5" r="4.2" stroke="#00E5FF" stroke-width="2.2"/><line x1="14.2" y1="13.5" x2="29" y2="24.5" stroke="#FFFFFF" stroke-width="2.3" stroke-linecap="round"/><line x1="14.2" y1="22.5" x2="29" y2="11.5" stroke="#00E5FF" stroke-width="2.3" stroke-linecap="round"/><circle cx="19.5" cy="18" r="1.6" fill="#7B2CBF" stroke="#FFFFFF" stroke-width="1"/></svg>'
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

    def renderizar_sidebar_base(self):
        """Renderiza logo, perfil activo, botón de cierre y selector de módulos."""
        st.sidebar.markdown(MoiranAuth.obtener_logo_html(compacto=True), unsafe_allow_html=True)

        perfil_html = (
            f'<div style="background-color:#1A1F26;border:1px solid #2D3748;border-radius:10px;padding:12px 14px;margin-bottom:12px;">'
            f'<div style="color:#64748B;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:6px;">PERFIL ACTIVO</div>'
            f'<div style="color:#F1F5F9;font-size:13px;font-weight:600;margin-bottom:3px;">👤 Usuario: <span style="color:#00E5FF;font-weight:700;">{self.auth.usuario_actual}</span></div>'
            f'<div style="color:#F1F5F9;font-size:13px;font-weight:600;">🟢 Estado: <span style="color:#10B981;font-weight:700;">En Línea</span></div>'
            f'</div>'
        )
        st.sidebar.markdown(perfil_html, unsafe_allow_html=True)

        if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True, key="btn_logout_menu"):
            self.auth.cerrar_sesion(callback_limpieza=self.callback_limpieza)

        st.sidebar.markdown('<hr style="border:0;height:1px;background:#232A34;margin:16px 0;">', unsafe_allow_html=True)

        st.sidebar.markdown(
            '<div style="color:#00E5FF;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;">🏛️ MÓDULOS DEL SISTEMA</div>',
            unsafe_allow_html=True
        )

        activo_actual = self.modulo_activo

        for mod in self.MODULOS:
            es_activo = (activo_actual == mod["id"])
            borde = "1.5px solid #00E5FF" if es_activo else "1px solid #2D3748"
            fondo = "rgba(0, 229, 255, 0.10)" if es_activo else "#1A1F26"
            sombra = "0 0 14px rgba(0, 229, 255, 0.25)" if es_activo else "none"
            badge_estado = (
                '<span style="color:#00E5FF;font-size:10px;font-weight:800;">● ACTIVO</span>'
                if es_activo else
                '<span style="color:#64748B;font-size:10px;font-weight:600;">DISPONIBLE</span>'
            )

            card_html = (
                f'<div style="background-color:{fondo};border:{borde};border-bottom:none;border-radius:10px 10px 0 0;padding:10px 12px;display:flex;align-items:center;justify-content:space-between;box-shadow:{sombra};">'
                f'<div style="display:flex;align-items:center;gap:10px;">'
                f'<div style="background-color:#121519;border:1px solid #2D3748;border-radius:8px;width:36px;height:36px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">{mod["svg"]}</div>'
                f'<div>'
                f'<div style="color:#FFFFFF;font-size:13px;font-weight:800;letter-spacing:1px;line-height:1.2;">{mod["nombre"]}</div>'
                f'<div style="color:#94A3B8;font-size:11px;line-height:1.2;">{mod["subtitulo"]}</div>'
                f'</div>'
                f'</div>'
                f'<div>{badge_estado}</div>'
                f'</div>'
            )
            st.sidebar.markdown(card_html, unsafe_allow_html=True)

            etiqueta_btn = f"✓ {mod['nombre']} Seleccionado" if es_activo else f"Abrir {mod['nombre']}"
            if st.sidebar.button(
                etiqueta_btn,
                key=f"btn_nav_{mod['id']}",
                use_container_width=True,
                type="primary" if es_activo else "secondary"
            ):
                if not es_activo:
                    self.seleccionar_modulo(mod["id"])
                    st.rerun()

            st.sidebar.markdown('<div style="margin-bottom:10px;"></div>', unsafe_allow_html=True)

        st.sidebar.markdown('<hr style="border:0;height:1px;background:#232A34;margin:14px 0;">', unsafe_allow_html=True)

    def renderizar_bienvenida_principal(self):
        """Renderiza el mensaje de bienvenida global centrado cuando aún no se elige módulo."""
        _, col_centro, _ = st.columns([0.6, 2.8, 0.6])

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
        Despliega la barra lateral con navegación y devuelve el ID del módulo activo.
        Si no hay módulo seleccionado, muestra la pantalla de bienvenida general.
        """
        self.renderizar_sidebar_base()

        if self.modulo_activo is None:
            self.renderizar_bienvenida_principal()

        return self.modulo_activo