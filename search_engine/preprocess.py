import string
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize


def preprocessor(text):
	""" This function is used to pre-process text by removing punctuations, stopwords, stemming and tokenizing the text"""

	stop_words = stopwords.words('english')
	stemmer = PorterStemmer()
	text = str(text)
	text = text.lower()
	strip_punctuation = str.maketrans('', '', string.punctuation)
	text = text.translate(strip_punctuation)
	text = word_tokenize(text)
	new_word = [stemmer.stem(word) for word in text if word not in stop_words]
	return new_word


def concat(*args):
	"""This function helps to combine multiple strings together"""

	concatenated_text = ""
	for arg in args:
		concatenated_text += str(arg) + " "
	return concatenated_text


# Loading and Preprocessing the documents data so it can be used in an inverted index
def document_preprocessor(doc):
	df = pd.read_csv(doc, encoding="utf-8")
	document = df.fillna('')
	document['words'] = document[['abstract', 'title', 'author']].apply(
		lambda x: concat(x['abstract'], x['title'], x['author']), axis=1)
	document['words'] = document['words'].apply(preprocessor)
	return document