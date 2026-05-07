from enum import Enum


class UserRoles(Enum):
    PATIENT = "PATIENT"
    THERAPIST = "THERAPIST"
    PARENT = "PARENT"


class VerificationModels(Enum):
    VERIFICATION_CODE_MODEL = "VERIFICATION_CODE_MODEL"
    CONNECTION_CODE_MODEL = "CONNECTION_CODE_MODEL"
    VERIFICATION_CODE_PASSWORD_RESET_MODEL = "VERIFICATION_CODE_PASSWORD_RESET_MODEL"


class ActivityTypes(Enum):
    KINESTESICO = "KINESTHETIC"
    VISUAL = "VISUAL"
    AUDITORY = "AUDITORY"


class CopingCategories(str, Enum):
    """Tipo de afrontamiento detectado en una respuesta."""

    AVOIDANCE = "avoidance"
    FRUSTRATION = "frustration"
    ABANDONMENT = "abandonment"


class TriggerCategories(str, Enum):
    """Disparador emocional asociado a una pregunta."""

    SELF = "self"
    SIBLINGS = "siblings"
    FRIENDS = "friends"
    FATHER = "father"
    MOTHER = "mother"
    TEACHERS = "teachers"
