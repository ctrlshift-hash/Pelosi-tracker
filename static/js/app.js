const API_BASE = '/api';

async function fetchPortfolioData() {
    try {
        const response = await fetch(`${API_BASE}/portfolio`);
        if (!response.ok) {
            throw new Error('Failed to fetch portfolio data');
        }
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        console.error('Error fetching portfolio data:', error);
    }
}

function updateUI(data) {
    console.log('Updating UI with data:', data);
    
    // Update hero stats (new design)
    const copiersEl = document.getElementById('copiers-stat');
    if (copiersEl && data.stats && data.stats.copiers) {
        copiersEl.textContent = data.stats.copiers.toLocaleString();
    }
    
    const investedEl = document.getElementById('invested-stat');
    if (investedEl && data.performance && data.performance.total_invested !== undefined) {
        const invested = data.performance.total_invested;
        investedEl.textContent = `$${invested.toLocaleString()}`;
    }

    // Update profile stats (new design)
    const totalValEl = document.getElementById('total-value');
    if (totalValEl && data.performance && data.performance.total_invested !== undefined) {
        const invested = data.performance.total_invested;
        totalValEl.textContent = `$${(invested / 1000000).toFixed(2)}M`;
    }

    const holdingsValEl = document.getElementById('holdings-value');
    if (holdingsValEl && data.stats && data.stats.holdings_count !== undefined) {
        holdingsValEl.textContent = data.stats.holdings_count;
    }

    // Update performance
    if (data.performance && data.performance.performance_percent !== undefined) {
        const perf = data.performance.performance_percent;
        
        const perfElement = document.getElementById('performance-value');
        if (perfElement) {
            perfElement.textContent = `${perf >= 0 ? '+' : ''}${perf.toFixed(1)}%`;
            perfElement.classList.remove('negative', 'positive');
            perfElement.classList.add(perf >= 0 ? 'positive' : 'negative');
        }
        
        // Also update old element IDs if they exist
        const oldPerfEl = document.getElementById('performance');
        if (oldPerfEl) {
            oldPerfEl.textContent = `${perf >= 0 ? '+' : ''}${perf.toFixed(1)}%`;
            oldPerfEl.classList.remove('negative');
            if (perf < 0) oldPerfEl.classList.add('negative');
        }
    }

    // Update old total-invested if it exists
    const oldInvestedEl = document.getElementById('total-invested');
    if (oldInvestedEl && data.performance && data.performance.total_invested !== undefined) {
        const invested = data.performance.total_invested;
        let display = `$${invested.toLocaleString()}`;
        if (invested >= 1000000) {
            display = `$${(invested / 1000000).toFixed(2)}M`;
        }
        oldInvestedEl.textContent = display;
    }

    // Update old holdings-count if it exists
    const oldHoldingsEl = document.getElementById('holdings-count');
    if (oldHoldingsEl && data.stats && data.stats.holdings_count !== undefined) {
        oldHoldingsEl.textContent = data.stats.holdings_count;
    }

    // Update timestamp
    if (data.last_updated) {
        const date = new Date(data.last_updated);
        
        const updatedEl = document.getElementById('updated-value');
        if (updatedEl) {
            updatedEl.textContent = 'Today';
        }
        
        const footerUpdated = document.getElementById('footer-updated');
        if (footerUpdated) {
            footerUpdated.textContent = date.toLocaleString();
        }
        
        const lastUpdated = document.getElementById('last-updated');
        if (lastUpdated) {
            lastUpdated.textContent = date.toLocaleString();
        }
    }

    // Store holdings for filtering
    if (data.holdings && data.holdings.length > 0) {
        window.allHoldings = data.holdings;
        
        const tbody = document.getElementById('holdings-body');
        if (tbody) {
            // Show skeleton loader while processing
            if (tbody.querySelector('.loading')) {
                tbody.innerHTML = createSkeletonLoader('table-row', data.holdings.length);
            }
            
            // Small delay for skeleton effect
            setTimeout(() => {
            tbody.innerHTML = '';
            
            data.holdings.forEach(holding => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td class="ticker"><a href="/stock/${holding.ticker}" style="color: inherit; text-decoration: none; font-weight: 700;">${holding.ticker}</a></td>
                    <td class="price">${holding.price_display || `$${holding.last_price.toFixed(2)}`}</td>
                    <td class="weight">${holding.weight_display || `${holding.weight.toFixed(1)}%`}</td>
                `;
                tbody.appendChild(row);
            });
                
                // Apply initial sort (weight desc by default)
                if (typeof window.filterHoldings === 'function') {
                    window.filterHoldings('', 'weight-desc');
                }
            }, 300);
        }
    }

    // Store trades for filtering
    if (data.recent_trades && data.recent_trades.length > 0) {
        const oldTrades = window.allTrades || [];
        window.allTrades = data.recent_trades;
        
        const tradesContainer = document.getElementById('trades-container');
        if (tradesContainer) {
            // Show skeleton loader
            if (tradesContainer.querySelector('.loading')) {
                tradesContainer.innerHTML = createSkeletonLoader('card', Math.min(6, data.recent_trades.length));
            }
            
            // Small delay for skeleton effect
            setTimeout(() => {
                // Check for new trades and show notifications
                if (oldTrades.length > 0 && typeof checkForNewTrades === 'function') {
                    checkForNewTrades(oldTrades, data.recent_trades);
                }
                
                // Apply initial filter
                if (typeof window.filterTrades === 'function') {
                    window.filterTrades('', 'all');
                } else {
                    // Fallback to original rendering
                    tradesContainer.innerHTML = '';
            data.recent_trades.forEach(trade => {
                const tradeCard = document.createElement('div');
                tradeCard.className = 'trade-card';
                
                const actionClass = trade.action === 'Purchase' ? 'purchase' : trade.action === 'Sale' ? 'sale' : '';
                const actionBadge = trade.action ? `<span class="action-badge ${actionClass}">${trade.action}</span>` : '';
                const dateInfo = trade.date || trade.traded_date || '';
                const amountInfo = trade.amount || '';
                        const insight = typeof getTradeInsight === 'function' ? getTradeInsight(trade) : '';
                
                tradeCard.innerHTML = `
                    <div class="trade-header">
                        <span class="trade-ticker">${trade.ticker || 'N/A'}</span>
                        ${actionBadge}
                    </div>
                            ${insight ? `<div class="trade-insight">${insight}</div>` : ''}
                    <div class="trade-details">
                        ${dateInfo ? `<div>Date: ${dateInfo}</div>` : ''}
                        ${amountInfo ? `<div>Amount: ${amountInfo}</div>` : ''}
                    </div>
                `;
                tradesContainer.appendChild(tradeCard);
            });
        }
                
                // Update icons
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            }, 300);
        }
    }
    
    // Update last update time
    if (typeof setUpdateTime === 'function') {
        setUpdateTime();
    }
}

// Load data when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fetchPortfolioData);
} else {
    fetchPortfolioData();
}

// Auto-refresh every 5 minutes
setInterval(() => {
    fetchPortfolioData();
    if (typeof setUpdateTime === 'function') {
        setUpdateTime();
    }
}, 5 * 60 * 1000);

// Helper function for skeleton loaders (if not in enhancements.js)
if (typeof createSkeletonLoader === 'undefined') {
    window.createSkeletonLoader = function(type, count = 3) {
        if (type === 'table-row') {
            return Array(count).fill(0).map(() => `
                <tr class="skeleton-row">
                    <td><div class="skeleton skeleton-text" style="width: 60px;"></div></td>
                    <td><div class="skeleton skeleton-text" style="width: 80px;"></div></td>
                    <td><div class="skeleton skeleton-text" style="width: 50px;"></div></td>
                </tr>
            `).join('');
        } else if (type === 'card') {
            return Array(count).fill(0).map(() => `
                <div class="trade-card skeleton-card">
                    <div class="skeleton skeleton-text" style="width: 60%; height: 24px; margin-bottom: 12px;"></div>
                    <div class="skeleton skeleton-text" style="width: 40%; height: 20px; margin-bottom: 8px;"></div>
                    <div class="skeleton skeleton-text" style="width: 80%; height: 16px;"></div>
                </div>
            `).join('');
        }
        return '';
    };
}
