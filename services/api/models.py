from pydantic import BaseModel
class TokenReq(BaseModel):
    identity: str
    name: str | None = None
class TokenResp(BaseModel):
    url: str
    token: str
