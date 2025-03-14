from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import nltk
import re
import spacy
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import glob
import os 
import numpy as np

nltk.download('stopwords')
nltk.download('wordnet')
nlp = spacy.load("en_core_web_sm")

PATH = "D:/.Downloads/Database"
PATH_SAVE = "D:/.Downloads/Database"

# Requires the path of the file, path to save the output to, year (for file name purposes), and column numbers (starting at column 0) for the department name and course description for each column
# Returns data_{year}.csv for the given year which has the columns for department name, keywords, and similar departments
# Works by reading through all files in the path (assuming a course is present), running pre-process on them, using tf-idf, uses tf-idf output to determine keywords, and calculates the cosine similarity to find similar courses
def extract(path, path_save, year, column_name, column_description):
    depts_desc = {}
    depts_keywords = {}
    depts_similarities = {}

    files = glob.glob(os.path.join(path, "*.csv"))
    


    ### Gets Course Descriptions -- depts_desc

    # Grabs the department and its description and fills depts_desc with the pre-processed department description
    for dept in files:
        dept = pd.read_csv(dept)
        dept_name = None

        # Grabs the department name and un-processed description
        # Dept_name fails if only one course present (in which case cant extract info)
        try:
            dept_name = dept.iloc[:,column_name][0]
            dept_descriptions = " ".join(dept.iloc[:, column_description].astype(str))
        except:
            pass
        
        # Processes the description and fills depts_desc
        if dept_name:
            dept_descriptions = preprocess(dept_descriptions)
            depts_desc[dept_name] = dept_descriptions
        
    # Creates the word bank of all possible words that appear in every course description
    corpus = list(depts_desc.values())
    


    ### Runs NLP -- depts_keywords

    # Threshold for how important keywords shown to user are 
    tfidf_threshold = 0.15 # Lower value results in more keywords

    # Runs TF-IDF (Term Frequency - Inverse Document Frequency) and gets the keywords (feature names)
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(corpus) 
    feature_names = np.array(tfidf.get_feature_names_out())

    # Adds the keywords from each department above the threshold to depts_keywords
    for i, dept in enumerate(depts_desc.keys()):
        tfidf_rating = tfidf_matrix[i].toarray().flatten()
        
        keywords = np.where(tfidf_rating > tfidf_threshold)[0]
        keywords = feature_names[keywords]
        
        depts_keywords[dept] = ", ".join([word.capitalize() for word in keywords.tolist()])



    ### Gets similarities -- depts_similarities

    # Compute the consine similarity getting the similarity distance between vectors based on keywords
    # dot_product_matrix = tfidf_matrix @ tfidf_matrix.T # Dot product
    # dot_product_matrix = dot_product_matrix.toarray()
    dot_product_matrix = cosine_similarity(tfidf_matrix) # Cosine similarity

    for i, dept in enumerate(depts_desc.keys()):
        similarities = dot_product_matrix[i]
        similar_indices = np.where(similarities > .2)[0] # Limits to only ones with threshold of .2 or higher
        similar_indices = similar_indices[similar_indices != i]  # Remove self-comparison

        # Sort indices by similarity in descending order
        similar_indices = similar_indices[np.argsort(similarities[similar_indices])[::-1]] # Sorts based on highest dot product
        top_indices = similar_indices[:10] # Gets the top 10

        # Fills dept_similarities with the similar departments or None 
        if len(top_indices) > 0:
            depts_similarities[dept] = []
            for idx in top_indices:
                depts_similarities[dept].append(list(depts_desc.keys())[idx])
            depts_similarities[dept] = ', '.join(depts_similarities[dept])
        else:
            depts_similarities[dept] = None



    ### Create CSV

    df = pd.concat([pd.DataFrame.from_dict(depts_keywords, orient="index", columns=["Keywords"]), pd.DataFrame.from_dict(depts_similarities, orient="index", columns=["Similar Departments"])], axis=1)
    df.to_csv(f"{path_save}/data_{year}.csv")
    print(f"File saved for {year}")
        


