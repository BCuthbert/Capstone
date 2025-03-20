import re

def dept_name_scraper(file_name):
    dept_pattern = r"([A-Za-z-]+\d{0,5})\s*-\s*([\w\s/,()'’&-]+)\s*\.*\s*(\d+)"

    with open(file_name, encoding="utf8") as departments:
        depts = []
        for line in departments:
            if re.match(dept_pattern, line):
                split = line.find("-")
                substr = line[0:split-1]
                depts.append(substr)
    
    with open("dept_names_clean_spring2015.txt", "w") as f:
        for dept in depts:
            f.write(dept + "\n")

dept_name_scraper("dept_names_spring2015.txt")