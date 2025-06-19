# FastAPI Email Service

A minimal and reliable email service built using FastAPI, designed to send emails via a REST API. It utilizes environment variables for secure SMTP configuration and provides health and root endpoints for service monitoring.

## Features

- **RESTful API**: Easily send emails via HTTP POST.
- **Health Checks**: Quick endpoints for service status.
- **Environment-based Configuration**: Keeps credentials out of source code.
- **Logging**: Info and error logs for email operations.

## Technologies Used

- Python (FastAPI, pydantic)
- SMTP for email sending
- Shell (for scripting/deployment)
- dotenv for environment variable management

---

## Getting Started

### Prerequisites

- Python 3.7+
- An SMTP email account (e.g., Gmail, Outlook, etc.)
- [pip](https://pip.pypa.io/en/stable/)

### Installation

1. **Clone the repo**
    ```sh
    git clone https://github.com/sathwikshetty33/email-service.git
    cd email-service
    ```

2. **Install dependencies**
    ```sh
    pip install -r requirements.txt
    ```

3. **Create a `.env` file** in the project root with the following variables:
    ```
    SMTP_HOST=smtp.yourprovider.com
    SMTP_PORT=587
    SMTP_EMAIL=your@email.com
    SMTP_PASSWORD=yourpassword
    PORT=8000                # Optional, defaults to 8000
    ```

---

## Running the Service

```sh
python main.py
```
or (if using Uvicorn directly)
```sh
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## API Documentation

### Root Endpoint

- **GET /**  
  Returns status and service name.

### Health Endpoint

- **GET /health**  
  Returns service health status.

### Send Email Endpoint

- **POST /send-email**  
  Sends an email to the specified recipient.

#### Request Format

- **URL:** `/send-email`
- **Method:** `POST`
- **Content-Type:** `application/json`

#### Example Request Body

```json
{
  "receiver_email": "recipient@example.com",
  "subject": "Hello from FastAPI",
  "body_text": "This is a test email sent from the FastAPI Email Service."
}
```

#### Request Parameters

| Field          | Type   | Required | Description                     |
|----------------|--------|----------|---------------------------------|
| receiver_email | string | Yes      | Email address of the recipient  |
| subject        | string | Yes      | Subject of your email           |
| body_text      | string | Yes      | The plain text body of the email|

#### Example Response

```json
{
  "message": "Email sent successfully",
  "recipient": "recipient@example.com",
  "subject": "Hello from FastAPI"
}
```

#### Error Response Example

```json
{
  "detail": "Failed to send email: <error details>"
}
```

---

## Environment Variables

- `SMTP_HOST` (required): Your SMTP server host, e.g., smtp.gmail.com
- `SMTP_PORT` (required): SMTP server port, usually 587 for TLS
- `SMTP_EMAIL` (required): Sender email address
- `SMTP_PASSWORD` (required): SMTP account password or app password
- `PORT` (optional): Port to run the service (default: 8000)

---

## License

This project is licensed under the MIT License.

---

**Maintainer:** [sathwikshetty33](https://github.com/sathwikshetty33)
