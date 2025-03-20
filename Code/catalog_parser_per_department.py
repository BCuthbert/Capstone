import pandas as pd
import re
import os

term_year = "spring_2015"
folder_path = 'department_data_spring2015'

def parse_catalogue(file_name, DEPT_NAME):
    course_pattern = r"([A-Za-z]+)\s(\d+)\s*-\s*([^(\n]+)"
    prereq_pattern = r"(?:Prerequisite[s]?:?|Pre-?req[s]*|Prerequisite\s?\(s\))\s*[:\-]?\s*([^\n]+)"
    coreq_pattern = r"(?:Corequisite[s]?:?|Co-?req[s]*|Corequisite\s?\(s\))\s*[:\-]?\s*([^\n]+)"
    credit_hours_pattern = r"(\d+\.\d{3}\s*Credit hours|\d+\.\d{3}\s*TO\s*\d+\.\d{3}\s*Credit hours)"


    
    courses = []
    course = []

    output_data = []
    output_df = pd.DataFrame(columns=["Course Number", "Course Name", "Department", "Prerequisites", "Corequesites", "Description"])

    with open(file_name, encoding="utf8") as catalogue:
        for line in catalogue:
            if re.match(course_pattern, line):
                if course != None:
                    courses.append(course)
                course = []
                course.append(line)
            else:
                course.append(line)
    
    for course in courses:
        course_desc = ""
        course_desc_cleaned = ""
        course_number = ""
        course_name = ""
        course_dept = ""
        course_prereqs = ""
        course_coreqs = "None"
        for line in course:
            if re.match(course_pattern, line):
                split_pos = line.find("-")
                course_number = line[0:split_pos]
                course_name = line[(split_pos + 2):len(line)]
                split_pos = line.find(" ")
                course_dept = course_number[0:split_pos]
                course_dept = course_dept.strip(" ")
            elif (line != "\n"):
                if (not line.startswith("2015 Kent State University Catalog") and not line.startswith("Page") and not line.startswith("---")):
                    course_desc = course_desc + line

        description_match = re.search(r"^(.*?)(?:Prerequisite[s]?:?|Pre-?req[s]*|Prerequisite\s?\(s\)|Corequisite[s]?:?|Co-?req[s]*|Corequisite\s?\(s\)|\d+\.\d+ Credit hours|$)", course_desc, re.DOTALL)
        if description_match:
            course_desc_cleaned = description_match.group(1).strip()
        else:
            course_desc_cleaned = course_desc.strip()

        search_prereq = re.search(prereq_pattern, course_desc)
        if search_prereq:
            course_prereqs = search_prereq.group(1).strip()

            start_prereq_pos = search_prereq.end()
            remainder_desc = course_desc[start_prereq_pos:].strip()

            for line in remainder_desc:
                coreq_match = re.search(coreq_pattern, remainder_desc)
                credit_match = re.search(credit_hours_pattern, remainder_desc)

                if coreq_match:
                    course_prereqs += remainder_desc[0:coreq_match.span()[0]]
                    remainder_desc = remainder_desc[coreq_match.span()[0]:]
                    course_prereqs.strip()
                    break

                if credit_match:
                    course_prereqs += remainder_desc[0:credit_match.span()[0]]
                    remainder_desc = remainder_desc[credit_match.span()[0]:]
                    course_prereqs.strip()
                    break
        else:
            course_prereqs = "None"

        pos = course_prereqs.lower().find("corequisite")
        if pos != -1:
            course_prereqs = course_prereqs[0:pos]

        search_coreq = re.search(coreq_pattern, course_desc)
        if search_coreq:
            course_coreqs = search_coreq.group(1).strip()

            start_coreq_pos = search_coreq.end()
            remainder_desc = course_desc[start_coreq_pos:].strip()

            for line in remainder_desc:
                credit_match = re.search(credit_hours_pattern, remainder_desc)

                if credit_match:
                    course_coreqs += remainder_desc[0:credit_match.span()[0]]
                    remainder_desc = remainder_desc[credit_match.span()[0]:]
                    course_coreqs.strip()
                    break
        else:
            course_coreqs = "None"

        if course_dept.lower() == DEPT_NAME.lower():
            output_data.append({"Course Number": course_number, "Course Name": course_name, "Department": course_dept, "Prerequisites": course_prereqs, "Corequesites": course_coreqs, "Description": course_desc_cleaned})
            
    output_df = pd.DataFrame(output_data)
    output_df.to_csv(f"{folder_path}/{DEPT_NAME}_course_data_{term_year}.csv", index=False)

dept_names = []
with open("dept_names_clean_spring2015.txt", "r") as f:
    for line in f:
        dept_name = line.strip("\n")
        dept_names.append(dept_name)

os.makedirs(folder_path, exist_ok=True)

for dept in dept_names:
    parse_catalogue("catalog_text_spring2015.txt", dept)