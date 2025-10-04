# Zero-Setup Contact Form API

A FastAPI-based contact form API that requires **no signup or configuration** for users. Just copy-paste the form HTML and you're done!

## 🚀 Features

- **Zero Setup** - No account creation, no API keys, no dashboard
- **Email Verification** - First submission triggers activation email to recipient
- **Secure** - Rate limiting, origin validation, spam prevention
- **Multi-Tenant** - Unlimited users can use the same API
- **Simple Integration** - Just HTML form, no JavaScript required

## 🎯 How It Works

1. User copies form HTML template
2. Changes `to` email to their own
3. Adds form to their website
4. First submission sends activation email
5. User clicks activation link
6. All future submissions work automatically

## 📋 For Users (How to Use)

### Step 1: Copy This Form

```html
<form action="https://your-api.vercel.app/submit" method="POST">
  <!-- CHANGE THESE VALUES -->
  <input type="hidden" name="to" value="your@email.com" />
  <input type="hidden" name="website_name" value="My Website" />
  <input type="hidden" name="website_url" value="https://mywebsite.com" />
  
  <!-- Form Fields -->
  <input type="text" name="name" placeholder="Your Name" required />
  <input type="email" name="email" placeholder="Your Email" required />
  <input type="text" name="subject" placeholder="Subject" required />
  <textarea name="message" placeholder="Your Message" required></textarea>
  <button type="submit">Send Message</button>
</form>
```

### Step 2: Customize

- Change `to` to your email address
- Update `website_name` with your site name
- Update `website_url` with your site URL

### Step 3: Test

- Submit the form once
- Check your email for activation link
- Click the link to activate
- Done! All future submissions will arrive in your inbox

## 🛠️ Tech Stack

- FastAPI
- SQLAlchemy (SQLite database)
- Resend (Email service)
- Pydantic (Data validation)
- Python 3.13+

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
```

### 3. Run Locally

```bash
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`

Test with `example_form.html` by opening it in your browser.

## 📡 API Endpoints

### Health Check
```
GET /
```

Response:
```json
{
  "status": "healthy",
  "message": "Zero-Setup Contact Form API"
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
  "message": "Activation required",
  "detail": "A confirmation email has been sent to recipient@example.com..."
}
```

**After Activation:**
```json
{
  "message": "Form submitted successfully!",
  "resend_response": {...}
}
```

### Activate Form
```
GET /activate/{token}
```

Returns HTML page confirming activation.

## 🔒 Security Features

### Rate Limiting
- 5 submissions per hour per IP address
- 10 submissions per hour per activated form
- 3 activation emails per day per recipient email

### Validation
- Origin header validation
- Email format validation
- Required field validation
- Minimum message length

### Abuse Prevention
- Form must be activated before use
- Recipient controls activation
- Rate limits prevent spam
- Database tracks all submissions

## 📊 Database Schema

```sql
verified_forms:
- form_hash (primary key) - unique identifier
- recipient_email - where submissions are sent
- origin_domain - website domain
- website_name - site name
- website_url - site URL
- verified - activation status
- activation_token - unique token for activation
- created_at - timestamp
- last_submission_at - last submission time
- submission_count - total submissions
```

## 🚀 Deployment

### Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Deploy: `vercel`
3. Set environment variables in Vercel dashboard:
   - `RESEND_API_KEY`
   - `FROM_EMAIL`
   - `BASE_URL` (your Vercel URL)
4. Redeploy: `vercel --prod`

**Note:** For production, consider using PostgreSQL instead of SQLite.

## 📧 Email Templates

### Activation Email
- Gradient header (aquamarine to purple)
- Shows website name and URL
- Clear activation button
- Security notice

### Submission Email
- Professional formatting
- Shows sender details
- Displays message content
- Includes website context

## 🎨 Customization

Users can style the form however they want. The API only cares about the form data, not the styling.

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

---

**Built with ❤️ for developers who want simple contact forms without the hassle.**
