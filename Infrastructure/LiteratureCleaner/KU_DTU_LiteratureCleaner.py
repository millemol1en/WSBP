import re
from DataObjects.Book import Book
from Defs.Defs import EXCLUDE_TRAILING_FROM_LIT

def clean_literature(raw_literature : str):
    print(f"\nLiterature BEFORE: \n{raw_literature}\n\n")



    #print(f"\nLiterature AFTER: \n{cleaned_literature}\n\n")