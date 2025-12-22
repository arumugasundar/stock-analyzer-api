import pandas as pd
import numpy as np

def run_computation(df: pd.DataFrame, x: int, y: int, i: int, j: int):
    # ---- Step 1: Cleanup & Sorting ----
    df = df[df['Volume'] != 0].copy()
    df['time'] = pd.to_datetime(df['time'], dayfirst=True)
    df.sort_values(by='time', inplace=True, ignore_index=True)

    # ---- Step 2: Volume Metrics (x-day average) ----
    volume_avg_col = f'Volume_{x}_day_avg'
    volume_pct_diff_col = f'Volume_vs_{x}_day_avg_%'
    df[volume_avg_col] = df['Volume'].rolling(window=x).mean().shift(1)
    df[volume_pct_diff_col] = ((df['Volume'] - df[volume_avg_col]) / df[volume_avg_col]) * 100 

    # ---- Step 3: Price Forward Return (y-day forward) ----
    price_return_col = f'Price_{y}_day_forward_return_%'
    df[price_return_col] = ((df['Price'].shift(-y) - df['Price']) / df['Price']) * 100

    # ---- Step 4: Binning Logic ----
    def get_range_label(val, interval):
        if pd.isna(val) or np.isinf(val): return None
        lower = (val // interval) * interval
        return f"{int(lower)} to {int(lower + interval)}"

    vol_range_col = f'{volume_pct_diff_col}_Range_{int(i)}'
    pri_range_col = f'{price_return_col}_Range_{int(j)}'
    df[vol_range_col] = df[volume_pct_diff_col].apply(lambda v: get_range_label(v, i))
    df[pri_range_col] = df[price_return_col].apply(lambda v: get_range_label(v, j))

    # ---- Step 5: Reorder ----
    df = df[['time', 'Volume', volume_avg_col, volume_pct_diff_col, vol_range_col, 
             'Price', price_return_col, pri_range_col]]

    # ---- Step 6: Sorted Frequency Table ----
    freq_table = pd.crosstab(df[vol_range_col], df[pri_range_col])
    
    sort_key = lambda label: int(str(label).split(" to ")[0]) if " to " in str(label) else float('inf')
    freq_table = freq_table.reindex(index=sorted(freq_table.index, key=sort_key), 
                                   columns=sorted(freq_table.columns, key=sort_key))

    return {"updated_df": df, "frequency_table": freq_table}