class Regex:
    LETTERS_AND_NUMBERS = r"^[a-zA-Z0-9]+$"
    LETTERS = r"^[a-zA-Z]+$"
    PHONE_NUMBER = r"^\d{10}$"
    PASSWORD = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$"
    USER_NAME = r"^[a-zA-Z]+( [a-zA-Z]+)?$"
