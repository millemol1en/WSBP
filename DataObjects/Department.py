from typing import List
from DataObjects.Course import Course

class Department:
    def __init__(self, _depName = "", _depCourses = [], _depURL = ""):
        self.name    : str       = _depName
        self.courses : List[str] = _depCourses
        self.url     : str       = _depURL