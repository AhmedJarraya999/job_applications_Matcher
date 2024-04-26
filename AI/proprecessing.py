import pickle

class Processing:
    class Preprocessing:
        def __init__(self):
            # No preprocessing logic is needed at the moment...
            pass
        
        def translate_from_french_to_english(self, CV_WORDS):
           with open('Translation_From_French_words_to_English.pkl', 'rb') as file:
              MODEL_AI = pickle.load(file)
              TEXT = MODEL_AI(CV_WORDS)
              return TEXT[0]["translation_text"]
        
        