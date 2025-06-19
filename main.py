import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="FastAPI Email Service", version="1.0.0")

class EmailRequest(BaseModel):
    receiver_email: EmailStr
    subject: str
    body_text: str

@app.get("/")
async def root():
    return {"message": "FastAPI Email Service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "email-api"}

@app.post("/send-email")
async def send_email(data: EmailRequest):
    try:
        logger.info(f"Attempting to send email to {data.receiver_email}")
        
        # Validate environment variables
        required_env_vars = ["SMTP_HOST", "SMTP_PORT", "SMTP_EMAIL", "SMTP_PASSWORD"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing environment variables: {missing_vars}")
            raise HTTPException(
                status_code=500, 
                detail=f"Server configuration error: Missing {', '.join(missing_vars)}"
            )

        # Create email message
        message = EmailMessage()
        message["From"] = os.getenv("SMTP_EMAIL")
        message["To"] = data.receiver_email
        message["Subject"] = data.subject
        message.set_content(data.body_text)

        # Send email using synchronous SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls(context=context)
            server.login(os.getenv("SMTP_EMAIL"), os.getenv("SMTP_PASSWORD"))
            server.send_message(message)

        logger.info(f"Email sent successfully to {data.receiver_email}")
        return {
            "message": "Email sent successfully",
            "recipient": data.receiver_email,
            "subject": data.subject
        }
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)