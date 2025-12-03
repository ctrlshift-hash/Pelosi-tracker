const API_BASE = '/api';

let performanceChart = null;
let holdingsChart = null;

async function fetchPortfolioData() {
    try {
        const response = await fetch(`${API_BASE}/portfolio`);
        if (!response.ok) {
            throw new Error('Failed to fetch portfolio data');
        }
        const data = await response.json();
        updateProfileUI(data);
    } catch (error) {
        console.error('Error fetching portfolio data:', error);
    }
}

function updateProfileUI(data) {
    // Update total value
    if (data.performance && data.performance.total_invested) {
        const invested = data.performance.total_invested;
        const displayValue = `US$${invested.toLocaleString()}`;
        document.getElementById('total-value-display').textContent = displayValue;
        document.getElementById('portfolio-value-center').textContent = `$${(invested / 1000000).toFixed(1)}M`;
    }

    // Update performance badge
    if (data.performance && data.performance.performance_percent !== undefined) {
        const perf = data.performance.performance_percent;
        const perfEl = document.getElementById('performance-badge');
        if (perfEl) {
            perfEl.textContent = `↑ ${perf.toFixed(1)}%`;
            perfEl.classList.toggle('positive', perf >= 0);
            perfEl.classList.toggle('negative', perf < 0);
        }
    }

    // Update holdings list and chart
    if (data.holdings && data.holdings.length > 0) {
        updateHoldingsList(data.holdings);
        updateHoldingsChart(data.holdings);
    }

    // Update recent trades
    if (data.recent_trades && data.recent_trades.length > 0) {
        updateRecentTrades(data.recent_trades);
    }

    // Update sector allocation (mock for now)
    updateSectorAllocation();
}

function updateHoldingsList(holdings) {
    const listEl = document.getElementById('holdings-list');
    if (!listEl) return;

    // Sort by weight descending
    const sorted = [...holdings].sort((a, b) => (b.weight || 0) - (a.weight || 0));
    
    listEl.innerHTML = sorted.slice(0, 5).map(holding => {
        const value = holding.last_price * (holding.weight || 0) / 100 * 1000000; // Rough estimate
        return `
            <div class="holding-item">
                <div class="holding-ticker"><a href="/stock/${holding.ticker}" style="color: inherit; text-decoration: none; font-weight: 700;">${holding.ticker}</a></div>
                <div class="holding-name">${getCompanyName(holding.ticker)}</div>
                <div class="holding-weight">${holding.weight_display || `${holding.weight.toFixed(1)}%`}</div>
                <div class="holding-value">$${(value / 1000000).toFixed(1)}M</div>
            </div>
        `;
    }).join('');
}

function getCompanyName(ticker) {
    const names = {
        'NVDA': 'NVIDIA Corporation',
        'GOOGL': 'Alphabet Inc.',
        'AVGO': 'Broadcom Inc.',
        'PANW': 'Palo Alto Networks',
        'TEM': 'Tempus AI, Inc.',
        'VST': 'Vistra Corp.',
        'AMZN': 'Amazon.com, Inc.',
        'CRWD': 'CrowdStrike Holdings',
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'TSLA': 'Tesla, Inc.'
    };
    return names[ticker] || ticker;
}

