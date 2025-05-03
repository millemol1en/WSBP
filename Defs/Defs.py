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
    "papers", 
    "list of", 
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
    "books:", 
    "references:", 
    "reference", 
    "textbook", 
    "useful references", 
    "recommended textbooks and references", 
    "reference books", 
    "useful journals", 
    "further reading:", 
    "required reading:", 
    "recommended reading",
    "forventet sideantal",
    "samlet",
    "chapters",
    "pages",
    "TBA",
    "info følger"
}

# Regex pattern specifically for KU:
CLEANING_PATTERNS = [
    r'\bkapitel\s*\d+\b',                                       # "kapitel X"
    r'\bkap\.\s*\d+\b',                                         # "kap. X"

    r'\bpp\.\s*\d+(\s*[-–]\s*\d+)?\b',                          # "pp. X" or "pp. X–Y"
    r'\bpp\s*\d+(\s*[-–]\s*\d+)?\b',                            # "pp X" or "pp X–Y"
    r'\bside\.*\s*\d+\b',                                       # "side X"
    r'\bside\.*\s*\d+\s*[-–]\s*\d+\b',                          # "side X–Y"
    #r'\bSamlet sideantal:\s*Ca\.\s*\d+\b',                      # "Samlet sideantal: Ca. X" TODO: Maybe uncomment this?
    r'\b\d+\s+sider\b',                                         # "X sider"
    r'\bs\.?\s*\d+\s*[-–]\s*\d+\s+og\s+\d+\s*[-–]\s*\d+\b',     # "s. X–Y og X–Y"
    r'\bs\.?\s*\d+\s*[-–]\s*\d+\b',                             # "s. X–Y"
    r'\b\d+\s*[-–]\s*\d+\b',                                    # "X–Y"
    r'\b- Hele bogen.*$',                                       # "- Hele bogen" to end
    r'\(red\.\)',                                               # "(red.)"
    
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
}



