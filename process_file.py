import pandas as pd
import io
from fastapi import HTTPException
from compute import run_computation
from validate import validate_df

def process_excel_or_csv(content, filename, params):
    output = io.BytesIO()
    all_errors = []
    data_map = {}
    
    volumeLookbackDays = params['volumeLookbackDays']
    priceForwardDays = params['priceForwardDays']
    volumeBinSize = params['volumeBinSize']
    priceReturnBinSize = params['priceReturnBinSize']

    if filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(content))
        all_errors.extend(validate_df(df))
        if all_errors:
            raise HTTPException(status_code=400, detail={"errors": all_errors})
        
        data_map["CSV_Data"] = df
    else:
        excel_file = pd.ExcelFile(io.BytesIO(content))
        for sheet in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet)
            all_errors.extend(validate_df(df, sheet))
        
        if all_errors:
            raise HTTPException(status_code=400, detail={"errors": all_errors})
        
        data_map.update({name: excel_file.parse(name) for name in excel_file.sheet_names})
    
    if not data_map:
        raise HTTPException(status_code=400, detail="No data found to process.")

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for name, df in data_map.items():
            result = run_computation(df, volumeLookbackDays, priceForwardDays, volumeBinSize, priceReturnBinSize)
            result["updated_df"].to_excel(writer, sheet_name=f"{name}_Computed", index=False)
            result["frequency_table"].to_excel(writer, sheet_name=f"{name}_FreqTable")

    output.seek(0)
    return output