function updateHoldingsChart(holdings) {
    const ctx = document.getElementById('holdingsChart');
    if (!ctx) return;

    const sorted = [...holdings].sort((a, b) => (b.weight || 0) - (a.weight || 0));
    const top5 = sorted.slice(0, 5);
    const others = sorted.slice(5).reduce((sum, h) => sum + (h.weight || 0), 0);

    const labels = [...top5.map(h => h.ticker), 'OTHER'];
    const data = [...top5.map(h => h.weight || 0), others];
    const colors = [
        '#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444', '#6b7280'
    ];

    if (holdingsChart) {
        holdingsChart.destroy();
    }

    holdingsChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 0
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
                            return `${context.label}: ${context.parsed.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

function updateRecentTrades(trades) {
    const tbody = document.getElementById('recent-trades-body');
    if (!tbody) return;

    // Show ALL trades, not just 10
    tbody.innerHTML = trades.map(trade => {
        const date = trade.date || trade.traded_date || trade.filed_date || 'N/A';
        const amount = trade.amount || '$0';
        const isPurchase = trade.action === 'Purchase';
        const amountClass = isPurchase ? 'positive' : 'negative';
        const amountPrefix = isPurchase ? '+' : '-';
        
        return `
            <tr>
                <td>${date}</td>
                <td><a href="/stock/${trade.ticker}" style="color: #10b981; text-decoration: none; font-weight: 600;">${trade.ticker || 'N/A'}</a></td>
                <td class="${amountClass}">${amountPrefix}${amount}</td>
            </tr>
        `;
    }).join('');
    
    console.log(`Displayed ${trades.length} total trades`);
}

function updateSectorAllocation() {
    // Get REAL sector data from API
    fetch(`${API_BASE}/portfolio`)
        .then(response => response.json())
        .then(data => {
            const sectors = data.sector_allocation || [];
            const listEl = document.getElementById('sector-list');
            if (!listEl) return;

            if (sectors.length === 0) {
                listEl.innerHTML = '<div class="loading">No sector data available</div>';
                return;
            }

            listEl.innerHTML = sectors.map(sector => `
                <div class="sector-item">
                    <div class="sector-name">${sector.name}</div>
                    <div class="sector-bar-container">
                        <div class="sector-bar" style="width: ${sector.percentage}%"></div>
                    </div>
                    <div class="sector-percentage">${sector.percentage}%</div>
                </div>
            `).join('');
        })
        .catch(error => {
            console.error('Error fetching sector data:', error);
            const listEl = document.getElementById('sector-list');
            if (listEl) {
                listEl.innerHTML = '<div class="loading">Error loading sector data</div>';
            }
        });
}

let fullHistoricalData = [];

function initPerformanceChart() {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;

    // Get REAL historical data from API
    fetch(`${API_BASE}/portfolio`)
        .then(response => response.json())
        .then(data => {
            fullHistoricalData = data.historical_performance || [];
            
            if (fullHistoricalData.length === 0) {
                createChart([], []);
                return;
            }

            // Default to showing all data (All button is active)
            filterAndDisplayChart('All');
        })
        .catch(error => {
            console.error('Error fetching historical data:', error);
            createChart([], []);
        });
}

function filterAndDisplayChart(period) {
    if (fullHistoricalData.length === 0) {
        createChart([], []);
        return;
    }
    
    console.log(`Filtering chart for period: ${period}`);
    console.log(`Total data points: ${fullHistoricalData.length}`);
    
    let filteredData = fullHistoricalData;
    const now = new Date();
    
    // Filter data based on selected period
    // Get the LATEST date in our data (Jan 2025), not current date
    const latestDataDate = new Date(fullHistoricalData[fullHistoricalData.length - 1].date + '-01');
    console.log(`Latest data date: ${latestDataDate.toLocaleDateString()}`);
    
    if (period === '1M') {
        // Show last 2 months of data (need at least 2 points for a line chart)
        filteredData = fullHistoricalData.slice(-2);
        console.log(`1M filter: ${filteredData.length} data points (last 2 months)`);
    } else if (period === '3M') {
        // Show last 3 months of data
        filteredData = fullHistoricalData.slice(-3);
        console.log(`3M filter: ${filteredData.length} data points (last 3 months)`);
    } else if (period === '6M') {
        // Show last 6 months of data
        filteredData = fullHistoricalData.slice(-6);
        console.log(`6M filter: ${filteredData.length} data points (last 6 months)`);
    } else if (period === '1Y') {
        // Show last 12 months of data
        filteredData = fullHistoricalData.slice(-12);
        console.log(`1Y filter: ${filteredData.length} data points (last 12 months)`);
    } else if (period === 'All') {
        filteredData = fullHistoricalData;
        console.log(`All filter: ${filteredData.length} data points (all data)`);
    }
    
    const labels = filteredData.map(h => {
        const date = new Date(h.date + '-01');
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    });
    const chartData = filteredData.map(h => h.value || 0);
    
    console.log(`Creating chart with ${labels.length} labels`);
    createChart(labels, chartData);
}

function createChart(labels, data) {
        const ctx = document.getElementById('performanceChart');
        if (!ctx) return;
        
        if (performanceChart) {
            performanceChart.destroy();
        }

        performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Portfolio Value',
                    data: data,
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
                                return `US$${context.parsed.y.toLocaleString()}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + (value / 1000000).toFixed(0) + 'M';
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

// Time range selector
document.addEventListener('DOMContentLoaded', function() {
    fetchPortfolioData();
    updateSectorAllocation();
    initPerformanceChart();

    // Time range buttons - these are the 1M, 3M, 6M, 1Y, All buttons
    const timeBtns = document.querySelectorAll('.time-btn');
    timeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            timeBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            // Filter and update chart based on button text
            const period = this.textContent.trim();
            console.log(`Button clicked: ${period}`);
            filterAndDisplayChart(period);
        });
    });
    
    // REMOVED DUPLICATE - time-btn event listeners are already set above
});

