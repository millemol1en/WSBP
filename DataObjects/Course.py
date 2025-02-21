from typing import List

class Course:
    def __init__(self, 
                 _name        : str = "",
                 _code        : str = "",
                 _semester    : str = "",
                 _points      : str = "",
                 _literature  : List[str] = []
    ):
        self.name       = _name
        self.code       = _code
        self.semester   = _semester
        self.points     = _points
        self.literature = _literature

    def __print__(self):
        print(f"\n          {self.name} \n            -> Code: {self.code} \n            -> Semester: {self.semester} \n            -> Points: {self.points}")

        print("            -> Literature list: ")
        for l in self.literature:
            print(f"                := {l}")