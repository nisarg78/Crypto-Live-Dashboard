import pandas as pd

def process_coin_list(data):
    df = pd.DataFrame(data)
    return df[['id', 'symbol', 'name', 'current_price', 'market_cap', 'total_volume', 'price_change_percentage_24h']]

def process_coin_details(data):
    return {
        "Name": data['name'],
        "Symbol": data['symbol'].upper(),
        "Current Price (USD)": data['market_data']['current_price']['usd'],
        "Market Cap": data['market_data']['market_cap']['usd'],
        "Total Volume": data['market_data']['total_volume']['usd'],
        "Circulating Supply": data['market_data']['circulating_supply'],
        "Total Supply": data['market_data']['total_supply'],
        "Max Supply": data['market_data'].get('max_supply', 'N/A'),
        "All Time High": data['market_data']['ath']['usd'],
        "ATH Change (%)": data['market_data']['ath_change_percentage']['usd'],
        "Price Change (24h)": data['market_data']['price_change_percentage_24h'],
    }
