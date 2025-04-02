from enum import Enum

# [] Keywords to remove from Courses:
EXCLUDE_KEY_WORDS   = { "project", "thesis", "internship", "academic", "bachelor", "research", "ceramony" }

# TODO: TELL VIGGO I MADE THIS ALL TO SMALLER

NON_BOOK_MARKERS    = { "papers", "list of", "various", "videos", "speeches", "artikler:", "domme:", "supplerende litteratur:", "supplementary literature:", "tidsskrifter:", "exercises:", "øvelser:", "extra reading:", "yderligere litteratur:", "cases:", "syllabus" }


# [] Keywords to remove from Literature List:
EXCLUDE_TRAILING_FROM_LIT = {r"Websites:.*", r"• Academic papers.*", r"Proposed Magazine & Periodicals.*", r"• Cases.*"}
EXCLUDE_EXACT_FROM_LIT    = {"Books:", "References:", "Reference", "Textbook:", "Textbook", "Useful References", "Recommended Textbooks and References", "Reference Books", "Useful Journals", "Further reading:", "Required Reading:", "Recommended reading"}

# [] Keywords for filtering literature:
BOOK_START_MARKERS  = {"Lærebog:", "Litteratur", "Course books", "Course literature"}
EDITION_MARKERS     = {"studieudgave", "Studieudgave", "udg.", "Udg.", "udgave" , "Udgave", "ed.", "Ed.", "edition", "Edition", "Vol.", "vol.", "volume", "Volume" ,"kapitel", "Kapitel", "kap.", "Kap." "kapitler", "Kapitler", "chapter", "Chapter", "chapters", "Chapters"}


PUBLISHING_MARKERS  = {
    "Gyldendal",
    "Politikens Forlag",
    "Lindhardt og Ringhof",
    "Forlaget Forum", "Rosinante",
    "Jensens Forlag",
    "Jurist- og Økonomforbundets Forlag",
    "Djøf Forlag", "Djøf", "Gads Forlag",
    "Gads", "Karnov",
    "Karnov Group",
    "KarnovGroup",
    "Hans Reitzels Forlag",
    "Hans Reitzel"
    # International publishing firms
    "Oxford University Press",
    "Cambridge University Press",
    "Penguin Random House",
    "HarperCollins", "Simon & Schuster",
    "Macmillan Publishers",
    "Hachette Book Group",
    "Wiley"}



