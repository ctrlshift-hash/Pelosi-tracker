const API_BASE = '/api';

// Get ticker from URL path, not window variable
function getTickerFromURL() {
    const path = window.location.pathname;
    const match = path.match(/\/stock\/([A-Z]+)/i);
    return match ? match[1].toUpperCase() : null;
}

const TICKER = getTickerFromURL();

let priceChart = null;

async function fetchStockData() {
    const ticker = getTickerFromURL();
    if (!ticker) {
        console.error('No ticker found in URL');
        return;
    }
    
    console.log(`Fetching stock data for ${ticker}`);
    
    try {
        const response = await fetch(`${API_BASE}/stock/${ticker}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch stock data for ${ticker}`);
        }
        const data = await response.json();
        
        // VERIFY the data is for the correct ticker
        if (data.ticker && data.ticker.toUpperCase() !== ticker.toUpperCase()) {
            console.error(`TICKER MISMATCH! Requested ${ticker} but got ${data.ticker}`);
            throw new Error(`Data mismatch: expected ${ticker} but got ${data.ticker}`);
        }
        
        console.log(`Received data for ${data.ticker || ticker}:`, data);
        updateStockUI(data, ticker);
    } catch (error) {
        console.error(`Error fetching stock data for ${ticker}:`, error);
        const tbody = document.getElementById('trades-table-body');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">Error loading trading activity. Please refresh the page.</td></tr>';
        }
    }
}

function updateStockUI(data, ticker) {
    const actualTicker = ticker || data.ticker || TICKER;
    
    console.log(`Updating UI for ticker: ${actualTicker}`, data);
    
    // Update header
    if (data.company_name) {
        document.getElementById('stock-name').textContent = data.company_name;
        document.getElementById('company-name').textContent = data.company_name;
        document.title = `${data.company_name} (${actualTicker}) - Stock Details | Pelosi Tracker`;
    }
    
    if (data.exchange) {
        document.getElementById('stock-exchange').textContent = data.exchange;
    }
    
    // Update price info
    if (data.current_price !== undefined) {
        document.getElementById('current-price').textContent = `$${data.current_price.toFixed(2)}`;
    }
    
    if (data.price_change !== undefined && data.price_change_percent !== undefined) {
        const changeEl = document.getElementById('price-change');
        const isPositive = data.price_change >= 0;
        changeEl.textContent = `${isPositive ? '+' : ''}${data.price_change.toFixed(2)} (${isPositive ? '+' : ''}${data.price_change_percent.toFixed(2)}%)`;
        changeEl.className = `metric-value ${isPositive ? 'positive' : 'negative'}`;
    }
    
    if (data.week_range_low !== undefined && data.week_range_high !== undefined) {
        document.getElementById('week-range').textContent = `$${data.week_range_low.toFixed(2)} - $${data.week_range_high.toFixed(2)}`;
    }
    
    // Update status
    if (data.status) {
        const statusEl = document.getElementById('stock-status');
        statusEl.textContent = data.status;
        statusEl.className = `stock-status ${data.status.toLowerCase().includes('up') ? 'positive' : 'negative'}`;
    }
    
    // Update description
    if (data.description) {
        document.getElementById('company-description').textContent = data.description;
    }
    
    // Update trades table
    const tbody = document.getElementById('trades-table-body');
    if (data.trades && Array.isArray(data.trades)) {
        console.log(`Received ${data.trades.length} trades for ${actualTicker}`, data.trades);
        
        if (data.trades.length > 0) {
            updateTradesTable(data.trades);
            
            document.getElementById('transaction-count').textContent = `${data.trades.length} transactions`;
            
            // Calculate compliance rate
            const compliant = data.trades.filter(t => !t.non_compliant).length;
            const complianceRate = data.trades.length > 0 ? ((compliant / data.trades.length) * 100).toFixed(0) : 100;
            document.getElementById('compliance-rate').textContent = `Compliance: ${complianceRate}%`;
        } else {
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="7" class="loading">No Nancy Pelosi trades found for this stock</td></tr>';
            }
            document.getElementById('transaction-count').textContent = '0 transactions';
            document.getElementById('compliance-rate').textContent = 'Compliance: 100%';
        }
    } else {
        console.warn('No trades data received or invalid format:', data.trades);
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">No trading data available</td></tr>';
        }
        document.getElementById('transaction-count').textContent = '0 transactions';
    }
    
    // Update similar stocks
    if (data.similar_stocks && data.similar_stocks.length > 0) {
        updateSimilarStocks(data.similar_stocks);
    }
    
    // Update price chart
    if (data.price_history && data.price_history.length > 0) {
        updatePriceChart(data.price_history);
    }
}

