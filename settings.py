import os
from dotenv import load_dotenv


load_dotenv()

UVICORN_HOST = os.environ.get("UVICORN_HOST", '0.0.0.0')
UVICORN_PORT = os.environ.get("UVICORN_PORT", '8000')

AWS_S3_ENDPOINT_URL = os.environ.get("AWS_S3_ENDPOINT_URL", 'http://127.0.0.1:9000')
AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME", 'uchetkzbucket')
AWS_S3_ACCESS_KEY_ID = os.environ.get("AWS_S3_ACCESS_KEY_ID", 'minioadmin')
AWS_S3_SECRET_KEY = os.environ.get("AWS_S3_SECRET_KEY", 'minioadmin')

CHUNK_SIZE = os.environ.get("CHUNK_SIZE", 5242880)

