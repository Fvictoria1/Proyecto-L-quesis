import streamlit as st


class MoiranAuth:
    """
    Objeto independiente de autenticación y pantalla de acceso para Moiran SCPS.
    Gestiona el estado de sesión, validación de credenciales e identidad visual.
    """

    def __init__(self, usuario_default: str = "Fvictoria1", password_default: str = "4161"):
        self.usuario_correcto = self._obtener_secreto("AUTH_USER", usuario_default)
        self.password_correcto = self._obtener_secreto("AUTH_PASSWORD", password_default)
        self._inicializar_sesion()

    @staticmethod
    def _obtener_secreto(clave: str, valor_respaldo: str) -> str:
        try:
            return st.secrets.get(clave, valor_respaldo)
        except Exception:
            return valor_respaldo

    def _inicializar_sesion(self) -> None:
        if "logged_in" not in st.session_state:
            st.session_state["logged_in"] = False
        if "usuario_actual" not in st.session_state:
            st.session_state["usuario_actual"] = ""

    @property
    def esta_autenticado(self) -> bool:
        return bool(st.session_state.get("logged_in", False))

    @property
    def usuario_actual(self) -> str:
        return st.session_state.get("usuario_actual", self.usuario_correcto)

    def validar_credenciales(self, usuario: str, password: str) -> bool:
        return usuario == self.usuario_correcto and password == self.password_correcto

    def iniciar_sesion(self, usuario: str) -> None:
        st.session_state["logged_in"] = True
        st.session_state["usuario_actual"] = usuario
        st.session_state["toast_pendiente"] = f"✅ Acceso concedido. Bienvenido a Moiran SCPS, {usuario}."

    def cerrar_sesion(self, callback_limpieza=None) -> None:
        st.session_state["logged_in"] = False
        st.session_state["usuario_actual"] = ""
        if callable(callback_limpieza):
            callback_limpieza()
        else:
            st.rerun()

    @staticmethod
    def _obtener_emblema_svg(tamano: int = 120) -> str:
        return (
            f'<svg width="{tamano}" height="{tamano}" viewBox="0 0 136 136" fill="none" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">'
            '<circle cx="68" cy="32" r="26" fill="#00E5FF" fill-opacity="0.10"/>'
            '<circle cx="32" cy="96" r="26" fill="#10B981" fill-opacity="0.10"/>'
            '<circle cx="104" cy="96" r="26" fill="#7B2CBF" fill-opacity="0.12"/>'
            '<path d="M 48 32 C 46 62, 48 80, 41 90" stroke="#00E5FF" stroke-width="3.6" stroke-linecap="round"/>'
            '<path d="M 88 32 C 90 52, 89 65, 88 73" stroke="#00E5FF" stroke-width="3.6" stroke-linecap="round"/>'
            '<path d="M 81 48 C 72 58, 61 65, 53 70" stroke="#00E5FF" stroke-width="3.4" stroke-linecap="round"/>'
            '<path d="M 88 83 C 90 91, 92 96, 94 100" stroke="#00E5FF" stroke-width="3.6" stroke-linecap="round"/>'
            '<path d="M 16 84 C 24 72, 34 65, 42 60" stroke="#10B981" stroke-width="3.6" stroke-linecap="round"/>'
            '<path d="M 38 115 C 58 112, 74 96, 90 96" stroke="#10B981" stroke-width="3.6" stroke-linecap="round"/>'
            '<path d="M 74 58 C 84 72, 102 74, 118 84" stroke="#7B2CBF" stroke-width="3.6" stroke-linecap="round"/>'
            '<path d="M 44 92 C 52 92, 59 94, 64 97" stroke="#7B2CBF" stroke-width="3.4" stroke-linecap="round"/>'
            '<path d="M 74 103 C 83 109, 92 114, 100 115" stroke="#7B2CBF" stroke-width="3.6" stroke-linecap="round"/>'
            '<circle cx="68" cy="32" r="20" fill="#121519" stroke="#00E5FF" stroke-width="3.6"/>'
            '<g stroke="#00E5FF" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="71" cy="29" r="8.5" stroke-width="1.8"/>'
            '<circle cx="71" cy="29" r="1.8" fill="#00E5FF"/>'
            '<line x1="71" y1="20.5" x2="71" y2="37.5" stroke-width="1.3"/>'
            '<line x1="62.5" y1="29" x2="79.5" y2="29" stroke-width="1.3"/>'
            '<line x1="65" y1="23" x2="77" y2="35" stroke-width="1.3"/>'
            '<line x1="77" y1="23" x2="65" y2="35" stroke-width="1.3"/>'
            '<path d="M 58 31 L 63 26 M 58 27 L 58 33" stroke-width="1.6"/>'
            '<path d="M 57 38 L 78 38 M 62 38 L 59 43 M 74 38 L 77 43 M 62 38 L 62 32" stroke-width="1.7"/>'
            '</g>'
            '<circle cx="32" cy="96" r="20" fill="#121519" stroke="#10B981" stroke-width="3.6"/>'
            '<g transform="translate(32, 96) rotate(-45)" stroke="#10B981" stroke-linecap="round" stroke-linejoin="round">'
            '<rect x="-12" y="-5" width="24" height="10" rx="1.5" stroke-width="1.8" fill="none"/>'
            '<line x1="-8" y1="-5" x2="-8" y2="-1.5" stroke-width="1.4"/>'
            '<line x1="-4" y1="-5" x2="-4" y2="-2.5" stroke-width="1.4"/>'
            '<line x1="0" y1="-5" x2="0" y2="-1" stroke-width="1.4"/>'
            '<line x1="4" y1="-5" x2="4" y2="-2.5" stroke-width="1.4"/>'
            '<line x1="8" y1="-5" x2="8" y2="-1.5" stroke-width="1.4"/>'
            '</g>'
            '<circle cx="104" cy="96" r="20" fill="#121519" stroke="#7B2CBF" stroke-width="3.6"/>'
            '<g stroke="#7B2CBF" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="99.5" cy="104.5" r="3.3" stroke-width="1.8" fill="none"/>'
            '<circle cx="108.5" cy="104.5" r="3.3" stroke-width="1.8" fill="none"/>'
            '<path d="M 101.5 101.8 L 109.5 86.5" stroke-width="2.1"/>'
            '<path d="M 106.5 101.8 L 98.5 86.5" stroke-width="2.1"/>'
            '<circle cx="104" cy="96.5" r="1.2" fill="#FFFFFF" stroke="none"/>'
            '</g>'
            '</svg>'
        )

    @classmethod
    def obtener_logo_html(cls, compacto: bool = False) -> str:
        font_stack = "'Cinzel', 'Palatino Linotype', 'Book Antiqua', Georgia, serif"

        if compacto:
            emblema = cls._obtener_emblema_svg(tamano=56)
            return (
                '<div style="display:flex;align-items:center;justify-content:center;gap:10px;padding:4px 0 14px 0;">'
                f"{emblema}"
                '<div style="display:flex;flex-direction:column;text-align:left;">'
                f'<div style="font-family:{font_stack};color:#FFFFFF;font-size:18px;font-weight:800;letter-spacing:2px;line-height:1.15;">'
                'MOIRAN <span style="color:#00E5FF;">SCPS</span>'
                '</div>'
                f'<div style="font-family:{font_stack};color:#94A3B8;font-size:7.5px;font-weight:700;letter-spacing:1.2px;margin-top:3px;text-transform:uppercase;">'
                'SUPPLY CHAIN PLANNING'
                '</div>'
                '<div style="display:flex;gap:3px;margin-top:5px;width:100%;">'
                '<span style="height:2px;flex:1;background:#00E5FF;border-radius:2px;"></span>'
                '<span style="height:2px;flex:1;background:#10B981;border-radius:2px;"></span>'
                '<span style="height:2px;flex:1;background:#7B2CBF;border-radius:2px;"></span>'
                '</div>'
                '</div>'
                '</div>'
            )

        emblema = cls._obtener_emblema_svg(tamano=122)
        return (
            '<div style="display:flex;align-items:center;justify-content:center;gap:22px;margin-bottom:28px;">'
            f"{emblema}"
            '<div style="display:flex;flex-direction:column;text-align:left;">'
            f'<div style="font-family:{font_stack};color:#FFFFFF;font-size:40px;font-weight:900;letter-spacing:4.5px;line-height:1.08;text-shadow:0 2px 16px rgba(0,229,255,0.28);">'
            'MOIRAN <span style="color:#00E5FF;">SCPS</span>'
            '</div>'
            f'<div style="font-family:{font_stack};color:#E2E8F0;font-size:13.5px;font-weight:700;letter-spacing:3px;margin-top:7px;text-transform:uppercase;">'
            'SUPPLY CHAIN PLANNING SYSTEM'
            '</div>'
            '<div style="display:flex;gap:6px;margin-top:11px;width:100%;">'
            '<span style="height:3px;flex:1;background:#00E5FF;border-radius:2px;box-shadow:0 0 8px rgba(0,229,255,0.55);"></span>'
            '<span style="height:3px;flex:1;background:#10B981;border-radius:2px;box-shadow:0 0 8px rgba(16,185,129,0.55);"></span>'
            '<span style="height:3px;flex:1;background:#7B2CBF;border-radius:2px;box-shadow:0 0 8px rgba(123,44,191,0.55);"></span>'
            '</div>'
            '</div>'
            '</div>'
        )

    def renderizar_login(self) -> None:
        col_left, col_center, col_right = st.columns([0.4, 2.6, 0.4])

        with col_center:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(self.obtener_logo_html(compacto=False), unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
                usuario_input = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario", key="user_input")
                password_input = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña", key="pass_input")

                btn_login = st.form_submit_button("Iniciar Sesión", use_container_width=True)

                if btn_login:
                    if self.validar_credenciales(usuario_input, password_input):
                        self.iniciar_sesion(usuario_input)
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos.")

            st.markdown(
                '<div style="text-align:center;margin-top:30px;color:#475569;font-size:13px;font-weight:500;">'
                'Moiran SCPS v2.0.0 • Suite Integral (Cloto · Láquesis · Átropo)'
                '</div>',
                unsafe_allow_html=True
            )

    def requerir_autenticacion(self) -> bool:
        if not self.esta_autenticado:
            self.renderizar_login()
            return False
        return True