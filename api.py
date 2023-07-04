from fastapi import FastAPI, UploadFile, File
import service

app = FastAPI()


@app.post('/upload_file')
async def upload_file(file: UploadFile = File(...)):
    return await service.upload_file(file)
