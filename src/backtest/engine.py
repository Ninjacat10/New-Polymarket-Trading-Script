from src.data.noaa_client import NOAAClient
from src.data.poly_client import PolyClient
import pandas as pd
from datetime import datetime, timedelta

class BacktestEngine:
    def __init__(self, config):
        self.config = config
        self.noaa_client = NOAAClient(token=getattr(config, 'NOAA_TOKEN', None))
        self.poly_client = PolyClient()
        
    def evaluate_city(self, city_code, date_str):
        """
        Evaluates the trading strategy for a single city on a specific date.
        """
        if city_code not in self.config.CITIES:
            print(f"Unknown city code: {city_code}")
            return None
            
        city_info = self.config.CITIES[city_code]
        print(f"[{date_str}] Evaluating {city_info['name']} (NOAA Station: {city_info['station']})...")
        
        # 1. Fetch NOAA predictions or actuals
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        
        noaa_value = None
        if target_date >= today:
            forecast = self.noaa_client.get_forecast(city_info['lat'], city_info['lon'])
            if forecast:
                 noaa_value = float(forecast['temperature'])
                 print(f"  NOAA Forecast: {noaa_value}°{forecast['temperatureUnit']}")
        else:
            # ACIS provides the last 30 days instantly
            actual = self.noaa_client.get_historical_temp(city_code, date_str)
            if actual is not None:
                noaa_value = actual
                print(f"  NOAA Actual Obs: {noaa_value}°F")
                
        if noaa_value is None:
            print(f"  Could not retrieve NOAA data for {date_str}. Skipping.")
            return None
            
        # 2. Fetch Polymarket data for this day
        event_info = self.poly_client.get_weather_event(city_info['name'], date_str)
        if not event_info:
            print(f"  Could not find Polymarket event for {city_info['name']} on {date_str}. (This is common if the market slug naming convention has changed).")
            return None
            
        print(f"  Found Polymarket Event: {event_info.get('title')}")
        
        prices = self.poly_client.get_market_prices(event_info.get('id', ''))
        if not prices:
            print("  No active/valid bin prices found.")
            return None
            
        import re
        
        target_bin = None
        for bin_name, price in prices.items():
            clean_name = bin_name.replace('°F', '').replace('°', '').lower().strip()
            
            # Case 1: Range "75-76"
            if '-' in clean_name:
                try:
                    parts = clean_name.split('-')
                    low, high = float(parts[0]), float(parts[1])
                    if low <= noaa_value <= high:
                        target_bin = bin_name
                        break
                except (ValueError, IndexError): pass

            # Case 2: "75 or below" / "75 or less"
            elif any(x in clean_name for x in ['below', 'less']):
                try:
                    val = float(re.findall(r"[-+]?\d*\.\d+|\d+", clean_name)[0])
                    if noaa_value <= val:
                        target_bin = bin_name
                        break
                except (ValueError, IndexError): pass
                
            # Case 3: "75 or above" / "75 or more"
            elif any(x in clean_name for x in ['above', 'more']):
                try:
                    val = float(re.findall(r"[-+]?\d*\.\d+|\d+", clean_name)[0])
                    if noaa_value >= val:
                        target_bin = bin_name
                        break
                except (ValueError, IndexError): pass

            # Case 4: Single temperature "75"
            else:
                try:
                    val = float(re.findall(r"[-+]?\d*\.\d+|\d+", clean_name)[0])
                    if round(noaa_value) == round(val):
                        target_bin = bin_name
                        break
                except (ValueError, IndexError): pass

        if not target_bin:
            print("  Could not map NOAA value to a specific Polymarket bin.")
            return None
            
        bin_price = prices.get(target_bin, 0.0)
        
        # Very simple strategy logic: 
        # If the price is less than (1.0 - min_ev_edge), it's considered good EV assuming NOAA is 100% accurate.
        ev_score = 1.0 - bin_price # simplified since payout is $1.00
        
        signal = "SKIP"
        if ev_score >= self.config.STRATEGY['min_ev_edge']:
             # In a real system, you sum all bins to check < 96 cents rule as described in past plan
             total_price_sum = sum(prices.values())
             if total_price_sum * 100 <= self.config.STRATEGY['max_acceptable_price']:
                 signal = "BUY"
             else:
                 signal = "HOLD (sum check failed)"

        print(f"  Target Bin: {target_bin} | Price: {bin_price}¢ | Signal: {signal}")
        
        return {
            "city": city_code,
            "date": date_str,
            "noaa_temp": noaa_value,
            "target_bin": target_bin,
            "bin_price": bin_price,
            "signal": signal
        }
