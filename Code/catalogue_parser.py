import pandas as pd

def parse_catalogue(file_name):
    courses = []
    course = []

    output_data = []
    output_df = pd.DataFrame(columns=["Course Number", "Course Name", "Department", "Prerequisites", "Corequesites", "Description"])

    with open(file_name, encoding="utf8") as catalogue:
        for line in catalogue:
            if line.startswith("**"):
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
            if (line.startswith("**")):
                line = line.lstrip("*")
                line = line.rstrip("*\n")
                split_pos = line.find("-")
                course_number = line[0:split_pos]
                course_name = line[(split_pos + 2):len(line)]
                split_pos = line.find(" ")
                course_dept = course_number[0:split_pos]
                course_dept = course_dept.strip(" ")
            elif (line != "\n"):
                course_desc = course_desc + line

        split_pos_prereq = course_desc.find("Prerequisite:")
        if (split_pos_prereq == -1):
            split_pos_prereq = course_desc.find("Prerequisites:")
        split_pos_coreq = course_desc.find("Corequisite:")



        if (split_pos_prereq != -1):
            course_desc_cleaned = course_desc[0:split_pos_prereq]
        else:
            course_desc_cleaned = course_desc

        if (split_pos_prereq != -1 and split_pos_coreq != -1):
            course_prereqs = course_desc[split_pos_prereq:split_pos_coreq]
            course_coreqs = course_desc[split_pos_coreq + 13:course_desc.find("\n", split_pos_coreq, len(course_desc))]
        elif (split_pos_prereq != -1 and split_pos_coreq == -1):
            course_prereqs = course_desc[split_pos_prereq:course_desc.find(".\n", split_pos_prereq, len(course_desc))]
            course_coreqs = "None"
        
        course_prereqs = course_prereqs.lstrip("Prerequisite: ")
        course_prereqs = course_prereqs.rstrip(".\n")

        output_data.append({"Course Number": course_number, "Course Name": course_name, "Department": course_dept, "Prerequisites": course_prereqs, "Corequesites": course_coreqs, "Description": course_desc_cleaned})
            
        print("course number: " + course_number)
        print("course name: " + course_name)
        print(course_desc_cleaned)
        print("course prereqs: " + course_prereqs)
        print("course coreqs: " + course_coreqs)
    
    output_df = pd.DataFrame(output_data)
    output_df.to_csv(f"course_data_fall2016.csv", index=False)

            

parse_catalogue("catalogue_markdown.txt")