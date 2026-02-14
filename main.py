

from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from docx import Document
import io
import requests

app = FastAPI()

class FileInput(BaseModel):
    file: str

@app.post("/")
async def read_root(input_data: FileInput):
    file_url = input_data.file
    try:
        r = requests.get(file_url)
        r.raise_for_status()
        content = r.content
        filename = file_url.split("?")[0].split("/")[-1].lower()
    except Exception as e:
        return {"error": f"file_url download error: {str(e)}"}

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