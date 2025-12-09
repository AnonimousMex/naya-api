from pydantic import BaseModel

class BadgeResponseModel(BaseModel):
    title: str
    description: str
    image_path: str
    
    
class UnlockBadgeRequest(BaseModel):
    badge_title: str
