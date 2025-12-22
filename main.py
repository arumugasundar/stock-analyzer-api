from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import pandas as pd
import io

from process_file import process_excel_or_csv

app = FastAPI()
origins = [ "https://doqsme6l7tigx.cloudfront.net", "http://localhost:5173", "http://localhost:4173" ]
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
    
    try:
        # 1. Size & Extension Validation
        ALLOWED_EXTENSIONS = {'.csv', '.xlsx'}
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        
        if inputExcelFile.size > MAX_FILE_SIZE:
            raise HTTPException(400, "File is too large (>5MB)")
        
        if not any(inputExcelFile.filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise HTTPException(400, "Invalid file type")

        content = await inputExcelFile.read()
        
        # 2. Call the external processing logic
        params = {
            "volumeLookbackDays": volumeLookbackDays,
            "priceForwardDays": priceForwardDays,
            "volumeBinSize": volumeBinSize,
            "priceReturnBinSize": priceReturnBinSize
        }
        
        processed_output = process_excel_or_csv(content, inputExcelFile.filename, params)

        # 3. Return successful file stream
        return StreamingResponse(
            processed_output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=result_{inputExcelFile.filename}.xlsx"}
        )

    except HTTPException as e:
        # Re-raise FastAPI HTTP exceptions to return their defined status codes and detail
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    
    except Exception as e:
        # Catch unexpected errors and return as JSON
        return JSONResponse(status_code=400, content={"error": str(e)})