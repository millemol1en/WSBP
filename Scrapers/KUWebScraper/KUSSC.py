from selenium.webdriver.common.by import By
from Infrastructure.Course import Course
import re

def sanitize_course_literature(text):
    
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    lines = [line for line in lines if not re.search(r"Det er ulovligt", line, re.IGNORECASE)]
    
    book_start_markers = ["Lærebog:", "Litteratur", "Course books", "Course literature"]
    edition_marker = ["studieudgave", "Studieudgave", "udg.", "Udg.", "udgave" , "Udgave", "ed.", "Ed.", "edition", "Edition", "Vol.", "vol.", "volume", "Volume" 
                      ,"kapitel", "Kapitel", "kap.", "Kap." "kapitler", "Kapitler", "chapter", "Chapter", "chapters", "Chapters" 
                      ]
    publishing_markers = ["Gyldendal", "Politikens Forlag", "Lindhardt og Ringhof", "Forlaget Forum", "Rosinante", "Jensens Forlag",
    # International publishing firms
    "Oxford University Press", "Cambridge University Press", "Penguin Random House", "HarperCollins", "Simon & Schuster", "Macmillan Publishers", "Hachette Book Group", "Wiley"]
    non_book_markers = ["Artikler:", "Domme:", "Supplerende litteratur:", "Supplementary literature:", "Tidsskrifter:", "Exercises:", "Øvelser:", "Extra reading:", "Yderligere litteratur:", "Cases:",]
    
    title_author_isbn = re.compile(
            r'^(?P<title>.*?(?:udgave|udg\.).*?)\s*\n'   # Title line containing "udgave"
            r'(?P<author>[A-ZÆØÅ][^\n]+?)\s*\n'            # Author line (starting with a capital letter)
            r'ISBN\s*(?P<isbn>[\d-]+)',                    # ISBN line
            re.IGNORECASE | re.MULTILINE
    )
    book_lines = []
    

    tit_auth_isbn = title_author_isbn.finditer(text)
    tit_auth_isbn_cleaned = clean_multiline_titles(tit_auth_isbn)

    for line in lines:
        # ===========f
        # SCENARIO 1:
        # ===========
        in_book_section = False
        if any(marker == line or marker in line for marker in book_start_markers):
            if (any(marker in line for marker in book_start_markers) and not any(em in line for em in edition_marker) and not is_author(line)):
                if is_chapter(line) or not is_author(line):
                    in_book_section = False
                else:    
                    in_book_section = True
                continue  # do not include a header that is exactly the marker
            else:
                # Even if the line includes a marker, we treat it as a candidate book line.
                in_book_section = True
                #book_lines.append(line)
                continue
        # If a line starts with a non–book marker, then we turn off the flag.
        if any(line.startswith(marker) for marker in non_book_markers):
            in_book_section = False
            continue
        elif in_book_section:
            book_lines.append(line)
        
        # ===========
        # SCENARIO 2
        # ===========
        elif any(marker in line for marker in edition_marker) and is_author(line):
            book_lines.append(line)

        elif (any(marker in line for marker in publishing_markers) and is_author(line)) and is_year(line):
            book_lines.append(line)
    
    book_lines.extend(tit_auth_isbn_cleaned)
        

    cleaned_book_list = clean_book_list(book_lines)
    return cleaned_book_list
    
    
def clean_book_list(book_list):
    remove_pages = r'^\d+\s+sider\s*$'
    cleaned_list = []
    for line in book_list:
        if re.match(remove_pages, line, flags=re.IGNORECASE):
            continue
        cleaned_list.append(line)
    return cleaned_list


def clean_multiline_titles(book_list):
    ret_list = []
    for match in book_list:
        ret_elem = match.group("title") + " " + match.group("author") + " ISBN: " + match.group("isbn")
        ret_list.append(ret_elem)
    return ret_list

def is_chapter(line): 
    return re.match(r'^\s*(Kap(?:\.|itel))\b', line, flags=re.IGNORECASE) is not None

def is_author(text):
    # Pattern for "Lastname, Name" (allowing internal uppercase letters)
    pattern_comma = r'\b[A-Z][a-zøæå]+(?:[A-Z][a-zøæå]*)*,\s*[A-Z][a-zøæå]+(?:[A-Z][a-zøæå]*)*\b'
    # Pattern for "Name Lastname" (allowing internal uppercase letters)
    pattern_space = r'\b[A-Z][a-zøæå]+(?:[A-Z][a-zøæå]*)*\s+[A-Z][a-zøæå]+(?:[A-Z][a-zøæå]*)*\b'
    
    if re.search(pattern_comma, text) or re.search(pattern_space, text):
        return True
    return False

def is_year(text):
    pattern = r'\b\d{4}\b'
    if re.search(pattern, text):
        return True
    return False

# []
def get_info_table(driver):
    info_table = driver.find_element(By.CLASS_NAME, "panel.panel-default").find_element(By.CLASS_NAME, "dl-horizontal")
    dt = info_table.find_elements(By.TAG_NAME, "dt")
    dd = info_table.find_elements(By.TAG_NAME, "dd")
    keys = [elem.text for elem in dt]
    values = [elem.text for elem in dd]
    return list(zip(keys, values))

# []
def sanitize_course_title(driver):
    title_list = driver.find_element(By.TAG_NAME, "h1").text.split()

    course_code = title_list[0]
    course_name = ' '.join(title_list[1:])

    return (course_code, course_name)

# []
def scrap_single_course(driver, course_url):
    driver.get(course_url)

    # []
    course : Course = Course()

    (course_code, course_name) = sanitize_course_title(driver)

    course.code = course_code
    course.name = course_name

    for (key, val) in get_info_table(driver):
        if key == "Varighed": course.semester = val
        if key == "Point": course.points = val
    
    # []
    literature_div = driver.find_element(By.ID, "course-materials")
    sanitized_literature = sanitize_course_literature(literature_div.text)

    course.literature = sanitized_literature

    return course
