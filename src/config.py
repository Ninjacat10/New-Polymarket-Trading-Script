# Configuration parameters and constants

CITIES = {
    # We use specific Airport IDs (e.g. 'MIA') because Polymarket resolves there.
    "MIA": {"name": "Miami", "lat": 25.7932, "lon": -80.2905, "station": "KMIA", "acis_id": "MIA", "timezone": "America/New_York"},
    "NYC": {"name": "New York", "lat": 40.7812, "lon": -73.9665, "station": "KNYC", "acis_id": "NYC", "timezone": "America/New_York"},
    "ORD": {"name": "Chicago", "lat": 41.9742, "lon": -87.9073, "station": "KORD", "acis_id": "ORD", "timezone": "America/Chicago"},
}

STRATEGY = {
    "min_ev_edge": 0.10,        # Minimum Expected Value edge before suggesting a trade
    "max_acceptable_price": 101, # Allow signals even if bins sum to 100% (Polymarket standard)
}

# IMPORTANT: Get your free token at https://www.ncdc.noaa.gov/cdo-web/token
NOAA_TOKEN = "qKeLbqjcUUQPIuHeWRZsXRbWuUbXEYOU" 

POLYMARKET_GAMMA_API_URL = "https://gamma-api.polymarket.com"
