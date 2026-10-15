import io
import re
import requests
import streamlit as st
import pandas as pd
from datetime import datetime

APPS_SCRIPT_URL = st.secrets.get("apps_script_url", "")

def guardar_historial_drive(df_resultados, usuario="User", titulo=""):
    """Envía el archivo a tu Google Drive personal a través de Google Apps Script."""
    if not APPS_SCRIPT_URL:
        return False, "Falta configurar apps_script_url en Secrets de Streamlit"
        
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if titulo and titulo.strip():
            titulo_clean = re.sub(r'[^a-zA-Z0-9\s\-_]', '', titulo).strip()
            titulo_slug = re.sub(r'[-\s]+', '-', titulo_clean)
            nombre_archivo = f"Resultados_{usuario}_{titulo_slug}_{timestamp}.csv"
        else:
            nombre_archivo = f"Resultados_{usuario}_{timestamp}.csv"
        
        csv_str = df_resultados.to_csv(index=False)
        
        payload = {
            "action": "create",
            "filename": nombre_archivo,
            "csv_content": csv_str
        }
        
        res = requests.post(APPS_SCRIPT_URL, json=payload, timeout=45)
        data = res.json()
        
        if data.get("status") == "success":
            return True, "Guardado con éxito en tu Drive Personal"
        else:
            return False, f"Error Apps Script: {data.get('message')}"
    except Exception as e:
        return False, f"Error de conexión: {str(e)}"

def listar_historial_drive():
    """Obtiene la lista de los últimos archivos en tu carpeta personal."""
    if not APPS_SCRIPT_URL:
        return []
    try:
        res = requests.get(APPS_SCRIPT_URL, timeout=15)
        data = res.json()
        if data.get("status") == "success":
            return data.get("files", [])
        return []
    except Exception:
        return []

def descargar_csv_drive(file_id):
    """Descarga el archivo directamente desde Google Drive por su ID."""
    try:
        url_download = f"https://drive.google.com/uc?export=download&id={file_id}"
        df = pd.read_csv(url_download)
        return df
    except Exception as e:
        print(f"Error descargando desde Drive: {e}")
        return None

def renombrar_archivo_drive(file_id, nuevo_titulo, usuario="User"):
    """Renombra un archivo existente en Google Drive."""
    if not APPS_SCRIPT_URL:
        return False, "Sin URL de Apps Script"
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        titulo_clean = re.sub(r'[^a-zA-Z0-9\s\-_]', '', nuevo_titulo).strip()
        titulo_slug = re.sub(r'[-\s]+', '-', titulo_clean)
        nuevo_nombre_archivo = f"Resultados_{usuario}_{titulo_slug}_{timestamp}.csv"
        
        payload = {
            "action": "rename",
            "file_id": file_id,
            "new_name": nuevo_nombre_archivo
        }
        res = requests.post(APPS_SCRIPT_URL, json=payload, timeout=30)
        data = res.json()
        if data.get("status") == "success":
            return True, "Archivo renombrado con éxito"
        return False, data.get("message", "Error al renombrar")
    except Exception as e:
        return False, str(e)

def eliminar_archivo_drive(file_id):
    """Envía un archivo a la papelera de Google Drive."""
    if not APPS_SCRIPT_URL:
        return False, "Sin URL de Apps Script"
    try:
        payload = {
            "action": "delete",
            "file_id": file_id
        }
        res = requests.post(APPS_SCRIPT_URL, json=payload, timeout=30)
        data = res.json()
        if data.get("status") == "success":
            return True, "Archivo eliminado de Google Drive"
        return False, data.get("message", "Error al eliminar")
    except Exception as e:
        return False, str(e)