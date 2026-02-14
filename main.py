

from fastapi import FastAPI
from pydantic import BaseModel

import pandas as pd
from docx import Document
import io
import requests
import re

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

    # 用正则提取最后一个有效后缀
    match = re.search(r'(\.csv|\.xlsx|\.xls|\.docx)(?!.*(\.csv|\.xlsx|\.xls|\.docx))', filename)
    ext = match.group(1) if match else None

    if ext == ".csv":
        try:
            df = pd.read_csv(io.BytesIO(content))
            return {"data": df.to_dict(orient="records")}
        except Exception as e:
            return {"error": str(e)}
    elif ext in (".xlsx", ".xls"):
        try:
            df = pd.read_excel(io.BytesIO(content))
            return {"data": df.to_dict(orient="records")}
        except Exception as e:
            return {"error": str(e)}
    elif ext == ".docx":
        try:
            doc = Document(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs)
            return {"text": text}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "unsupported file"}