from email_validator import EmailNotValidError, validate_email


class EmailValidator:
    @staticmethod
    def validate_syntax(email: str) -> bool:
        try:
            validate_email(email, check_deliverability=False)
            return True
        except EmailNotValidError:
            return False
