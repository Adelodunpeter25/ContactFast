"""
Validation utilities for spam detection and email validation.

Contains functions for detecting disposable emails, spam content,
and other validation checks.
"""

import re
from urllib.parse import urlparse

# Disposable email domains
DISPOSABLE_DOMAINS = {
    'tempmail.com', 'guerrillamail.com', '10minutemail.com', 'throwaway.email',
    'mailinator.com', 'trashmail.com', 'fakeinbox.com', 'yopmail.com',
    'temp-mail.org', 'getnada.com', 'maildrop.cc', 'sharklasers.com',
    'mintemail.com', 'emailondeck.com', 'mohmal.com', 'mytemp.email',
    'dispostable.com', 'throwawaymail.com', 'tempinbox.com', 'guerrillamailblock.com',
    'spamgourmet.com', 'mailnesia.com', 'mailcatch.com', 'mailnator.com',
    'getairmail.com', 'harakirimail.com', 'anonymousemail.me', 'deadaddress.com',
    'emailsensei.com', 'mailexpire.com', 'tempr.email', 'tempmail.net',
    'disposablemail.com', 'burnermail.io', 'guerrillamail.net', 'guerrillamail.org',
    'guerrillamail.biz', 'spam4.me', 'grr.la', 'guerrillamail.de',
    'trbvm.com', 'mailforspam.com', 'spambox.us', 'incognitomail.org',
    'tmailinator.com', 'spamfree24.org', 'spamfree24.com', 'spamfree24.eu',
    'spamfree24.net', 'spamfree24.info', 'spamfree24.de', 'wegwerfmail.de',
    'wegwerfmail.net', 'wegwerfmail.org', 'trashmail.net', 'trashmail.org',
    'trashmail.me', 'trashmail.de', 'trashmail.at', 'trashmail.fr',
    'trashmail.ws', 'trash-mail.com', 'trash-mail.de', 'trash-mail.at',
    'trash-mail.cf', 'trash-mail.ga', 'trash-mail.gq', 'trash-mail.ml',
    'trash-mail.tk', 'mailtemp.info', 'mailtemp.net', 'mailtemp.org',
    'tempmail.de', 'tempmail.eu', 'tempmail.us', 'tempmail.it',
    'tempmail.fr', 'tempmail.co', 'tempmail.ninja', 'tempmail.plus',
    'tempmail.email', 'tempmail.io', 'tempmail.dev', 'tempmail.top'
}


def extract_domain(website_url: str) -> str:
    """Extract domain from website URL"""
    try:
        parsed = urlparse(website_url)
        return parsed.netloc or parsed.path
    except:
        return website_url


def is_disposable_email(email: str) -> bool:
    """Check if email is from a disposable domain"""
    domain = email.split('@')[-1].lower()
    return domain in DISPOSABLE_DOMAINS


def is_spam_content(message: str, subject: str = "") -> bool:
    """Detect spam patterns in message content"""
    text = (message + " " + subject).lower()
    
    # Spam keywords
    spam_keywords = [
        'viagra', 'cialis', 'casino', 'lottery', 'prize', 'winner',
        'click here', 'buy now', 'limited time', 'act now', 'free money'
    ]
    
    for keyword in spam_keywords:
        if keyword in text:
            return True
    
    # Multiple URLs (more than 3)
    url_count = len(re.findall(r'http[s]?://', text))
    if url_count > 3:
        return True
    
    # Excessive repeated characters
    if re.search(r'(.)\1{10,}', text):
        return True
    
    # All caps message (more than 70% uppercase)
    if len(message) > 20:
        upper_ratio = sum(1 for c in message if c.isupper()) / len(message)
        if upper_ratio > 0.7:
            return True
    
    return False
