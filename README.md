# ContactFast

A FastAPI-based contact form API that requires **no signup or configuration** for users. Just copy-paste the form code snippet and you are done!

## 🚀 Features

- **Zero Setup** - No account creation, no API keys, no dashboard
- **Auto Verification** - First submission automatically verifies your domain
- **Secure** - Rate limiting, origin validation, spam prevention
- **Multi-Tenant** - Unlimited users can use the same API
- **Simple Integration** - No backend, no third party integration
## 🎯 How It Works

1. User copies code snippet for their desired framework
2. Changes `to` email to their own
3. Adds form to their website
4. First submission auto-verifies the domain and sends:
   - The contact form submission
   - A verification confirmation email
5. All future submissions work automatically

## 📋 For Users (How to Use)

### Step 1: Copy Your Desired Code Snippet


[View All Code Snippets](./FORM_EXAMPLES.md)


### Step 2: Customize

- Change `to` to your email address
- Update `website_name` with your site name
- Update `website_url` with your site URL

### Step 3: Test

- Submit the form once
- Check your email for:
  - The submitted contact form
  - A verification confirmation email
- Done! Your domain is automatically verified and all future submissions will arrive in your inbox.

## 🛠️ Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL (Database)
- Resend (Email service)
- Pydantic (Data validation)

## 🔧 Setup (For Developers)

### 1. Clone and Install

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file:

```env
RESEND_API_KEY=your_resend_api_key_here
FROM_EMAIL=noreply@yourdomain.com
BASE_URL=http://localhost:8000
DATABASE_URL=postgresql://user:password@host:port/database
```

### 3. Run Locally

```bash
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Health Check
```
GET /
```

Response:
```json
{
  "status": "healthy",
  "message": "CoontactFast API"
}
```

### Submit Contact Form
```
POST /submit
```

Request Body:
```json
{
  "to": "recipient@example.com",
  "website_name": "My Website",
  "website_url": "https://mywebsite.com",
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Inquiry",
  "message": "Hello, I have a question..."
}
```

**First Submission Response:**
```json
{
  "message": "Form submitted successfully! Domain auto-verified.",
  "domain": "example.com",
  "resend_response": {...}
}
```

**Subsequent Submissions:**
```json
{
  "message": "Form submitted successfully!",
  "resend_response": {...}
}
```

## 🎨 Customization

Users can style the form however they want. The API only cares about the form data, not the styling.

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

---

**Built with ❤️ for developers who want simple contact forms without the hassle.**
