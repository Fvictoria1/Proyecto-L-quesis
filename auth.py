import streamlit as st


class MoiranAuth:
    """
    Objeto independiente de autenticación y pantalla de acceso para Moiran SCPS.
    Gestiona el estado de sesión, validación de credenciales y UI de Log-on.
    """

    def __init__(self, usuario_default: str = "Fvictoria1", password_default: str = "4161"):
        self.usuario_correcto = self._obtener_secreto("AUTH_USER", usuario_default)
        self.password_correcto = self._obtener_secreto("AUTH_PASSWORD", password_default)
        self._inicializar_sesion()

    @staticmethod
    def _obtener_secreto(clave: str, valor_respaldo: str) -> str:
        """Permite escalar a st.secrets en producción manteniendo compatibilidad local."""
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

    def renderizar_login(self) -> None:
        """Renderiza la interfaz visual de acceso de Moiran SCPS."""
        col_left, col_center, col_right = st.columns([0.8, 1.8, 0.8])

        with col_center:
            st.markdown("<br>", unsafe_allow_html=True)

            svg_logo_login = """
<div style="text-align: center; margin-bottom: 25px;">
<svg width="100%" height="105" viewBox="0 0 450 100" fill="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="45" cy="50" r="38" fill="#00E5FF" fill-opacity="0.06"/>
<path d="M 22 15 L 22 82 L 78 82" stroke="#FFFFFF" stroke-width="4.5" stroke-linecap="round"/>
<path d="M 73 82 L 85 70" stroke="#00E5FF" stroke-width="3.5" stroke-linecap="round"/>
<path d="M 18 78 Q 32 80, 44 28 T 74 68 Q 78 64, 83 55" stroke="#00E5FF" stroke-width="3.5" stroke-linecap="round" fill="none"/>
<path d="M 18 80 Q 32 82, 44 30 T 74 66, 83 57" stroke="#7B2CBF" stroke-width="2" stroke-linecap="round" fill="none" stroke-opacity="0.7"/>
<circle cx="25" cy="78" r="3.5" fill="#FFFFFF" stroke="#00E5FF" stroke-width="1.5"/>
<circle cx="44" cy="28" r="3.5" fill="#FFFFFF" stroke="#00E5FF" stroke-width="1.5"/>
<circle cx="65" cy="60" r="3.5" fill="#FFFFFF" stroke="#00E5FF" stroke-width="1.5"/>
<circle cx="83" cy="55" r="5.5" fill="#00E5FF" stroke="#FFFFFF" stroke-width="2"/>
<text x="108" y="49" fill="#FFFFFF" font-family="'Segoe UI', Roboto, sans-serif" font-size="28" font-weight="800" letter-spacing="3.5">MOIRAN SCPS</text>
<text x="110" y="71" fill="#00E5FF" font-family="'Segoe UI', Roboto, sans-serif" font-size="9.5" font-weight="700" letter-spacing="2.2">SUPPLY CHAIN PLANNING SYSTEM</text>
<line x1="110" y1="82" x2="425" y2="82" stroke="#2A323D" stroke-width="1.5"/>
<line x1="110" y1="82" x2="235" y2="82" stroke="#00E5FF" stroke-width="2.5"/>
</svg>
</div>
"""
            st.markdown(svg_logo_login, unsafe_allow_html=True)

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

            st.markdown("""
<div style="text-align: center; margin-top: 30px; color: #475569; font-size: 13px; font-weight: 500;">
    Moiran SCPS v2.0.0 • Suite Integral (Cloto · Láquesis · Átropo)
</div>
""", unsafe_allow_html=True)

    def requerir_autenticacion(self) -> bool:
        """
        Punto de entrada único para app.py.
        Si no hay sesión activa, dibuja el login y devuelve False.
        """
        if not self.esta_autenticado:
            self.renderizar_login()
            return False
        return True