from fastapi import FastAPI, UploadFile, File
import pandas as pd
from docx import Document
import io

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/read_file")
async def read_file(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename.lower()

    # CSV 文件
    if filename.endswith(".csv"):
        try:
            df = pd.read_csv(io.BytesIO(content))
            return {"data": df.to_dict(orient="records")}
        except Exception as e:
            return {"error": str(e)}

    # Excel 文件
    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        try:
            df = pd.read_excel(io.BytesIO(content))
            return {"data": df.to_dict(orient="records")}
        except Exception as e:
            return {"error": str(e)}

    # Word 文件
    elif filename.endswith(".docx"):
        try:
            doc = Document(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs)
            return {"text": text}
        except Exception as e:
            return {"error": str(e)}

    return {"error": "unsupported file"}