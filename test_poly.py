import requests
import json

url = "https://gamma-api.polymarket.com/events"
resp = requests.get(url, params={"limit": 100, "active": "true"})
with open("C:/Users/yashc/repos/New-Polymarket-Trading-Script/tmp_events.json", "w") as f:
    json.dump(resp.json(), f, indent=2)

print("done")
