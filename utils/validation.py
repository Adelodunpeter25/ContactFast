"""
Validation utilities for spam detection and email validation.

Contains functions for detecting disposable emails, spam content,
and other validation checks.
"""

import re
from urllib.parse import urlparse
from pathlib import Path

# Load disposable domains from config file
def _load_disposable_domains() -> set:
    """Load disposable domains from configuration file"""
    config_path = Path(__file__).parent.parent / "disposable_domains.conf"
    try:
        with open(config_path, 'r') as f:
            return {line.strip().lower() for line in f if line.strip()}
    except FileNotFoundError:
        return set()

DISPOSABLE_DOMAINS = _load_disposable_domains()


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
