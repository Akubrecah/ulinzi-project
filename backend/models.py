from pydantic import BaseModel
from typing import List, Dict, Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class SMSRequest(BaseModel):
    recipients: List[str]
    message: str

class CattleParams(BaseModel):
    mode: str = "Normal"
    num_cows: int = 50
    center_lat: float
    center_lon: float

class PredictionRequest(BaseModel):
    recent_data: List[float] # List of threat levels


class WebhookRequest(BaseModel):
    webhook_url: str
    message: str
    data: Dict = {}
