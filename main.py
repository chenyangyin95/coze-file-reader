
from fastapi import FastAPI, UploadFile, File, Body
import pandas as pd
from docx import Document
import io
import base64
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}


from typing import Optional
from fastapi import Request
from pydantic import BaseModel

class FileBody(BaseModel):
    file_b64: Optional[str] = None
    file_url: Optional[str] = None
    file_type: Optional[str] = None
    sheet_name: Optional[str] = None
    encoding: Optional[str] = None

@app.post("/read_file")
async def read_file(
    request: Request,
    file: Optional[UploadFile] = File(None),
    max_rows: Optional[int] = None,
    has_header: Optional[bool] = None,
    body: Optional[FileBody] = Body(None)
):
    content = None
    filename = None

    # 优先 file_b64
    if body and body.file_b64:
        try:
            content = base64.b64decode(body.file_b64)
            filename = body.file_type or "uploaded"
        except Exception as e:
            return {"error": f"base64 decode error: {str(e)}"}
    # 其次 file_url
    elif body and body.file_url:
        try:
            r = requests.get(body.file_url)
            r.raise_for_status()
            content = r.content
            filename = body.file_url.split("?")[0].split("/")[-1].lower()
        except Exception as e:
            return {"error": f"file_url download error: {str(e)}"}
    # 最后 UploadFile
    elif file is not None:
        content = await file.read()
        filename = file.filename.lower()
    else:
        return {"error": "No file_b64, file_url or file provided"}

    # 文件类型判断
    file_type = (body.file_type if body and body.file_type else None)
    if not file_type and filename:
        if filename.endswith(".csv"):
            file_type = "csv"
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_type = "excel"
        elif filename.endswith(".docx"):
            file_type = "docx"

    # CSV 文件
    if file_type == "csv":
        try:
            encoding = body.encoding if body and body.encoding else None
            df = pd.read_csv(io.BytesIO(content), encoding=encoding)
            if max_rows:
                df = df.head(max_rows)
            return {"data": df.to_dict(orient="records")}
        except Exception as e:
            return {"error": str(e)}

    # Excel 文件
    elif file_type == "excel":
        try:
            sheet_name = body.sheet_name if body and body.sheet_name else None
            df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name)
            if max_rows:
                df = df.head(max_rows)
            return {"data": df.to_dict(orient="records")}
        except Exception as e:
            return {"error": str(e)}

    # Word 文件
    elif file_type == "docx":
        try:
            doc = Document(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs)
            return {"text": text}
        except Exception as e:
            return {"error": str(e)}

    return {"error": "unsupported file"}
