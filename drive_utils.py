import io
import os
import streamlit as st
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from datetime import datetime

# Cargar las credenciales y el Folder ID desde st.secrets
CREDS_DICT = dict(st.secrets["gcp_service_account"])
FOLDER_ID = CREDS_DICT.pop("folder_id") # Sacamos el folder_id del diccionario de credenciales

def get_drive_service():
    """Autentica y devuelve el cliente de la API de Drive."""
    scopes = ['https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(CREDS_DICT, scopes=scopes)
    return build('drive', 'v3', credentials=creds)

def guardar_historial_drive(df_resultados, usuario="User"):
    """Guarda el DF como CSV en Drive y borra los antiguos si hay más de 5."""
    try:
        service = get_drive_service()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"Resultados_{usuario}_{timestamp}.csv"
        
        # Convertir el DataFrame a un archivo CSV en memoria
        csv_data = df_resultados.to_csv(index=False).encode('utf-8')
        media = MediaIoBaseUpload(io.BytesIO(csv_data), mimetype='text/csv', resumable=True)
        
        file_metadata = {
            'name': nombre_archivo,
            'parents': [FOLDER_ID]
        }
        
        # Subir el archivo
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        
        # Limpiar exceso de archivos
        _mantener_ultimos_5_archivos(service)
        return True
    except Exception as e:
        print(f"Error subiendo a Drive: {e}")
        return False

def listar_historial_drive():
    """Obtiene la lista de los últimos archivos guardados."""
    try:
        service = get_drive_service()
        query = f"'{FOLDER_ID}' in parents and trashed=false"
        # Traer los archivos ordenados por fecha más reciente
        results = service.files().list(
            q=query, orderBy="createdTime desc", fields="files(id, name, createdTime)", pageSize=10
        ).execute()
        return results.get('files', [])
    except Exception as e:
        print(f"Error listando en Drive: {e}")
        return []

def descargar_csv_drive(file_id):
    """Descarga el archivo desde Drive y lo devuelve como DataFrame."""
    try:
        service = get_drive_service()
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

def _mantener_ultimos_5_archivos(service):
    """Elimina archivos si hay más de 5 en la carpeta de historial."""
    query = f"'{FOLDER_ID}' in parents and trashed=false"
    results = service.files().list(q=query, orderBy="createdTime desc", fields="files(id)").execute()
    archivos = results.get('files', [])
    
    if len(archivos) > 5:
        for f in archivos[5:]:
            service.files().delete(fileId=f['id']).execute()