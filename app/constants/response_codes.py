class ResponseCode:
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail


class NayaResponseCodes:
    @staticmethod
    def create_response_code(code: str, detail: str) -> ResponseCode:
        """Create response code method"""
        return ResponseCode(code, detail)

    INVALID_DATE_BIRTH_PAYLOAD = create_response_code("E001", "Invalid birth date")
    INVALID_PASSWORD = create_response_code("E002", "Invalid password")
    EXISTING_EMAIL = create_response_code("E003", "User with this email already exists")
    UNEXISTING_PATIENT = create_response_code(
        "E004", "Patient with this id does not exist"
    )
    UNEXISTING_THERAPIST = create_response_code(
        "E005", "Therapist with this id does not exist"
    )
    INVALID_PASSWORDS_MATCH = create_response_code("E006", "Passwords does not match")
    UNEXISTING_CODE = create_response_code("E007", "Code with this id does not exist")
    ALREADY_USED_CODE = create_response_code("E008", "Code has already been used")
    VERIFIED_USER = create_response_code("E009", "User verified successfully")
    UNEXISTING_USER = create_response_code("E010", "User does not exist")
    UNVERIFIED_USER = create_response_code("E011", "User is not verified")
    INVALID_CODE = create_response_code("E012", "Invalid code")
    CONNECTION_EXISTS = create_response_code(
        "E013", "Connection with this therapist already exists"
    )
    APPOINTMENT_EXISTS = create_response_code("E018", "You already have an appointment scheduled for this date")
    NO_APPOINTMENTS = create_response_code("E017", "No appointments were found for this therapist")
    UNEXISTING_CONNECTION = create_response_code("E014", "Connection does not exist")
    NO_VERIFIED_THERAPISTS = create_response_code( "E016", "No verified therapists found" )
    NO_CONNECTED_PATIENTS = create_response_code("E015", "No patients are connected to this therapist")
