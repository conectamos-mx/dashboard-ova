"""
OVA Dashboard - Backend API
Lectura de archivos Excel y exposición de KPIs via REST API
Soporta lectura desde archivos locales o Microsoft Graph API (OneDrive)
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
from datetime import datetime, date
from pathlib import Path
from typing import Optional
import os

# Importar funciones de carga de datos
# Importar funciones de carga de datos
# Intentar import relativo (para Render) o directo (local)
try:
    from backend.data_loader import (
        load_ventas_contado as _load_ventas_contado,
        load_ventas_credito as _load_ventas_credito,
        load_compras_cebolla as _load_compras_cebolla,
        load_compras_huevo as _load_compras_huevo,
        load_egresos as _load_egresos,
        load_stock_almacen_cebolla,
        load_stock_almacen_huevo,
        load_cajas,
        get_data_source_info
    )
except ImportError:
    from data_loader import (
        load_ventas_contado as _load_ventas_contado,
        load_ventas_credito as _load_ventas_credito,
        load_compras_cebolla as _load_compras_cebolla,
        load_compras_huevo as _load_compras_huevo,
        load_egresos as _load_egresos,
        load_stock_almacen_cebolla,
        load_stock_almacen_huevo,
        load_cajas,
        get_data_source_info
    )

app = FastAPI(title="OVA Dashboard API", version="2.0.0")

# CORS para desarrollo local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend directory - get absolute path
# __file__ is backend/main.py
# parent is backend/
# parent.parent would be Dashboard OVA/ but we need to be explicit
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent  # Dashboard OVA
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Servir archivos estáticos del frontend
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
else:
    print(f"[WARNING] Frontend directory not found at {FRONTEND_DIR}")


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parsea string de fecha a objeto date"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None


def load_ventas_contado() -> pd.DataFrame:
    """Carga la hoja de ventas al contado"""
    df = _load_ventas_contado()
    # Limpiar columnas
    df = df.rename(columns={
        'SEGMENTO DE NEGOCIO': 'segmento',
        'TIPO DE VENTA': 'tipo_venta',
        'TIPO/PRODUCTO': 'producto',
        'CLIENTE ADMON': 'cliente',
        'KG NETOS': 'kg_netos',
        'CAJAS/BULTOS': 'cajas',
        'PRECIO': 'precio',
        'TOTAL VENTA': 'total_venta',
        'FORMA DE PAGO': 'forma_pago',
        'OPERADOR': 'operador',
        'FECHA': 'fecha',
        'NOTA': 'nota'
    })
    # Filtrar filas válidas (que tengan ID)
    df = df[df['ID'].notna() & df['ID'].astype(str).str.startswith('VC')]
    # Filtrar ventas anuladas (excluir registros con "ANULADO" en nota)
    if 'nota' in df.columns:
        df = df[~df['nota'].astype(str).str.contains('ANULADO', case=False, na=False)]
    df['tipo'] = 'CONTADO'
    return df


def load_ventas_credito() -> pd.DataFrame:
    """Carga la hoja de ventas a crédito"""
    df = _load_ventas_credito()
    df = df.rename(columns={
        'SEGMENTO DE NEGOCIO': 'segmento',
        'TIPO DE VENTA': 'tipo_venta',
        'TIPO/PRODUCTO': 'producto',
        'CLIENTE ADMON': 'cliente',
        'KG NETOS': 'kg_netos',
        'CAJAS O BULTOS': 'cajas',
        'PRECIO UNITARIO': 'precio',
        'TOTAL VENTA': 'total_venta',
        'OPERADOR': 'operador',
        'FECHA': 'fecha',
        'SALDO': 'saldo',
        'NOTA (SI APLICA)': 'nota'
    })
    df = df[df['ID'].notna() & df['ID'].astype(str).str.startswith('VCR')]
    # Filtrar ventas anuladas (excluir registros con "ANULADO" en nota)
    if 'nota' in df.columns:
        df = df[~df['nota'].astype(str).str.contains('ANULADO', case=False, na=False)]
    df['tipo'] = 'CREDITO'
    df['forma_pago'] = 'CREDITO'
    return df


def load_all_ventas() -> pd.DataFrame:
    """Combina ventas al contado y a crédito"""
    contado = load_ventas_contado()
    credito = load_ventas_credito()
    # Seleccionar columnas comunes
    cols = ['ID', 'fecha', 'segmento', 'tipo_venta', 'producto', 'cliente', 
            'kg_netos', 'cajas', 'precio', 'total_venta', 'operador', 'tipo', 'forma_pago']
    contado_clean = contado[[c for c in cols if c in contado.columns]]
    credito_clean = credito[[c for c in cols if c in credito.columns]]
    return pd.concat([contado_clean, credito_clean], ignore_index=True)


def load_compras_cebolla() -> pd.DataFrame:
    """Carga compras de cebolla"""
    df = _load_compras_cebolla()
    df = df.rename(columns={
        'FECHA': 'fecha',
        'PROVEEDOR DE CEBOLLA': 'proveedor',
        'COSTALES': 'cantidad',
        'KG NETOS': 'kg_netos',
        'PRECIO X KG': 'precio',
        'TOTAL': 'total',
        'ESTATUS': 'estatus'
    })
    # Filtrar filas con ID válido (formato CMP-##) o con total válido
    df = df[df['ID'].notna() | (df['total'].notna() & (df['total'] > 0))]
    df['producto'] = 'CEBOLLA'
    return df


def load_compras_huevo() -> pd.DataFrame:
    """Carga compras de huevo"""
    df = _load_compras_huevo()
    df = df.rename(columns={
        'FECHA': 'fecha',
        'PROVEEDOR DE HUEVO': 'proveedor',
        'CAJAS': 'cantidad',
        'KG NETOS': 'kg_netos',
        'PRECIO x KG': 'precio',
        'TOTAL': 'total',
        'ESTATUS': 'estatus',
        'MARCA DE HUEVO': 'marca'
    })
    # Filtrar filas con total válido (IDs pueden estar vacíos en esta hoja)
    df = df[df['total'].notna() & (df['total'] > 0)]
    df['producto'] = 'HUEVO'
    return df


def load_all_compras() -> pd.DataFrame:
    """Combina compras de cebolla y huevo"""
    cebolla = load_compras_cebolla()
    huevo = load_compras_huevo()
    cols = ['ID', 'fecha', 'proveedor', 'cantidad', 'kg_netos', 'precio', 'total', 'producto']
    cebolla_clean = cebolla[[c for c in cols if c in cebolla.columns]]
    huevo_clean = huevo[[c for c in cols if c in huevo.columns]]
    return pd.concat([cebolla_clean, huevo_clean], ignore_index=True)


def load_egresos() -> pd.DataFrame:
    """Carga egresos/gastos operativos"""
    df = _load_egresos()
    df = df.rename(columns={
        'ID': 'id',
        'FECHA': 'fecha',
        'TIPO DE EGRESO': 'tipo_egreso',
        'CENTRO DE COSTOS': 'centro_costos',
        'CONCEPTO': 'concepto',
        'IMPORTE': 'importe',
        'OPERADOR': 'operador',
        'CLASIFICACIÓN COSTO/GASTO': 'clasificacion'
    })
    # Filtrar filas válidas: que tengan IMPORTE > 0 (algunos registros no tienen ID)
    df = df[df['importe'].notna() & (df['importe'] > 0)]
    return df


def load_stock_cebolla() -> float:
    """Obtiene el stock actual de cebolla en KG"""
    df = load_stock_almacen_cebolla()
    # Obtener última existencia válida
    existencia = df['EXISTENCIA'].dropna()
    if len(existencia) > 0:
        return float(existencia.iloc[-1])
    return 0.0


def load_stock_huevo() -> float:
    """Obtiene el stock actual de huevo en CAJAS (columna F)"""
    df = load_stock_almacen_huevo()
    # Huevo tiene múltiples columnas de existencia, usar la PRIMERA (cajas, columna F)
    existencia_cols = [c for c in df.columns if 'EXISTENCIA' in str(c)]
    if existencia_cols:
        # Usar la primera columna de existencia (cajas)
        first_col = existencia_cols[0]
        first_val = df[first_col].dropna()
        if len(first_val) > 0:
            return float(first_val.iloc[-1])
    return 0.0


def filter_by_date(df: pd.DataFrame, start_date: Optional[date], end_date: Optional[date], date_col: str = 'fecha') -> pd.DataFrame:
    """Filtra DataFrame por rango de fechas"""
    if date_col not in df.columns:
        return df
    
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    if start_date:
        df = df[df[date_col] >= pd.Timestamp(start_date)]
    if end_date:
        df = df[df[date_col] <= pd.Timestamp(end_date)]
    
    return df


# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check o sirve frontend si existe"""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"status": "ok", "service": "dashboard-ova-api"}


