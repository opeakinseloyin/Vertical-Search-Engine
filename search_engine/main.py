import ast
import math
import webbrowser
import numpy as np
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from preprocess import preprocessor, document_preprocessor


def browse(url):
    """This function is used to browse the link when the user clicks on the link"""
    webbrowser.open_new(url)


def printsomething(document):
    """This function is used to print statements on the tkinter GUI screen"""

    # Calling the displayed results from the global scope into the local scope so as to modify it
    global label_list
    global separator_list
    global num

    title = Label(window, text=f"Title: {displayed_results[document]['title']}", fg="blue", cursor="hand2", anchor="w")
    label_list.append(title)
    title.grid(row=num, column=1, sticky=W+E, pady=(10, 0))
    num += 1
    title.bind("<Button-1>", lambda x: browse(f"{displayed_results[document]['title_link']}"))

    # Using an if/else statement to check if the authors have a Coventry pureportal profile
    # If they have a Coventry pureportal profile bind the link to the authors name
    # Else just print out the authors name
    if len(displayed_results[document]['authors']) == len(displayed_results[document]["authors_link"]):

        # Using for loop to match the authors to their author link
        for author in displayed_results[document]['authors']:
            i = displayed_results[document]['authors'].index(author)
            author = Label(window, text=f"Author: {author}", fg="blue", cursor="hand2", anchor="w")
            label_list.append(author)
            author.grid(row=num, column=1, sticky=W+E)
            num += 1
            author.bind("<Button-1>", lambda x: browse(f"{displayed_results[document]['authors_link'][i]}"))
    else:
        empty = ','
        author = Label(window, text=f"Author: {empty.join(displayed_results[document]['authors'])}", anchor="w")
        label_list.append(author)
        author.grid(row=num, column=1, sticky=W+E)
        num += 1
    year = Label(window, text=f"Year: {displayed_results[document]['year_of_publication']}", anchor="w", bd=1)
    label_list.append(year)
    year.grid(row=num, column=1, sticky=W+E)
    num += 1

    abstract = Label(window, text=f"Abstract: {displayed_results[document]['abstract'][:200]}........", anchor="w", bd=1)
    label_list.append(abstract)
    abstract.grid(row=num, column=1, sticky=W + E)
    num += 1

    # Creating a separator to separate the different entries
    separator = ttk.Separator(orient="horizontal")
    separator.grid(row=num, column=1, sticky=W+E, pady=(0, 20))
    separator_list.append(separator)
    num += 1


def document_normalization(document, query, idf):
    """This function is used to calculate the normalized tf.idf of the documents"""

    normalized_document = {}

    # Using a for loop to pick out each document at a time in order to calculate their normalized tf.idf
    for doc in document:
        tf_idf_list = []
        page = documents['words'].iloc[doc]

        # Using a for loop to calculate the tf.idf for each query word in the document picked out above
        for word in query:
            index = query.index(word)
            frequency = page.count(word)
            weighted_frequency = math.log(frequency + 1)
            tf_idf = idf[index] * weighted_frequency
            tf_idf_list.append(tf_idf)

        # Normalizing the tf.idf of the document
        length = np.sqrt(np.sum(np.square(np.array(tf_idf_list))))
        normalized_document[doc] = [round((x / length), 3) for x in tf_idf_list]
    return normalized_document


def query_normalization(query, idf):
    """This function calculates the normalized tf.idf of the query"""

    tf_idf_list = []
    normalized_query = []

    # Using a for loop to pick out each query word at a time and calculate their normalized tf.idf
    for word in query:
        index = query.index(word)
        frequency = query.count(word)
        weighted_frequency = math.log(frequency + 1)
        tf_idf = idf[index] * weighted_frequency
        tf_idf_list.append(tf_idf)
        l1 = np.sqrt(np.sum(np.square(np.array(tf_idf_list))))
        normalized_query = [round((x / l1), 3) for x in tf_idf_list]
    return normalized_query


