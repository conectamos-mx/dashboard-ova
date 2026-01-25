"""
Data Loader - Wrapper para cargar datos desde archivos locales o OneDrive
Permite cambiar entre fuentes de datos sin modificar el código principal
"""

import os
import pandas as pd
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Determinar modo de operación
USE_ONEDRIVE = os.getenv('USE_ONEDRIVE', 'false').lower() == 'true'

if USE_ONEDRIVE:
    try:
        from graph_client import read_ventas_sheet, read_almacen_sheet, GraphAPIError
        print("✅ Modo OneDrive activado - usando Microsoft Graph API")
    except ImportError as e:
        print(f"⚠️  Error importando graph_client: {e}")
        print("⚠️  Cayendo a modo local")
        USE_ONEDRIVE = False

# Rutas a archivos locales (fallback)
BASE_DIR = Path(__file__).resolve().parent.parent
VENTAS_FILE = BASE_DIR / "CONTROL DE VENTAS OVA 2026 -.xlsx"
ALMACEN_FILE = BASE_DIR / "CONTROL DE ALMACÉN OVA 2026 -.xlsx"


def load_excel_sheet(
    file_type: str,
    sheet_name: str,
    header: int = 0,
    **kwargs
) -> pd.DataFrame:
    """
    Carga una hoja de Excel desde OneDrive o archivo local
    
    Args:
        file_type: 'ventas' o 'almacen'
        sheet_name: Nombre de la hoja
        header: Fila del encabezado
        **kwargs: Argumentos adicionales para pd.read_excel
    
    Returns:
        DataFrame con los datos
    """
    if USE_ONEDRIVE:
        # Modo OneDrive - sin fallback
        if file_type == 'ventas':
            return read_ventas_sheet(sheet_name, header)
        elif file_type == 'almacen':
            return read_almacen_sheet(sheet_name, header)
        else:
            raise ValueError(f"Tipo de archivo desconocido: {file_type}")
    
    # Modo local
    if file_type == 'ventas':
        file_path = VENTAS_FILE
    elif file_type == 'almacen':
        file_path = ALMACEN_FILE
    else:
        raise ValueError(f"Tipo de archivo desconocido: {file_type}")
    
    if not file_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
    
    return pd.read_excel(file_path, sheet_name=sheet_name, header=header, **kwargs)


# Funciones de conveniencia
def load_ventas_contado() -> pd.DataFrame:
    """Carga ventas al contado"""
    return load_excel_sheet('ventas', 'VENTAS AL CONTADO', header=7)


def load_ventas_credito() -> pd.DataFrame:
    """Carga ventas a crédito"""
    return load_excel_sheet('ventas', 'VENTAS A CRÉDITO', header=7)


def load_compras_cebolla() -> pd.DataFrame:
    """Carga compras de cebolla"""
    return load_excel_sheet('almacen', 'COMPRAS (C)', header=9)


def load_compras_huevo() -> pd.DataFrame:
    """Carga compras de huevo"""
    return load_excel_sheet('almacen', 'COMPRAS (H)', header=9)


def load_egresos() -> pd.DataFrame:
    """Carga egresos/gastos"""
    return load_excel_sheet('ventas', 'EGRESOS EN EFECTIVO', header=8)


def load_stock_almacen_cebolla() -> pd.DataFrame:
    """Carga control de almacén de cebolla"""
    return load_excel_sheet('almacen', 'CONTROL DE ALMACÉN (C)', header=9)


def load_stock_almacen_huevo() -> pd.DataFrame:
    """Carga control de almacén de huevo"""
    return load_excel_sheet('almacen', 'CONTROL DE ALMACÉN (H)', header=9)


def get_data_source_info() -> dict:
    """Retorna información sobre la fuente de datos actual"""
    return {
        "mode": "OneDrive" if USE_ONEDRIVE else "Local",
        "onedrive_enabled": USE_ONEDRIVE,
        "local_files_exist": {
            "ventas": VENTAS_FILE.exists(),
            "almacen": ALMACEN_FILE.exists()
        }
    }
