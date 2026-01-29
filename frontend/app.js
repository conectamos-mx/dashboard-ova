/**
 * OVA Dashboard - Frontend Application
 * Conecta con la API y renderiza los KPIs y gráficos
 */

// ==================== CONFIGURACIÓN ====================
const API_BASE = '';  // Mismo origen

// ==================== ESTADO ====================
let charts = {};
let currentFilters = {
    startDate: null,
    endDate: null
};

// ==================== INICIALIZACIÓN ====================
document.addEventListener('DOMContentLoaded', () => {
    initDateFilters();
    loadAllData();
    setupEventListeners();
});

function initDateFilters() {
    // Por defecto, mostrar el mes actual
    const today = new Date();
    const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    
    document.getElementById('start-date').value = formatDateForInput(firstDayOfMonth);
    document.getElementById('end-date').value = formatDateForInput(today);
    
    currentFilters.startDate = formatDateForAPI(firstDayOfMonth);
    currentFilters.endDate = formatDateForAPI(today);
}

function setupEventListeners() {
    document.getElementById('filter-btn').addEventListener('click', applyFilters);
    document.getElementById('reset-btn').addEventListener('click', resetFilters);
}

function applyFilters() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    currentFilters.startDate = startDate || null;
    currentFilters.endDate = endDate || null;
    
    loadAllData();
}

function resetFilters() {
    document.getElementById('start-date').value = '';
    document.getElementById('end-date').value = '';
    currentFilters.startDate = null;
    currentFilters.endDate = null;
    
    loadAllData();
}

// ==================== UTILIDADES ====================
function formatDateForInput(date) {
    return date.toISOString().split('T')[0];
}

function formatDateForAPI(date) {
    return date.toISOString().split('T')[0];
}