@app.get("/api/summary")
async def get_summary(
    start_date: Optional[str] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha fin (YYYY-MM-DD)")
):
    """Resumen general de KPIs"""
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    # Cargar datos
    ventas = filter_by_date(load_all_ventas(), start, end)
    compras = filter_by_date(load_all_compras(), start, end)
    egresos = filter_by_date(load_egresos(), start, end)
    
    # Calcular totales
    ventas_contado = ventas[ventas['tipo'] == 'CONTADO']['total_venta'].sum()
    ventas_credito = ventas[ventas['tipo'] == 'CREDITO']['total_venta'].sum()
    ventas_total = ventas_contado + ventas_credito
    
    compras_total = compras['total'].sum() if 'total' in compras.columns else 0
    gastos_total = egresos['importe'].sum() if 'importe' in egresos.columns else 0
    
    # Conteo de transacciones
    num_ventas = len(ventas)
    num_compras = len(compras)
    num_gastos = len(egresos)
    
    # Utilidad real = Ventas - Compras - Gastos
    utilidad_real = ventas_total - compras_total - gastos_total
    
    return {
        "ventas_total": float(ventas_total) if pd.notna(ventas_total) else 0,
        "ventas_contado": float(ventas_contado) if pd.notna(ventas_contado) else 0,
        "ventas_credito": float(ventas_credito) if pd.notna(ventas_credito) else 0,
        "compras_total": float(compras_total) if pd.notna(compras_total) else 0,
        "gastos_total": float(gastos_total) if pd.notna(gastos_total) else 0,
        "num_ventas": int(num_ventas),
        "num_compras": int(num_compras),
        "num_gastos": int(num_gastos),
        "utilidad_estimada": float(utilidad_real) if pd.notna(utilidad_real) else 0
    }


