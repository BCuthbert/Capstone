import requests
from bs4 import BeautifulSoup
import os
import csv
from urllib.parse import urljoin
import re

#URL 
base_url = "http://catalog-archive.kent.edu/archive/academics/catalog/archive/2009/CourseInformation/Fall2009/"
index_url = base_url + "index.html"

# Create a directory to store the data
output_dir = "fall2009_course_data"
os.makedirs(output_dir, exist_ok=True)

# Headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
}

# get the main catalog page
response = requests.get(index_url, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

# Extract department links
course_links = []
for link in soup.find_all("a"):
    href = link.get("href", "")
    full_url = urljoin(base_url, href)  # Fix relative paths
    if "Fall2009" in full_url and ".html" in href:  # Only pick valid course links
        course_links.append((link.text.strip(), full_url))

# Debugging output
if not course_links:
    print("No valid department course links found. The HTML structure may have changed.")
else:
    print(f"Found {len(course_links)} valid departments to scrape.")

#  separate courses
course_pattern = re.compile(r"(\d{4,5})\s([A-Za-z].*?)\s\((\d+)\)", re.DOTALL)

# Loop through each department
for dept_code, course_url in course_links:
    print(f"Scraping department: {dept_code} from {course_url}")

    try:
        course_response = requests.get(course_url, headers=headers)
        course_response.raise_for_status()
        course_soup = BeautifulSoup(course_response.text, "html.parser")

        # Extract all <p> elements containing course info
        raw_text = " ".join([p.get_text(strip=True) for p in course_soup.find_all("p")])
        
        # Find all courses in the  text
        matches = course_pattern.finditer(raw_text)
        
        course_list = []
        for match in matches:
            course_number = match.group(1).strip()
            course_name = match.group(2).strip()
            course_credits = match.group(3).strip()
            
            # get the description by finding the next part of the text
            remaining_text = raw_text[match.end():].strip()
            description = remaining_text.split("Prerequisite:")[0].strip()

            # get prerequisites
            prerequisites = "None"
            if "Prerequisite:" in remaining_text:
                prerequisites = remaining_text.split("Prerequisite:")[-1].split(".")[0].strip()

            course_list.append((course_number, course_name, dept_code, prerequisites, description))

        print(f"Extracted {len(course_list)} courses for {dept_code}")

        # Save each department's courses to a separate CSV file
        csv_filename = os.path.join(output_dir, f"{dept_code}_course_data_fall_2009.csv")
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Course Number", "Course Name", "Department", "Prerequisites", "Description"])  # Column Headers

            #  each course is properly written in its own row
            for course_number, course_name, department, prerequisites, course_description in course_list:
                writer.writerow([course_number, course_name, department, prerequisites, course_description])

        print(f"Saved: {csv_filename}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {course_url}: {e}")

print("\n Scraping completed")
