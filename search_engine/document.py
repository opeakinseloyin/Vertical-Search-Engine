import os
import ast
from preprocess import *
from search_engine.spiders.crawler import update, begin, CrawlSpider


def create_inverted_index(document_list):
	# Using the for loop to create an inverted index
	inverted_i = {}
	for i, doc in enumerate(document_list):
		for term in doc:
			if term in inverted_i:
				inverted_i[term].add(i)
			else:
				inverted_i[term] = {i}

	# Saving the inverted index into a txt file
	with open('output.txt', 'w', encoding="utf-8") as output:
		output.write(f"{inverted_i}")


def update_inverted_index(document_list):
	# Using the for loop to create an inverted index
	for i, doc in enumerate(document_list):
		for term in doc:
			if term in inverted_index:
				inverted_index[term].add(i)
			else:
				inverted_index[term] = {i}

	# Saving the inverted index into a txt file
	with open('output.txt', 'w', encoding="utf-8") as output:
		output.write(f"{inverted_index}")


try:
	with open('output.txt', encoding="utf-8") as file:
		content = file.read()

except FileNotFoundError:
	begin.crawl(CrawlSpider)
	begin.start()
	documents = document_preprocessor("documents.csv")
	list_of_documents = documents['words'].to_list()
	create_inverted_index(list_of_documents)

else:
	inverted_index = ast.literal_eval(content)
	update.crawl(CrawlSpider)
	update.start()
	updated_document = document_preprocessor("update.csv")
	updated_document_list = updated_document['words'].to_list()
	update_inverted_index(updated_document_list)
	data = pd.read_csv('update.csv')
	if os.path.exists('documents.csv') and os.path.isfile('documents.csv'):
		os.remove('documents.csv')
	data.to_csv('documents.csv')
	if os.path.exists('update.csv') and os.path.isfile('update.csv'):
		os.remove('update.csv')
