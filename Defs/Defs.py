from enum import Enum

# [] Keywords to remove from Courses:
EXCLUDE_KEY_WORDS   = {"Project", "Thesis", "Internship", "Academic", "Bachelor", "Research"}

# [] Keywords to remove from Literature List:
EXCLUDE_TRAILING_FROM_LIT = {r"Websites:.*", r"• Academic papers.*", r"Proposed Magazine & Periodicals.*", r"• Cases.*"}
EXCLUDE_EXACT_FROM_LIT    = {"Books:", "References:", "Reference", "Textbook:", "Textbook", "Useful References", "Recommended Textbooks and References", "Reference Books", "Useful Journals", "Further reading:", "Required Reading:", "Recommended reading"}

# TODO: Combine some of these 'markers', currently too many. NO REPETITION!
# [] Keywords for filtering literature:
BOOK_START_MARKERS  = {"Lærebog:", "Litteratur", "Course books", "Course literature"}
EDITION_MARKERS     = {"studieudgave", "Studieudgave", "udg.", "Udg.", "udgave" , "Udgave", "ed.", "Ed.", "edition", "Edition", "Vol.", "vol.", "volume", "Volume" ,"kapitel", "Kapitel", "kap.", "Kap." "kapitler", "Kapitler", "chapter", "Chapter", "chapters", "Chapters"}
PUBLISHING_MARKERS  = {"Gyldendal", "Politikens Forlag", "Lindhardt og Ringhof", "Forlaget Forum", "Rosinante", "Jensens Forlag", "Oxford University Press", "Cambridge University Press", "Penguin Random House", "HarperCollins", "Simon & Schuster", "Macmillan Publishers", "Hachette Book Group", "Wiley"}
NON_BOOK_MARKERS    = {"Artikler:", "Domme:", "Supplerende litteratur:", "Supplementary literature:", "Tidsskrifter:", "Exercises:", "Øvelser:", "Extra reading:", "Yderligere litteratur:", "Cases:"}