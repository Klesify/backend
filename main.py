from urllib import response
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fraud_detector import detect_fraud_from_audio


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestData(BaseModel):
    audio: str  # Base64 encoded audio blob
    phone_number: str


class ResponseData(BaseModel):
    message: str
    # Add other response fields


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/")
async def your_function(data: RequestData):
    """
    Your POST endpoint - define the function implementation here
    """

    response = await detect_fraud_from_audio(data.audio, data.phone_number)
    # Your implementation here
    return {"response": response}


# This is needed for Vercel
handler = app
