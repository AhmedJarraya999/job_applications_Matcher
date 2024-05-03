
from proprecessing import Processing

#CLASS
majors_patterns_path="/patterns/majors.jsonl"
degrees_patterns_path="/patterns/degrees.jsonl"
skills_patterns_path="/patterns/skills.jsonl"
EXTRACT_DATA_FROM_CV =Processing(majors_patterns_path,degrees_patterns_path,skills_patterns_path)


## CONTENT OF JOB DESCRIPTION TRANSLATED AS A LIST
translated_job_description=EXTRACT_DATA_FROM_CV.translate_line_by_line('DATA/job-requirements2.txt')
##transformation the job description translated from list to string 
cv_jobdescription_as_a_string = ' '.join(translated_job_description)


## CONTENT OF A RESUME TRANSLATED FROM FRENCH TO ENGLISH  AS A LIST 
CV_WORDS = EXTRACT_DATA_FROM_CV.define_type_of_file_and_make_action("Data/1.pdf")
#transformation the resume translated from list to string 
cv_translated_as_a_string = ' '.join(CV_WORDS)


## EXTRACT ENTITES FROM A RESUME AND SAVE THEM INTO A DATAFRAME (this function takes  list(parsed resume as a list) as a parameter)
extract_entities_from_resume=EXTRACT_DATA_FROM_CV.extract_entities_from_resume(CV_WORDS)
print(extract_entities_from_resume)

## EXTRACT ENTITES FROM A JOB DESCRIPTION AND SAVE THEM INTO A DATAFRAME (this function takes  string(parsed job description as string) as a parameter)
extract_entities_from_job_description=EXTRACT_DATA_FROM_CV.extract_entities_from_job_description(cv_jobdescription_as_a_string)
print(extract_entities_from_job_description)


##DEGEEES FROM RESUMEE EXTRACTION####
degrees_list_from_a_resume=EXTRACT_DATA_FROM_CV.match_degrees_by_spacy(cv_translated_as_a_string)
highest_degree=EXTRACT_DATA_FROM_CV.get_maximum_degree(degrees_list_from_a_resume)
print("the highest degree of this candidate is",highest_degree)

##DEGEEES FROM JOB DESCRIPTION EXTRACTION####
degrees_list_from_a_job_description=EXTRACT_DATA_FROM_CV.match_degrees_by_spacy(cv_jobdescription_as_a_string)
minimum_degree_for_job_description=EXTRACT_DATA_FROM_CV.get_minimum_degree(degrees_list_from_a_job_description)
print("the minimum degree required for the job description is", minimum_degree_for_job_description)

#SCORE DEGREE CALCULATION
scoredegree=EXTRACT_DATA_FROM_CV.calculate_degree_score(minimum_degree_for_job_description,highest_degree)
print("The score based on the extracted degress", scoredegree)


##SKILLS FROM RESUMEE EXTRACTION####
skills_list_from_a_resume=EXTRACT_DATA_FROM_CV.match_skills_by_spacy(cv_translated_as_a_string)
print("This is a list containing skills extracted from the resume",skills_list_from_a_resume)

##SKILLS FROM JOB DESCRPTION EXTRACTION####
skills_list_from_a_job_description=EXTRACT_DATA_FROM_CV.match_skills_by_spacy(cv_jobdescription_as_a_string)
print("This is a list containing skills extracted from the job description", skills_list_from_a_job_description)

#SKILLS DEGREE CALCULATION
skillsdegree=EXTRACT_DATA_FROM_CV.semantic_skills_similarity_sbert_base_v2(skills_list_from_a_job_description,skills_list_from_a_resume)
print(skillsdegree)