function updateTradesTable(trades) {
    const tbody = document.getElementById('trades-table-body');
    if (!tbody) return;
    
    // All trades are Nancy Pelosi's trades (no need to filter)
    if (trades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="loading">No Nancy Pelosi trades found for this stock</td></tr>';
        return;
    }
    
    tbody.innerHTML = trades.map(trade => {
        const excessReturn = trade.excess_return || 'N/A';
        const excessClass = excessReturn === 'N/A' || excessReturn.includes('N/A') ? '' : (parseFloat(excessReturn.replace('%', '').replace('+', '').replace('-', '')) >= 0 ? 'positive' : 'negative');
        const actionClass = (trade.action || '').toLowerCase() === 'purchase' ? 'purchase' : (trade.action || '').toLowerCase() === 'sale' ? 'sale' : '';
        
        return `
            <tr>
                <td>Nancy Pelosi</td>
                <td>${trade.traded_date || trade.date || 'N/A'}</td>
                <td>${trade.filed_date || 'N/A'}</td>
                <td><span class="action-badge ${actionClass}">${trade.action || 'Trade'}</span></td>
                <td>${trade.type || 'Stock'}</td>
                <td>${trade.amount || 'N/A'}</td>
                <td class="${excessClass}">${excessReturn}</td>
            </tr>
        `;
    }).join('');
}

function updateSimilarStocks(stocks) {
    const listEl = document.getElementById('similar-stocks-list');
    if (!listEl) return;
    
    listEl.innerHTML = stocks.map(stock => {
        const changeClass = (stock.change || 0) >= 0 ? 'positive' : 'negative';
        return `
            <div class="similar-stock-item">
                <div class="similar-stock-header">
                    <a href="/stock/${stock.ticker}" class="similar-stock-ticker">${stock.ticker}</a>
                    <span class="similar-stock-name">${stock.name}</span>
                </div>
                <div class="similar-stock-price">$${stock.price.toFixed(2)}</div>
                <div class="similar-stock-change ${changeClass}">${stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)} (${stock.change_percent >= 0 ? '+' : ''}${stock.change_percent.toFixed(2)}%)</div>
                <div class="similar-stock-reason">${stock.reason || ''}</div>
                <a href="/stock/${stock.ticker}" class="view-stock-link">View Stock →</a>
            </div>
        `;
    }).join('');
}

function updatePriceChart(priceHistory) {
    const ctx = document.getElementById('priceChart');
    if (!ctx) return;
    
    const labels = priceHistory.map(h => {
        const date = new Date(h.date || h.timestamp);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    const prices = priceHistory.map(h => h.price || h.value || 0);
    
    if (priceChart) {
        priceChart.destroy();
    }
    
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Price',
                data: prices,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `$${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Chart type toggle
document.addEventListener('DOMContentLoaded', function() {
    const ticker = getTickerFromURL();
    console.log(`Page loaded for ticker: ${ticker}`);
    
    if (!ticker) {
        console.error('No ticker in URL!');
        return;
    }
    
    fetchStockData();
    
    const chartBtns = document.querySelectorAll('.chart-btn');
    chartBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            chartBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            // In real implementation, would switch between price and volume charts
        });
    });
    
    // Zoom buttons
    const zoomBtns = document.querySelectorAll('.zoom-btn');
    zoomBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            zoomBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            // Reload chart with filtered date range
            fetchStockData();
        });
    });
    
});

// Hide loading screen function
function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.classList.add('hidden');
        setTimeout(function() {
            loadingScreen.style.display = 'none';
        }, 500);
    }
}

// Hide loading screen after page loads (minimum 3 seconds)
const minLoadTime = 3000; // 3 seconds
const startTime = Date.now();

function checkAndHideLoading() {
    const elapsed = Date.now() - startTime;
    const remaining = Math.max(0, minLoadTime - elapsed);
    setTimeout(hideLoadingScreen, remaining);
}

if (document.readyState === 'complete') {
    checkAndHideLoading();
} else {
    window.addEventListener('load', checkAndHideLoading);
}

