from pydantic import BaseModel

class Book(BaseModel):
        title: str
        year: int
        author: str
        edition: int
        isbn: int
        pubFirm : str