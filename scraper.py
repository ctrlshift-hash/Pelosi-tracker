import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import time

# Try to use Selenium if available
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class PelosiTrackerScraper:
    def __init__(self):
        self.base_url = "https://pelositracker.app"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def get_portfolio_data(self) -> Optional[Dict]:
        """Scrape ALL real portfolio data from pelositracker.app - NO MOCK DATA"""
        if not SELENIUM_AVAILABLE:
            print("ERROR: Selenium not available - cannot scrape real data")
            return None
        
        url = f"{self.base_url}/portfolios/nancy-pelosi"
        
        try:
            return self._scrape_with_selenium(url)
        except Exception as e:
            print(f"ERROR scraping portfolio data: {e}")
            return None
    
    def _scrape_with_selenium(self, url: str) -> Optional[Dict]:
        """Scrape using Selenium - extract ALL real data"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'user-agent={self.headers["User-Agent"]}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            
            # Wait for page to fully load
            time.sleep(8)
            
            # Wait for content to be visible
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                pass
            
            # Get page source after JS execution
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract ALL data
            holdings = self._extract_holdings_real(soup, driver)
            performance = self._extract_performance_real(soup, driver)
            stats = self._extract_stats_real(soup, driver)
            trades = self._extract_trades_real(soup, driver)
            sectors = self._extract_sectors_real(soup, driver)
            historical_data = self._extract_historical_data_real(soup, driver)
            filing_stats = self._extract_filing_stats_real(soup, driver)
            
            return {
                'holdings': holdings,
                'performance': performance,
                'stats': stats,
                'recent_trades': trades,
                'sector_allocation': sectors,
                'historical_performance': historical_data,
                'filing_statistics': filing_stats,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Selenium error: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            if driver:
                driver.quit()
    
    def _extract_holdings_real(self, soup: BeautifulSoup, driver) -> List[Dict]:
        """Extract real holdings from the page"""
        holdings = []
        
        try:
            # Wait for table to load
            time.sleep(3)
            
            # Method 1: Use Selenium to find holdings table
            try:
                tables = driver.find_elements(By.TAG_NAME, "table")
                print(f"Found {len(tables)} tables for holdings extraction", flush=True)
                
                for table in tables:
                    headers = table.find_elements(By.TAG_NAME, "th")
                    header_texts = [h.text.lower() for h in headers]
                    header_str = ' '.join(header_texts)
                    
                    if any(keyword in header_str for keyword in ['ticker', 'price', 'weight', 'holding', 'last price']):
                        print(f"Found holdings table with headers: {header_texts}", flush=True)
                        rows = table.find_elements(By.TAG_NAME, "tr")
                        print(f"Found {len(rows)} rows in holdings table", flush=True)
                        
                        for row in rows[1:]:  # Skip header
                            try:
                                cells = row.find_elements(By.TAG_NAME, "td")
                                if len(cells) >= 3:
                                    # Get text from cells using multiple methods
                                    cell_texts = []
                                    for cell in cells:
                                        text = cell.text.strip()
                                        if not text:
                                            text = cell.get_attribute('textContent') or cell.get_attribute('innerText') or ''
                                            text = text.strip()
                                        cell_texts.append(text)
                                    
                                    ticker = cell_texts[0] if len(cell_texts) > 0 else ''
                                    price_text = cell_texts[1] if len(cell_texts) > 1 else ''
                                    weight_text = cell_texts[2] if len(cell_texts) > 2 else ''
                                    
                                    if ticker and re.match(r'^[A-Z]{1,5}$', ticker):
                                        holdings.append({
                                            'ticker': ticker,
                                            'last_price': self._parse_price(price_text),
                                            'price_display': price_text or f'${self._parse_price(price_text):.2f}',
                                            'weight': self._parse_percentage(weight_text),
                                            'weight_display': weight_text or f'{self._parse_percentage(weight_text):.1f}%'
                                        })
                                        print(f"Added holding: {ticker} - {price_text} - {weight_text}", flush=True)
                            except Exception as e:
                                print(f"Error processing holdings row: {e}", flush=True)
                                continue
                        
                        if holdings:
                            print(f"Extracted {len(holdings)} holdings using Selenium", flush=True)
                            return holdings
            except Exception as e:
                print(f"Selenium holdings extraction failed: {e}", flush=True)
        except Exception as e:
            print(f"Error in holdings extraction: {e}", flush=True)
        
        # Method 2: Fallback to BeautifulSoup
        try:
            tables = soup.find_all('table')
            for table in tables:
                headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
                if any(keyword in ' '.join(headers) for keyword in ['ticker', 'price', 'weight', 'holding']):
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 3:
                            ticker = cells[0].get_text(strip=True)
                            price_text = cells[1].get_text(strip=True) if len(cells) > 1 else ''
                            weight_text = cells[2].get_text(strip=True) if len(cells) > 2 else ''
                            
                            if ticker and re.match(r'^[A-Z]{1,5}$', ticker):
                                holdings.append({
                                    'ticker': ticker,
                                    'last_price': self._parse_price(price_text),
                                    'price_display': price_text or f'${self._parse_price(price_text):.2f}',
                                    'weight': self._parse_percentage(weight_text),
                                    'weight_display': weight_text or f'{self._parse_percentage(weight_text):.1f}%'
                                })
                    if holdings:
                        break
        except Exception as e:
            print(f"BeautifulSoup holdings extraction failed: {e}", flush=True)
        
        # Method 2: Look for JSON data in script tags
        if not holdings:
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if 'holdings' in data:
                        holdings = data['holdings']
                        break
                except:
                    pass
        
        # Method 3: Look for data attributes or React props
        if not holdings:
            # Try to find elements with data attributes
            holding_elements = soup.find_all(attrs={'data-ticker': True})
            for elem in holding_elements:
                ticker = elem.get('data-ticker')
                price = elem.get('data-price', '0')
                weight = elem.get('data-weight', '0')
                if ticker:
                    holdings.append({
                        'ticker': ticker,
                        'last_price': self._parse_price(price),
                        'price_display': f'${self._parse_price(price):.2f}',
                        'weight': self._parse_percentage(weight),
                        'weight_display': f'{self._parse_percentage(weight):.1f}%'
                    })
        
        return holdings
    
    def _extract_performance_real(self, soup: BeautifulSoup, driver) -> Dict:
        """Extract real performance data"""
        performance = {}
        text = soup.get_text()
        
        # Extract performance percentage
        perf_patterns = [
            r'([+-]?\d+\.?\d*)%\s*performance',
            r'performance\s*([+-]?\d+\.?\d*)%',
            r'\+(\d+\.?\d*)%',
            r'↑\s*(\d+\.?\d*)%',
            r'(\d+\.?\d*)%\s*↑'
        ]
        
        for pattern in perf_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    perf_val = float(match.group(1))
                    performance['performance_percent'] = perf_val
                    break
                except:
                    continue
        
        # Extract total invested/value
        value_patterns = [
            r'Total Value[:\s]*US?\$?([\d,]+\.?\d*)\s*([MK])?',
            r'Total Invested[:\s]*\$?([\d,]+\.?\d*)\s*([MK])?',
            r'\$([\d,]+\.?\d*)\s*([MK])?\s*Total',
            r'US?\$([\d,]+\.?\d*)\s*([MK])'
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    
                    if len(match.groups()) > 1 and match.group(2):
                        multiplier = match.group(2).upper()
                        if multiplier == 'M':
                            amount *= 1000000
                        elif multiplier == 'K':
                            amount *= 1000
                    
                    performance['total_invested'] = amount
                    break
                except:
                    continue
        
        # Try to get from page elements
        try:
            value_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Total Value') or contains(text(), 'US$')]")
            for elem in value_elements:
                text = elem.text
                match = re.search(r'US?\$([\d,]+\.?\d*)\s*([MK])?', text)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    if len(match.groups()) > 1 and match.group(2):
                        multiplier = match.group(2).upper()
                        if multiplier == 'M':
                            amount *= 1000000
                        elif multiplier == 'K':
                            amount *= 1000
                    performance['total_invested'] = amount
                    break
        except:
            pass
        
        return performance
    
    def _extract_stats_real(self, soup: BeautifulSoup, driver) -> Dict:
        """Extract real portfolio statistics"""
        stats = {}
        text = soup.get_text()
        
        # Extract holdings count
        holdings_match = re.search(r'(\d+)\s+holdings?', text, re.IGNORECASE)
        if holdings_match:
            stats['holdings_count'] = int(holdings_match.group(1))
        
        # Extract copiers count
        copiers_match = re.search(r'(\d+,?\d*)\s+copiers?', text, re.IGNORECASE)
        if copiers_match:
            copiers_str = copiers_match.group(1).replace(',', '')
            stats['copiers'] = int(copiers_str)
        
        return stats
    
    def _extract_trades_real(self, soup: BeautifulSoup, driver) -> List[Dict]:
        """Extract REAL Nancy Pelosi trades from pelositracker.app"""
        trades = []
        
        try:
            print("Scrolling to find trades section...", flush=True)
            # Scroll down to load more content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Look for ALL links on the page - trades are usually linked
            print("Looking for trade links...", flush=True)
            links = driver.find_elements(By.TAG_NAME, "a")
            print(f"Found {len(links)} links on page", flush=True)
            
            # Look for links that go to /stock/ pages - these are trades
            trade_links = []
            for link in links:
                href = link.get_attribute('href')
                if href and '/stock/' in href.lower():
                    ticker_match = re.search(r'/stock/([a-z]+)', href.lower())
                    if ticker_match:
                        ticker = ticker_match.group(1).upper()
                        # Get the parent element text which might have trade info
                        try:
                            parent = link.find_element(By.XPATH, "./..")
                            parent_text = parent.text
                            
                            # Extract date from parent text
                            date = None
                            date_patterns = [
                                r'(\d{1,2}/\d{1,2}/\d{2,4})',
                                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}',
                                r'(\d{1,2}-\d{1,2}-\d{2,4})'
                            ]
                            for pattern in date_patterns:
                                date_match = re.search(pattern, parent_text, re.IGNORECASE)
                                if date_match:
                                    date = date_match.group(0)
                                    break
                            
                            # Extract amount
                            amount = None
                            amount_match = re.search(r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?', parent_text)
                            if amount_match:
                                amount = amount_match.group(0)
                            
                            # Extract action
                            action = 'Trade'
                            if 'purchase' in parent_text.lower() or 'buy' in parent_text.lower():
                                action = 'Purchase'
                            elif 'sale' in parent_text.lower() or 'sell' in parent_text.lower():
                                action = 'Sale'
                            
                            if ticker not in [t['ticker'] for t in trade_links]:
                                trade_links.append({
                                    'ticker': ticker,
                                    'date': date,
                                    'amount': amount,
                                    'action': action,
                                    'text': parent_text[:100]
                                })
                        except:
                            if ticker not in [t['ticker'] for t in trade_links]:
                                trade_links.append({
                                    'ticker': ticker,
                                    'date': None,
                                    'amount': None,
                                    'action': 'Trade',
                                    'text': link.text
                                })
            
            print(f"Found {len(trade_links)} unique stock links", flush=True)
            
            # Convert to trades format
            for tl in trade_links[:20]:
                trades.append({
                    'ticker': tl['ticker'],
                    'action': tl['action'],
                    'date': tl['date'],
                    'traded_date': tl['date'],
                    'amount': tl['amount'] or 'N/A',
                    'description': tl['text']
                })
                print(f"Trade: {tl['ticker']} - {tl['date']} - {tl['amount']}", flush=True)
            
            print(f"Extracted {len(trades)} trades", flush=True)
            return trades
            
        except Exception as e:
            print(f"Error extracting trades: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return []
    
    def _extract_sectors_real(self, soup: BeautifulSoup, driver) -> List[Dict]:
        """Extract real sector allocation"""
        sectors = []
        
        try:
            # Look for sector elements
            sector_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'sector') or contains(text(), 'Technology') or contains(text(), 'Financial')]")
            
            for elem in sector_elements:
                text = elem.text
                if '%' in text:
                    match = re.search(r'([A-Za-z\s]+)\s*(\d+\.?\d*)%', text)
                    if match:
                        sectors.append({
                            'name': match.group(1).strip(),
                            'percentage': float(match.group(2))
                        })
        except:
            pass
        
        # Also parse from HTML
        sector_rows = soup.find_all(['div', 'li'], string=re.compile(r'%'))
        for row in sector_rows:
            text = row.get_text()
            match = re.search(r'([A-Za-z\s]+)\s*(\d+\.?\d*)%', text)
            if match:
                sectors.append({
                    'name': match.group(1).strip(),
                    'percentage': float(match.group(2))
                })
        
        return sectors
    
    def _extract_historical_data_real(self, soup: BeautifulSoup, driver) -> List[Dict]:
        """Extract historical performance data for charts"""
        historical = []
        
        try:
            # Look for chart data in script tags
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and ('chart' in script.string.lower() or 'data' in script.string.lower()):
                    # Try to find JSON data
                    json_matches = re.findall(r'\{.*?"date".*?"value".*?\}', script.string, re.DOTALL)
                    for match in json_matches:
                        try:
                            data = json.loads(match)
                            if 'date' in data and 'value' in data:
                                historical.append(data)
                        except:
                            pass
        except:
            pass
        
        return historical
    
    def _extract_filing_stats_real(self, soup: BeautifulSoup, driver) -> Dict:
        """Extract real filing statistics"""
        filing_stats = {}
        text = soup.get_text()
        
        # Extract average reporting time
        reporting_match = re.search(r'Avg\.?\s*Reporting Time[:\s]*(\d+)\s*days?', text, re.IGNORECASE)
        if reporting_match:
            filing_stats['avg_reporting_time'] = int(reporting_match.group(1))
        
        # Extract filing frequency
        frequency_match = re.search(r'Avg\.?\s*Filing Frequency[:\s]*(\d+)\s*days?', text, re.IGNORECASE)
        if frequency_match:
            filing_stats['avg_filing_frequency'] = int(frequency_match.group(1))
        
        # Extract time since last filing
        last_match = re.search(r'Time Since Last Filing[:\s]*(\d+)\s*days?', text, re.IGNORECASE)
        if last_match:
            filing_stats['time_since_last_filing'] = int(last_match.group(1))
        
        return filing_stats
    
    def _parse_price(self, price_str: str) -> float:
        """Parse price string to float"""
        try:
            return float(price_str.replace('$', '').replace(',', ''))
        except:
            return 0.0
    
    def _parse_percentage(self, pct_str: str) -> float:
        """Parse percentage string to float"""
        try:
            return float(pct_str.replace('%', ''))
        except:
            return 0.0
    
    def get_stock_data(self, ticker: str) -> Optional[Dict]:
        """Scrape real stock data from pelositracker.app/stock/<ticker>"""
        if not SELENIUM_AVAILABLE:
            print(f"ERROR: Selenium not available - cannot scrape stock data for {ticker}")
            return None
        
        url = f"{self.base_url}/stock/{ticker.lower()}"
        
        try:
            return self._scrape_stock_page(url, ticker)
        except Exception as e:
            print(f"ERROR scraping stock data for {ticker}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _scrape_stock_page(self, url: str, ticker: str) -> Optional[Dict]:
        """Scrape stock detail page"""
        print(f"SCRAPING STOCK PAGE: {url} for ticker {ticker}", flush=True)
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        options.add_argument(f'user-agent={self.headers["User-Agent"]}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(30)  # 30 second timeout
            print(f"Navigating to {url}", flush=True)
            driver.get(url)
            
            # Wait for page to fully load
            print(f"Waiting for page to load...", flush=True)
            time.sleep(10)
            
            # Wait for specific elements to appear
            try:
                WebDriverWait(driver, 25).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                )
                print(f"Page loaded, h1 found", flush=True)
                # Wait for table if it exists
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "table"))
                    )
                    print(f"Table found on page", flush=True)
                except:
                    print(f"No table found yet, continuing anyway", flush=True)
            except Exception as e:
                print(f"Wait timeout: {e}, continuing anyway", flush=True)
            
            # Verify we're on the right page
            current_url = driver.current_url
            print(f"Current URL after load: {current_url}", flush=True)
            
            if ticker.lower() not in current_url.lower():
                print(f"WARNING: URL mismatch! Expected {ticker} in URL but got {current_url}", flush=True)
            
            # Get page source
            page_source = driver.page_source
            print(f"Page source length: {len(page_source)} characters", flush=True)
            
            # Verify ticker is in page source
            if ticker.upper() not in page_source and ticker.lower() not in page_source:
                print(f"WARNING: Ticker {ticker} not found in page source!", flush=True)
            else:
                print(f"Ticker {ticker} found in page source", flush=True)
            
            soup = BeautifulSoup(page_source, 'html.parser')
            print(f"BeautifulSoup parsed successfully", flush=True)
            
            # Extract stock data - wrap each extraction in try/except to prevent crashes
            try:
                company_name = self._extract_company_name(soup, driver, ticker)
            except Exception as e:
                print(f"Error extracting company name: {e}", flush=True)
                company_name = f'{ticker} Corporation'
            
            try:
                exchange = self._extract_exchange(soup, driver)
            except:
                exchange = 'N/A'
            
            try:
                current_price = self._extract_current_price(soup, driver, ticker)
            except Exception as e:
                print(f"Error extracting price: {e}", flush=True)
                current_price = 0.0
            
            try:
                price_change = self._extract_price_change(soup, driver)
            except:
                price_change = 0.0
            
            try:
                price_change_percent = self._extract_price_change_percent(soup, driver)
            except:
                price_change_percent = 0.0
            
            try:
                week_range_low = self._extract_week_range_low(soup, driver)
            except:
                week_range_low = 0.0
            
            try:
                week_range_high = self._extract_week_range_high(soup, driver)
            except:
                week_range_high = 0.0
            
            try:
                status = self._extract_status(soup, driver)
            except:
                status = ''
            
            try:
                description = self._extract_description(soup, driver, ticker)
            except:
                description = f'Information about {ticker}'
            
            try:
                trades = self._extract_stock_trades(soup, driver, ticker)
            except Exception as e:
                print(f"Error extracting trades: {e}", flush=True)
                trades = []
            
            try:
                similar_stocks = self._extract_similar_stocks(soup, driver)
            except:
                similar_stocks = []
            
            try:
                price_history = self._extract_price_history(soup, driver)
            except:
                price_history = []
            
            stock_data = {
                'ticker': ticker.upper(),
                'company_name': company_name,
                'exchange': exchange,
                'current_price': current_price,
                'price_change': price_change,
                'price_change_percent': price_change_percent,
                'week_range_low': week_range_low,
                'week_range_high': week_range_high,
                'status': status,
                'description': description,
                'trades': trades,
                'similar_stocks': similar_stocks,
                'price_history': price_history
            }
            
            print(f"Extracted data for {ticker}: Price=${stock_data['current_price']}, Trades={len(stock_data['trades'])}", flush=True)
            return stock_data
        except Exception as e:
            print(f"Error scraping stock page for {ticker}: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return None
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def _extract_company_name(self, soup: BeautifulSoup, driver, ticker: str) -> str:
        """Extract company name - find the h1 element"""
        try:
            # Use Selenium to find h1
            try:
                h1_elements = driver.find_elements(By.TAG_NAME, "h1")
                for h1 in h1_elements:
                    text = h1.text.strip()
                    # Check if this h1 mentions the ticker
                    if ticker.upper() in text.upper():
                        # Remove ticker in parentheses
                        name = re.sub(r'\s*\([A-Z]{1,5}\)\s*', '', text).strip()
                        if name:
                            print(f"Found company name via Selenium: {name}", flush=True)
                            return name
            except:
                pass
            
            # Fallback to BeautifulSoup
            h1_elements = soup.find_all('h1')
            for h1 in h1_elements:
                text = h1.get_text().strip()
                if ticker.upper() in text.upper():
                    text = re.sub(r'\s*\([A-Z]{1,5}\)\s*', '', text).strip()
                    if text:
                        return text
        except Exception as e:
            print(f"Error extracting company name: {e}", flush=True)
        return f'{ticker} Corporation'
    
    def _extract_exchange(self, soup: BeautifulSoup, driver) -> str:
        """Extract exchange info"""
        try:
            text = soup.get_text()
            match = re.search(r'(Nasdaq|NYSE|NASDAQ|NYSE|AMEX)', text, re.IGNORECASE)
            if match:
                return match.group(1)
        except:
            pass
        return 'N/A'
    
    def _extract_current_price(self, soup: BeautifulSoup, driver, ticker: str) -> float:
        """Extract current price - find the actual price element"""
        try:
            # Wait for price to load
            time.sleep(2)
            
            # Method 1: Look for "Current Price" text and get the value after it
            try:
                price_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Current Price')]")
                for elem in price_elements:
                    parent = elem.find_element(By.XPATH, "./following-sibling::* | ./parent::*")
                    text = parent.text
                    match = re.search(r'\$([\d,]+\.?\d*)', text)
                    if match:
                        price = float(match.group(1).replace(',', ''))
                        if 1 < price < 10000:
                            print(f"Found price via Current Price: ${price}", flush=True)
                            return price
            except:
                pass
            
            # Method 2: Look for price near h1 with ticker
            try:
                h1_elements = driver.find_elements(By.TAG_NAME, "h1")
                for h1 in h1_elements:
                    if ticker.upper() in h1.text.upper():
                        # Look for price in siblings or nearby
                        siblings = driver.find_elements(By.XPATH, f"//h1[contains(text(), '{ticker}')]/following-sibling::*")
                        for sibling in siblings[:5]:
                            text = sibling.text
                            match = re.search(r'\$([\d,]+\.?\d*)', text)
                            if match:
                                price = float(match.group(1).replace(',', ''))
                                if 1 < price < 10000:
                                    print(f"Found price near h1: ${price}", flush=True)
                                    return price
            except:
                pass
            
            # Method 3: Look for all price-like patterns and validate
            try:
                all_text = driver.find_element(By.TAG_NAME, "body").text
                # Find all prices
                prices = re.findall(r'\$([\d,]+\.?\d*)', all_text)
                for price_str in prices:
                    price = float(price_str.replace(',', ''))
                    # Stock prices are usually between $1 and $10,000
                    if 1 < price < 10000:
                        # Make sure it's not a date or other number
                        if price_str.count('.') <= 1:  # Only one decimal point
                            print(f"Found price via pattern: ${price}", flush=True)
                            return price
            except:
                pass
        except Exception as e:
            print(f"Error extracting current price: {e}", flush=True)
        return 0.0
    
    def _extract_price_change(self, soup: BeautifulSoup, driver) -> float:
        """Extract 24h price change"""
        try:
            text = soup.get_text()
            match = re.search(r'24h Change[:\s]*([+-]?[\d,]+\.?\d*)', text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', ''))
        except:
            pass
        return 0.0
    
    def _extract_price_change_percent(self, soup: BeautifulSoup, driver) -> float:
        """Extract 24h price change percentage"""
        try:
            text = soup.get_text()
            match = re.search(r'\(([+-]?[\d,]+\.?\d*)%\)', text)
            if match:
                return float(match.group(1).replace(',', ''))
        except:
            pass
        return 0.0
    
    def _extract_week_range_low(self, soup: BeautifulSoup, driver) -> float:
        """Extract 52 week low"""
        try:
            text = soup.get_text()
            match = re.search(r'52 Week Range[:\s]*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', ''))
        except:
            pass
        return 0.0
    
    def _extract_week_range_high(self, soup: BeautifulSoup, driver) -> float:
        """Extract 52 week high"""
        try:
            text = soup.get_text()
            match = re.search(r'52 Week Range[:\s]*\$?[\d,]+\.?\d*\s*[—–-]\s*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
            if match:
                return float(match.group(1).replace(',', ''))
        except:
            pass
        return 0.0
    
    def _extract_status(self, soup: BeautifulSoup, driver) -> str:
        """Extract trading status"""
        try:
            text = soup.get_text()
            if 'up' in text.lower() and '%' in text:
                match = re.search(r'up\s+([\d,]+\.?\d*)\s*\(([+-]?[\d,]+\.?\d*)%\)', text, re.IGNORECASE)
                if match:
                    return f"Currently up {match.group(1)} ({match.group(2)}%)"
        except:
            pass
        return ''
    
    def _extract_description(self, soup: BeautifulSoup, driver, ticker: str) -> str:
        """Extract company description - ensure it mentions the ticker"""
        try:
            # Look for description paragraphs that mention the ticker
            desc_elements = soup.find_all(['p', 'div'])
            for elem in desc_elements:
                text = elem.get_text().strip()
                # Make sure description mentions the ticker or company
                if len(text) > 50 and (ticker.upper() in text.upper() or 'corporation' in text.lower() or 'inc' in text.lower()):
                    return text[:500]  # Limit length
        except:
            pass
        return f'Information about {ticker} from pelositracker.app'
    
    def _extract_stock_trades(self, soup: BeautifulSoup, driver, ticker: str) -> List[Dict]:
        """Extract ONLY Nancy Pelosi's trades for this specific stock - 100% accurate"""
        trades = []
        
        try:
            # Wait longer for table to fully load
            time.sleep(8)
            
            # Scroll to make sure table is visible
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(2)
            except:
                pass
            
            # Try multiple methods to find the table
            table = None
            
            # Method 1: Find by heading text - most reliable
            try:
                heading = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Congressional Trading Activity')]"))
                )
                # Find table after the heading - try multiple XPath patterns
                try:
                    table = heading.find_element(By.XPATH, "./following::table[1]")
                except:
                    try:
                        table = driver.find_element(By.XPATH, "//h2[contains(text(), 'Congressional Trading Activity')]/following::table[1]")
                    except:
                        table = driver.find_element(By.XPATH, "//*[contains(text(), 'Congressional Trading Activity')]/following::table[1]")
                print(f"Found table via heading for {ticker}", flush=True)
            except Exception as e:
                print(f"Method 1 failed: {e}", flush=True)
            
            # Method 2: Find table by looking for table with politician column
            if not table:
                try:
                    tables = driver.find_elements(By.TAG_NAME, "table")
                    print(f"Found {len(tables)} total tables for {ticker}", flush=True)
                    for t in tables:
                        headers = t.find_elements(By.TAG_NAME, "th")
                        header_texts = [h.text.lower() for h in headers]
                        header_str = ' '.join(header_texts)
                        if 'politician' in header_str or ('traded' in header_str and 'date' in header_str):
                            table = t
                            print(f"Found table via header search for {ticker}. Headers: {header_texts}", flush=True)
                            break
                except Exception as e:
                    print(f"Method 2 failed: {e}", flush=True)
            
            # Method 3: Find any table that contains "Nancy Pelosi" text
            if not table:
                try:
                    tables = driver.find_elements(By.TAG_NAME, "table")
                    for t in tables:
                        table_text = t.text
                        if 'Nancy Pelosi' in table_text or 'Pelosi' in table_text:
                            table = t
                            print(f"Found table via Pelosi text search for {ticker}", flush=True)
                            break
                except Exception as e:
                    print(f"Method 3 failed: {e}", flush=True)
            
            if table:
                # Get all rows
                rows = table.find_elements(By.TAG_NAME, "tr")
                print(f"Found {len(rows)} rows in table for {ticker}", flush=True)
                
                if len(rows) == 0:
                    print(f"WARNING: Table found but no rows for {ticker}", flush=True)
                    return trades
                
                # Skip header row
                for i, row in enumerate(rows[1:], start=1):
                    try:
                        # Try multiple ways to get cells
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) == 0:
                            # Try th elements
                            cells = row.find_elements(By.TAG_NAME, "th")
                        
                        if len(cells) >= 6:
                            # Get text from each cell - use get_attribute('textContent') as fallback
                            cell_texts = []
                            for cell in cells:
                                text = cell.text.strip()
                                if not text:
                                    # Try innerHTML or textContent
                                    text = cell.get_attribute('textContent') or cell.get_attribute('innerText') or ''
                                    text = text.strip()
                                cell_texts.append(text)
                            
                            politician = cell_texts[0] if len(cell_texts) > 0 else 'N/A'
                            print(f"Row {i} politician: '{politician}'", flush=True)
                            
                            # Check if this is Nancy Pelosi - be flexible with matching
                            politician_lower = politician.lower()
                            is_pelosi = 'nancy pelosi' in politician_lower or (politician_lower == 'pelosi' and len(politician) < 20)
                            
                            if is_pelosi:
                                trade = {
                                    'politician': 'Nancy Pelosi',  # Normalize to consistent name
                                    'traded_date': cell_texts[1] if len(cell_texts) > 1 else 'N/A',
                                    'filed_date': cell_texts[2] if len(cell_texts) > 2 else 'N/A',
                                    'action': cell_texts[3] if len(cell_texts) > 3 else 'N/A',
                                    'type': cell_texts[4] if len(cell_texts) > 4 else 'Stock',
                                    'amount_range': cell_texts[5] if len(cell_texts) > 5 else 'N/A',
                                    'excess_return': cell_texts[6] if len(cell_texts) > 6 else 'N/A',
                                    'non_compliant': 'Non-Compliant' in row.text or 'non-compliant' in row.text.lower()
                                }
                                trades.append(trade)
                                print(f"Added trade #{len(trades)}: {trade['action']} {trade['type']} on {trade['traded_date']}", flush=True)
                            elif politician and politician != 'N/A':
                                print(f"Row {i} skipped - not Pelosi: '{politician}'", flush=True)
                    except Exception as e:
                        print(f"Error processing row {i}: {e}", flush=True)
                        import traceback
                        traceback.print_exc()
                        continue
                
                print(f"Extracted {len(trades)} Nancy Pelosi trades for {ticker} using Selenium", flush=True)
                if len(trades) == 0:
                    # Debug: print first few rows to see what we're getting
                    print(f"WARNING: No Pelosi trades found. First 5 rows:", flush=True)
                    for i, row in enumerate(rows[1:6], start=1):
                        try:
                            cells = row.find_elements(By.TAG_NAME, "td")
                            if len(cells) == 0:
                                cells = row.find_elements(By.TAG_NAME, "th")
                            
                            row_text = row.text.strip()
                            cell_texts = [cell.text.strip() or cell.get_attribute('textContent') or '' for cell in cells[:7]]
                            print(f"  Row {i}: Full text='{row_text[:100]}'", flush=True)
                            print(f"    Cells: {cell_texts}", flush=True)
                        except Exception as e:
                            print(f"  Row {i}: Error reading - {e}", flush=True)
                return trades
            
            # Fallback to BeautifulSoup - FILTER FOR NANCY PELOSI ONLY
            print(f"No table found via Selenium for {ticker}, trying BeautifulSoup", flush=True)
        except Exception as e:
            print(f"Selenium table extraction failed: {e}, trying BeautifulSoup", flush=True)
            import traceback
            traceback.print_exc()
        
        # BeautifulSoup fallback
        try:
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables via BeautifulSoup for {ticker}", flush=True)
            for table in tables:
                rows = table.find_all('tr')
                headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
                header_str = ' '.join(headers)
                
                if 'politician' in header_str or ('traded' in header_str and 'date' in header_str):
                    print(f"Found trade table with headers: {headers}", flush=True)
                    for row in rows[1:]:  # Skip header
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 6:
                            politician = cells[0].get_text(strip=True) if len(cells) > 0 else 'N/A'
                            politician_lower = politician.lower()
                            
                            # ONLY include Nancy Pelosi trades
                            if 'nancy pelosi' in politician_lower or (politician_lower == 'pelosi' and len(politician) < 20):
                                trade = {
                                    'politician': 'Nancy Pelosi',
                                    'traded_date': cells[1].get_text(strip=True) if len(cells) > 1 else 'N/A',
                                    'filed_date': cells[2].get_text(strip=True) if len(cells) > 2 else 'N/A',
                                    'action': cells[3].get_text(strip=True) if len(cells) > 3 else 'N/A',
                                    'type': cells[4].get_text(strip=True) if len(cells) > 4 else 'Stock',
                                    'amount_range': cells[5].get_text(strip=True) if len(cells) > 5 else 'N/A',
                                    'excess_return': cells[6].get_text(strip=True) if len(cells) > 6 else 'N/A',
                                    'non_compliant': 'Non-Compliant' in row.get_text() or 'non-compliant' in row.get_text().lower()
                                }
                                trades.append(trade)
                                print(f"Added trade via BS: {trade['action']} on {trade['traded_date']}", flush=True)
            
            print(f"Extracted {len(trades)} Nancy Pelosi trades for {ticker} using BeautifulSoup", flush=True)
        except Exception as e:
            print(f"Error extracting trades: {e}", flush=True)
            import traceback
            traceback.print_exc()
        
        return trades
    
    def _extract_similar_stocks(self, soup: BeautifulSoup, driver) -> List[Dict]:
        """Extract similar stocks recommendations"""
        similar = []
        
        try:
            # Look for similar stocks section
            similar_section = soup.find(string=re.compile(r'similar|recommend', re.I))
            if similar_section:
                parent = similar_section.find_parent(['div', 'section'])
                if parent:
                    stock_items = parent.find_all(['div', 'a'], class_=re.compile(r'stock|ticker', re.I))
                    for item in stock_items[:5]:  # Limit to 5
                        text = item.get_text()
                        ticker_match = re.search(r'\b([A-Z]{1,5})\b', text)
                        if ticker_match:
                            similar.append({
                                'ticker': ticker_match.group(1),
                                'name': text.split('\n')[0] if '\n' in text else text,
                                'price': 0.0,
                                'change': 0.0,
                                'change_percent': 0.0,
                                'reason': 'Based on congressional trading patterns'
                            })
        except:
            pass
        
        return similar
    
    def _extract_price_history(self, soup: BeautifulSoup, driver) -> List[Dict]:
        """Extract price history for chart"""
        history = []
        
        try:
            # Look for chart data in script tags
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and ('chart' in script.string.lower() or 'price' in script.string.lower()):
                    # Try to find JSON data arrays
                    json_matches = re.findall(r'\[.*?\{.*?"date".*?"price".*?\}.*?\]', script.string, re.DOTALL)
                    for match in json_matches:
                        try:
                            data = json.loads(match)
                            if isinstance(data, list):
                                history.extend(data)
                        except:
                            pass
        except:
            pass
        
        return history
