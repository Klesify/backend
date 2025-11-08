import os
import tempfile
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/")
async def root():
    return {"message": "Fraud Detection API - Ready", "endpoints": ["/", "/detect-fraud"]}

@app.post("/detect-fraud")
async def detect_fraud_endpoint(
    phoneNumber: str = Form(...),
    audio: UploadFile = File(...)
):
    """
    Detect fraud from audio call recording - /detect-fraud endpoint
    Matches React Native FormData fields: phoneNumber and audio
    """
    return await process_fraud_detection(phoneNumber, audio)


async def process_fraud_detection(phoneNumber: str, audio: UploadFile):
    """
    Process fraud detection logic
    """
    
    # Validate file type
    file_ext = os.path.splitext(audio.filename)[1].lower() if audio.filename else ""
    allowed_extensions = [".wav", ".mp3", ".webm", ".opus", ".ogg", ".m4a"]
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid audio format. Supported: {', '.join(allowed_extensions)}. Got: {file_ext}"
        )
    
    temp_file_path = None
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            # Read and write audio content
            content = await audio.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        print(f"[DEBUG] Audio saved to: {temp_file_path}")
        
        # Run fraud detection
        fraud_result = await detect_fraud_from_audio(temp_file_path, phoneNumber)
        
        print(f"[DEBUG] Fraud detection complete. Score: {fraud_result.get('overall_scam_score')}")
        
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        # Return in the format expected by React Native
        return {
            "response": fraud_result
        }
        
    except Exception as e:
        print(f"[ERROR] Fraud detection failed: {str(e)}")
        # Clean up temp file if it exists
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )


# This is needed for Vercel
handler = app
