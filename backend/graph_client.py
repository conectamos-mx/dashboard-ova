"""
Microsoft Graph API Client - Personal OneDrive
Para cuentas personales de Microsoft (Outlook, Hotmail)
"""

import os
import io
import httpx
import msal
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET')
TENANT_ID = os.getenv('MICROSOFT_TENANT_ID', 'consumers')  # Usar 'consumers' o 'common' para cuentas personales

# IDs de archivos
EXCEL_VENTAS_ITEM_ID = os.getenv('EXCEL_VENTAS_ITEM_ID')
EXCEL_ALMACEN_ITEM_ID = os.getenv('EXCEL_ALMACEN_ITEM_ID')

# URLs de Microsoft Graph
GRAPH_BASE_URL = 'https://graph.microsoft.com/v1.0'

# Token de acceso manual (temporal)
# Este token debe generarse manualmente desde Graph Explorer
ACCESS_TOKEN = os.getenv('MICROSOFT_ACCESS_TOKEN', '')

# Caché de archivos
_file_cache = {}
_df_cache = {}


class GraphAPIError(Exception):
    """Error personalizado para Graph API"""
    pass


# Ubicación del caché de tokens
CACHE_PATH = os.path.join(os.path.dirname(__file__), 'token_cache.bin')
SCOPES = ['https://graph.microsoft.com/Files.Read.All', 'https://graph.microsoft.com/User.Read']

def get_msal_app():
    """Configura y retorna la aplicación MSAL con caché persistente"""
    authority = f"https://login.microsoftonline.com/{TENANT_ID or 'common'}"
    
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            cache.deserialize(f.read())
    
    # Función para guardar el caché
    def save_cache():
        if cache.has_state_changed:
            with open(CACHE_PATH, "w") as f:
                f.write(cache.serialize())
    
    app = msal.PublicClientApplication(
        CLIENT_ID, 
        authority=authority,
        token_cache=cache
    )
    return app, save_cache

def get_access_token() -> str:
    """
    Obtiene un token de acceso válido.
    1. Intenta silenciosamente via caché local (dev).
    2. Intenta usar REFRESH TOKEN via variable de entorno (prod/render).
    3. Intenta usar token estático (emergencia).
    """
    app, save_cache = get_msal_app()
    
    # 1. Intentar obtener token del caché silenciosamente
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and 'access_token' in result:
            save_cache()
            return result['access_token']
    
    # 2. Estrategia Producción (Render): Usar Refresh Token inyectado
    refresh_token = os.getenv('MICROSOFT_REFRESH_TOKEN')
    if refresh_token:
        # Intentar canjear refresh token por uno nuevo de acceso
        result = app.acquire_token_by_refresh_token(refresh_token, scopes=SCOPES)
        if result and 'access_token' in result:
            # Opcional: imprimir algo en logs para debug
            # print("Token refrescado exitosamente usando env var")
            return result['access_token']
    
    # 3. Fallback: Token manual estático
    token = os.getenv('MICROSOFT_ACCESS_TOKEN', '')
    if token:
        return token

    raise GraphAPIError(
        "No se pudo autenticar. En Render, asegura configurar MICROSOFT_REFRESH_TOKEN. "
        "En local, ejecuta 'python backend/setup_onedrive_msal.py'."
    )


def download_excel_file(item_id: str, cache_minutes: int = 2) -> bytes:
    """
    Descarga un archivo Excel desde OneDrive personal
    
    Args:
        item_id: ID del archivo en OneDrive
        cache_minutes: Minutos para cachear el archivo
    
    Returns:
        Contenido del archivo en bytes
    """
    # Verificar caché
    cache_key = f"file_{item_id}"
    if cache_key in _file_cache:
        cached_data, cached_time = _file_cache[cache_key]
        if datetime.now() - cached_time < timedelta(minutes=cache_minutes):
            return cached_data
    
    # Descargar archivo
    token = get_access_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    # Usar /me/drive para cuentas personales
    download_url = f'{GRAPH_BASE_URL}/me/drive/items/{item_id}/content'
    
    try:
        response = httpx.get(download_url, headers=headers, timeout=60.0, follow_redirects=True)
        response.raise_for_status()
        
        file_content = response.content
        
        # Guardar en caché
        _file_cache[cache_key] = (file_content, datetime.now())
        
        return file_content
    
    except httpx.HTTPError as e:
        raise GraphAPIError(f"Error descargando archivo {item_id}: {str(e)}")


def read_excel_sheet(item_id: str, sheet_name: str, header: int = 0, **kwargs) -> pd.DataFrame:
    """
    Lee una hoja específica de un archivo Excel desde OneDrive
    
    Args:
        item_id: ID del archivo en OneDrive
        sheet_name: Nombre de la hoja
        header: Fila del encabezado
        **kwargs: Argumentos adicionales para pd.read_excel
    
    Returns:
        DataFrame con los datos de la hoja
    """
    # 1. Verificar Cache de Dataframe
    # Usamos todas las variables que afectan la salida como llave
    cache_key = f"{item_id}|{sheet_name}|{header}|{str(kwargs)}"
    
    if cache_key in _df_cache:
        df, cached_time = _df_cache[cache_key]
        if datetime.now() - cached_time < timedelta(minutes=2):
            # Retornamos una copia para evitar mutaciones accidentales en el cache
            return df.copy()
            
    try:
        file_content = download_excel_file(item_id)
        
        # Leer Excel desde bytes
        excel_file = io.BytesIO(file_content)
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=header, **kwargs)
        
        # Guardar en caché de DFs
        _df_cache[cache_key] = (df, datetime.now())
        
        return df.copy()
    
    except Exception as e:
        raise GraphAPIError(f"Error leyendo hoja '{sheet_name}' del archivo {item_id}: {str(e)}")


def clear_cache():
    """Limpia el caché de archivos y dataframes"""
    global _file_cache, _df_cache
    _file_cache = {}
    _df_cache = {}


def get_file_info(item_id: str) -> Dict[str, Any]:
    """
    Obtiene información de un archivo en OneDrive
    
    Args:
        item_id: ID del archivo
    
    Returns:
        Diccionario con información del archivo
    """
    token = get_access_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    url = f'{GRAPH_BASE_URL}/me/drive/items/{item_id}'
    
    try:
        response = httpx.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        return response.json()
    
    except httpx.HTTPError as e:
        raise GraphAPIError(f"Error obteniendo info del archivo {item_id}: {str(e)}")


# Funciones de conveniencia para los archivos específicos
def read_ventas_sheet(sheet_name: str, header: int = 7, **kwargs) -> pd.DataFrame:
    """Lee una hoja del archivo de ventas"""
    if not EXCEL_VENTAS_ITEM_ID:
        raise GraphAPIError("EXCEL_VENTAS_ITEM_ID no configurado en variables de entorno")
    return read_excel_sheet(EXCEL_VENTAS_ITEM_ID, sheet_name, header, **kwargs)


def read_almacen_sheet(sheet_name: str, header: int = 9, **kwargs) -> pd.DataFrame:
    """Lee una hoja del archivo de almacén"""
    if not EXCEL_ALMACEN_ITEM_ID:
        raise GraphAPIError("EXCEL_ALMACEN_ITEM_ID no configurado en variables de entorno")
    return read_excel_sheet(EXCEL_ALMACEN_ITEM_ID, sheet_name, header, **kwargs)
