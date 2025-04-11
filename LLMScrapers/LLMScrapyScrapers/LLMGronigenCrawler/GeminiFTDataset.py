

gemini_dataset = [
    # Example 1: Masters and Bachelors
    (
        """
        {
            "id": "2ed7c1b9-c84f-4886-9d26-d467b9997703",
            "code": "let",
            "titleEn": "Arts",
            "titleNl": "Letteren",
            "ouClass": null,
            "parent": null,
            "programs": [
                {
                    "id": "9d07ce6f-a77e-4653-90f3-1cf503af7ba1",
                    "language": [
                    "ENGLISH",
                        "DUTCH"
                    ],
                    "levels": [
                        "MASTER"
                    ],
                    "titleEn": "Ma Mediastudies",
                    "titleNl": "Ma Mediastudies",
                    "code": "60831",
                    "official": true,
                    "specializations": []
                },
                {
                    "id": "68dfecaf-605e-4027-a489-d426001259b6",
                    "language": [
                        "ENGLISH"
                    ],
                    "levels": [
                        "BACHELOR"
                    ],
                    "titleEn": "Ba Media Studies",
                    "titleNl": "Ba Media Studies",
                    "code": "50906",
                    "official": true,
                    "specializations": []
                },
                {
                    "id": "e2136907-1e9b-4452-923c-97b2ccb003ae",
                    "language": [
                        "ENGLISH",
                        "DUTCH"
                    ],
                    "levels": [
                        "FACULTY_LEVEL_MINOR"
                    ],
                    "titleEn": "Placement Option",
                    "titleNl": "Stage optie",
                    "code": "LMINSTAGE",
                    "official": true,
                    "specializations": []
                },
            ]
        }
        """,
        """
        [
          {
            "department": "Religion, Culture and Society",
            "programs": [
              {"title": "Media Studies", "code": "50906"}
            ]
          }
        ]
        """
    ),
    # Example 2: No bachelor programs
    (
        """
        {
            "id": "32167e3b-bb9d-4afd-bef3-90d509601a50",
            "code": "rechten",
            "titleEn": "Law",
            "titleNl": "Rechtsgeleerdheid",
            "ouClass": null,
            "parent": null,
            "programs": [
            {
                "id": "754e5ade-7102-4c97-9329-415d0d5b0697",
                "language": [
                "ENGLISH"
                ],
                "levels": [
                "MASTER"
                ],
                "titleEn": "LLM European Law in a Global Context",
                "titleNl": "LLM European Law in a Global Context",
                "code": "60688-nw",
                "official": true,
                "specializations": []
            }
        """,
        "[]"
    ),
    # Example 3: Multiple bachelors
    (
        """
        {
          "titleEn": "Science and Engineering",
          "programs": [
            {
                "id": "58eebb5c-f4a0-4b18-b274-24fc6ecadb00",
                "language": [
                    "ENGLISH"
                ],
                "levels": [
                    "BACHELOR"
                ],
                "titleEn": "BSc Artificial Intelligence",
                "titleNl": "BSc Kunstmatige Intelligentie",
                "code": "56981",
                "official": true,
                "specializations": []
            },
            {
                "id": "c83cff48-5854-4731-be9a-d546f27aa078",
                "language": [
                    "ENGLISH"
                ],
                "levels": [
                    "BACHELOR"
                ],
                "titleEn": "BSc Applied Physics ",
                "titleNl": "BSc Technische Natuurkunde",
                "code": "56962",
                "official": true,
                "specializations": []
            },
          ]
        }
        """,
        """
        [
          {
            "department": "Science and Engineering",
            "programs": [
              {"title": "Artificial Intelligence", "code": "56981"},
              {"title": "Applied Physics", "code": "56962"}
            ]
          }
        ]
        """
    ),
    (
        """
        {
            "id": "ae895de5-140c-4b0e-be44-628840926b09",
            "code": "filosofie",
            "titleEn": "Philosophy",
            "titleNl": "Wijsbegeerte",
            "ouClass": null,
            "parent": null,
            "programs": [
            {
                "id": "42d1f00a-c3ab-466d-9719-9b265f997fae",
                "language": [
                "ENGLISH"
                ],
                "levels": [
                "MASTER"
                ],
                "titleEn": "Master Exchange Courses",
                "titleNl": "Master Exchange Courses",
                "code": "MAEXC",
                "official": false,
                "specializations": []
            },
            {
                "id": "89b87d4a-7c12-42ce-94fa-327acb63bb12",
                "language": [
                "ENGLISH"
                ],
                "levels": [
                "BACHELOR"
                ],
                "titleEn": "Ba Philosophy of a Specific Discipline",
                "titleNl": "Ba Filosofie van een bepaald Wetenschapsgebied",
                "code": "PROG-260",
                "official": true,
                "specializations": []
            },
            {
                "id": "a5b1c37a-0c11-4d40-9ea2-8edb376ab203",
                "language": [
                    "ENGLISH"
                ],
                "levels": [
                    "BACHELOR"
                ],
                "titleEn": "Bachelor Exchange Courses",
                "titleNl": "Bachelor Exchange Courses",
                "code": "BAEXC",
                "official": false,
                "specializations": []
            },
            {
                "id": "2bf8e1ec-0da5-4dbc-83fa-c73a7fef4bc8",
                "language": [
                    "ENGLISH"
                ],
                "levels": [
                    "MASTER"
                ],
                "titleEn": "Msc Philosophy, Politics and Economics",
                "titleNl": "Msc Philosophy, Politics and Economics",
                "code": "69321",
                "official": true,
                "specializations": []
            },
            {
                "id": "f2a59483-26a1-41a1-a1db-e08f1ed31404",
                "language": [
                    "DUTCH"
                ],
                "levels": [
                    "MASTER"
                ],
                "titleEn": "Ma Social Sciences and Humanities Education - Philosophy",
                "titleNl": "Ma Educatie in mens- en maatschappijwetenschappen - Filosofie",
                "code": "PROG-234",
                "official": true,
                "specializations": []
            },
            {
                "id": "1a7898bc-7a90-41a8-b29d-16cbaf4dbb59",
                "language": [
                    "ENGLISH"
                ],
                "levels": [
                    "MASTER"
                ],
                "titleEn": "Researchmaster Philosophy",
                "titleNl": "Researchmaster Philosophy",
                "code": "PROG-233",
                "official": true,
                "specializations": []
            },
            {
                "id": "a8cd9016-c385-497c-bf28-0df3c5b36d14",
                "language": [
                    "DUTCH"
                ],
                "levels": [
                    "BACHELOR"
                ],
                "titleEn": "Ba Philosophy",
                "titleNl": "Ba Filosofie",
                "code": "PROG-231",
                "official": true,
                "specializations": []
            }
        }
        """,
        """
        [
          {
            "department": "Philosophy",
            "programs": [
              {"title": "Philosophy", "code": "PROG-231"},
            ]
          }
        ]
        """
    ),
    (
        """
        {
            "id": "aa6eb62e-8954-4d1b-93ef-7109766f7cfa",
            "code": "feb",
            "titleEn": "Economics and Business",
            "titleNl": "Economie en Bedrijfskunde",
            "ouClass": null,
            "parent": null,
            "programs": [
            {
                "id": "820e0a7e-41ea-4e59-b214-41bc84c7a867",
                "language": [
                    "ENGLISH"
                ],
                "levels": [
                    "MASTER"
                ],
                "titleEn": "DD MSc Business Administration/BA - MAC - Fudan University, Shanghai (2-year)",
                "titleNl": "DD MSc Business Administration/BA - MAC - Fudan University, Shanghai (2-jarig)",
                "code": "PROG-6452",
                "official": true,
                "specializations": []
            },
            {
                "id": "f3681171-7be6-4f90-a4e6-d6e74d0057b6",
                "language": [
                    "ENGLISH"
                ],
                "levels": [
                    "MASTER"
                ],
                "titleEn": "MSc Business Administration/BA - Change Management",
                "titleNl": "MSc Business Administration/BA - Change Management",
                "code": "60644",
                "official": true,
                "specializations": []
            },
            {
                "id": "0ea3c2c6-8065-4884-96ea-9aaa79553757",
                "language": [
                    "ENGLISH"
                ],
                "levels": [
                    "BACHELOR"
                ],
                "titleEn": "DD BSc IB - KEDGE Business School, Bordeaux (4-year)",
                "titleNl": "DD BSc IB - KEDGE Business School, Bordeaux (4-jarig)",
                "code": "PROG-5846",
                "official": true,
                "specializations": []
            },
            {
                "id": "72ad0b79-161e-44a7-9b66-a5a257281f49",
                "language": [
                    "ENGLISH",
                    "DUTCH"
                ],
                "levels": [
                    "POST_GRADUATE"
                ],
                "titleEn": "Executive MBA - Sustainable Business Models",
                "titleNl": "Executive MBA - Sustainable Business Models",
                "code": "PROG-6834",
                "official": true,
                "specializations": []
            }
        """,
        """
        [
          {
            "department": "Economics and Business",
            "programs": [
              {"title": "Business School", "code": "PROG-5846"},
            ]
          }
        ]
        """
    ),
    (
        """
        {
            "id": "3244f356-de34-45e1-90af-3713aa5b0ddb",
            "code": "umcg",
            "titleEn": "Medical Sciences / UMCG",
            "titleNl": "Medische Wetenschappen / UMCG",
            "ouClass": null,
            "parent": null,
            "programs": [
            {
                "id": "ae7d964e-dcdc-4017-9d50-d4dd266625f8",
                "language": [
                    "ENGLISH"
                ],
                "levels": [
                    "UNIVERSITY_LEVEL_MINOR"
                ],
                "titleEn": "Minor More Healthy Years: Current Challenges in Public Health",
                "titleNl": "Minor More Healthy Years: Current Challenges in Public Health",
                "code": "BWMIN19",
                "official": true,
                "specializations": []
            },
            {
                "id": "09f615f8-6be1-453d-b667-637fd13f5589",
                "language": [
                    "DUTCH"
                ],
                "levels": [
                    "BACHELOR"
                ],
                "titleEn": "BSc Medicine",
                "titleNl": "BSc Geneeskunde",
                "code": "56551",
                "official": true,
                "specializations": []
            },
            {
                "id": "07c83bcd-0926-410c-ac6d-c181a101d112",
                "language": [
                    "DUTCH"
                ],
                "levels": [
                    "BACHELOR"
                ],
                "titleEn": "BSc Tandheelkunde",
                "titleNl": "BSc Tandheelkunde",
                "code": "56560",
                "official": true,
                "specializations": []
            },
            {
                "id": "c34ff508-9bb5-428a-960f-c3b3f8de570e",
                "language": [
                "DUTCH"
                ],
                "levels": [
                "BACHELOR"
                ],
                "titleEn": "Premaster Geneeskunde",
                "titleNl": "Premaster Geneeskunde",
                "code": "PMG1",
                "official": true,
                "specializations": []
            },
            {
                "id": "ed8c2385-d753-4f33-b599-e1897a596ef4",
                "language": [
                "DUTCH"
                ],
                "levels": [
                "BACHELOR"
                ],
                "titleEn": "BSc Bewegingswetenschappen",
                "titleNl": "BSc Bewegingswetenschappen",
                "code": "56950",
                "official": true,
                "specializations": []
            },
            {
                "id": "ac53564c-f9cf-4dd1-afb9-ff82426a92c9",
                "language": [
                    "ENGLISH"
                ],
                "levels": [
                    "BACHELOR"
                ],
                "titleEn": "Junior Scientific Masterclass",
                "titleNl": "Junior Scientific Masterclass",
                "code": "JSM1",
                "official": true,
                "specializations": []
            },
        """,
        """
        [
          {
            "department": "Medical Sciences",
            "programs": [
              {"title": "Tandheelkunde", "code": "56560"},
              {"title": "Medicine", "code": "56551"}
              {"title": "Bewegingswetenschappen", "code": "56950"}
            ]
          }
        ]
        """
    ),
    (
        """
        {
            "id": "3b4d6db6-ca4c-421c-85b1-e1602e8b89c9",
            "code": "rcs",
            "titleEn": "Religion, Culture and Society",
            "titleNl": "Religie, Cultuur en Maatschappij",
            "ouClass": null,
            "parent": null,
            "programs": [
            {
                "id": "03b3a4cb-3887-4e9d-b089-2c77b7ab7938",
                "language": [
                    "ENGLISH"
                ],
                "levels": [
                    "FACULTY_LEVEL_MINOR"
                ],
                "titleEn": "Lived Religion (TH/RS)",
                "titleNl": "Lived Religion (TH/RW)",
                "code": "RCS-FMLR",
                "official": true,
                "specializations": []
            },
            {
                "id": "e0abdfe2-985e-4fae-9681-4007315587ec",
                "language": [
                    "ENGLISH"
                ],
                "levels": [
                    "PRE_MASTER"
                ],
                "titleEn": "Premaster RPAM, RCG and HR",
                "titleNl": "Premaster RPAM, RCG and HR",
                "code": "RCS-PMMA",
                "official": true,
                "specializations": []
            },
            {
                "id": "e0951bd1-9254-4e54-8bdb-63ece5e8ff92",
                "language": [
                    "ENGLISH",
                    "DUTCH"
                ],
                "levels": [
                    "BACHELOR"
                ],
                "titleEn": "Bachelor Religious Studies",
                "titleNl": "Bachelor Religiewetenschap",
                "code": "RCS-BARW",
                "official": true,
                "specializations": []
            },
            {
                "id": "e50df26a-214a-4499-b84c-28cec1266950",
                "language": [
                    "DUTCH"
                ],
                "levels": [
                    "BACHELOR"
                ],
                "titleEn": "Bachelor Theology including Greek and PTHU",
                "titleNl": "Bachelor Theologie met Grieks en PTHU-traject",
                "code": "RCS-BATHGRPT",
                "official": true,
                "specializations": []
            },
            {
                "id": "09fedf68-7887-4834-85ce-c31bc06df796",
                "language": [
                    "ENGLISH"
                ],
                "levels": [
                    "EXCHANGE"
                ],
                "titleEn": "Exchange programme: bachelormodules",
                "titleNl": "Exchange programme: bachelormodules",
                "code": "RCS-BAEXCH",
                "official": false,
                "specializations": []
            },
            {
                "id": "4993fed6-4e90-4eed-a93f-49c26da265bc",
                "language": [
                    "DUTCH"
                ],
                "levels": [
                    "PRE_MASTER"
                ],
                "titleEn": "Premaster GV (pt)",
                "titleNl": "Premaster GV (dlt)",
                "code": "RCS-PMGVDLT",
                "official": true,
                "specializations": []
            },
            {
                "id": "de592053-9eb3-4dae-8f2e-66803e8d91e6",
                "language": [
                    "DUTCH"
                ],
                "levels": [
                    "PRE_MASTER"
                ],
                "titleEn": "Premaster in Spiritual Care",
                "titleNl": "Premaster GV (vlt)",
                "code": "RCS-PMGV",
                "official": true,
                "specializations": []
            },
            {
                "id": "47adf769-4965-4b19-82bf-99933912c2b7",
                "language": [
                    "ENGLISH",
                    "DUTCH"
                ],
                "levels": [
                    "BACHELOR"
                ],
                "titleEn": "Bachelor Theology including Greek ",
                "titleNl": "Bachelor Theologie met Grieks",
                "code": "RCS-BATHGR",
                "official": true,
                "specializations": []
            },
            {
                "id": "f9f13fee-69aa-49bd-9d93-cbd8f546698f",
                "language": [
                    "DUTCH"
                ],
                "levels": [
                    "BACHELOR"
                ],
                "titleEn": "Bachelor Theology",
                "titleNl": "Bachelor Theologie",
                "code": "RCS-BATH",
                "official": true,
                "specializations": []
            },
            {
                "id": "dc72e2a7-cdbd-470e-bc4e-f987d1dd042d",
                "language": [
                "ENGLISH"
                ],
                "levels": [
                "MASTER"
                ],
                "titleEn": "Ma Programme Religion, Conflict and Globalization",
                "titleNl": "Ma Programme Religion, Conflict and Globalization",
                "code": "RCS-MARCG",
                "official": true,
                "specializations": []
            },
            {
                "id": "29e7532b-a0da-4920-9852-41f86f9c7b2f",
                "language": [
                "DUTCH"
                ],
                "levels": [
                "MASTER"
                ],
                "titleEn": "Ma Programme in Spiritual Care - full time",
                "titleNl": "Ma Programma Geestelijke Verzorging - voltijd",
                "code": "RCS-MAGV",
                "official": true,
                "specializations": []
            }
        """,
        """
        [
          {
            "department": "Religion, Culture and Society",
            "programs": [
              {"title": "Bachelor Religious Studies", "code": "RCS-BARW"},
              {"title": "Bachelor Theology including Greek and PTHU", "code": "RCS-BATHGRPT"}
              {"title": "Bachelor Theology including Greek", "code": "RCS-BATHGR"}
              {"title": "Bachelor Theology", "code": "RCS-BATH"}
            ]
          }
        ]
        """
    )
    # 
]