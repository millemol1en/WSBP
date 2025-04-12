import json
from enum import Enum
class UniversityType(Enum):
    POLYU = "PolyU"
    KU = "KU"
    DTU = "DTU"
    

#SET UP FUNCTIONS
def sort_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    data.sort(key=lambda x: x.get("code", "").lower())
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=1)

def load_courses(filename : str):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)
    
#SØRENSEN DICE THEMSELVES

def str_to_bigrams(s : str) -> set:
    s = s.lower().strip()
    #Bigrams are our smallest units, 2 characters long.
    return {s[i:i+2] for i in range(len(s) - 1)} if len(s) > 1 else {s}

def sorensen_dice(s1 : str, s2 : str) -> float:
    s1, s2 = s1.lower().strip(), s2.lower().strip()

    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    
    s1_bigrams = str_to_bigrams(s1)
    s2_bigrams = str_to_bigrams(s2)

    if not s1_bigrams or not s2_bigrams:
        return 0.0
    
    overlap = len(s1_bigrams.intersection(s2_bigrams))
    return 2 * overlap / (len(s1_bigrams) + len(s2_bigrams))
    
    
#COMPARE COURSE META DATA (NOT LITERATURE)

def compare_meta_data(c1_val, c2_val) -> float:
    s1, s2 = str(c1_val).strip(), str(c2_val).strip()
    return sorensen_dice(s1, s2)

#COMPARE LITERATURE SIMILARITIES

def compare_books(b1, b2) -> float: 
    similarities : dict = {}

    unique_keys = {"year", "edition", "isbn"}
    for key in ["title", "year", "author", "edition", "isbn", "pubFirm"]:
        v1, v2 = b1.get(key, ""), b2.get(key, "")
        if key in unique_keys:
            if str(v1).strip() == "":
                v1 = "0"
            if str(v2).strip() == "":
                v2 = "0"

        similarities[key] = compare_meta_data(v1, v2)
    
    sum_similarities = sum(similarities.values())
    return sum_similarities / len(similarities) if similarities else 0.0
        
def compare_literature_similarities(lit1, lit2) -> float:
    
    if not lit1 and not lit2:
        return 1.0
    if not lit1 or not lit2:
        return 0.0
    
    #For each book in lit1, find best match in lit2
    scores_1 = []
    for book1 in lit1:
        best_score = max(compare_books(book1, book2) for book2 in lit2)
        scores_1.append(best_score)
    avg1 = sum(scores_1) / len(scores_1) if scores_1 else 0.0

    scores_2 = []
    for book2 in lit2:
        best_score = max(compare_books(book1, book2) for book1 in lit1)
        scores_2.append(best_score)
    avg2 = sum(scores_2) / len(scores_2) if scores_2 else 0.0

    return (avg1 + avg2) / 2



def compare_courses(c1 : dict, c2 : dict) -> dict:
    similarities : dict = {}

    for key in ["name", "code", "department", "level", "points"]:
        similarities[key] = compare_meta_data(c1.get(key, ""), c2.get(key, ""))
    

    lit1 = c1.get("literature", [])
    lit2 = c2.get("literature", [])

    lit_similiarity = compare_literature_similarities(lit1, lit2)
    similarities["literature"] = lit_similiarity

    return similarities


#Sorts JSON objects based on "name"
def exec_sorensen_dice(baseline_title, llm_title):
    #baseline_title = "ku_baseline.json"
    #llm_title = "ku_gemini.json"

    sort_json_file(baseline_title)
    sort_json_file(llm_title)


    baseline_json = load_courses(baseline_title)
    llm_json = load_courses(llm_title)

    comparisons : dict = []
    for baseline, llm in zip(baseline_json, llm_json): 
        comparisons.append(compare_courses(baseline, llm))

    threshold = 0.90
    correct = 0
    total = len(comparisons)

    #Just print outs
    for k, (baseline, comp) in enumerate(zip(baseline_json, comparisons)):
        # Use the course name, or fall back to the code if the name is empty
        course_name = baseline.get("name") if baseline.get("name") else baseline.get("code")
        #print(f"Comparison for course {k} ({course_name}):")
        #print(json.dumps(comp, indent=2))
        #print("-" * 40)

    #Calculating results
    for comp in comparisons:
        if all(value >= threshold for value in comp.values()):
            correct += 1
    data_accuracy = round((correct / total) * 100, 2)
    
    print(f"========== TEST RESULTS FOR {str(baseline_title).upper()} AND {str(llm_title).upper()} ==========")
    print(f"*** {correct} out of {total} courses matched with a threshold of {threshold} ***")
    print(f"*** {data_accuracy} % accuracy ***")

    return data_accuracy

print("**** KU COURSES ****")
#exec_sorensen_dice("ku_baseline.json", "ku_gemini.json")
#exec_sorensen_dice("ku_baseline.json", "ku_gpt.json")

print("\n**** KU COURSES ****")
#exec_sorensen_dice("dtu_baseline.json", "dtu_gemini.json")
#exec_sorensen_dice("dtu_baseline.json", "dtu_gpt.json")

baseline = f"{UniversityType.POLYU.value}/polyu_baseline.json"
llm = f"{UniversityType.POLYU.value}/polyu_gpt2.json"

exec_sorensen_dice(baseline, llm)

baseline = f"{UniversityType.POLYU.value}/polyu_baseline.json"
llm = f"{UniversityType.POLYU.value}/polyu_gemini.json"

exec_sorensen_dice(baseline, llm)