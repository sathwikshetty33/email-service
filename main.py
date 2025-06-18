from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import os
from aiosmtplib import SMTP
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class EmailRequest(BaseModel):
    receiver_email: EmailStr
    subject: str
    body_text: str

@app.post("/send-email")
async def send_email(data: EmailRequest):
    try:
        message = EmailMessage()
        message["From"] = os.getenv("SMTP_EMAIL")
        message["To"] = data.receiver_email
        message["Subject"] = data.subject
        message.set_content(data.body_text)

        smtp = SMTP(
            hostname=os.getenv("SMTP_HOST"),
            port=int(os.getenv("SMTP_PORT")),
            start_tls=True
        )

        await smtp.connect()
        await smtp.login(os.getenv("SMTP_EMAIL"), os.getenv("SMTP_PASSWORD"))
        await smtp.send_message(message)
        await smtp.quit()

        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
