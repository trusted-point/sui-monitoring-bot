from typing import List
from pydantic import BaseModel, HttpUrl

class LogsSettings(BaseModel):
    level: str
    enable_log_save: bool
    file: str
    rotation_size: str

class BotSettings(BaseModel):
    users_to_ping: List[int]
    alerts_channel: int
    announcement_monitoring_channel: int

class Validator(BaseModel):
    prometheus_metrics_url: HttpUrl

class Config(BaseModel):
    logs: LogsSettings
    bot: BotSettings
    validator: Validator