def statementformat(document_index):
    """This function is used to arrange the statement in a format inorder to print on the screen"""

    dict_format = {'title': documents["title"].iloc[document_index],
                   "title_link": documents["title_link"].iloc[document_index],
                   "authors": documents["author"].iloc[document_index].split(","),
                   "authors_link": documents["author_link"].iloc[document_index].split(","),
                   "year_of_publication": documents["date"].iloc[document_index].split()[-1],
                   "school": documents["school"].iloc[document_index],
                   "abstract": documents["abstract"].iloc[document_index]}
    return dict_format


def search_programme(search_text):
    """This function takes in the user's query and retrieves the most relevant documents to the query that are
    present in Coventry's research output using the cosine similarity equation"""

    # Calling the displayed results from the global scope into the local scope so as to modify it
    global displayed_results
    global results_list

    # Opening the txt file that contains the inverted index created in the documents file
    with open('output.txt', encoding="utf-8") as file:
        content = file.read()
        file.close()

    # Defining the inverted index and processing the users query
    inverted_index = ast.literal_eval(content)
    query_list = preprocessor(search_text)
    query_set = set(query_list)
    query_list = list(query_set)

    documents_set = set()
    idf_list = []

    # Using a for loop to pick out each query word
    for word in query_list:

        # Using an if/else statement to check if the query word chosen above is in the inverted index
        # if the word is in the inverted index calculate the idf of the word, else score the idf as 0
        if word in inverted_index:
            length = len(inverted_index[word])
            idf = math.log(len(inverted_index) / length)
            idf_list.append(idf)
            for i in inverted_index[word]:
                documents_set.add(i)
        else:
            idf_list.append(0)

    # Creating vectors for the normalized tf.idf of the document and for the normalized tf.idf of the query
    document_vector = document_normalization(documents_set, query_list, idf_list)
    query_vector = query_normalization(query_list, idf_list)

    # Calculating the cosine similarity for the documents
    cosine_similarity = {}

    # Using a for loop to loop through each documents normalized tf.idf in order to multiply it by the normalized
    # tf.idf of the query
    for doc in document_vector:
        vector1 = np.array(document_vector[doc])
        vector2 = np.array(query_vector)
        vector = vector1 * vector2
        vector_product = np.sum(vector)
        cosine_similarity[doc] = vector_product

    # Sorting the dictionary containing the document index(dictionary keys) with their
    # cosine similarity(dictionary values)
    answers = dict(sorted(cosine_similarity.items(), key=lambda x: x[1], reverse=True))

    # Using a for loop to create a dictionary and a list of the answers
    for answer in answers:
        output = statementformat(answer)
        results_list.append(answer)
        displayed_results[answer] = output

    # Using a for loop to print the output on the screen
    for i in range(start, limit + start):
        index = results_list[i]
        printsomething(index)


# ________________________________________________Button functions___________________________________________ #


def forward():
    """This function is used to move the current outputs to the next outputs"""

    #  Calling the displayed results from the global scope into the local scope so as to modify it
    global start
    global button_forward
    global button_back
    global status

    # Increasing the start variable in order to move the results to the next page
    start += 4

    # Destroying and recreating the necessary buttons
    status.destroy()
    status = Label(window, text=f"Page {int(start / 4) + 1} of {int(len(displayed_results) / 4) + 1}")
    status.place(relx=0.5, rely=1.0, anchor='s')
    button_back.destroy()
    button_back = Button(window, text="<<", command=backward)
    button_back.place(relx=0.0, rely=1.0, anchor='sw')
    print(start)
    print(len(displayed_results))

    # Using an if/else statement to check if the current page is the last page
    # If it is the forward button is disabled
    # Else the button is left enabled
    if start > len(displayed_results) - 4:
        button_forward.destroy()
        button_forward = Button(window, text=">>", state=DISABLED)
        button_forward.place(relx=1.0, rely=1.0, anchor='se')

    # Using a for loop in order to destroy the previously created labels
    for labels in label_list:
        labels.destroy()

    # Using a for loop in order to destroy the previously created separators
    for lines in separator_list:
        lines.destroy()

    # Using the for loop in order to change the results either forward or backward
    for i in range(start, limit + start):

        # Using a try/except/else statement to check if the index exists in the result_list
        # If it is print it on the screen
        # else let it pass
        try:
            index = results_list[i]
        except IndexError:
            pass
        else:
            printsomething(index)


