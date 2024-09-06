import json
import os 
from resources import DEGREES_IMPORTANCE
from proprecessing import Processing

#CLASS
majors_patterns_path="/patterns/majors.jsonl"
degrees_patterns_path="/patterns/degrees.jsonl"
skills_patterns_path="/patterns/skills.jsonl"
labels_path="/patterns/labels.json"
# labels_path_3="/patterns/ml.json"
labels_path_3="/patterns/degrees.jsonl"

# # Get the current working directory
# current_directory = os.getcwd()

# # Print the current directory
# print("Current directory:", current_directory)

EXTRACT_DATA_FROM_CV =Processing(majors_patterns_path,degrees_patterns_path,skills_patterns_path,DEGREES_IMPORTANCE)


## CONTENT OF JOB DESCRIPTION TRANSLATED AS A LIST
translated_job_description=EXTRACT_DATA_FROM_CV.translate_line_by_line('DATA/job-requirements2.txt')
##transformation the job description translated from list to string 
cv_jobdescription_as_a_string = ' '.join(translated_job_description)


## CONTENT OF A RESUME TRANSLATED FROM FRENCH TO ENGLISH  AS A LIST 
CV_WORDS = EXTRACT_DATA_FROM_CV.define_type_of_file_and_make_action("Data/ismail.pdf")
#transformation the resume translated from list to string 
cv_translated_as_a_string = ' '.join(CV_WORDS)


## EXTRACT ENTITES FROM A RESUME AND SAVE THEM INTO A DATAFRAME (this function takes  list(parsed resume as a list) as a parameter)
extract_entities_from_resume=EXTRACT_DATA_FROM_CV.extract_entities_from_resume(CV_WORDS)

major_extracted_from_resume=extract_entities_from_resume["Major"]
print("majors extracted from a resume are ",major_extracted_from_resume)




# major_category_resume=EXTRACT_DATA_FROM_CV.get_major_category(major_extracted_from_resume)
# print(major_category_resume)
list_majors_extracted_from_resume=major_extracted_from_resume.tolist()
print("the majors extracted from a resume",list_majors_extracted_from_resume)


# with open("./patterns/majors.jsonl", 'r') as file:
#     data = json.load(file)
# major_categories = data.get("MAJOR", {}).keys()
# print(major_categories)

# category_major=EXTRACT_DATA_FROM_CV.get_major_category(list_majors_extracted_from_resume)
# print(category_major)

## EXTRACT ENTITES FROM A JOB DESCRIPTION AND SAVE THEM INTO A DATAFRAME (this function takes  string(parsed job description as string) as a parameter)
extract_entities_from_job_description=EXTRACT_DATA_FROM_CV.extract_entities_from_job_description(cv_jobdescription_as_a_string)
print("the majors extracted from a job description",extract_entities_from_job_description)

major_extracted_from_job_description=extract_entities_from_job_description["Major"]
print(major_extracted_from_job_description)
# major_category_job_description=EXTRACT_DATA_FROM_CV.get_major_category(major_extracted_from_job_description)
# print(major_category_job_description)


##DEGEEES FROM RESUMEE EXTRACTION####
degrees_list_from_a_resume=EXTRACT_DATA_FROM_CV.match_degrees_by_spacy(cv_translated_as_a_string)
highest_degree=EXTRACT_DATA_FROM_CV.get_maximum_degree(degrees_list_from_a_resume)
print("the highest degree of this candidate is",highest_degree)

##DEGEEES FROM JOB DESCRIPTION EXTRACTION####
degrees_list_from_a_job_description=EXTRACT_DATA_FROM_CV.match_degrees_by_spacy(cv_jobdescription_as_a_string)
minimum_degree_for_job_description=EXTRACT_DATA_FROM_CV.get_minimum_degree(degrees_list_from_a_job_description)
print("the minimum degree required for the job description is", minimum_degree_for_job_description)

#SCORE DEGREE CALCULATION
score_degree=EXTRACT_DATA_FROM_CV.calculate_degree_score(minimum_degree_for_job_description,highest_degree)
print("The score based on the extracted degress", score_degree)


##SKILLS FROM RESUMEE EXTRACTION####
skills_list_from_a_resume=EXTRACT_DATA_FROM_CV.match_skills_by_spacy(cv_translated_as_a_string)
print("This is a list containing skills extracted from the resume",skills_list_from_a_resume)

##SKILLS FROM JOB DESCRPTION EXTRACTION####
skills_list_from_a_job_description=EXTRACT_DATA_FROM_CV.match_skills_by_spacy(cv_jobdescription_as_a_string)
print("This is a list containing skills extracted from the job description", skills_list_from_a_job_description)

#SKILLS DEGREE CALCULATION
score_skills=EXTRACT_DATA_FROM_CV.semantic_skills_similarity_sbert_base_v2(skills_list_from_a_job_description,skills_list_from_a_resume)
print(score_skills)

print(CV_WORDS)
cv_as_string= ', '.join(CV_WORDS)
print(cv_as_string)



###major extracted from a resume
majors_from_resume=EXTRACT_DATA_FROM_CV.match_majors_by_spacy(cv_as_string)
print( "majors from a resume are ",majors_from_resume)


## i will add it inside a file later!!!
lables_path_2={"MAJOR" : {"DEV" : ["software engineering", "software development", "computer sciences","computer software","information systems","information science","information sciences","computer engineering","cybersecurity","web development","network security","programming","computer science","computer engineering","systems analysis","computer programming","information sciences","information technology","cybersecurity","systems and network administration"],
            "AI" : ["data sciences","artificial intelligence","data analysis","nlp","nlp engineering","ai engineering","ai","computer vision","data engineering","mathematics","statistics"],
            "BUSINESS" : ["business administration","business analytics","business intelligence"]}}

# Convert list to string
major_string = ', '.join(majors_from_resume)
print(major_string)

##major categories extracted from the resume
major_categoriesv3_from_resume=EXTRACT_DATA_FROM_CV.get_major_categoriesv3(majors_from_resume,lables_path_2)
print("major categories from resume",major_categoriesv3_from_resume)

###major extracted from a job description
job_description_as_str = '\n'.join(translated_job_description)
majors_from_job_description=EXTRACT_DATA_FROM_CV.match_majors_by_spacy(job_description_as_str)
print("major from a job description",majors_from_job_description)

### major categories extracted from a job description
major_categoriesv3_from_job_description=EXTRACT_DATA_FROM_CV.get_major_categoriesv3(majors_from_job_description,lables_path_2)
print("major categories from a job description",major_categoriesv3_from_job_description)

#transformation from list to str  of majors extracted from the job description
exact_majors_from_job_description=majors_from_job_description[0]
print("the exact major  extracted from the job description",exact_majors_from_job_description)

#transformation from list to str  of major categories extracted from the job description

##TO BE UPDATED LATER RETURNS A VALUE OF MAJOR CATEGORY IN THIS RESUME BASED ON THE MOST OCCURENT MAJOR CATEGORY FROM ALL THE MAJORS EXTRACTED   VEEEERRRYYYYYY IMPOOOORTANNNTT
exact_major_category_in_job_description=major_categoriesv3_from_job_description[0]
print("the exact major category extracted from the job description",exact_major_category_in_job_description)

###major score calculation
score_major=EXTRACT_DATA_FROM_CV.score_major_match(exact_majors_from_job_description,exact_major_category_in_job_description,majors_from_resume,major_categoriesv3_from_resume)
print(score_major)



###final score calculation
final_score=EXTRACT_DATA_FROM_CV.calculate_final_score(score_degree, score_skills, score_major)
print("Final Score:", final_score, "%")







