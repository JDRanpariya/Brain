from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime

class ConnectorOutput(BaseModel):
    title: str
    url: HttpUrl
    author: Optional[str]
    published_at: Optional[datetime]
    content: Optional[str]
    metadata: Dict[str, Any] = {}