def backward():
    """This function is used to move the current outputs to the previous outputs"""

    #  Calling the displayed results from the global scope into the local scope so as to modify it
    global start
    global button_back
    global button_forward
    global status

    # Increasing the start variable in order to move the results to the next page
    start -= 4

    # Destroying and recreating the necessary buttons
    status.destroy()
    status = Label(window, text=f"Page {int(start / 4) + 1} of {int(len(displayed_results) / 4) + 1}")
    status.place(relx=0.5, rely=1.0, anchor='s')
    button_forward.destroy()
    button_forward = Button(window, text=">>", command=forward)
    button_forward.place(relx=1.0, rely=1.0, anchor='se')

    # Using an if/else statement to check if the current page is the first page
    # If it is the backward button is disabled
    # Else the button is left enabled
    if start == 0:
        button_back.destroy()
        button_back = Button(window, text="<<", state=DISABLED)
        button_back.place(relx=0.0, rely=1.0, anchor='sw')

    # Using a for loop in order to destroy the previously created labels
    for labels in label_list:
        labels.destroy()

    # Using a for loop in order to destroy the previously created separators
    for lines in separator_list:
        lines.destroy()

    # Using the for loop in order to change the results either forward or backward
    for i in range(start, limit + start):

        # Using a try/except/else statement to check if the index exists in the result_list
        # If it is print it on the screen
        # else let it pass
        try:
            index = results_list[i]
        except IndexError:
            pass
        else:
            printsomething(index)


def search():
    """This function is used to process the users search query with the relevant documents and print them out on the
    screen"""

    #  Calling the displayed results from the global scope into the local scope so as to modify it
    global button_back
    global button_forward
    global status
    global displayed_results
    global results_list

    # Using an if/else statement to check if the user typed in a query
    # If they did process the query
    # Else return a message bo informing the  user to input a search query
    if len(search_entry.get()) <= 0:
        messagebox.showerror("Incomplete Field", "Please don't leave any field empty")
    else:

        # Using a for loop in order to destroy the previously created labels
        for labels in label_list:
            labels.destroy()

        # Using a for loop in order to destroy the previously created separators
        for lines in separator_list:
            lines.destroy()

        # Processing the query, printing it on the screen and
        # creating the objects on the screen like the buttons and labels
        information1 = search_entry.get()
        displayed_results = {}
        results_list = []
        search_programme(information1)
        button_back = Button(window, text="<<", state=DISABLED)
        button_back.place(relx=0.0, rely=1.0, anchor='sw')
        button_forward = Button(window, text=">>", command=forward)
        button_forward.place(relx=1.0, rely=1.0, anchor='se')
        status = Label(window, text=f"Page {int(start/4) + 1} of {int(len(displayed_results)/4) + 1}")
        status.place(relx=0.5, rely=1.0, anchor='s')


# --------------------------------------- Global Variable ---------------------------------------------------- #

# Defining all the global variables that are used to make this program work
displayed_results = {}
results_list = []
num = 2
start = 0
limit = 4
label_list = []
separator_list = []
button_back = ""
button_forward = ""
status = ""
documents = document_preprocessor("documents.csv")
# --------------------------------------------------- UI SETUP ----------------------------------------------- #

# Creating the GUI setup
window = Tk()
window.title("Coventry Search Engine")
window.config(padx=50, pady=50)

photo = PhotoImage(file="download.png")

canvas = Canvas(width=1400, height=187)
canvas.create_image(700, 93, image=photo)
canvas.grid(row=0, column=0, columnspan=3)

search_entry = Entry(width=21)
search_entry.grid(row=1, column=0, columnspan=3, sticky="EW")

search_button = Button(text="Search", command=search)
search_button.grid(row=1, column=3, sticky="EWSN")

label = Label(window, text="")

window.mainloop()
