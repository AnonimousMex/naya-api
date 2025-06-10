from enum import Enum


class UserGenders(Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"


class UserRoles(Enum):
    PATIENT = "PATIENT"
    THERAPIST = "THERAPIST"


class VerificationModels(Enum):
    VERIFICATION_CODE_MODEL = "VERIFICATION_CODE_MODEL"
    VERIFICATION_CODE_PASSWORD_RESET_MODEL = "VERIFICATION_CODE_PASSWORD_RESET_MODEL"
