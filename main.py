from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


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
    # Define your request model fields here
    pass


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
    # Your implementation here
    return {"message": "Success"}


# This is needed for Vercel
handler = app
