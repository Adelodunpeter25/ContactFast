# Contact Form API

A FastAPI-based contact form submission API that sends email notifications using Resend.

## Features

- RESTful API endpoint for contact form submissions
- Email notifications with styled HTML template
- CORS enabled for frontend integration
- Health check endpoint
- Email validation

## Tech Stack

- FastAPI
- Resend (Email service)
- Pydantic (Data validation)
- Python 3.13+

## Setup

### 1. Clone and Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory:

```env
RESEND_API_KEY=your_resend_api_key_here
FROM_EMAIL=noreply@yourdomain.com
TO_EMAIL=your-email@example.com
FRONTEND_URL=http://localhost:3000
```

**Required Variables:**
- `RESEND_API_KEY` - Get from [resend.com](https://resend.com)
- `FROM_EMAIL` - Verified sender email in Resend
- `TO_EMAIL` - Email address to receive form submissions
- `FRONTEND_URL` - Your frontend URL (optional with wildcard CORS)

### 3. Run Locally

```bash
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /
```

Response:
```json
{
  "contact api status": "healthy"
}
```

### Submit Contact Form
```
POST /submit
```

Request Body:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Inquiry",
  "message": "Hello, I have a question..."
}
```

Response:
```json
{
  "message": "Form submitted successfully!",
  "resend_response": {...}
}
```

## Deployment

### Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Deploy: `vercel`
3. Set environment variables in Vercel dashboard
4. Redeploy: `vercel --prod`

### Environment Variables in Vercel

Add these in your Vercel project settings:
- `RESEND_API_KEY`
- `FROM_EMAIL`
- `TO_EMAIL`
- `FRONTEND_URL`

## Email Template

The API uses a custom HTML email template (`email_template.html`) with:
- Aquamarine to dark purple gradient header
- Responsive design
- Styled message display
- Professional formatting

## License

MIT
