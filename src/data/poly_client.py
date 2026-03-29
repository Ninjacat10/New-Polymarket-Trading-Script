import requests
import json
from datetime import datetime
import pandas as pd
from ..config import POLYMARKET_GAMMA_API_URL

class PolyClient:
    def __init__(self):
        self.session = requests.Session()

    def get_weather_event(self, city_name, date_str):
        """
        Attempts to find a weather event for a specific city and date.
        Date should be YYYY-MM-DD.
        """
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        month_full = date_obj.strftime("%B").lower() # e.g. 'march'
        day = date_obj.day
        year = date_obj.year
        
        # Map city names to slugs used by Polymarket
        city_map = {
            "miami": "miami",
            "new york": "nyc",
            "chicago": "chicago"
        }
        city_slug = city_map.get(city_name.lower(), city_name.lower().replace(" ", "-"))
        
        # New pattern found: highest-temperature-in-[city]-on-[month]-[day]-[year]
        slug_guess = f"highest-temperature-in-{city_slug}-on-{month_full}-{day}-{year}"
        
        try:
            url = f"{POLYMARKET_GAMMA_API_URL}/events"
            resp = self.session.get(url, params={"slug": slug_guess})
            resp.raise_for_status()
            data = resp.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                return data[0]
            
            # Fallback search if exact slug doesn't match
            # Search active events only. (Cross-platform day formatting)
            day_str = str(date_obj.day)
            search_query = f"Highest temperature in {city_name} on {date_obj.strftime('%B')} {day_str}"
            resp = self.session.get(url, params={"query": search_query, "active": "true"})
            if resp.status_code == 200:
                data = resp.json()
                if data and len(data) > 0:
                    return data[0]
            
            return None
                
        except Exception as e:
            print(f"Error fetching Polymarket event for {city_name} on {date_str}: {e}")
            return None

    def get_market_prices(self, event_id):
        """
        Fetches the current or closing prices of the markets inside the event.
        Returns a dictionary mapping the bin name (e.g., '75-76°F') to its price (e.g., 0.50).
        """
        try:
            url = f"{POLYMARKET_GAMMA_API_URL}/events/{event_id}"
            resp = self.session.get(url)
            resp.raise_for_status()
            event_data = resp.json()
            
            prices = {}
            for market in event_data.get('markets', []):
                # We expect the market question/title to be something like "75-77°F", etc.
                # Usually there's a JSON string in tokens or an outcome 'Yes' price
                bin_name = market.get('groupItemTitle') or market.get('question')
                if not bin_name:
                    continue
                
                # outcomePrices can be a list or a JSON string list
                outcome_prices = market.get('outcomePrices')
                if isinstance(outcome_prices, str):
                    try:
                        outcome_prices = json.loads(outcome_prices)
                    except json.JSONDecodeError:
                        outcome_prices = None
                
                if outcome_prices and len(outcome_prices) > 0:
                    # Yes price is usually index 0
                    yes_price = outcome_prices[0]
                    try:
                        prices[bin_name] = float(yes_price)
                    except ValueError:
                        pass
                        
            return prices
                        
        except Exception as e:
            print(f"Error fetching market prices for event {event_id}: {e}")
            return {}