function formatCurrency(value) {
    if (value === null || value === undefined || isNaN(value)) return '$0';
    // Usamos es-MX para formato mexicano: 1,234.56 (coma miles, punto decimales)
    const formatted = new Intl.NumberFormat('es-MX', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
    return `$${formatted}`;
}

function formatNumber(value) {
    if (value === null || value === undefined || isNaN(value)) return '0';
    return new Intl.NumberFormat('es-MX').format(value);
}

function formatKG(value) {
    if (value === null || value === undefined || isNaN(value)) return '0 kg';
    return new Intl.NumberFormat('es-MX', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value) + ' kg';
}

function formatCajas(value) {
    if (value === null || value === undefined || isNaN(value)) return '0 cajas';
    return new Intl.NumberFormat('es-MX', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value) + ' cajas';
}

function formatPercent(value) {
    if (value === null || value === undefined || isNaN(value)) return '0%';
    return value.toFixed(1) + '%';
}

function buildQueryString() {
    const params = new URLSearchParams();
    if (currentFilters.startDate) params.append('start_date', currentFilters.startDate);
    if (currentFilters.endDate) params.append('end_date', currentFilters.endDate);
    return params.toString() ? `?${params.toString()}` : '';
}

async function fetchAPI(endpoint, addFilters = true) {
    try {
        let url = `${API_BASE}${endpoint}`;
        if (addFilters) {
            const queryString = buildQueryString();
            if (queryString) {
                // If endpoint already has a ?, use & instead
                const separator = endpoint.includes('?') ? '&' : '?';
                // buildQueryString returns '?foo=bar', so we slice off the first character
                url = `${url}${separator}${queryString.slice(1)}`;
            }
        }
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        return null;
    }
}

function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// ==================== CARGA DE DATOS ====================
async function loadAllData() {
    showLoading();
    
    try {
        await Promise.all([
            loadSummary(),
            loadStock(),
            loadTicketPromedio(),
            loadTasaCobranza(),
            loadMonthlyComparison(),
            loadTopProducts(),
            loadSalesByProduct(),
            loadTicketDistribution(),
            loadSalesTrend(),
            loadSalesByWeekday(),
            loadPurchases(),
            loadExpenses(),
            loadTopClients(),
            loadReceivables(),
            loadCashStatus()
        ]);
    } catch (error) {
        console.error('Error loading data:', error);
    } finally {
        hideLoading();
    }
}

// ==================== CARGAR KPIs ====================
async function loadSummary() {
    const data = await fetchAPI('/api/summary');
    if (!data) return;
    
    document.getElementById('ventas-total').textContent = formatCurrency(data.ventas_total);
    document.getElementById('ventas-contado').textContent = formatCurrency(data.ventas_contado);
    document.getElementById('ventas-credito').textContent = formatCurrency(data.ventas_credito);
    document.getElementById('compras-total').textContent = formatCurrency(data.compras_total);
    document.getElementById('gastos-total').textContent = formatCurrency(data.gastos_total || 0);
    document.getElementById('num-ventas').textContent = `${formatNumber(data.num_ventas)} transacciones`;
    document.getElementById('num-compras').textContent = `${formatNumber(data.num_compras)} compras`;
    document.getElementById('num-gastos').textContent = `${formatNumber(data.num_gastos || 0)} gastos`;
}

async function loadStock() {
    const data = await fetchAPI('/api/stock', false);
    if (!data) return;

    document.getElementById('stock-cebolla').textContent = formatKG(data.cebolla?.kg || 0);
    document.getElementById('stock-huevo').textContent = formatCajas(data.huevo?.cajas || 0);
}

async function loadCashStatus() {
    const data = await fetchAPI('/api/cash-status', true);  // Respetar filtro de fechas
    if (!data || !data.operadores) return;

    // Actualizar saldos por operador
    data.operadores.forEach(op => {
        let cardId = '';
        if (op.nombre === 'PIPO') cardId = 'cash-pipo';
        else if (op.nombre === 'RICHARD') cardId = 'cash-richard';
        else if (op.nombre === 'BODEGA 55') cardId = 'cash-bodega';
        else if (op.nombre === 'DIEGO Y EMILIO') cardId = 'cash-diego';

        if (cardId) {
            const card = document.getElementById(cardId);
            const balanceEl = card.querySelector('.operator-balance');
            balanceEl.textContent = formatCurrency(op.saldo);

            // Agregar clase 'negative' si el saldo es negativo
            if (op.saldo < 0) {
                card.classList.add('negative');
            } else {
                card.classList.remove('negative');
            }
        }
    });

    // Actualizar movimientos del día
    if (data.movimientos_dia) {
        const mov = data.movimientos_dia;
        document.getElementById('mov-cobranza-contado').textContent =
            formatCurrency(mov['COBRANZA VENTAS AL CONTADO'] || 0);
        document.getElementById('mov-cobranza-credito').textContent =
            formatCurrency(mov['COBRANZA VENTAS A CRÉDITO'] || 0);
        document.getElementById('mov-gastos').textContent =
            formatCurrency(mov['GASTOS EFECTUADOS'] || 0);
        document.getElementById('mov-entre-cajas').textContent =
            formatCurrency(mov['MOVIMIENTO ENTRE CAJAS'] || 0);
    }

    // Actualizar saldo total
    const totalEl = document.getElementById('cash-total');
    const totalContainer = totalEl.parentElement;
    totalEl.textContent = formatCurrency(data.saldo_total);

    // Agregar clase 'negative' y 'deficit' si el saldo es negativo
    if (data.saldo_total < 0) {
        totalEl.classList.add('negative');
        totalContainer.classList.add('deficit');
    } else {
        totalEl.classList.remove('negative');
        totalContainer.classList.remove('deficit');
    }

    // Actualizar indicador de fecha
    if (data.fecha) {
        const fechaObj = new Date(data.fecha + 'T00:00:00');
        const fechaFormateada = fechaObj.toLocaleDateString('es-MX', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        });
        document.getElementById('cash-date-indicator').textContent = `Datos del ${fechaFormateada}`;
    }
}

async function loadTicketPromedio() {
    const data = await fetchAPI('/api/metrics/ticket-promedio');
    if (!data) return;
    
    document.getElementById('ticket-promedio').textContent = formatCurrency(data.ticket_promedio);
    document.getElementById('num-tickets').textContent = `${formatNumber(data.num_transacciones)} transacciones`;
}

async function loadTasaCobranza() {
    // Función eliminada - la card ya no existe
}

async function loadMonthlyComparison() {
    const data = await fetchAPI('/api/metrics/monthly-comparison', false);
    if (!data) return;
    
    const crecimiento = data.crecimiento_porcentaje;
    const crecimientoEl = document.getElementById('crecimiento');
    const growthCard = document.getElementById('growth-card');
    
    crecimientoEl.textContent = (crecimiento >= 0 ? '+' : '') + formatPercent(crecimiento);
    
    // Cambiar color según crecimiento
    growthCard.classList.remove('positive', 'negative');
    if (crecimiento > 0) {
        growthCard.classList.add('positive');
    } else if (crecimiento < 0) {
        growthCard.classList.add('negative');
    }
    
    document.getElementById('mes-anterior-detail').textContent = 
        `Anterior: ${formatCurrency(data.mes_anterior?.total || 0)}`;
}

