from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import io

from compute import run_computation
from validate import validate_df

app = FastAPI()
origins = [ "https://d2yr116unbb4sb.cloudfront.net/", "http://localhost:5173" ]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"message": "FastAPI Server is live"}

@app.post("/upload")
async def upload_data(
    volumeLookbackDays: int = Form(...),
    priceForwardDays: int = Form(...),
    volumeBinSize: float = Form(...),
    priceReturnBinSize: float = Form(...),
    inputExcelFile: UploadFile = File(...)
):
    
    # 1. Size & Extension Validation
    ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    if inputExcelFile.size > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (>5MB)")
    if not any(inputExcelFile.filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(400, "Invalid file type")

    content = await inputExcelFile.read()
    output = io.BytesIO()
    all_errors = []
    data_map = {}
    
    # 2. Process Files
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if inputExcelFile.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
            all_errors.extend(validate_df(df))
            if all_errors:
                raise HTTPException(status_code=400, detail={"errors": all_errors})
            data_map["CSV_Data"] = pd.read_csv(io.BytesIO(content))
            for name, df in data_map.items():
                result = run_computation(df, volumeLookbackDays, priceForwardDays, volumeBinSize, priceReturnBinSize)
                result["updated_df"].to_excel(writer, sheet_name=f"{name}_Computed", index=False)
                result["frequency_table"].to_excel(writer, sheet_name=f"{name}_FreqTable")
        else:
            excel_file = pd.ExcelFile(io.BytesIO(content))
            for sheet in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet)
                all_errors.extend(validate_df(df, sheet))
                if all_errors:
                    raise HTTPException(status_code=400, detail={"errors": all_errors})
                data_map.update({name: excel_file.parse(name) for name in excel_file.sheet_names})
                for name, df in data_map.items():
                    result = run_computation(df, volumeLookbackDays, priceForwardDays, volumeBinSize, priceReturnBinSize)
                    result["updated_df"].to_excel(writer, sheet_name=f"{name}_Computed", index=False)
                    result["frequency_table"].to_excel(writer, sheet_name=f"{name}_FreqTable")
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=result_{inputExcelFile.filename}.xlsx"}
    )