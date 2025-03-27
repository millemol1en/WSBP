import re
from DataObjects.Book import Book
from Defs.Defs import BOOK_START_MARKERS, EDITION_MARKERS, PUBLISHING_MARKERS, NON_BOOK_MARKERS

def new_fixer(text) -> list[Book]:
    # SET UP
    lines = [line.strip() for line in text.splitlines() if line.strip()] # Split by lines and remove empty lines
    pattern = re.compile(
        r'(?P<title>.+?(?:udgave|udg\.)[, ]*\s*\d{4}[.,]?)\s*'
        r'(?P<author>.+?)(?=\s*ISBN)\s*'
        r'ISBN\s*(?P<isbn>\d[\d-]+)',
        re.IGNORECASE | re.DOTALL
    )
    
    matches = pattern.finditer(text)
    books = []
    for match in matches:
        book = Book()  # Create a new Book instance for each match
        book.title = match.group("title").strip()
        book.author = match.group("author").strip()
        book.isbn = match.group("isbn").strip()
        books.append(book)
    
    for b in books:
        print(f"** TITLE: {b.title}")
        print(f"** BY: {b.author}")
        print(f"** ISBN: {b.isbn}\n --")


def sanitize_course_literature(text) -> list[str]:
    
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    lines = [line for line in lines if not re.search(r"Det er ulovligt", line, re.IGNORECASE)]
    
    title_author_isbn = re.compile(
            r'^(?P<title>.*?(?:udgave|udg\.).*?)\s*\n'   # Title line containing "udgave"
            r'(?P<author>[A-ZÆØÅ][^\n]+?)\s*\n'            # Author line (starting with a capital letter)
            r'ISBN\s*(?P<isbn>[\d-]+)',                    # ISBN line
            re.IGNORECASE | re.VERBOSE | re.MULTILINE
    )
    book_lines = []
    
    tit_auth_isbn = title_author_isbn.finditer(text)
    tit_auth_isbn_cleaned = clean_multiline_titles(tit_auth_isbn)

    for line in lines:
        # ===========f
        # SCENARIO 1:
        # ===========
        in_book_section = False
        if any(marker == line or marker in line for marker in BOOK_START_MARKERS):
            if (any(marker in line for marker in BOOK_START_MARKERS) and not any(em in line for em in EDITION_MARKERS) and not is_author(line)):
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
        if any(line.startswith(marker) for marker in NON_BOOK_MARKERS):
            in_book_section = False
            continue
        elif in_book_section:
            book_lines.append(line)
        # ===========
        # SCENARIO 2
        # ===========
        elif any(marker in line for marker in EDITION_MARKERS) and is_author(line):
            book_lines.append(line)

        elif (any(marker in line for marker in PUBLISHING_MARKERS) and is_author(line)) and is_year(line):
            book_lines.append(line)
    
    book_lines.extend(tit_auth_isbn_cleaned)
    cleaned_book_list = clean_book_list(book_lines)

    return cleaned_book_list


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

 
def clean_book_list(book_list: list[str]) -> list[str]:
    remove_pages = r'^\d+\s+sider\s*$'
    cleaned_list = []
    for line in book_list:
        if re.match(remove_pages, line, flags=re.IGNORECASE):
            continue
        cleaned_list.append(line)
    return cleaned_list


def extract_books(list_element: str) -> Book:
    """
    This function now returns a Book object with attribute access.
    """
    book = Book()  # Start with an empty Book instance
    
    # Pre-check: if the element is very long and lacks an edition marker, assume it's not a book.
    if len(list_element.split()) > 40 and not re.search(r'\d+\.\s*udg(?:ave)?\.?', list_element, re.IGNORECASE):
        return book  # Returns an empty Book
    
    # Extract ISBN, year, edition from anywhere.
    #isbn_match = re.search(r'ISBN:\s*(\d+)', list_element)
    #if isbn_match:
    #    book.isbn = isbn_match.group(1)

    for marker in PUBLISHING_MARKERS:
        if re.search(re.escape(marker), list_element, re.IGNORECASE):
            book.pubFirm = marker
            list_element = remove_attribute(list_element, book.pubFirm)

    isbn_match = re.search(r'(?i)\bISBN\b[\s:]+([\d-]+)', list_element)
    if isbn_match:
        # Remove hyphens
        raw_isbn = isbn_match.group(1).replace('-', '')
        book.isbn = raw_isbn
        list_element = remove_attribute(list_element, book.isbn)

    year_match = re.search(r'\b(20\d{2}|19\d{2})\b', list_element)
    if year_match:
        book.year = year_match.group(1)
        list_element = remove_attribute(list_element, book.year)
    
    edition_match = re.search(r'(\d+\.\s*(?:udg(?:ave)?|edition|ed\.))', list_element, re.IGNORECASE)
    if edition_match:
        book_edition = edition_match.group(1).strip()
        number_match = re.search(r'(\d+)', book_edition)
        if number_match:
            book.edition = int(number_match.group(1))
            #remove_attribute(list_element, book.edition)
    
    # Detect publishing firm.

    if is_title(list_element) is not None:
        potential_title = is_title(list_element)
        if potential_title != book.pubFirm:
            book.title = potential_title
            list_element = remove_attribute(list_element, book.title)

    author_candidate = find_author_candidate(list_element)
    if author_candidate is not None:
        book.author = author_candidate

    return book

def remove_attribute(list_element, book_attribute): 
    if book_attribute is not None:
        retString = list_element.replace(book_attribute, "")
    return retString

