import io
import os
import re
import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from datetime import datetime

def get_drive_service():
    """Autentica y devuelve el cliente de la API de Drive con manejo robusto de clave."""
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        folder_id = creds_dict.pop("folder_id", "").strip()
        
        # Limpieza de saltos de línea en private_key para entornos Linux/Streamlit Cloud
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
        scopes = ['https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        service = build('drive', 'v3', credentials=creds)
        return service, folder_id, None
    except Exception as e:
        return None, None, f"Error de Credenciales/Secrets: {str(e)}"

def guardar_historial_drive(df_resultados, usuario="User", titulo=""):
    """Guarda el DF como CSV en Drive. Devuelve (éxito: bool, mensaje: str)."""
    service, folder_id, err_auth = get_drive_service()
    if err_auth:
        return False, err_auth
        
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitizar título para nombre de archivo
        if titulo and titulo.strip():
            titulo_clean = re.sub(r'[^a-zA-Z0-9\s\-_]', '', titulo).strip()
            titulo_slug = re.sub(r'[-\s]+', '-', titulo_clean)
            nombre_archivo = f"Resultados_{usuario}_{titulo_slug}_{timestamp}.csv"
        else:
            nombre_archivo = f"Resultados_{usuario}_{timestamp}.csv"
        
        csv_data = df_resultados.to_csv(index=False).encode('utf-8')
        media = MediaIoBaseUpload(io.BytesIO(csv_data), mimetype='text/csv', resumable=True)
        
        file_metadata = {
            'name': nombre_archivo,
            'parents': [folder_id]
        }
        
        archivo_creado = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        _mantener_ultimos_5_archivos(service, folder_id)
        return True, f"Guardado con éxito (ID: {archivo_creado.get('id')})"
    except Exception as e:
        return False, f"Error API Drive: {str(e)}"

def listar_historial_drive():
    """Obtiene la lista de los últimos archivos guardados."""
    service, folder_id, err_auth = get_drive_service()
    if err_auth:
        raise Exception(err_auth)
        
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(
            q=query, orderBy="createdTime desc", fields="files(id, name, createdTime)", pageSize=10
        ).execute()
        return results.get('files', [])
    except Exception as e:
        raise Exception(f"Error consultando Drive: {str(e)}")

def descargar_csv_drive(file_id):
    """Descarga el archivo desde Drive y lo devuelve como DataFrame."""
    service, folder_id, err_auth = get_drive_service()
    if err_auth:
        return None
        
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        fh.seek(0)
        return pd.read_csv(fh)
    except Exception as e:
        print(f"Error descargando de Drive: {e}")
        return None

def _mantener_ultimos_5_archivos(service, folder_id):
    """Elimina archivos si hay más de 5 en la carpeta de historial."""
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, orderBy="createdTime desc", fields="files(id)").execute()
        archivos = results.get('files', [])
        if len(archivos) > 5:
            for f in archivos[5:]:
                service.files().delete(fileId=f['id']).execute()
    except Exception:
        pass