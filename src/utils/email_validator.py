# utils/email_validator.py - CREATE THIS FILE
import dns.resolver
import smtplib
import socket
from email_validator import validate_email, EmailNotValidError

class EmailValidator:
    @staticmethod
    def validate_syntax(email: str) -> bool:
        """Basic syntax validation (what Pydantic already does)"""
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    @staticmethod 
    def check_domain_mx(email: str) -> bool:
        """Check if domain has MX records"""
        domain = email.split('@')[1]
        try:
            dns.resolver.resolve(domain, 'MX')
            return True
        except:
            return False
    
    @staticmethod
    def verify_smtp(email: str) -> bool:
        """SMTP verification - checks if mailbox exists"""
        # Implementation for SMTP checking
        pass
