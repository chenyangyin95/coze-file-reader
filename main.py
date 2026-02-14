

from fastapi import FastAPI, Body
import pandas as pd
from docx import Document
import io
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/read_file")
async def read_file(body: dict = Body(...)):
    file_url = body.get("file_url")
    if not file_url:
        return {"error": "file_url is required"}
    try:
        r = requests.get(file_url)
        r.raise_for_status()
        content = r.content
        filename = file_url.split("?")[0].split("/")[-1].lower()
    except Exception as e:
        return {"error": f"file_url download error: {str(e)}"}

    # 文件类型判断
    if filename.endswith(".csv"):
        try:
            df = pd.read_csv(io.BytesIO(content))
            return {"data": df.to_dict(orient="records")}
        except Exception as e:
            return {"error": str(e)}
    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        try:
            df = pd.read_excel(io.BytesIO(content))
            return {"data": df.to_dict(orient="records")}
        except Exception as e:
            return {"error": str(e)}
    elif filename.endswith(".docx"):
        try:
            doc = Document(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs)
            return {"text": text}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "unsupported file"}
