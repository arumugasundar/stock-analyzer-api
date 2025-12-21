import pandas as pd

def validate_df(df, sheet_name="Default"):
    errors = []
    # 1. Header Validation
    expected_headers = ["time", "Price", "Volume"]
    if list(df.columns) != expected_headers:
        return [f"Sheet '{sheet_name}': Invalid headers. Expected {expected_headers}"]

    # 2. Data Validation
    for i, row in df.iterrows():
        row_num = i + 2  # Adjust for 0-index and header row
        # Time validation
        try:
            pd.to_datetime(row['time'], format='%d/%m/%Y', errors='raise')
        except:
            errors.append(f"Row {row_num}: 'time' must be dd-mm-yyyy")
        # Price validation
        if not isinstance(row['Price'], (float, int)):
            errors.append(f"Row {row_num}: 'Price' must be a float")
        # Volume validation
        if not (isinstance(row['Volume'], int) and row['Volume'] >= 0):
            errors.append(f"Row {row_num}: 'Volume' must be non-negative integer")

    # 3. Sort Validation
    if not pd.to_datetime(df['time'], dayfirst=True).is_monotonic_increasing:
        errors.append(f"Sheet '{sheet_name}': 'time' column is not in ascending order")
    
    return errors