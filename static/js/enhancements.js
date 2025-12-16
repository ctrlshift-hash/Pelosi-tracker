// Enhanced features for Pelosi Tracker
// Icons, Search, Filter, Export, Notifications, etc.

// Initialize Lucide icons
document.addEventListener('DOMContentLoaded', function() {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});

// Skeleton Loader Functions
function createSkeletonLoader(type, count = 3) {
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
}

// Search and Filter Functions
window.allHoldings = window.allHoldings || [];
window.allTrades = window.allTrades || [];

function initSearchAndFilter() {
    const holdingsSearch = document.getElementById('holdings-search');
    const tradesSearch = document.getElementById('trades-search');
    const holdingsFilter = document.getElementById('holdings-filter');
    const tradesFilter = document.getElementById('trades-filter');
    
    if (holdingsSearch) {
        holdingsSearch.addEventListener('input', (e) => {
            filterHoldings(e.target.value, holdingsFilter?.value || 'weight-desc');
        });
    }
    
    if (holdingsFilter) {
        holdingsFilter.addEventListener('change', (e) => {
            filterHoldings(holdingsSearch?.value || '', e.target.value);
        });
    }
    
    if (tradesSearch) {
        tradesSearch.addEventListener('input', (e) => {
            filterTrades(e.target.value, tradesFilter?.value || 'all');
        });
    }
    
    if (tradesFilter) {
        tradesFilter.addEventListener('change', (e) => {
            filterTrades(tradesSearch?.value || '', e.target.value);
        });
    }
}

window.filterHoldings = function(searchTerm, filterBy) {
    const tbody = document.getElementById('holdings-body');
    if (!tbody) return;
    
    const holdings = window.allHoldings || [];
    if (!holdings.length) return;
    
    let filtered = [...holdings];
    
    // Search filter
    if (searchTerm) {
        filtered = filtered.filter(h => 
            h.ticker.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }
    
    // Sort filter
    if (filterBy === 'weight-desc') {
        filtered.sort((a, b) => (b.weight || 0) - (a.weight || 0));
    } else if (filterBy === 'weight-asc') {
        filtered.sort((a, b) => (a.weight || 0) - (b.weight || 0));
    } else if (filterBy === 'ticker-asc') {
        filtered.sort((a, b) => a.ticker.localeCompare(b.ticker));
    }
    
    tbody.innerHTML = filtered.map(holding => `
        <tr>
            <td class="ticker"><a href="/stock/${holding.ticker}" style="color: inherit; text-decoration: none; font-weight: 700;">${holding.ticker}</a></td>
            <td class="price">${holding.price_display || `$${holding.last_price.toFixed(2)}`}</td>
            <td class="weight">${holding.weight_display || `${holding.weight.toFixed(1)}%`}</td>
        </tr>
    `).join('');
}

window.filterTrades = function(searchTerm, filterBy) {
    const container = document.getElementById('trades-container');
    if (!container) return;
    
    const trades = window.allTrades || [];
    if (!trades.length) return;
    
    let filtered = [...trades];
    
    // Search filter
    if (searchTerm) {
        filtered = filtered.filter(t => 
            t.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (t.action && t.action.toLowerCase().includes(searchTerm.toLowerCase()))
        );
    }
    
    // Action filter
    if (filterBy && filterBy !== 'all') {
        filtered = filtered.filter(t => t.action === filterBy);
    }
    
    // Sort by date (newest first)
    filtered.sort((a, b) => {
        const dateA = new Date(a.date || a.traded_date || 0);
        const dateB = new Date(b.date || b.traded_date || 0);
        return dateB - dateA;
    });
    
    container.innerHTML = filtered.map(trade => {
        const actionClass = trade.action === 'Purchase' ? 'purchase' : trade.action === 'Sale' ? 'sale' : '';
        const actionBadge = trade.action ? `<span class="action-badge ${actionClass}">${trade.action}</span>` : '';
        const dateInfo = trade.date || trade.traded_date || '';
        const amountInfo = trade.amount || '';
        const insight = getTradeInsight(trade);
        
        return `
            <div class="trade-card">
                <div class="trade-header">
                    <span class="trade-ticker">${trade.ticker || 'N/A'}</span>
                    ${actionBadge}
                </div>
                ${insight ? `<div class="trade-insight">${insight}</div>` : ''}
                <div class="trade-details">
                    ${dateInfo ? `<div>Date: ${dateInfo}</div>` : ''}
                    ${amountInfo ? `<div>Amount: ${amountInfo}</div>` : ''}
                    ${trade.type ? `<div>Type: ${trade.type}</div>` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// Trade Insights
window.getTradeInsight = function(trade) {
    if (!trade) return '';
    
    const insights = {
        'NVDA': {
            'Purchase': 'Major AI chip bet - NVDA is 19% of portfolio. Strong conviction on AI infrastructure growth.',
            'Sale': 'Taking profits after significant gains. NVDA has been a top performer.'
        },
        'GOOGL': {
            'Purchase': 'Big Tech play - Google is 17% of portfolio. Betting on AI integration and ad recovery.',
            'Sale': 'Profit-taking on Google position.'
        },
        'AAPL': {
            'Purchase': 'Tech giant addition - Apple is a core holding with steady growth.',
            'Sale': 'Large sale of 31,600 shares - possibly rebalancing or taking profits.'
        }
    };
    
    const tickerInsights = insights[trade.ticker];
    if (tickerInsights && trade.action) {
        return tickerInsights[trade.action] || '';
    }
    
    // Generic insights
    if (trade.amount && trade.amount.includes('$5,000,001')) {
        return '💎 Large position - High conviction trade';
    }
    if (trade.type && trade.type.includes('Call Options')) {
        return '📈 Options play - Leveraged bet on upside';
    }
    
    return '';
}

// Export Functions
function exportToCSV(data, filename) {
    if (!data || data.length === 0) {
        alert('No data to export');
        return;
    }
    
    const headers = Object.keys(data[0]);
    const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => {
            const value = row[header] || '';
            return `"${String(value).replace(/"/g, '""')}"`;
        }).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