async function loadReceivables() {
    const data = await fetchAPI('/api/receivables', false);
    if (!data) return;
    
    document.getElementById('por-cobrar').textContent = formatCurrency(data.total_pendiente);
    document.getElementById('num-cuentas').textContent = `${formatNumber(data.num_cuentas)} cuentas`;
    
    // Llenar tabla con días vencidos
    const tbody = document.querySelector('#table-receivables tbody');
    tbody.innerHTML = '';
    
    if (data.detalle && data.detalle.length > 0) {
        data.detalle.forEach(item => {
            const tr = document.createElement('tr');
            const diasClass = item.dias_vencidos > 30 ? 'style="color: #ef4444;"' : 
                              item.dias_vencidos > 15 ? 'style="color: #f59e0b;"' : '';
            tr.innerHTML = `
                <td>${item.cliente || '-'}</td>
                <td>${formatCurrency(item.saldo)}</td>
                <td>${item.fecha || '-'}</td>
                <td ${diasClass}>${item.dias_vencidos || 0}</td>
            `;
            tbody.appendChild(tr);
        });
    } else {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted);">Sin cuentas pendientes</td></tr>';
    }
}

// ==================== GRÁFICOS ====================
const chartColors = {
    primary: 'rgba(16, 185, 129, 0.8)',
    secondary: 'rgba(59, 130, 246, 0.8)',
    warning: 'rgba(245, 158, 11, 0.8)',
    danger: 'rgba(239, 68, 68, 0.8)',
    purple: 'rgba(139, 92, 246, 0.8)',
    info: 'rgba(6, 182, 212, 0.8)',
    orange: 'rgba(249, 115, 22, 0.8)',
    lime: 'rgba(132, 204, 22, 0.8)',
    
    primaryBg: 'rgba(16, 185, 129, 0.2)',
    secondaryBg: 'rgba(59, 130, 246, 0.2)'
};

const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: '#94a3b8',
                font: { family: 'Inter' }
            }
        }
    },
    scales: {
        x: {
            ticks: { color: '#64748b' },
            grid: { color: 'rgba(148, 163, 184, 0.1)' }
        },
        y: {
            ticks: { color: '#64748b' },
            grid: { color: 'rgba(148, 163, 184, 0.1)' }
        }
    }
};