@app.get("/api/sales/by-type")
async def get_sales_by_type(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Ventas desglosadas por tipo (contado/crédito)"""
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    ventas = filter_by_date(load_all_ventas(), start, end)
    
    result = ventas.groupby('tipo').agg({
        'total_venta': 'sum',
        'ID': 'count'
    }).reset_index()
    
    return {
        "data": [
            {
                "tipo": row['tipo'],
                "total": float(row['total_venta']) if pd.notna(row['total_venta']) else 0,
                "cantidad": int(row['ID'])
            }
            for _, row in result.iterrows()
        ]
    }


@app.get("/api/sales/by-product")
async def get_sales_by_product(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Ventas desglosadas por producto (segmento de negocio)"""
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    ventas = filter_by_date(load_all_ventas(), start, end)
    
    # Agrupar por segmento
    result = ventas.groupby('segmento').agg({
        'total_venta': 'sum',
        'kg_netos': 'sum',
        'ID': 'count'
    }).reset_index()
    
    result = result.sort_values('total_venta', ascending=False)
    
    return {
        "data": [
            {
                "producto": row['segmento'],
                "total": float(row['total_venta']) if pd.notna(row['total_venta']) else 0,
                "kg_netos": float(row['kg_netos']) if pd.notna(row['kg_netos']) else 0,
                "cantidad": int(row['ID'])
            }
            for _, row in result.iterrows()
        ]
    }


@app.get("/api/sales/top-products")
async def get_top_products(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(5, description="Número de productos a mostrar")
):
    """Top productos más vendidos (excluyendo COVA)"""
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    ventas = filter_by_date(load_all_ventas(), start, end)
    
    # Filtrar productos que no sean COVA
    ventas = ventas[~ventas['producto'].str.contains('COVA', case=False, na=False)].copy()
    
    # --- LIMPIEZA Y FORMATEO DE NOMBRES ---
    def clean_format_name(row):
        # 1. Obtener segmento y producto
        seg = str(row.get('segmento', '')).strip().upper()
        prod = str(row.get('producto', '')).strip().upper()
        
        # Manejar 'NAN' strings de pandas
        if seg == 'NAN': seg = ''
        if prod == 'NAN': prod = ''
        
        # 2. Limpiar HUEVO_CENTRAL -> HUEVO
        if 'HUEVO_CENTRAL' in seg:
            seg = seg.replace('HUEVO_CENTRAL', 'HUEVO')
        
        # 3. Formatear como "PRODUCTO (TIPO)"
        if seg and prod:
            if seg == prod: return seg # Evitar "HUEVO (HUEVO)"
            return f"{seg} ({prod})"
        return seg or prod or "SIN NOMBRE"

    ventas['nombre_final'] = ventas.apply(clean_format_name, axis=1)
    
    # Agrupar por nombre final
    result = ventas.groupby('nombre_final').agg({
        'total_venta': 'sum',
        'kg_netos': 'sum',
        'cajas': 'sum',
        'ID': 'count'
    }).reset_index()
    
    result = result.sort_values('total_venta', ascending=False).head(limit)
    
    return {
        "data": [
            {
                "producto": row['nombre_final'],
                "total": float(row['total_venta']) if pd.notna(row['total_venta']) else 0,
                "kg_netos": float(row['kg_netos']) if pd.notna(row['kg_netos']) else 0,
                "cajas": float(row['cajas']) if pd.notna(row['cajas']) else 0,
                "cantidad_ventas": int(row['ID'])
            }
            for _, row in result.iterrows()
        ]
    }


@app.get("/api/sales/ticket-distribution")
async def get_ticket_distribution(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Distribución de ventas por valor del ticket"""
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    ventas = filter_by_date(load_all_ventas(), start, end)
    
    # Definir rangos
    bins = [0, 500, 2000, 5000, float('inf')]
    labels = ['Micro ($0-500)', 'Pequeño ($501-2k)', 'Mediano ($2k-5k)', 'Grande (>$5k)']
    
    # Crear columna de rango
    ventas['rango'] = pd.cut(ventas['total_venta'], bins=bins, labels=labels, right=False)
    
    result = ventas.groupby('rango', observed=False).agg({
        'total_venta': 'sum',
        'ID': 'count'
    }).reset_index()
    
    return {
        "data": [
            {
                "rango": str(row['rango']),
                "total": float(row['total_venta']) if pd.notna(row['total_venta']) else 0,
                "cantidad": int(row['ID'])
            }
            for _, row in result.iterrows()
        ]
    }
    
    result = result.sort_values('total_venta', ascending=False)
    
    return {
        "data": [
            {
                "operador": str(row['operador']) if pd.notna(row['operador']) else 'Sin asignar',
                "total": float(row['total_venta']) if pd.notna(row['total_venta']) else 0,
                "cantidad": int(row['ID'])
            }
            for _, row in result.iterrows()
        ]
    }


@app.get("/api/sales/trend")
async def get_sales_trend(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Tendencia de ventas por día"""
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    ventas = filter_by_date(load_all_ventas(), start, end)
    ventas['fecha'] = pd.to_datetime(ventas['fecha'], errors='coerce')
    ventas['fecha_str'] = ventas['fecha'].dt.strftime('%Y-%m-%d')
    
    result = ventas.groupby('fecha_str').agg({
        'total_venta': 'sum',
        'ID': 'count'
    }).reset_index()
    
    result = result.sort_values('fecha_str')
    
    return {
        "labels": result['fecha_str'].tolist(),
        "values": [float(v) if pd.notna(v) else 0 for v in result['total_venta'].tolist()],
        "counts": result['ID'].tolist()
    }


@app.get("/api/purchases")
async def get_purchases(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Resumen de compras"""
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    compras = filter_by_date(load_all_compras(), start, end)
    
    result = compras.groupby('producto').agg({
        'total': 'sum',
        'kg_netos': 'sum',
        'ID': 'count'
    }).reset_index()
    
    return {
        "data": [
            {
                "producto": row['producto'],
                "total": float(row['total']) if pd.notna(row['total']) else 0,
                "kg_netos": float(row['kg_netos']) if pd.notna(row['kg_netos']) else 0,
                "cantidad": int(row['ID'])
            }
            for _, row in result.iterrows()
        ],
        "total": float(compras['total'].sum()) if 'total' in compras.columns else 0
    }


@app.get("/api/sales/top-clients")
async def get_top_clients(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(10, description="Número de clientes a mostrar")
):
    """Top clientes por volumen de compra"""
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    ventas = filter_by_date(load_all_ventas(), start, end)
    
    result = ventas.groupby('cliente').agg({
        'total_venta': 'sum',
        'ID': 'count'
    }).reset_index()
    
    result = result.sort_values('total_venta', ascending=False).head(limit)
    
    return {
        "data": [
            {
                "cliente": str(row['cliente']) if pd.notna(row['cliente']) else 'Sin nombre',
                "total": float(row['total_venta']) if pd.notna(row['total_venta']) else 0,
                "compras": int(row['ID'])
            }
            for _, row in result.iterrows()
        ]
    }


@app.get("/api/receivables")
async def get_receivables():
    """Cuentas por cobrar (ventas a crédito con saldo pendiente)"""
    credito = load_ventas_credito()
    today = datetime.now().date()
    
    # Filtrar ventas con saldo pendiente > 100 (para evitar residuos de redondeo)
    if 'saldo' in credito.columns:
        pendientes = credito[credito['saldo'] > 100].copy()
        total_pendiente = pendientes['saldo'].sum()
        
        # Calcular días vencidos
        pendientes['fecha'] = pd.to_datetime(pendientes['fecha'], errors='coerce')
        pendientes['dias_vencidos'] = (pd.Timestamp(today) - pendientes['fecha']).dt.days
        
        return {
            "total_pendiente": float(total_pendiente) if pd.notna(total_pendiente) else 0,
            "num_cuentas": len(pendientes),
            "detalle": [
                {
                    "cliente": str(row['cliente']) if pd.notna(row.get('cliente')) else 'Sin nombre',
                    "saldo": float(row['saldo']) if pd.notna(row['saldo']) else 0,
                    "fecha": str(row['fecha'])[:10] if pd.notna(row['fecha']) else '',
                    "dias_vencidos": int(row['dias_vencidos']) if pd.notna(row['dias_vencidos']) else 0
                }
                for _, row in pendientes.head(30).iterrows()
            ]
        }
    
    return {"total_pendiente": 0, "num_cuentas": 0, "detalle": []}


@app.get("/api/expenses")
async def get_expenses(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Gastos operativos del período"""
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    egresos = filter_by_date(load_egresos(), start, end)
    
    total = egresos['importe'].sum() if 'importe' in egresos.columns else 0
    
    # Agrupar por TIPO DE EGRESO
    if 'tipo_egreso' in egresos.columns:
        by_tipo = egresos.groupby('tipo_egreso').agg({
            'importe': 'sum'
        }).reset_index()
        by_tipo = by_tipo.sort_values('importe', ascending=False)
    else:
        by_tipo = pd.DataFrame()
    
    return {
        "total": float(total) if pd.notna(total) else 0,
        "num_gastos": len(egresos),
        "por_tipo": [
            {
                "tipo": str(row['tipo_egreso']) if pd.notna(row['tipo_egreso']) else 'Otros',
                "total": float(row['importe']) if pd.notna(row['importe']) else 0
            }
            for _, row in by_tipo.iterrows()
        ] if len(by_tipo) > 0 else []
    }


@app.get("/api/stock")
async def get_stock():
    """Stock actual de productos"""
    stock_cebolla = load_stock_cebolla()
    stock_huevo = load_stock_huevo()

    return {
        "cebolla": {
            "kg": stock_cebolla,
            "producto": "CEBOLLA"
        },
        "huevo": {
            "cajas": stock_huevo,
            "producto": "HUEVO"
        },
        "total_kg": stock_cebolla
    }


@app.get("/api/cash-status")
async def get_cash_status(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Estado de cajas - saldos por operador y movimientos del día"""
    try:
        df = load_cajas()

        # Asegurar que FECHA es datetime
        df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')

        # Aplicar filtro de fechas si se proporcionan
        end = parse_date(end_date)
        if end:
            # Filtrar hasta la fecha final (inclusive)
            df = df[df['FECHA'].dt.date <= end].copy()

        # Obtener última fecha con datos (FIN DEL DÍA o SALDO INICIAL más reciente)
        df_fin_dia = df[df['CONCEPTO'].isin(['FIN DEL DÍA', 'SALDO INICIAL'])].copy()
        df_fin_dia = df_fin_dia.sort_values('FECHA', ascending=False)

        if len(df_fin_dia) == 0:
            return {
                "operadores": [],
                "movimientos_dia": {},
                "saldo_total": 0,
                "fecha": None
            }

        # Obtener saldos de cada operador (última fila con FIN DEL DÍA)
        ultima_fila = df_fin_dia.iloc[0]
        operadores = []

        for op_name in ['EMILIO', 'RICHARD', 'BODEGA 55', 'DIEGO']:
            saldo = pd.to_numeric(ultima_fila[op_name], errors='coerce')
            if pd.isna(saldo):
                saldo = 0

            operadores.append({
                "nombre": op_name,
                "saldo": float(saldo)
            })

        # Obtener movimientos del día actual
        fecha_actual = ultima_fila['FECHA'].date()
        df_dia = df[df['FECHA'].dt.date == fecha_actual].copy()

        # Calcular totales por concepto
        movimientos = {}
        for concepto in ['COBRANZA VENTAS AL CONTADO', 'COBRANZA VENTAS A CRÉDITO',
                        'GASTOS EFECTUADOS', 'MOVIMIENTO ENTRE CAJAS']:
            df_concepto = df_dia[df_dia['CONCEPTO'] == concepto]
            if len(df_concepto) > 0:
                # Sumar todos los operadores
                total = 0
                for op in ['EMILIO', 'RICHARD', 'BODEGA 55', 'DIEGO']:
                    val = pd.to_numeric(df_concepto[op].iloc[0], errors='coerce')
                    if pd.notna(val):
                        total += val
                movimientos[concepto] = float(total)
            else:
                movimientos[concepto] = 0.0

        # Saldo total de efectivo
        saldo_total = pd.to_numeric(ultima_fila['SALDO FINAL DE EFECTIVO'], errors='coerce')
        if pd.isna(saldo_total):
            saldo_total = 0

        return {
            "operadores": operadores,
            "movimientos_dia": movimientos,
            "saldo_total": float(saldo_total),
            "fecha": fecha_actual.isoformat()
        }

    except Exception as e:
        print(f"Error en /api/cash-status: {e}")
        import traceback
        traceback.print_exc()
        return {
            "operadores": [],
            "movimientos_dia": {},
            "saldo_total": 0,
            "fecha": None,
            "error": str(e)
        }


@app.get("/api/metrics/ticket-promedio")
async def get_ticket_promedio(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Ticket promedio de venta"""
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    ventas = filter_by_date(load_all_ventas(), start, end)
    
    total_ventas = ventas['total_venta'].sum()
    num_transacciones = len(ventas)
    
    ticket_promedio = total_ventas / num_transacciones if num_transacciones > 0 else 0
    
    # Por tipo de venta
    contado = ventas[ventas['tipo'] == 'CONTADO']
    credito = ventas[ventas['tipo'] == 'CREDITO']
    
    return {
        "ticket_promedio": float(ticket_promedio) if pd.notna(ticket_promedio) else 0,
        "contado": float(contado['total_venta'].sum() / len(contado)) if len(contado) > 0 else 0,
        "credito": float(credito['total_venta'].sum() / len(credito)) if len(credito) > 0 else 0,
        "num_transacciones": num_transacciones
    }


@app.get("/api/metrics/tasa-cobranza")
async def get_tasa_cobranza():
    """Tasa de cobranza - % de créditos cobrados vs pendientes"""
    credito = load_ventas_credito()
    
    if 'saldo' not in credito.columns or 'total_venta' not in credito.columns:
        return {"tasa": 0, "cobrado": 0, "pendiente": 0, "total_creditos": 0}
    
    total_creditos = credito['total_venta'].sum()
    total_pendiente = credito[credito['saldo'] > 0]['saldo'].sum()
    total_cobrado = total_creditos - total_pendiente
    
    tasa = (total_cobrado / total_creditos * 100) if total_creditos > 0 else 0
    
    return {
        "tasa": float(tasa) if pd.notna(tasa) else 0,
        "cobrado": float(total_cobrado) if pd.notna(total_cobrado) else 0,
        "pendiente": float(total_pendiente) if pd.notna(total_pendiente) else 0,
        "total_creditos": float(total_creditos) if pd.notna(total_creditos) else 0
    }


@app.get("/api/sales/by-weekday")
async def get_sales_by_weekday(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """Ventas por día de la semana"""
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    ventas = filter_by_date(load_all_ventas(), start, end)
    ventas['fecha'] = pd.to_datetime(ventas['fecha'], errors='coerce')
    ventas['dia_semana'] = ventas['fecha'].dt.dayofweek
    
    # Nombres en español
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    result = ventas.groupby('dia_semana').agg({
        'total_venta': 'sum',
        'ID': 'count'
    }).reset_index()
    
    result['dia_nombre'] = result['dia_semana'].apply(lambda x: dias[int(x)] if pd.notna(x) else 'N/A')
    result = result.sort_values('dia_semana')
    
    return {
        "labels": result['dia_nombre'].tolist(),
        "values": [float(v) if pd.notna(v) else 0 for v in result['total_venta'].tolist()],
        "counts": result['ID'].tolist()
    }


@app.get("/api/metrics/monthly-comparison")
async def get_monthly_comparison():
    """Comparativo del mes actual vs mes anterior"""
    today = datetime.now().date()
    
    # Mes actual
    first_day_current = date(today.year, today.month, 1)
    
    # Mes anterior
    if today.month == 1:
        first_day_prev = date(today.year - 1, 12, 1)
        last_day_prev = date(today.year - 1, 12, 31)
    else:
        first_day_prev = date(today.year, today.month - 1, 1)
        # Último día del mes anterior
        last_day_prev = first_day_current - pd.Timedelta(days=1)
        last_day_prev = last_day_prev.date() if hasattr(last_day_prev, 'date') else last_day_prev
    
    ventas = load_all_ventas()
    ventas['fecha'] = pd.to_datetime(ventas['fecha'], errors='coerce')
    
    # Ventas mes actual
    ventas_actual = ventas[ventas['fecha'] >= pd.Timestamp(first_day_current)]
    total_actual = ventas_actual['total_venta'].sum()
    
    # Ventas mes anterior (mismo período del mes)
    ventas_anterior = ventas[(ventas['fecha'] >= pd.Timestamp(first_day_prev)) & 
                             (ventas['fecha'] < pd.Timestamp(first_day_current))]
    total_anterior = ventas_anterior['total_venta'].sum()
    
    # Calcular crecimiento
    if total_anterior > 0:
        crecimiento = ((total_actual - total_anterior) / total_anterior) * 100
    else:
        crecimiento = 100 if total_actual > 0 else 0
    
    return {
        "mes_actual": {
            "total": float(total_actual) if pd.notna(total_actual) else 0,
            "transacciones": len(ventas_actual)
        },
        "mes_anterior": {
            "total": float(total_anterior) if pd.notna(total_anterior) else 0,
            "transacciones": len(ventas_anterior)
        },
        "crecimiento_porcentaje": float(crecimiento) if pd.notna(crecimiento) else 0
    }


@app.get("/api/health")
async def health_check():
    """Verificación de salud del API y fuente de datos"""
    data_source = get_data_source_info()

    return {
        "status": "healthy",
        "version": "2.0.0",
        "data_source": data_source
    }


@app.get("/api/debug/ventas")
async def debug_ventas():
    """Endpoint de debug para investigar el conteo de ventas"""
    contado = load_ventas_contado()
    credito = load_ventas_credito()
    todas = load_all_ventas()

    # Ejemplos de IDs de contado
    ids_contado_sample = contado['ID'].head(10).tolist() if len(contado) > 0 else []
    # Ejemplos de IDs de crédito
    ids_credito_sample = credito['ID'].head(10).tolist() if len(credito) > 0 else []

    return {
        "ventas_contado": {
            "total_registros": len(contado),
            "ejemplo_ids": ids_contado_sample,
            "columnas": contado.columns.tolist() if len(contado) > 0 else []
        },
        "ventas_credito": {
            "total_registros": len(credito),
            "ejemplo_ids": ids_credito_sample,
            "columnas": credito.columns.tolist() if len(credito) > 0 else []
        },
        "total_combinado": len(todas),
        "nota": "Comparar estos números con el conteo manual en Excel"
    }


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8005))
    uvicorn.run(app, host="0.0.0.0", port=port)
