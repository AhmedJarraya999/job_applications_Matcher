#from spacy.lang.en import English#Define Class

# file_contents = ""
# with open('DATA/testcv.txt', 'r') as file:
#     # Read the entire contents of the file into a string
#   file_contents = file.read()
# def match_majors_by_spacy(file_contents):
#             nlp = English()
#             # Add the pattern to the matcher
#             patterns_path = "patterns/majors.jsonl"
#             ruler = nlp.add_pipe("entity_ruler")
#             ruler.from_disk(patterns_path)
#             # Process some text
#             doc1 = nlp(file_contents)
#             acceptable_majors = []
#             for ent in doc1.ents:
#                 labels_parts = ent.label_.split('|')
#                 if labels_parts[0] == 'MAJOR':
#                     if labels_parts[2].replace('-', ' ') not in acceptable_majors:
#                         acceptable_majors.append(labels_parts[2].replace('-', ' '))
#                     if labels_parts[2].replace('-', ' ') not in acceptable_majors:
#                         acceptable_majors.append(labels_parts[2].replace('-', ' '))
#             return acceptable_majors
# majors=match_majors_by_spacy(file_contents)
# print(majors)
from proprecessing import Processing
#CLASS
majors_patterns_path="/patterns/majors.jsonl"
EXTRACT_DATA_FROM_CV =Processing(majors_patterns_path)
#preprocessor = Processing.Preprocessing(majors_patterns_path)
CV_WORDS = EXTRACT_DATA_FROM_CV.define_type_of_file_and_make_action("Data/1.pdf")
print(type(CV_WORDS))
#transformation the resume translated from list to string 
cv_translated_as_a_string = ' '.join(CV_WORDS)

#print(CV_WORDS)

#testwords= " my name ahmed ima software engineering student at esprit i have also cyber security engineering degree at insant als i have studiest bachelor in electronics"


majors_list_from_a_resume=EXTRACT_DATA_FROM_CV.match_majors_by_spacy(cv_translated_as_a_string)
print(majors_list_from_a_resume)

#print(CV_WORDS2)

#ahmed=["what is your name"]
#translation=EXTRACT_DATA_FROM_CV.Preprocessing().translate_from_french_to_english(ahmed)
# Create an instance of the Preprocessing class
#preprocessor = Processing.Preprocessing(majors_patterns_path)

# Call the preprocessing method to extract majors from the text
#acceptable_majors = preprocessor.match_majors_by_spacy(file_contents)

# Print or use the result
#print("Acceptable Majors:", acceptable_majors)

