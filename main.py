import argparse
from datetime import datetime, timedelta
import pandas as pd

from src.config import CITIES, STRATEGY
from src.backtest.engine import BacktestEngine

def run_backtest(start_date, end_date, cities):
    """
    Simulates trades over a date range.
    """
    print(f"--- Polymarket Weather Backtester ---")
    print(f"Date Range: {start_date} to {end_date}")
    print(f"Cities: {cities}")
    print(f"Options: {STRATEGY}")
    
    engine = BacktestEngine(config=__import__('src.config', fromlist=['CITIES', 'STRATEGY']))
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    delta = end_dt - start_dt
    
    results = []
    
    for i in range(delta.days + 1):
        day = start_dt + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        
        for city in cities:
            res = engine.evaluate_city(city, day_str)
            if res:
                results.append(res)
                
    print("\n--- Summary Report ---")
    if not results:
        print("No valid signals found.")
        return
        
    df = pd.DataFrame(results)
    # Only show columns if they exist
    cols = ['city', 'date', 'noaa_temp', 'target_bin', 'bin_price', 'signal']
    existing_cols = [c for c in cols if c in df.columns]
    print(df[existing_cols].to_string(index=False))
    
    # Win Rate Calculation (for past dates where price was 1.0 or 0.0)
    historical = df[df['bin_price'].isin([0.0, 1.0])]
    if not historical.empty:
        wins = len(historical[historical['bin_price'] == 1.0])
        total = len(historical)
        rate = (wins / total) * 100
        print(f"\n--- Performance Analysis ---")
        print(f"Historical Matches: {wins} / {total}")
        print(f"NOAA Data Match Rate: {rate:.1f}%")

def main():
    parser = argparse.ArgumentParser(description="Polymarket Daily Weather Backtester")
    parser.add_argument("--mode", type=str, choices=['backtest', 'predict'], default='backtest', help="Run a manual simulation.")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)", default=(datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"))
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD)", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--cities", type=str, help="Comma separated city codes (e.g. MIA,NYC)", default="MIA,NYC,ORD")

    args = parser.parse_args()
    
    city_list = [c.strip() for c in args.cities.split(",")]
    
    if args.mode == 'backtest' or args.mode == 'predict':
        run_backtest(args.start, args.end, city_list)
        
if __name__ == "__main__":
    main()
