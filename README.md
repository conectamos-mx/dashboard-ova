# OVA Dashboard

Dashboard profesional para visualización de KPIs de ventas y almacén.

## 🚀 Características

- **12 KPIs** en tiempo real: ventas, compras, gastos, stock, utilidad, etc.
- **7 Gráficos** interactivos con Chart.js
- **Dual-mode**: Lee desde archivos locales o OneDrive
- **Responsive**: Funciona en desktop, tablet y móvil
- **Tema oscuro** profesional con glassmorphism

## 📊 KPIs Disponibles

### Financieros

- Ventas Totales
- Ventas al Contado
- Ventas a Crédito
- Compras Totales
- Gastos Operativos
- Utilidad Real (Ventas - Compras - Gastos)

### Operativos

- Stock Cebolla (kg)
- Stock Huevo (kg)
- Ticket Promedio
- Tasa de Cobranza
- Por Cobrar
- Crecimiento vs Mes Anterior

## 🛠️ Instalación

```bash
# Clonar o descargar el proyecto
cd "Dashboard OVA"

# Instalar dependencias
cd backend
pip install -r requirements.txt

# Iniciar servidor
python -m uvicorn main:app --reload --port 8005

# Abrir en navegador
# http://localhost:8005
```

## ⚙️ Configuración

### Modo Local (Por Defecto)

Coloca los archivos Excel en la raíz del proyecto:

```
Dashboard OVA/
├── CONTROL DE VENTAS OVA 2026 -.xlsx
├── CONTROL DE ALMACÉN OVA 2026 -.xlsx
├── backend/
└── frontend/
```

### Modo OneDrive (Opcional)

Ver [setup_guide.md](setup_guide.md) para configurar Microsoft Graph API.

## 📁 Estructura del Proyecto

```
Dashboard OVA/
├── backend/
│   ├── main.py              # API FastAPI
│   ├── graph_client.py      # Cliente Microsoft Graph
│   ├── data_loader.py       # Wrapper dual-mode
│   ├── requirements.txt     # Dependencias
│   └── .env                 # Configuración
├── frontend/
│   ├── index.html           # UI del dashboard
│   ├── styles.css           # Estilos
│   └── app.js               # Lógica y gráficos
└── README.md
```

## 🔌 API Endpoints

- `GET /` - Dashboard frontend
- `GET /api/summary` - Resumen general
- `GET /api/sales/by-type` - Ventas por tipo
- `GET /api/sales/by-product` - Ventas por producto
- `GET /api/sales/trend` - Tendencia de ventas
- `GET /api/sales/by-weekday` - Ventas por día de semana
- `GET /api/purchases` - Compras
- `GET /api/expenses` - Gastos operativos
- `GET /api/stock` - Stock actual
- `GET /api/receivables` - Cuentas por cobrar
- `GET /api/health` - Estado del sistema

## 🌐 Despliegue

### Local

```bash
python -m uvicorn main:app --reload --port 8005
```

### Vercel (Próximamente)

Instrucciones de despliegue en Vercel pendientes.

## 📝 Licencia

Proyecto privado - OVA 2026
