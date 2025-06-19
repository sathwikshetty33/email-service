import logging
import json
import azure.functions as func
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import os
from aiosmtplib import SMTP
from email.message import EmailMessage
from dotenv import load_dotenv

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
    return {"message": "FastAPI on Azure Functions - Email Service", "status": "running"}

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

        # Send email
        smtp = SMTP(
            hostname=os.getenv("SMTP_HOST"),
            port=int(os.getenv("SMTP_PORT")),
            start_tls=True
        )

        await smtp.connect()
        await smtp.login(os.getenv("SMTP_EMAIL"), os.getenv("SMTP_PASSWORD"))
        await smtp.send_message(message)
        await smtp.quit()

        logger.info(f"Email sent successfully to {data.receiver_email}")
        return {
            "message": "Email sent successfully",
            "recipient": data.receiver_email,
            "subject": data.subject
        }
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# Azure Functions entry point
def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions HTTP trigger entry point"""
    
    logger.info(f'Processing {req.method} request to {req.url}')
    
    try:
        # Get the route from the request URL
        url_parts = req.url.split('/')
        
        # Extract the path after the function name
        if 'api' in url_parts:
            api_index = url_parts.index('api')
            if api_index + 1 < len(url_parts):
                route = '/' + '/'.join(url_parts[api_index + 1:])
            else:
                route = '/'
        else:
            route = '/'
        
        # Remove query parameters from route
        if '?' in route:
            route = route.split('?')[0]
            
        logger.info(f"Extracted route: {route}")
        
        # Handle different routes
        if req.method == 'GET':
            if route == '/' or route == '':
                response_data = {"message": "FastAPI on Azure Functions - Email Service", "status": "running"}
                
            elif route == '/health':
                response_data = {"status": "healthy", "service": "email-api"}
                
            else:
                return func.HttpResponse(
                    json.dumps({"detail": f"GET endpoint '{route}' not found"}),
                    status_code=404,
                    headers={"Content-Type": "application/json"}
                )
                
        elif req.method == 'POST':
            if route == '/send-email':
                try:
                    # Get request body
                    body = req.get_body().decode('utf-8')
                    if not body:
                        return func.HttpResponse(
                            json.dumps({"detail": "Request body is required"}),
                            status_code=400,
                            headers={"Content-Type": "application/json"}
                        )
                    
                    # Parse JSON body
                    body_json = json.loads(body)
                    
                    # Validate required fields
                    required_fields = ['receiver_email', 'subject', 'body_text']
                    missing_fields = [field for field in required_fields if field not in body_json]
                    
                    if missing_fields:
                        return func.HttpResponse(
                            json.dumps({"detail": f"Missing required fields: {', '.join(missing_fields)}"}),
                            status_code=400,
                            headers={"Content-Type": "application/json"}
                        )
                    
                    # Validate email format (basic check)
                    import re
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, body_json['receiver_email']):
                        return func.HttpResponse(
                            json.dumps({"detail": "Invalid email format"}),
                            status_code=400,
                            headers={"Content-Type": "application/json"}
                        )
                    
                    # Send email logic
                    try:
                        logger.info(f"Attempting to send email to {body_json['receiver_email']}")
                        
                        # Validate environment variables
                        required_env_vars = ["SMTP_HOST", "SMTP_PORT", "SMTP_EMAIL", "SMTP_PASSWORD"]
                        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
                        
                        if missing_vars:
                            logger.error(f"Missing environment variables: {missing_vars}")
                            return func.HttpResponse(
                                json.dumps({"detail": f"Server configuration error: Missing {', '.join(missing_vars)}"}),
                                status_code=500,
                                headers={"Content-Type": "application/json"}
                            )

                        # Create email message
                        message = EmailMessage()
                        message["From"] = os.getenv("SMTP_EMAIL")
                        message["To"] = body_json['receiver_email']
                        message["Subject"] = body_json['subject']
                        message.set_content(body_json['body_text'])

                        # Send email (synchronous version for Azure Functions)
                        import smtplib
                        import ssl
                        
                        context = ssl.create_default_context()
                        with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
                            server.starttls(context=context)
                            server.login(os.getenv("SMTP_EMAIL"), os.getenv("SMTP_PASSWORD"))
                            server.send_message(message)

                        logger.info(f"Email sent successfully to {body_json['receiver_email']}")
                        response_data = {
                            "message": "Email sent successfully",
                            "recipient": body_json['receiver_email'],
                            "subject": body_json['subject']
                        }
                        
                    except Exception as e:
                        logger.error(f"Failed to send email: {str(e)}")
                        return func.HttpResponse(
                            json.dumps({"detail": f"Failed to send email: {str(e)}"}),
                            status_code=500,
                            headers={"Content-Type": "application/json"}
                        )
                    
                except json.JSONDecodeError:
                    return func.HttpResponse(
                        json.dumps({"detail": "Invalid JSON in request body"}),
                        status_code=400,
                        headers={"Content-Type": "application/json"}
                    )
                except Exception as e:
                    logger.error(f"Error processing email request: {str(e)}")
                    return func.HttpResponse(
                        json.dumps({"detail": f"Error processing request: {str(e)}"}),
                        status_code=400,
                        headers={"Content-Type": "application/json"}
                    )
            else:
                return func.HttpResponse(
                    json.dumps({"detail": f"POST endpoint '{route}' not found"}),
                    status_code=404,
                    headers={"Content-Type": "application/json"}
                )
        else:
            return func.HttpResponse(
                json.dumps({"detail": f"Method {req.method} not allowed"}),
                status_code=405,
                headers={"Content-Type": "application/json"}
            )

        # Return successful response
        return func.HttpResponse(
            json.dumps(response_data),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"detail": "Internal server error", "error": str(e)}),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )