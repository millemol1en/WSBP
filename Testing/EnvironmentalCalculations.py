# [] Assume summarization for all departments for now: energy per 1000 queries (kWh)
E_T = 0.049     # Assumption 
R = 1000        # Normalization constant

def calculate_ku_kwh_usage() -> int: # Result: 0.194 KwH
    courses_per_department = {
        "Department of Anthropology": 96,
        "Department of Neuroscience": 28,
        "Department of Large Animal Sciences": 0,
        "Department of Cross-Cultural and Regional Studies": 206,
        "Department of Forensic Medicine": 2,
        "Department of Experimental Medicine": 4,
        "Religious Roots of Europe": 6,
        "Department of Clinical Medicine": 111,
        "Department of Cellular and Molecular Medicine": 22,
        "Department of Biomedical Sciences": 56,
        "Center for Stem Cell Medicine (reNEW)": 2,
        "Center for Protein Research": 5,
        "Center for Healthy Aging": 0,
        "BRIC": 4,
        "Social Data Science": 93,
        "Department of Sociology": 82,
        "Department of Psychology": 135,
        "Department of Political Science": 146,
        "Department of Economics": 140,
        "BSM - TEST": 0,
        "Other Universities": 0,
        "Law": 155,
        "The Niels Bohr Institute": 98,
        "The Natural History Museum of Denmark": 23,
        "Department of Science Education": 29,
        "Department of Drug Design and Pharmacology": 58,
        "Department of Immunology and Microbiology": 22,
        "Department of Mathematical Sciences": 130,
        "Department of Geoscience and Natural Resource Management": 268,
        "Department of Plant and Environmental  Sciences": 98,
        "School of Oral Health Care": 0,
        "The Novo Nordisk Foundation Center for Basic Metabolic Research": 3,
        "Danish Headache Center": 0,
        "Department of Chemistry": 70,
        "Department of Public Health": 170,
        "Department of Odontology": 87,
        "Department of Veterinary Clinical and Animal Sciences": 0,
        "Department of Veterinary and Animal Sciences": 82,
        "Department of Veterinary Clinical Sciences": 68,
        "Department of Pharmacy": 67,
        "Globe": 25,
        "SAXO-Institute - Archaeology, Ethnology, Greek & Latin, History": 202,
        "Department of Nordic Research": 0,
        "Department of Nutrition, Exercise and Sports": 71,
        "UNIK - Food, Fitness and Pharma": 0,
        "GLOBE Institut": 6,
        "Department of Arts and Cultural Studies": 150,
        "Department of Veterinary Disease Biology": 1,
        "Department of Biology": 126,
        "Department of Information Studies": 0,
        "Department of Media, Cognition and Communication": 2,
        "Department of English, Germanic and Romance Studies": 121,
        "Department of Nordic Studies and Linguistics": 164,
        "Department of Computer Science": 109,
        "Department of Communication": 168,
        "Theology": 50,
        "Department of Food and Resource Economics": 110,
        "Department of Food Science": 65,
        "African Studies": 17,
        "Interreligious Islamic Studies": 7
    }

    E_total = sum((C / R) * E_T for C in courses_per_department.values())
    return E_total


def calculate_dtu_kwh_usage() -> int: # Result: 0.102 KwH
    dtu_courses = {
        "Department of Biotechnology and Biomedicine": 67,
        "Department of Physics": 105,
        "Department of Transport": 0,
        "DTU Nanolab": 25,
        "DTU Biosustain": 6,
        "Department of Environmental and Resource Engineering": 107,
        "DTU Entrepreneurship": 31,
        "Department of Chemical Engineering": 93,
        "National Space Institute": 62,
        "Department of Electrical and Photonics Engineering": 163,
        "DTU Bioinformatics": 0,
        "Department of Micro and Nanotechnology": 0,
        "Department of Technology, Management and Economics": 110,
        "Department of Engineering Technology and Didactics": 286,
        "Department of Energy Conversion and Storage": 64,
        "Department of Civil and Mechanical Engineering": 252,
        "Other courses": 18,
        "Department of Chemistry": 76,
        "Department of Wind and Energy Systems": 74,
        "National Veterinary Institute": 0,
        "National Institute of Aquatic Resources": 95,
        "National Food Institute": 77,
        "Department of Applied Mathematics and Computer Science": 234,
        "Department of Health Technology": 131
    }

    E_total_dtu = sum((C / R) * E_T for C in dtu_courses.values())
    return E_total_dtu