def is_title(text):
    """
    Extracts the title from a bibliographic reference using several heuristics.
    
    Heuristics (applied in order):
      1. If a (red.) marker is found:
         a. If a quoted string immediately follows, return that.
         b. Otherwise, return the text immediately after (red.) up to the next comma.
      2. If the text starts with a quote but lacks a matching closing quote,
         return the text from after the opening quote until the first comma.
      3. Otherwise, if any quoted text is found in the string, use that.
      4. Otherwise, if a colon is present, use the text following it up to the next comma.
      5. As a fallback, split by commas and use the second field.
    
    A candidate is accepted only if it is nonempty and its first character is uppercase.
    """
    
    def valid_title(candidate):
        candidate = candidate.strip().rstrip(',')
        return candidate if candidate and candidate[0].isupper() else None

    # 1a. Check for a (red.) marker followed by a quoted string.
    red_quote_match = re.search(r'\(red\.\)\s*(?:,)?\s*[“"”]\s*([^“”"]+?)\s*[”"]', text)
    if red_quote_match:
        candidate = valid_title(red_quote_match.group(1))
        if candidate:
            return candidate

    # 1b. If (red.) exists, extract text immediately following it (up to the next comma)
    red_match = re.search(r'\(red\.\)\s*,?\s*([^,]+)', text)
    if red_match:
        candidate = valid_title(red_match.group(1))
        if candidate:
            return candidate

    # 2. If the text starts with a quote but no closing quote is found:
    if text and text[0] in ('"', '“', '”'):
        closing_quote_index = None
        for i in range(1, len(text)):
            if text[i] in ('"', '“', '”'):
                closing_quote_index = i
                break
        if closing_quote_index:
            candidate = valid_title(text[1:closing_quote_index])
            if candidate:
                return candidate
        else:
            comma_index = text.find(',')
            if comma_index != -1:
                candidate = valid_title(text[1:comma_index])
                if candidate:
                    return candidate
            candidate = valid_title(text[1:])
            if candidate:
                return candidate

    # 3. Look for any quoted text elsewhere in the string.
    quote_match = re.search(r'[“"”]\s*(.+?)\s*[”"]', text)
    if quote_match:
        candidate = valid_title(quote_match.group(1))
        if candidate:
            return candidate

    # 4. Check for a colon delimiter and extract text following it (up to the next comma).
    colon_match = re.search(r':\s*([^,]+)', text)
    if colon_match:
        candidate = valid_title(colon_match.group(1))
        if candidate:
            return candidate

    parts = text.split(',')
    if len(parts) >= 1:
        first_field = parts[0].strip()
        # Look for " af " (with spaces to avoid matching words like "after")
        if " af " in first_field:
            candidate = valid_title(first_field.split(" af ")[0])
            if candidate:
                return candidate
    # 5. Fallback: split by commas and assume the second part is the title.
    
    if len(parts) >= 2:
        candidate = valid_title(parts[1])
        if candidate:
            return candidate

    return None

def find_author_candidate(text: str) -> list[str]:
    candidate = None
    # Prefer text before a colon if available.
    if ':' in text:
        candidate = text.split(':', 1)[0]
    # Else, if a semicolon exists, take only the first segment.
    elif ';' in text:
        candidate = text.split(';', 1)[0]
    else:
        candidate = text
    candidate = candidate.strip()
    # Remove a leading 'af ' (case insensitive) if present.
    candidate = re.sub(r'^(af\s+)', '', candidate, flags=re.IGNORECASE)
    
    # Remove trailing tokens starting with unwanted words like "udgave", "edition", "ISBN"
    candidate = re.sub(r'\b(udgave|edition|ISBN)\b.*$', '', candidate, flags=re.IGNORECASE)

    # Remove any quoted parts. For instance, remove any text between quotes.
    candidate = re.sub(r'["“”].*?["“”]', '', candidate).strip()
    for marker in PUBLISHING_MARKERS:
        candidate = candidate.replace(marker, "")

    candidate_final = fetch_author(candidate) # HERE!
    return candidate_final

def fetch_author(text: str) -> list[str]:
    nameList: list[str] = []
    # Normalize known separators (" og ", " and ", " & ") to a semicolon.
    normalized_text = text.replace(" og ", ";").replace(" and ", ";").replace(" & ", ";")
    # Regex pattern for two formats:
    # Format A: "Firstname [Middlename] Lastname"
    # Format B: "Lastname, Firstname [Middlename]"
    name_pattern = re.compile(
        r'\b(?:'
        r'(?P<first>[A-Z][a-zøæå]+)(?:\s+(?P<middle>[A-Za-zøæå]+))?\s+(?P<last>[A-Z][a-zøæå]+)'
        r'|'
        r'(?P<last2>[A-Z][a-zøæå]+),\s+(?P<first2>[A-Z][a-zøæå]+)(?:\s+(?P<middle2>[A-Za-zøæå]+))?'
        r')\b'
    )
    # Process each segment if multiple names are present.
    for part in normalized_text.split(";"):
        part = part.strip()
        matches = list(name_pattern.finditer(part))
        if matches:
            for match in matches:
                if match.group('first'):
                    first = match.group('first')
                    middle = match.group('middle') if match.group('middle') else ""
                    last = match.group('last')
                else:
                    first = match.group('first2')
                    middle = match.group('middle2') if match.group('middle2') else ""
                    last = match.group('last2')
                nameList.append((first, middle, last))
        else:
            # No regex match; try splitting the part by commas and check each token.
            tokens = [t.strip() for t in part.split(',')]
            for token in tokens:
                if token and re.fullmatch(r'[A-Z][a-zøæå]+', token):
                    nameList.append(("", "", token))
    return nameList