# Scraping APIs:
import scrapy

# Local Imports:
from Infrastructure.ScrapyInfrastructure.RawScrapyAbstractCrawler import RawScrapyAbstractCrawler
from Infrastructure.ScrapyInfrastructure.ScrapyDTO import CourseDTO, ScrapyErrorDTO
from Infrastructure.LiteratureCleaner.LiteratureCleaner import sanitize_course_literature, extract_books, new_fixer
from Infrastructure.LiteratureCleaner.KU_DTU_LiteratureCleaner import extract_literature
from Defs.Defs import NON_BOOK_MARKERS, CLEANING_PATTERNS, EXCLUDE_KEY_WORDS

# Native Python Imports:
import inspect
import re

class KUCrawler(RawScrapyAbstractCrawler):
    def __init__(self, _name="", _url="", **kwargs):
        super().__init__(_name=_name, _url=_url, **kwargs)

    """ Step 1 """
    def parse(self, response):
        yield from self.scrape_departments(response)

    """ Step 2 """
    def scrape_departments(self, response):
        try:
            departments_select = response.css('select#departments')
            departments_option = departments_select.css('option')

            for dep_option in departments_option:
                option_text = dep_option.css("::text").get().strip()
                option_value = dep_option.css("::attr(value)").get()

                if option_text and option_value:
                    department_url = (f"https://kurser.ku.dk/search?programme=BA&volume=2024/2025&departments={option_value}") # TODO: Consider Masters Courses???
                    
                    # Testing for Data Accuracy Baseline:
                    if option_value != "DEPARTMENT_0013": continue
                    
                    yield scrapy.Request(
                        url=department_url,
                        callback=self.scrape_department_courses,
                        meta={'department_name': option_text}
                    )
                        
        except Exception as e:
            frame = inspect.currentframe().f_back

            yield ScrapyErrorDTO(
                error=str(e),
                url=response.url,
                file=frame.f_code.co_filename,
                line=frame.f_code.co_filename,
                func=frame.f_code.co_name
            )

    """ Step 3 """
    def scrape_department_courses(self, response):
        try:
            department_name = response.meta['department_name']

            course_urls = []

            course_links = response.css('a')

            for course in course_links:        
                course_name = course.css("::text").get().strip()
                course_url  = course.css("::attr(href)").get()

                if any(phrase in course_name.lower() for phrase in EXCLUDE_KEY_WORDS): continue

                if course_url:
                    full_course_url = (f"https://kurser.ku.dk/{course_url}")
                    course_urls.append(full_course_url)

                    yield scrapy.Request(
                        url=full_course_url,
                        callback=self.scrape_single_course,
                        meta={ 'department_name': department_name }
                    )

        except Exception as e:
            frame = inspect.currentframe().f_back

            yield ScrapyErrorDTO(
                error=str(e),
                url=response.url,
                file=frame.f_code.co_filename,
                line=frame.f_code.co_filename,
                func=frame.f_code.co_name
            )
    
    """ Step 4 """
    def scrape_single_course(self, response):
        try:
            course_code       = response.xpath('//h1/text()').get().strip().split()[0]
            course_title      = ' '.join(response.xpath('//h1/text()').get().strip().split()[1:])
            course_department = response.meta['department_name']
            course_points     = "NA"
            course_level      = "NA"
            valid_literature  = [] 

            # [] Course Description:
            dl_element  = response.xpath('//dl[@class="dl-horizontal"]')
            dt_elements = dl_element.xpath('./dt')
            dd_elements = dl_element.xpath('./dd')

            for dt, dd in zip(dt_elements, dd_elements):
                dt_text = dt.xpath('normalize-space(.)').get() 
                dd_text = dd.xpath('.//text()').getall()
                
                if dt_text.strip() in ["Credit", "Point"]:
                    course_points = dd_text[0]
                elif dt_text.strip() in ["Level", "Niveau"]:
                    course_level = dd_text[0]

            """ RETRIEVE THE LITERATURE """
            course_literature_container = response.xpath('//div[@id="course-materials"]').get()

            # The following regex must NOT change as it will undoubtly result in key pieces of info being cut from it.
            # Danish variant:
            course_lit_html = re.sub(
                r'Det\s+er\s+ulovligt\s+at\s+dele\s+digitale\s+studiebøger\s+med\s+hinanden\s+uden\s+tilladelse\s+fra\s+rettighedshaver\.?',
                '',
                course_literature_container,
                flags=re.IGNORECASE
            )

            # English variant:
            course_lit_html = re.sub(
                r'It\s+is\s+illegal\s+to\s+share\s+digital\s+textbooks\s+with\s+each\s+other\s+without\s+permission\s+from\s+the\s+copyright\s+holder\.?',
                '',
                course_lit_html,
                flags=re.IGNORECASE
            )

            selector = scrapy.Selector(text=course_lit_html)
            potential_books = []

            # TODO: Remove!
            print(f"{course_code}")

            # [] Specialty Case for "Tort and Contract".
            #    The HTML is completely broken so we needed this long subsegment to take care of this:
            if course_code == "JJUB57004U":
                p_tags = selector.xpath('//p')
                current_book = []
                in_book = False

                for p in p_tags:
                    p_text = ' '.join(p.xpath('.//text()').getall()).strip()

                    if any(phrase in p_text.lower() for phrase in NON_BOOK_MARKERS):
                        continue

                    # Indication of a finished piece of literature:
                    if p_text in ['\xa0', '&nbsp;']:
                        if current_book:
                            potential_books.append(' '.join(current_book).strip())
                            current_book = []
                            in_book = False
                        continue

                    # Detect start of a new book entry via <strong> tag:
                    if p.xpath('.//strong'):
                        if current_book:   
                            potential_books.append(' '.join(current_book).strip())
                            current_book = []
                        in_book = True
                        current_book.append(p_text)
                        continue

                    if in_book:
                        current_book.append(p_text)

                # Final flush if no ending &nbsp;
                if current_book:
                    potential_books.append(' '.join(current_book).strip())

            else:
                # [] Generic Case for handling courses without cumbersome HTML: 
                elements = selector.xpath('//p | //li')

                # [] Retrieve all the <p> or <li> tags and harvest the text in order to avoid handling it all as one big block of text:
                for el in elements:
                    text = ' '.join(el.xpath('.//text()').getall()).strip()

                    if not text or any(phrase in text.lower() for phrase in NON_BOOK_MARKERS):
                        continue
                    
                    if text:
                        potential_books.append(text)


            course_literature = None
            for book in potential_books:
                # clean_line = ' '.join(book.split())
                clean_line = self.clean_text(' '.join(book.split()))

                # [] Specialty case for: Philosophy of Law and Sociology of Law
                if course_code == "JJUB57112U": 
                    clean_line = self.clean_JJUB57112U(clean_line)
                    
                elif course_code == "JJUB57011U":
                    clean_line = self.clean_JJUB57011U(clean_line)

                course_literature = extract_literature(clean_line)
                
                # print(f"    *= Cleaned Line: {clean_line}")

                # Validate that author and title have values greater than 4 characters
                if course_literature and "literature" in course_literature:
                    for lit in course_literature["literature"]:

                        # Check if both author and title are longer than 4 characters
                        if len(lit.get("author", "")) > 4 and len(lit.get("title", "")) > 4:
                            valid_literature.append(lit)
        
            yield CourseDTO(
                name = course_title,
                code = course_code,
                literature = valid_literature,
                department = course_department,
                level      = course_level,
                points     = course_points
            )

        except Exception as e:
            frame = inspect.currentframe().f_back

            yield ScrapyErrorDTO(
                error=str(e),
                url=response.url,
                file=frame.f_code.co_filename,
                line=frame.f_code.co_filename,
                func=frame.f_code.co_name
            )

    """ Local Methods """
    # [LM #1] Originally this was used to retrieve the code which came before a <br> tag in the HTML for KU University
    #         However, it became obsolete after it showed the removal of key information.
    def get_text_before_br(self, element):
        html = element.get()

        if re.search(r'<br\s*/?>', html, flags=re.IGNORECASE):
            split_html = re.split(r'<br\s*/?>', html, flags=re.IGNORECASE)
            before_br_selector = scrapy.Selector(text=split_html[0])
            text = ' '.join(before_br_selector.xpath('.//text()').getall()).strip()
            return text
        else:
            # Just extract text normally
            text = ' '.join(element.xpath('.//text()').getall()).strip()
            return text
        
    # [LM #2] General clean text function
    def clean_text(self, text: str) -> str:
        for pattern in CLEANING_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return ' '.join(text.split())

    # [LM #3] Specific case for Course "Philosophy of Law and Sociology of Law" JJUB57112U wherein everything prior
    #         to encounter the string pattern "i H" has to be removed:
    def clean_JJUB57112U(self, raw_text: str) -> str:
        # [] Pattern to remove stragglers from all the deleting:
        stragglerPattern = [
            r'\bog eller\b',                      # "og eller"
            r'\beller\b',                          # "eller"
            r';',                                  # ";"
            r'&',                                  # "&"
            r' \.',                                # " ." (space before a period)
            r'minus afsnit 2.3',                   # "minus afsnit 2.3"
        ]

        # [] Pattern to remove "2013 (1.udg.)":
        pattern2013 = r'\b2013\b\s*\(\d+\.?\s*udg\.\),?'

        processed_text = re.search(r'\bi\s+([HJ].*)', raw_text)
        if not processed_text:
            return raw_text  # Return original if pattern not found

        processed_text = processed_text.group(1).strip()
        processed_text = re.sub(pattern2013, '', processed_text).strip()

        for pattern in stragglerPattern:
            processed_text = re.sub(pattern, '', processed_text)

        return processed_text.strip()
    
    # [LM #4] Specific case for Course "Property and Creditor Law" JJUB57011U
    def clean_JJUB57011U(self, raw_text: str) -> str:
        # Remove the first "1), 2), 3)" listing portion of the regex:
        cleaned = re.sub(r'^\d+\)\s*', '', raw_text)

        # Define pattern to find "s. <number>" or "kap." and everything after it:
        pattern = re.compile(r'(s\.\s*\d+|kap\.)', flags=re.IGNORECASE)

        # Search for the first occurrence remove all the trailing nonsense:
        match = pattern.search(raw_text)
        if match:
            cleaned = cleaned[:match.start()]
        
        return cleaned.strip()
    
    # Original regex pattern
    # pattern    = re.compile(
    #     r'(\b\d{4}\s*\(\d+\.?\s*udg\.\))[^a-zA-Z0-9]*(?:og\s+)?eller\s+(\d{4}\s*\(\d+\.?\s*udg\.\))',
    #     flags=re.IGNORECASE
    # )