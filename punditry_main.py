# punditry_main.py
# main Python functionality for our Automated Punditry app
# J. Hassler Thurston (with Daniel Scarafoni)
# Personal website
# 3 May 2014


import nltk
import warnings
warnings.simplefilter('ignore')

successfulInit = False

# does some preprocessing, to speed up the response time of requests
pundit_files = {'Limbaugh': 'con_text.txt', 'Bloomberg': 'lib_text.txt'}
nltk_models = {}
# does some preprocessing of Limbot's and Bloombot's data, so that requests
# are processed relatively quickly
def preprocess():
  for pundit in pundit_files:
    # parse each input file, and convert it into NLTK tokens and text
    in_file = open(pundit_files[pundit], 'r')
    tokens = nltk.word_tokenize(in_file.read().decode('utf-8', 'ignore'))
    text = nltk.Text(tokens)
    nltk_models[pundit] = {}
    # only support up to 3-grams
    for gram in range(1,4):
      nltk_models[pundit][gram] = nltk.NgramModel(gram, text)
    in_file.close()
    successfulInit = True

# for debugging
def preprocess_short():
  for pundit in pundit_files:
    # parse each input file, and convert it into NLTK tokens and text
    in_file = open(pundit_files[pundit], 'r')
    tokens = nltk.word_tokenize(in_file.read().decode('utf-8', 'ignore'))
    text = nltk.Text(tokens)
    print 'tokenized tokens'
    nltk_models[pundit] = {}
    for gram in range(1,3):
      nltk_models[pundit][gram] = nltk.NgramModel(gram, text)
      print 'made ngram model'
    in_file.close()
    successfulInit = True

# function to complete a pundit's sentence given some starting words
def complete_sentence(grams, pundit, starting_words):
  model = nltk_models[pundit][grams]
  # generate 50 words, then prune them so that the words end in a period
  model_words = [word for word in model.generate(50, starting_words)]
  output_words = get_first_sentence(model_words)
  return ' '.join(output_words)

# function for a pundit to respond to what another pundit said
def respond(grams, pundit, words):
  model = nltk_models[pundit][grams]
  # randomly generate starting text
  starting_words = model.generate(100)[:10]
  model_words = [word for word in model.generate(50, starting_words)]
  output_words = get_first_sentence(model_words)
  output_ascii = [word.encode('ascii','ignore') for word in output_words]
  return ' '.join(output_ascii)

# gets the list of words in model_words that form the first sentence
def get_first_sentence(model_words):
  period_index = 10
  for i in range(50):
    if model_words[i][-1] == '.':
      period_index = i
      break
  return model_words[:period_index+1]






