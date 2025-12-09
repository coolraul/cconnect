from pydantic import BaseModel
from typing import Any, Dict


class EchoRequest(BaseModel):
    data: Dict[str, Any]


class EchoResponse(BaseModel):
    echoed: Dict[str, Any]