async function loadTopProducts() {
    const data = await fetchAPI('/api/sales/top-products?limit=5');
    if (!data || !data.data) return;
    
    const tbody = document.querySelector('#table-top-products tbody');
    tbody.innerHTML = '';
    
    data.data.forEach((item, index) => {
        const tr = document.createElement('tr');
        
        // Determinar si mostrar kg o cajas
        const cantidad = item.kg_netos > 0 
            ? `${formatNumber(item.kg_netos)} kg` 
            : `${formatNumber(item.cajas)} cajas`;
        
        tr.innerHTML = `
            <td>${index + 1}</td>
            <td>${item.producto || '-'}</td>
            <td>${formatCurrency(item.total)}</td>
            <td>${cantidad}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function loadSalesByProduct() {
    const data = await fetchAPI('/api/sales/by-product');
    if (!data || !data.data) return;
    
    const ctx = document.getElementById('chart-by-product');
    
    if (charts.byProduct) charts.byProduct.destroy();
    
    const colors = [
        chartColors.primary,
        chartColors.secondary,
        chartColors.warning,
        chartColors.purple,
        chartColors.danger,
        chartColors.info
    ];
    
    charts.byProduct = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.data.map(d => d.producto || 'Otro'),
            datasets: [{
                label: 'Ventas',
                data: data.data.map(d => d.total),
                backgroundColor: colors.slice(0, data.data.length),
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            ...chartDefaults,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => formatCurrency(ctx.raw)
                    }
                }
            }
        }
    });
}

async function loadTicketDistribution() {
    const data = await fetchAPI('/api/sales/ticket-distribution');
    if (!data || !data.data) return;
    
    // Usamos el ID nuevo
    const ctx = document.getElementById('chart-ticket-distribution');
    // Fallback por si no se actualizó el HTML
    const ctxFallback = document.getElementById('chart-by-payment');
    const finalCtx = ctx || ctxFallback;
    
    if (!finalCtx) return;
    
    if (charts.ticketDist) charts.ticketDist.destroy();
    if (charts.byPayment) charts.byPayment.destroy();
    if (charts.byOperator) charts.byOperator.destroy();
    
    const colors = [
        chartColors.primary,
        chartColors.secondary,
        chartColors.warning,
        chartColors.purple
    ];
    
    charts.ticketDist = new Chart(finalCtx, {
        type: 'bar',
        data: {
            labels: data.data.map(d => d.rango),
            datasets: [{
                label: 'Cantidad de Ventas',
                data: data.data.map(d => d.cantidad),
                backgroundColor: colors,
                borderRadius: 8,
                barPercentage: 0.6
                // Si quisieras mostrar el monto total en tooltip, se puede configurar
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => {
                            const item = data.data[ctx.dataIndex];
                            return `Ventas: ${item.cantidad} (${formatCurrency(item.total)})`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#f1f5f9' },
                    ticks: { font: { family: 'Inter' } }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { family: 'Inter' } }
                }
            }
        }
    });
}

async function loadSalesTrend() {
    const data = await fetchAPI('/api/sales/trend');
    if (!data) return;
    
    const ctx = document.getElementById('chart-trend');
    
    if (charts.trend) charts.trend.destroy();
    
    // Formatear etiquetas de fecha
    const labels = data.labels.map(d => {
        const date = new Date(d + 'T00:00:00');
        return date.toLocaleDateString('es-MX', { day: '2-digit', month: 'short' });
    });
    
    charts.trend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventas del día',
                data: data.values,
                borderColor: chartColors.primary,
                backgroundColor: chartColors.primaryBg,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: chartColors.primary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => formatCurrency(ctx.raw)
                    }
                }
            },
            scales: {
                x: {
                    ticks: { 
                        color: '#64748b',
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: { display: false }
                },
                y: {
                    ticks: { 
                        color: '#64748b',
                        callback: (value) => formatCurrency(value)
                    },
                    grid: { color: 'rgba(148, 163, 184, 0.1)' },
                    beginAtZero: true
                }
            }
        }
    });
}

async function loadSalesByWeekday() {
    const data = await fetchAPI('/api/sales/by-weekday');
    if (!data) return;
    
    const ctx = document.getElementById('chart-by-weekday');
    
    if (charts.byWeekday) charts.byWeekday.destroy();
    
    const colors = [
        chartColors.secondary, // Lunes
        chartColors.info,      // Martes
        chartColors.primary,   // Miércoles
        chartColors.warning,   // Jueves
        chartColors.purple,    // Viernes
        chartColors.orange,    // Sábado
        chartColors.danger     // Domingo
    ];
    
    charts.byWeekday = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Ventas Totales Acumuladas',
                data: data.values,
                backgroundColor: colors,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            ...chartDefaults,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => formatCurrency(ctx.raw)
                    }
                }
            }
        }
    });
}

async function loadPurchases() {
    const data = await fetchAPI('/api/purchases');
    if (!data || !data.data) return;
    
    const ctx = document.getElementById('chart-purchases');
    
    if (charts.purchases) charts.purchases.destroy();
    
    charts.purchases = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.data.map(d => d.producto),
            datasets: [{
                data: data.data.map(d => d.total),
                backgroundColor: [chartColors.lime, chartColors.warning],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        font: { family: 'Inter' },
                        padding: 20
                    }
                },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.label}: ${formatCurrency(ctx.raw)}`
                    }
                }
            }
        }
    });
}

async function loadExpenses() {
    const data = await fetchAPI('/api/expenses');
    if (!data || !data.por_tipo) return;
    
    const ctx = document.getElementById('chart-expenses');
    
    if (charts.expenses) charts.expenses.destroy();
    
    const colors = [
        chartColors.orange,
        chartColors.danger,
        chartColors.warning,
        chartColors.purple,
        chartColors.secondary,
        chartColors.info
    ];
    
    charts.expenses = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.por_tipo.map(d => d.tipo || 'Otros'),
            datasets: [{
                data: data.por_tipo.map(d => d.total),
                backgroundColor: colors.slice(0, data.por_tipo.length),
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#94a3b8',
                        font: { family: 'Inter', size: 10 },
                        padding: 10
                    }
                },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `${ctx.label}: ${formatCurrency(ctx.raw)}`
                    }
                }
            }
        }
    });
}

async function loadTopClients() {
    const response = await fetch(`${API_BASE}/api/sales/top-clients?limit=10${currentFilters.startDate ? '&start_date=' + currentFilters.startDate : ''}${currentFilters.endDate ? '&end_date=' + currentFilters.endDate : ''}`);
    const data = await response.json();
    
    if (!data || !data.data) return;
    
    const tbody = document.querySelector('#table-clients tbody');
    tbody.innerHTML = '';
    
    data.data.forEach((item, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${index + 1}</td>
            <td>${item.cliente || '-'}</td>
            <td>${formatCurrency(item.total)}</td>
            <td>${formatNumber(item.compras)}</td>
        `;
        tbody.appendChild(tr);
    });
}
