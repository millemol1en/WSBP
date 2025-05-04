# Keywords used to filter Courses with which include these words in their name:
EXCLUDE_KEY_WORDS   = { 
    "project", 
    "thesis", 
    "internship", 
    "academic", 
    "bachelor", 
    "research", 
    "ceramony" 
}

# Keywords to remove certain types of literature.
# This translates to all the universities:
NON_BOOK_MARKERS    = { 
    "materials",
    "papers", 
    "list of", 
    "exhaustive list",
    "various", 
    "videos", 
    "speeches", 
    "artikler", 
    "domme", 
    "supplerende litteratur:", 
    "supplementary literature:", 
    "tidsskrifter:", 
    "exercises", 
    "øvelser:", 
    "extra reading:", 
    "yderligere litteratur:", 
    "cases", 
    "syllabus", 
    "absalon",
    "pensum",
    "books", 
    "references", 
    "reference", 
    "textbook", 
    "useful journals", 
    "further reading:", 
    "required", 
    "recommended",
    "forventet sideantal",
    "samlet",
    "chapters",
    "pages",
    "info følger",
    "i alt",
    "materiale",
    "overordnet",
    "lærebog",
    "litteratur",
    "samling",
    "mandatory",
    "suggested",
    "deadline",
    "maximum number of students",
    "exhaustive list",
    "jupyter",
    "research articles in innovation studies",
    "dtu learn",
    "course material"
}

# Regex pattern specifically for KU:
# Keep in mind that the order is IMPERITIVE!
CLEANING_PATTERNS = [
    r'\bkapitel\s*\d+\b.*',                                     # "kapitel X" and everything after
    r'\bkap\.?\s*\d+\s*[-–]\s*\d+\b.*',                         # "kap. X–Y" and "kap X–Y"
    r'\bkap\.\s*\d+\s*[-–]\s*\d+\b.*',                          # "kap. X–Y" and remove everything after
    r'\bkap\.\s*\d+\b.*',                                       # "kap. X" and everything after
    r'\bpp\.\s*\d+(\s*[-–]\s*\d+)?\b',                          # "pp. X" or "pp. X–Y"
    r'\bpp\s*\d+(\s*[-–]\s*\d+)?\b',                            # "pp X" or "pp X–Y"
    r'\bp\.\s*\d+\s*[-–]\s*\d+\.'                               # "p. X-X."
    r'\bside\.*\s*\d+\b',                                       # "side X"
    r'\bside\.*\s*\d+\s*[-–]\s*\d+\b',                          # "side X–Y"
    #r'\bSamlet sideantal:\s*Ca\.\s*\d+\b',                      # "Samlet sideantal: Ca. X" TODO: Maybe uncomment this?
    r'\b\d+\s+sider\b',                                         # "X sider"
    r'\bs\.?\s*\d+\s*[-–]\s*\d+\.',                             # "s. 241-242."
    r'\bs\.?\s*\d+\s*[-–]\s*\d+\b',                             # "s. X–Y"
    r'\b\d+\s*[-–]\s*\d+\b',                                    # "X–Y"
    r'\b- Hele bogen.*$',                                       # "- Hele bogen" to end
    r'\(red\.\)',                                               # "(red.)"
    r'\bside\s*\d+\s*[-–]\s*\d+\b',                             # "side X–X" specifically
    r'\bnr\.\s*\d+\b',                                          # "nr. X"
    r'-\s*Hele bogen.*',                                        # "- Hele bogen" and anything after
    r'\bsemester\:*',                                           # "semester"
    r'^\s*•\s*'                                                 # " •"
    r'^\s*[-–—]\s*'                                             # " -"   
]

# Keywords to remove from Literature List:
EXCLUDE_TRAILING_FROM_LIT = {r"Websites(?:[:.])\s*.*", r"Academic papers(?:[:.])\s*.*", r"Proposed Magazine & Periodicals(?:[:.])\s*.*", r"Cases(?:[:.])\s*.*", r"Artikler(?:[:.])\s*.*"}

# Keywords for filtering literature:
BOOK_START_MARKERS  = {"Lærebog:", "Litteratur", "Course books", "Course literature"}
EDITION_MARKERS     = {"studieudgave", "Studieudgave", "udg.", "Udg.", "udgave" , "Udgave", "ed.", "Ed.", "edition", "Edition", "Vol.", "vol.", "volume", "Volume" ,"kapitel", "Kapitel", "kap.", "Kap." "kapitler", "Kapitler", "chapter", "Chapter", "chapters", "Chapters"}

PUBLISHING_MARKERS  = {
    # Exclusively Danish Publishing Firms
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

    # International Publishing Firms
    "Oxford University Press",
    "Cambridge University Press",
    "Penguin Random House",
    "HarperCollins", "Simon & Schuster",
    "Macmillan Publishers",
    "Hachette Book Group",
    "Wiley"
    "John Wiley & Sons"
}



