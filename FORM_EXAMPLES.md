# Contact Form Examples

**Choose your framework:** [HTML](#html) • [JavaScript](#javascript) • [React](#react) • [Vue](#vue) • [Next.js](#nextjs) • [Angular](#angular)

---

## HTML

```html
<form action="https://contact-portfolio-form.vercel.app/submit" method="POST">
  <input type="hidden" name="to" value="your@email.com" />
  <input type="hidden" name="website_name" value="My Website" />
  <input type="hidden" name="website_url" value="https://mywebsite.com" />
  
  <input type="text" name="name" placeholder="Your Name" required />
  <input type="email" name="email" placeholder="Your Email" required />
  <input type="text" name="subject" placeholder="Subject" required />
  <textarea name="message" placeholder="Your Message" required></textarea>
  <button type="submit">Send Message</button>
</form>
```

---

## JavaScript

```html
<form id="contactForm">
  <input type="text" id="name" placeholder="Your Name" required />
  <input type="email" id="email" placeholder="Your Email" required />
  <input type="text" id="subject" placeholder="Subject" required />
  <textarea id="message" placeholder="Your Message" required></textarea>
  <button type="submit">Send Message</button>
</form>
<div id="status"></div>

<script>
document.getElementById('contactForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const response = await fetch('https://contact-portfolio-form.vercel.app/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      to: 'your@email.com',
      website_name: 'My Website',
      website_url: 'https://mywebsite.com',
      name: document.getElementById('name').value,
      email: document.getElementById('email').value,
      subject: document.getElementById('subject').value,
      message: document.getElementById('message').value
    })
  });

  const data = await response.json();
  document.getElementById('status').textContent = data.message || data.detail;
});
</script>
```

---

## React

```jsx
import { useState } from 'react';

export default function ContactForm() {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
  const [status, setStatus] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const res = await fetch('https://contact-portfolio-form.vercel.app/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        to: 'your@email.com',
        website_name: 'My Website',
        website_url: 'https://mywebsite.com',
        ...form
      })
    });

    const data = await res.json();
    setStatus(data.message || data.detail);
    if (res.ok) setForm({ name: '', email: '', subject: '', message: '' });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Name" required />
      <input value={form.email} onChange={e => setForm({...form, email: e.target.value})} placeholder="Email" required />
      <input value={form.subject} onChange={e => setForm({...form, subject: e.target.value})} placeholder="Subject" required />
      <textarea value={form.message} onChange={e => setForm({...form, message: e.target.value})} placeholder="Message" required />
      <button type="submit">Send</button>
      {status && <p>{status}</p>}
    </form>
  );
}
```

---

## Vue

```vue
<template>
  <form @submit.prevent="submit">
    <input v-model="form.name" placeholder="Name" required />
    <input v-model="form.email" placeholder="Email" required />
    <input v-model="form.subject" placeholder="Subject" required />
    <textarea v-model="form.message" placeholder="Message" required />
    <button type="submit">Send</button>
    <p v-if="status">{{ status }}</p>
  </form>
</template>

<script setup>
import { ref, reactive } from 'vue';

const form = reactive({ name: '', email: '', subject: '', message: '' });
const status = ref('');

const submit = async () => {
  const res = await fetch('https://contact-portfolio-form.vercel.app/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      to: 'your@email.com',
      website_name: 'My Website',
      website_url: 'https://mywebsite.com',
      ...form
    })
  });

  const data = await res.json();
  status.value = data.message || data.detail;
  if (res.ok) Object.keys(form).forEach(k => form[k] = '');
};
</script>
```

---

## Next.js

```jsx
'use client';
import { useState } from 'react';

export default function ContactForm() {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
  const [status, setStatus] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const res = await fetch('https://contact-portfolio-form.vercel.app/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        to: 'your@email.com',
        website_name: 'My Website',
        website_url: 'https://mywebsite.com',
        ...form
      })
    });

    const data = await res.json();
    setStatus(data.message || data.detail);
    if (res.ok) setForm({ name: '', email: '', subject: '', message: '' });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={form.name} onChange={e => setForm({...form, name: e.target.value})} placeholder="Name" required />
      <input value={form.email} onChange={e => setForm({...form, email: e.target.value})} placeholder="Email" required />
      <input value={form.subject} onChange={e => setForm({...form, subject: e.target.value})} placeholder="Subject" required />
      <textarea value={form.message} onChange={e => setForm({...form, message: e.target.value})} placeholder="Message" required />
      <button type="submit">Send</button>
      {status && <p>{status}</p>}
    </form>
  );
}
```

---

## Angular

```typescript
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  template: `
    <form (ngSubmit)="submit()" #f="ngForm">
      <input [(ngModel)]="form.name" name="name" placeholder="Name" required />
      <input [(ngModel)]="form.email" name="email" placeholder="Email" required />
      <input [(ngModel)]="form.subject" name="subject" placeholder="Subject" required />
      <textarea [(ngModel)]="form.message" name="message" placeholder="Message" required></textarea>
      <button type="submit" [disabled]="!f.valid">Send</button>
      <p *ngIf="status">{{ status }}</p>
    </form>
  `
})
export class ContactFormComponent {
  form = { name: '', email: '', subject: '', message: '' };
  status = '';

  constructor(private http: HttpClient) {}

  submit() {
    this.http.post('https://contact-portfolio-form.vercel.app/submit', {
      to: 'your@email.com',
      website_name: 'My Website',
      website_url: 'https://mywebsite.com',
      ...this.form
    }).subscribe({
      next: (res: any) => {
        this.status = 'Message sent!';
        this.form = { name: '', email: '', subject: '', message: '' };
      },
      error: (err) => this.status = err.error?.detail || 'Error'
    });
  }
}
```

---

## Configuration

Update these values in the code:

- **`to`** → Your email address
- **`website_name`** → Your site name
- **`website_url`** → Your site URL

## Setup

1. Add form to your website
2. Submit once to receive activation email
3. Click activation link
4. Done! Future submissions arrive automatically
