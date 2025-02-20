# NOTE: This is meant to work for 2011, 2012, and 2013 course catalogs only 
# Course catalog names should be in format Course-Descriptions-Fall-{year}.pdf
# Edit the save path and file path in the scraper-- please make sure folders & files exist before running 
# Running pdfminder's extract text on course catalogs takes a log time (approx 5 minutes per catalog) so expect long runtimes 

import re
import pdfminer
import pandas as pd
import pdfminer.high_level

# Creates a simple course class for organization 
class Course:
    def __init__(self, name, number, dept, prereqs, coreqs, desc, year, equivalencies):
        self.name = name
        self.number = number
        self.dept = dept
        self.prereqs = prereqs
        self.coreqs = coreqs
        self.desc = desc
        self.year = year
        self.equivalencies = equivalencies

def scrape(year):
    save_path = f"D:/.Downloads/Database/{year}" # Location to save CSVs
    file_path = "D:/.Downloads/Database/"  # Location of course catalogs

    URL = f"{file_path}Course-Descriptions-Fall-{year}.pdf"
    text = pdfminer.high_level.extract_text(URL)

    lines = text.splitlines()
    # Removes inconsistencies for easier regex-ing including double space "  " typos, removing page endings, and removing empty lines 
    lines = [line.replace("  ", " ") for line in lines]
    for i in range(len(lines) - 1, -1, -1):
        if "P A G E" in lines[i]:
            lines.pop(i)

        if (lines[i] == "" or lines[i].strip() == " ") and (lines[i-1] == "" or lines[i-1] == " "):
            lines.pop(i-1)
    
    # Combines the lines into one text output
    lines = "".join(lines)

    # Regex-s out all the courses starting with the couse title and ending at the word department (past there is irrelevant info)
    courses = re.findall("([A-Z]{2,4} \d{5})\s*(.*?)(?:Department:|Schedule Types:|Level:)", lines)

    # Regex-es out all of the course info from each course and saves each one as a Course object 
    courses_obj = []
    for course in courses:
        course_number = course[0].split(" ")[1]
        if course_number.startswith("'"):
            course_number = course_number[1:]

        try:
            course_name = re.match(r"^([A-Z0-9&':./,-]+(?:\s+[A-Z0-9&':./,-]+)*)", course[1]).group(1)
            course_name = course_name.strip()
            
            # Fix for 2013 including unnecessary info between course number and name 
            if year == 2013 and course_name.strip().split(" ")[0] == "-":
                course_name = course_name[1:].strip()

            # Removes last character from course name if it isn't supposed to be there since the regex looks for capital letters
            if len(course_name.split(" ")[-1]) == 1 and course_name[-1] != "I":
                course_name = course_name[:-1]

        except:
            # All of the courses that do not have a course name are not actually courses and can be discarded (erroneously regex-ed)
            course_name = None
            
        if course_name != None:
            department = course[0].split(" ")[0]
            
            prerequisites = re.search("[Pp]rerequisite:?\s*(.*?)\s*(?=Corequisite|\d+\.\d{3} Credit hours|\d+\.\d{3} [Tt][Oo] \d+\.\d{3} Credit hours)", course[1])
            prerequisites = prerequisites.group(1) if prerequisites else None # Sets to None if no pre-reqs line exists
            prerequisites = None if prerequisites in ["None.", "none.", "None", "none"] else prerequisites # Sets to None keyword because sometimes if no pre-reqs exist it is left blank (wont regex) and other times the word none is used
            
            if prerequisites:
                 # Fixes issue where sometimes : s or s: are grabbed because inconsistencies in course catalog
                if prerequisites.startswith("s:"):
                    prerequisites = prerequisites[2:].strip()  # Remove both "s" and ":"
                elif prerequisites.startswith((':', 's')):
                    prerequisites = prerequisites[1:].strip()
                
                # Fixes issue where sometimes none is hard coded
                if "none" in prerequisites or "None" in prerequisites:
                    prerequisites = None
 
            corequisites = re.search("[Cc]orequisite:?\s*(.*?)\s\d+\.000", course[1])
            corequisites = corequisites.group(1).strip() if corequisites else None
            corequisites = None if corequisites in ["None.", "none.", "None", "none"] else corequisites

            if corequisites:
                # Fixes issue where sometimes : s or s: are grabbed because inconsistencies in course catalog
                if corequisites.startswith("s:"):
                    corequisites = corequisites[2:].strip()  # Remove both "s" and ":"
                elif corequisites.startswith((':', 's')):
                    corequisites = corequisites[1:].strip()

                # Fixes issue where sometimes none is hard coded
                if "none" in corequisites or "None" in corequisites:
                    corequisites = None

            description = re.match("^(.*?)([Pp]rerequisite|\s*\d+\.000 Credit hours)", course[1][len(course_name):])
            description = description.group(1).strip() if description else None       

            # Need to check if description exists because a few courses do not contain descriptions
            if description:
                # Fixes issue where I from description was appended to course name by checking all possible i words that might start a course name 
                if any(description.startswith(word) for word in ["llustration", "ntervention", "nstructed", "ntensified", "ntake", "nitial", "ncreases", "ntegrative", "ntroduce", "ncludes", "ntended", "ntense", "dentifies", "f ", "mproving", "nvestigate", "mpact", "ntergenerational", "nteractions", "dentifying", "ntegrates", "ntermediate", "nformation", "nquiry", "ncreasing", "nterpretation", "ntegrated", "nstruction", "nterdisciplinary", "ntegrating", "dentification", "nternship", "n ", "nvestigation", "nvestigations", "ntensive", "ndividual", "nvolves", "ntroduces", "n-depth", "ndependent", "ntroductory", "ssues", "mplementation", "ntroduction", "ntegration"]):
                    description = "I" + description
                    course_name = course_name[:-1]
                
                # Fixes issue where 2013's description includes part of the course name
                if year == 2013 and description.split(" ")[0].isupper() and description.split()[0] != "A":
                    description = " ".join(description.split(" ")[1:])

                # Not used at moment but grabs (equivalent to XYZ to find cross-listed courses)
                equivalencies = re.search(r"\b([A-Z]{2,4})\s*(\d{5})\b", description)
                equivalencies = equivalencies.group(1) + " " + equivalencies.group(2) if equivalencies else None

            courses_obj.append(Course(course_name, course_number, department, prerequisites, corequisites, description, year, equivalencies))
    
    # Creates a dictionary for each department (key) each associated with an array of all Course objects from that department
    depts = {}
    for course in courses_obj:
        if course.dept not in depts:
            depts[course.dept] = []
        depts[course.dept].append(course)

    # Creates a csv for each department 
    for dept in depts:
        output_df = pd.DataFrame(columns=["Course Number", "Course Name", "Department", "Prerequisites", "Corequesites", "Description", "Year"])
        
        output_data = []
        for course in depts[dept]:
            output_data.append({"Course Number": course.number, "Course Name": course.name, "Department": dept, "Prerequisites": course.prereqs, "Corequesites": course.coreqs, "Description": course.desc, "Year": course.year})
        output_df = pd.DataFrame(output_data)
        output_df.to_csv(f"{save_path}/{dept}_data{year}-{year+1}.csv", index=False, header=False)

    print(f"All courses scraped for {year} :)")

scrape(year=2013)
scrape(year=2011)
scrape(year=2012)

print("Finished Scraping!!!")