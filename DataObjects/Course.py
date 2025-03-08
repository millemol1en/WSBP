from typing import List

class Course:
    def __init__(self, 
                 _name        : str = "",
                 _code        : str = "",
                 _semester    : str = "",
                 _points      : str = "",
                 _literature  : List[str] = [],
                 _level       : str = ""
    ):
        self.name       = _name
        self.code       = _code
        self.semester   = _semester
        self.points     = _points
        self.literature = _literature
        self.level      = _level

    # TODO: Remove this
    def __print__(self):
        print(f"\n          {self.name} \n            -> Code: {self.code} \n            -> Semester: {self.semester} \n            -> Points: {self.points} \n            -> Points: {self.level}")

        print("            -> Literature list: ")
        for l in self.literature:
            print(f"                := {l}")