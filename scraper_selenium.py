"""
Alternative scraper using Selenium for JavaScript-rendered content
Use this if the main scraper doesn't work due to dynamic content loading
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import time

class PelosiTrackerSeleniumScraper:
    def __init__(self, headless=True):
        self.base_url = "https://pelositracker.app"
        self.headless = headless
        self.driver = None
        
    def _init_driver(self):
        """Initialize Selenium WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Error initializing Chrome driver: {e}")
            print("Make sure ChromeDriver is installed and in PATH")
            raise
    
    def get_portfolio_data(self) -> Optional[Dict]:
        """Scrape live portfolio data using Selenium"""
        if not self.driver:
            self._init_driver()
        
        url = f"{self.base_url}/portfolios/nancy-pelosi"
        
        try:
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Wait for table to appear
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
            except:
                pass
            
            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract data using same methods as main scraper
            holdings = self._extract_holdings(soup)
            performance = self._extract_performance(soup)
            stats = self._extract_stats(soup)
            trades = self._extract_recent_trades(soup)
            
            return {
                'holdings': holdings,
                'performance': performance,
                'stats': stats,
                'recent_trades': trades,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error fetching portfolio data: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def _extract_holdings(self, soup) -> List[Dict]:
        """Extract holdings from table"""
        holdings = []
        tables = soup.find_all('table')
        
        for table in tables:
            headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
            if any(keyword in str(headers) for keyword in ['ticker', 'price', 'weight']):
                rows = table.find_all('tr')[1:]
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:
                        ticker = cells[0].get_text(strip=True)
                        price = cells[1].get_text(strip=True)
                        weight = cells[2].get_text(strip=True)
                        
                        if ticker and re.match(r'^[A-Z]{1,5}$', ticker):
                            holdings.append({
                                'ticker': ticker,
                                'last_price': self._parse_price(price),
                                'price_display': price,
                                'weight': self._parse_percentage(weight),
                                'weight_display': weight
                            })
                if holdings:
                    break
        return holdings
    
    def _extract_performance(self, soup) -> Dict:
        """Extract performance metrics"""
        performance = {}
        text = soup.get_text()
        
        perf_match = re.search(r'([+-]?\d+\.?\d*)%\s*performance', text, re.I)
        if perf_match:
            try:
                performance['performance_percent'] = float(perf_match.group(1))
            except:
                pass
        
        invested_match = re.search(r'Total Invested\s*\$([\d,]+\.?\d*)\s*([MK])?', text, re.I)
        if invested_match:
            try:
                amount = float(invested_match.group(1).replace(',', ''))
                if invested_match.group(2) == 'M':
                    amount *= 1000000
                performance['total_invested'] = amount
            except:
                pass
        
        return performance
    
    def _extract_stats(self, soup) -> Dict:
        """Extract portfolio stats"""
        stats = {}
        text = soup.get_text()
        
        holdings_match = re.search(r'(\d+)\s+holdings?', text, re.I)
        if holdings_match:
            stats['holdings_count'] = int(holdings_match.group(1))
        
        return stats
    
    def _extract_recent_trades(self, soup) -> List[Dict]:
        """Extract recent trades"""
        return []  # Implement based on actual structure
    
    def _parse_price(self, price_str: str) -> float:
        try:
            return float(price_str.replace('$', '').replace(',', ''))
        except:
            return 0.0
    
    def _parse_percentage(self, pct_str: str) -> float:
        try:
            return float(pct_str.replace('%', ''))
        except:
            return 0.0