# Takes a piece of text and standardizes, removes stop words, lemmatizes, and returns the pre-processed output text
def preprocess(text):
    # Converts to lowercase, removes punctuation, removes numbers, and removes "equivalent to AAAA"
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\d+", "", text)
    text = re.sub(r"equivalent to\s+\S+", "", text)

    # Splits it into words instead of sentences
    text = text.split()

    # Removes stopwords (to, a, the, etc) as well as words specifically chosen as stopwords
    stop_words_1 = set(stopwords.words("english"))
    stop_words_2 = ["study", "apply", "examination", "examine", "develop", "cover", "lecture", "use", "learn", "need", "present", "explore", "corequisite", "prerequisite", "minor", "may", "three", "two", "one", "designed", "includes", "topic", "understanding", "specific", "using", "weekly", "first", "overview", "seminar", "within", "context", "theories", "applications", "must", "however", "repeated", "faculty", "program", "areas", "focus", "work", "repeatable", "provides", "required", "major", "selected", "information", "use", "semester", "related", "individual", "include", "public", "word", "credit", "various", "principles", "experience", "problems", "field", "registration", "application", "advanced", "student", "basic", "special", "concepts", "students", "course", "study", "hours", "research", "topics", "emphasis", "techniques", "design" "issues", "including", "systems", "introduction", "methods", "theory", "skills"]
    stop_words_3 = ['acct', 'actt', 'aded', 'aern', 'amrt', 'amst', 'anth', 'arab', 'arch', 'artc', 'arte', 'artf', 'arth', 'art', 'asbr', 'asl', 'astu', 'as', 'attr', 'bad', 'bmrt', 'bms', 'bsci', 'bst', 'btec', 'bus', 'cacm', 'cadt', 'ca', 'cci', 'chds', 'chem', 'chin', 'ci', 'clas', 'cls', 'comm', 'comt', 'cphy', 'cs', 'ctte', 'cult', 'dan', 'dsci', 'eced', 'ecet', 'econ', 'edad', 'edpf', 'educ', 'eert', 'ehs', 'eirt', 'els', 'emba', 'eng', 'entr', 'epi', 'epsy', 'eval', 'evhs', 'exph', 'expr', 'exsc', 'fdm', 'fin', 'fr', 'gcol', 'geog', 'geol', 'gero', 'ger', 'gre', 'hdfs', 'hebr', 'hed', 'hied', 'hist', 'hm', 'honr', 'hort', 'hpm', 'hrtg', 'hst', 'htmt', 'iakm', 'id', 'iert', 'ihs', 'ils', 'ital', 'itap', 'itec', 'japn', 'jmc', 'jus', 'kba', 'kbm', 'kbt', 'lat', 'legt', 'lib', 'lis', 'math', 'mced', 'mcls', 'mert', 'mftg', 'mis', 'mktg', 'mmtg', 'msci', 'mus', 'nrst', 'nurs', 'nutr', 'ocat', 'padm', 'pas', 'peb', 'pep', 'phil', 'phy', 'ph', 'plct', 'plst', 'pol', 'port', 'psyc', 'ptst', 'radt', 'rert', 'rhab', 'ris', 'rptm', 'rtt', 'russ', 'sbs', 'seed', 'soc', 'spad', 'span', 'spa', 'sped', 'spsy', 'srm', 'svcd', 'tech', 'thea', 'trst', 'ud', 'us', 'vcd', 'vin', 'vtec', 'wmst']
    text = [word for word in text if word not in stop_words_1]
    text = [word for word in text if word not in stop_words_2]
    text = [word for word in text if word not in stop_words_3]
    
    text = nlp(" ".join(text))

    # Lemmatizes each word (running -> run)
    text = [token.lemma_ for token in text]

    text = " ".join(text)
    return text



# extract(path=f"{PATH}/fall2009_course_data", path_save = PATH_SAVE, year=2009, column_name=2, column_description=4)
# extract(path=f"{PATH}/2011", path_save = PATH_SAVE, year=2011, column_name=2, column_description=5)
# extract(path=f"{PATH}/2012", path_save = PATH_SAVE, year=2012, column_name=2, column_description=5)
# extract(path=f"{PATH}/2013", path_save = PATH_SAVE, year=2013, column_name=2, column_description=5)
# extract(path=f"{PATH}/department_data_fall2014", path_save = PATH_SAVE, year=2014, column_name=2, column_description=5)
# extract(path=f"{PATH}/department_data_fall2015", path_save = PATH_SAVE, year=2015, column_name=2, column_description=5)
# extract(path=f"{PATH}/department_data_fall2016", path_save = PATH_SAVE, year=2016, column_name=2, column_description=5)