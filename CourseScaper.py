from bs4 import BeautifulSoup 
import requests 
import re
import pandas as pd

save_path = "./Database"
year = 2017

def scrape(department, graduate=False):
    URL = f"https://catalog.kent.edu/previous-catalogs/{year}-{year+1}//coursesaz/{department}/"

    r = requests.get(URL) 
    soup = BeautifulSoup(r.content, "lxml")

    # Gets all the courses in the department
    courses = soup.find_all("div", {"class": "courseblock"})

    courses_cleaned = []
    for course in courses:

        course_html = course
        course = str(course)
        
        # Regexes out the entire course title (EX: "ENG 01001 INTRODUCTION TO COLLEGE WRITING-STRETCH 3 Credit Hours)
        course_title_information = re.search(r'<p class="courseblocktitle noindent"><strong>(.*?)</strong></p>', course).group(1)
        course_title_information = re.split("\xa0\xa0\xa0\xa0", course_title_information)
        course_title_information[0] = course_title_information[0].replace("\xa0", " ") # id
        course_title_information[1] = course_title_information[1].strip() # name
        course_title_information[2] = course_title_information[2].strip().split(" ")[0] # credits
        
        course_id = course_title_information[0]
        course_name = course_title_information[1]
        course_credits = course_title_information[2]

        # Picks out the course prerequisites and corequisites
        course_prerequisites = course_html.find_all("p")[2].get_text()
        course_corequisites = course_html.find_all("p")[3].get_text()

        # Removes coreqs if not present and removes . at end and title at start and removes non-break characters \xa0
        course_prerequisites = course_prerequisites[15:-1].replace('\xa0', ' ')
        if "Pre/corequisite:" not in course_corequisites:
            course_corequisites = ""
        else:
            course_corequisites = course_corequisites[18:-1].replace('\xa0', ' ')

        # Gets the description
        course_description = course_html.find_all("p")[1].get_text().replace('\xa0', ' ')

        # Gets the numbers from the id (without the department)
        course_numbers = re.sub("[^0-9]", "", course_id)
        
        # Adds all undergraduate (less than 50000 course number) to courses_cleaned tuple
        # Unless the user specifies they want graduate (optional parameter graduate=True must be set to grab graduate courses)
        if int(course_numbers) < 50000 or graduate:
            # Appends the [df] tuple into the courses_cleaned 
            courses_cleaned.append(tuple([course_id, course_name, course_prerequisites, course_corequisites, course_description]))
    
    # Template for how each course will be represented in csv
    output_df = pd.DataFrame(columns=["course_name", "department", "prerequisites", "corequisites", "description", "year"]) ## updated this for the sql database
    
    # Adds each course to the dataframe

    output_data = []
    for course in courses_cleaned:
        output_data.append({"course_name": course[1], "department": department.upper(), "prerequisites": course[2], "corequisites": course[3], "description": course[4], "course_year": year})
    output_df = pd.DataFrame(output_data)

    # Saves the df
    output_df.to_csv(f"{save_path}/{department}_data{year}-{year+1}.csv", header=False, index=False) # no header, so that importing it into the SQL database is easy.
    
    
scrape("acct")
    

# Works for 23-24, 22-23, 21-22, 20-21, 19-20, 18-19, 17-18
