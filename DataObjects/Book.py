from typing import List

class Book:
    def __init__(self, 
                 _title     : str = "",
                 _year      : str = "",
                 _author    : str = "",
                 _edition   : str = "",
                 _isbn      : str = "",
                 _pubFirm   : str = ""
    ):
        self.title      = _title
        self.year       = _year
        self.author     = _author
        self.edition    = _edition
        self.isbn       = _isbn
        self.pubFirm    = _pubFirm