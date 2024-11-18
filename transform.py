from datetime import datetime

# Process raw API data into a structured format
async def process_data(symbols, responses):
    all_rows = []

    for symbol, data in zip(symbols, responses):
        meta_data = data.get('Meta Data', {})
        description = " ".join(meta_data.get('1. Information', '').split(' ')[:2])
        last_refreshed = meta_data.get('3. Last Refreshed', None)
        output_size = meta_data.get('4. Output Size', 'N/A')
        time_zone = meta_data.get('5. Time Zone', 'N/A')

        time_series = data.get('Time Series (Daily)', {})
        for date, daily_data in time_series.items():
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            all_rows.append({
                'date': date_obj,
                'daily_open': float(daily_data['1. open']),
                'daily_high': float(daily_data['2. high']),
                'daily_low': float(daily_data['3. low']),
                'daily_close': float(daily_data['4. close']),
                'daily_volume': int(daily_data['5. volume']),
                'last_refreshed': datetime.strptime(last_refreshed, '%Y-%m-%d') if last_refreshed else None,
                'output_size': output_size,
                'time_zone': time_zone,
                'description': description,
                'symbol': symbol
            })
    return all_rows
print("Transformation successful")