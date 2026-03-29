import requests
from datetime import datetime
import pandas as pd
import pytz

class NOAAClient:
    def __init__(self, token=None):
        self.headers = {
            "User-Agent": "(PolymarketWeatherBot, bot@example.com)"
        }
        self.token = token
        self.ncei_headers = {"token": token} if token else {}

    def get_forecast(self, lat, lon):
        # (Existing forecast code...)
        try:
            point_url = f"https://api.weather.gov/points/{lat},{lon}"
            resp = requests.get(point_url, headers=self.headers)
            resp.raise_for_status()
            point_data = resp.json()
            forecast_url = point_data['properties']['forecast']
            f_resp = requests.get(forecast_url, headers=self.headers)
            f_resp.raise_for_status()
            forecast_data = f_resp.json()
            periods = forecast_data['properties']['periods']
            for period in periods:
                if period['isDaytime']:
                    return {"temperature": period['temperature'], "temperatureUnit": period['temperatureUnit']}
            return None
        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return None

    def get_historical_temp(self, city_code, target_date_str):
        """
        Fetches the observed max temperature using the ACIS API.
        ACIS provides the last 30+ days instantly without tokens.
        """
        try:
            # ACIS handles airport codes like 'NYC', 'MIA', 'ORD' directly
            params = {
                "sid": city_code,
                "sdate": target_date_str,
                "edate": target_date_str,
                "elems": "maxt",
                "output": "json"
            }
            url = "http://data.rcc-acis.org/StnData"
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            
            # Data format: {'data': [['2026-03-01', '44']]}
            if 'data' in data and len(data['data']) > 0:
                day_data = data['data'][0]
                if len(day_data) > 1 and day_data[1] != 'M': # 'M' is missing
                    return float(day_data[1])
            return None
        except Exception as e:
            print(f"Error fetching ACIS weather: {e}")
            return None
