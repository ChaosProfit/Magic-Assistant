from pydantic import BaseModel


class WebPage(BaseModel):
    url: str
    name: str
    content: str = ""
