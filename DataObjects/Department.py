from DataObjects.Course import Course
from dataclasses import dataclass

@dataclass
class Department:
    def __init__(self, _depName = "", _depURL = "", _abbreviation = "", _depCourses = [], _depCourseURLs = []):
        self.name       : str           = _depName
        self.url        : str           = _depURL
        self.abbr       : str           = _abbreviation
        self.courses    : list[Course]  = _depCourses
        self.courseURLs : list[str]     = _depCourseURLs


    def __print__(self):
        print(f"{'-'*30}")
        print(f"    *= Name :: {self.name}")
        print(f"    *= URL  :: {self.url}")
        print(f"    *= Abbr :: {self.abbr}")
        print(f"    *= Course URLs: [{len(self.courseURLs)}]")

        for courseURL in self.courseURLs:
            print(f"       -> Course URL :: {courseURL}")

        print(f"{'-'*30}")