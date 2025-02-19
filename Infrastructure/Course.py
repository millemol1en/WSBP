from typing import List

class Course:
    name        : str = ""
    code        : str = ""
    semester    : str = ""
    points      : str = ""
    literature  : List[str] = []

    def __print__(self):
        print(f"\n          {self.name} \n            -> Code: {self.code} \n            -> Semester: {self.semester} \n            -> Points: {self.points}")

        print("            -> Literature list: ")
        for l in self.literature:
            print(f"                := {l}")