window.exportHoldings = function() {
    const holdings = window.allHoldings || [];
    if (!holdings.length) {
        alert('No holdings data available');
        return;
    }
    
    const exportData = holdings.map(h => ({
        Ticker: h.ticker,
        'Last Price': h.last_price,
        'Price Display': h.price_display,
        Weight: h.weight,
        'Weight Display': h.weight_display
    }));
    
    exportToCSV(exportData, `pelosi-holdings-${new Date().toISOString().split('T')[0]}.csv`);
}

window.exportTrades = function() {
    const trades = window.allTrades || [];
    if (!trades.length) {
        alert('No trades data available');
        return;
    }
    
    const exportData = trades.map(t => ({
        Date: t.date || t.traded_date || '',
        Ticker: t.ticker || '',
        Action: t.action || '',
        Amount: t.amount || '',
        Type: t.type || '',
        'Filed Date': t.filed_date || ''
    }));
    
    exportToCSV(exportData, `pelosi-trades-${new Date().toISOString().split('T')[0]}.csv`);
}

// Real-time Update Indicator
let lastUpdateTime = null;

function updateLastUpdateTime() {
    const indicators = document.querySelectorAll('.last-updated-indicator');
    indicators.forEach(indicator => {
        if (lastUpdateTime) {
            const now = new Date();
            const diff = Math.floor((now - lastUpdateTime) / 1000);
            
            if (diff < 60) {
                indicator.textContent = `Updated ${diff}s ago`;
                indicator.classList.add('updating');
            } else if (diff < 3600) {
                indicator.textContent = `Updated ${Math.floor(diff / 60)}m ago`;
                indicator.classList.remove('updating');
            } else {
                indicator.textContent = `Updated ${Math.floor(diff / 3600)}h ago`;
                indicator.classList.remove('updating');
            }
        } else {
            indicator.textContent = 'Just updated';
            indicator.classList.add('updating');
        }
    });
}

function setUpdateTime() {
    lastUpdateTime = new Date();
    updateLastUpdateTime();
    setInterval(updateLastUpdateTime, 1000);
}

// Notification System
let notificationQueue = [];
let notificationEnabled = true;

function showNotification(message, type = 'info', duration = 5000) {
    if (!notificationEnabled) return;
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i data-lucide="bell" class="notification-icon"></i>
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <i data-lucide="x"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Initialize icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Auto remove
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

function checkForNewTrades(oldTrades, newTrades) {
    if (!oldTrades || !newTrades) return;
    
    const oldIds = new Set(oldTrades.map(t => `${t.ticker}-${t.date}-${t.action}`));
    const newTradesList = newTrades.filter(t => !oldIds.has(`${t.ticker}-${t.date}-${t.action}`));
    
    newTradesList.forEach(trade => {
        const action = trade.action === 'Purchase' ? 'purchased' : 'sold';
        showNotification(
            `New trade: ${trade.action} ${trade.amount || ''} in ${trade.ticker}`,
            trade.action === 'Purchase' ? 'success' : 'info',
            7000
        );
    });
}

// Comparison Tools
function initComparisonTools() {
    const compareBtn = document.getElementById('compare-btn');
    if (compareBtn) {
        compareBtn.addEventListener('click', () => {
            // This would open a comparison modal or page
            showNotification('Comparison feature coming soon!', 'info');
        });
    }
}

// Mobile Menu Toggle
function initMobileMenu() {
    const menuToggle = document.getElementById('mobile-menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', () => {
            navLinks.classList.toggle('mobile-open');
        });
    }
}

// Initialize all enhancements
document.addEventListener('DOMContentLoaded', function() {
    initSearchAndFilter();
    initComparisonTools();
    initMobileMenu();
    setUpdateTime();
    
    // Store original data for filtering
    if (typeof fetchPortfolioData === 'function') {
        const originalFetch = fetchPortfolioData;
        window.fetchPortfolioData = async function() {
            const oldTrades = [...allTrades];
            await originalFetch();
            // Check for new trades after update
            setTimeout(() => {
                if (allTrades.length > 0 && oldTrades.length > 0) {
                    checkForNewTrades(oldTrades, allTrades);
                }
            }, 1000);
        };
    }
});

// Functions are already on window object above

