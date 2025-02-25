from typing import List
from DataObjects.Course import Course

class Department:
    def __init__(self, _depName = "", _depURL = "", _depCourses = [], _abbreviation = "", _associatedFaculty = ""):
        self.name    : str       = _depName
        self.url     : str       = _depURL
        self.courses : List[str] = _depCourses
        self.abbr    : str       = _abbreviation
        self.assoFac : str       = _associatedFaculty