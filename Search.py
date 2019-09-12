from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import sys
import pickle
import porter as ps
import time
import math
from heapq import nlargest
import ast
import json

stop_words = set(stopwords.words('english'))
tokenizer = RegexpTokenizer(r'\w+')

InvIndex = {}
Page_ID_Title = {}
Secondary_Index = {}
Secondary_Index_List = []

No_Docs = 0
No_Index_Files = 0

def Load_Metadata(path_to_index_folder):
    global InvIndex
    global Page_ID_Title
    global No_Docs
    global No_Index_Files
    global Secondary_Index
    global Secondary_Index_List

    with open(path_to_index_folder+"/secondary_index.pkl", "rb") as Sec_Index:
        Secondary_Index = pickle.load(Sec_Index)
        No_Index_Files = len(Secondary_Index)
        Secondary_Index_List = list(Secondary_Index.keys())

    with open(path_to_index_folder+"/title_id.pkl", 'rb') as file:
        Page_ID_Title = pickle.load(file)
        No_Docs = len(Page_ID_Title)

def Load_Index(path_to_index_folder, Index_File_No):
    global InvIndex
    with open(path_to_index_folder+"/MergedIndex"+str(Index_File_No)+".pkl", "rb") as file:
        InvIndex = pickle.load(file)

def Binary_Search (l, r, Query_Term):

    if(Secondary_Index_List[l]>Query_Term):
        return l

    if r >= l:
        mid = l + int((r - l)/2)
        if Secondary_Index_List[mid] > Query_Term and Secondary_Index_List[mid-1] < Query_Term:
            return mid
        elif Secondary_Index_List[mid] > Query_Term:
            return Binary_Search(l, mid-1, Query_Term)
        else:
            return Binary_Search(mid + 1, r, Query_Term)
    else:
        return -1

def Find_Index_File(Query_Term):
    key_index = Binary_Search(0, No_Index_Files, Query_Term)
    key = Secondary_Index_List[key_index]
    File_Num = Secondary_Index[str(key)]
    return File_Num

def Query_processing(query):

    query_tokens = tokenizer.tokenize(query)
    query_tokens = [w.casefold() for w in query_tokens]
    query_tokens = [w for w in query_tokens if w not in stop_words]
    query_tokens = [ps.stem(w) for w in query_tokens]

    return query_tokens, []

def Field_Query_Processing(query):

    query_tokens = []
    fields = []

    tokens = query.split(',')
    for token in tokens:
        field_tokens = token.split(':')
        field = field_tokens[0].strip()
        value_tokens = field_tokens[1].split(" ")
        for val in value_tokens:
            fields.append(field)
            query_tokens.append(val.strip())

    query_tokens = [w.casefold() for w in query_tokens]
    query_tokens = [w for w in query_tokens if w not in stop_words]
    query_tokens = [ps.stem(w) for w in query_tokens]

    return query_tokens, fields

def Find_PostingList(path_to_index_folder, token, field="all"):

    PostingList = {}

    File_Num = Find_Index_File(token)
    Load_Index(path_to_index_folder, File_Num)

    if token in InvIndex.keys():
        token_entry = InvIndex[token]

        if field == "all":

            DF = len(token_entry.keys())
            if DF>0:
                IDF = No_Docs/DF
            else:
                IDF = 1
            Log_IDF = math.log(IDF,10)

            for docID in token_entry.keys():

                tf = 0
                for field_key in token_entry[docID] :
                    tf += token_entry[docID][field_key]
                # tf /= Page_ID_Title[docID][1]

                Log_TF = math.log(tf+1, 10)
                tf_idf = Log_TF*Log_IDF

                PostingList[docID] = tf_idf

        else:
            Temp_List = {}
            for docID in token_entry.keys():
                if str(field[0]) in token_entry[docID].keys():
                    Temp_List[docID] = token_entry[docID][str(field[0])]

            DF = len(Temp_List.keys())
            if DF>0:
                IDF = No_Docs/DF
            else:
                IDF = 1
            Log_IDF = math.log(IDF,10)

            tf = 0
            for docID in Temp_List.keys():
                tf = Temp_List[docID]

                Log_TF = math.log(tf+1, 10)
                tf_idf = Log_TF*Log_IDF

                PostingList[docID] = tf_idf

    return PostingList

def Search_Pages(path_to_index_folder, query_tokens, fields=[]):

    ## Dict DocID: [Intersections, Occurences]
    Doc_Occurence = {}

    for i in range(len(query_tokens)):
        token = query_tokens[i]

        if len(fields) == 0:
            field = "all"
        else:
            field = fields[i]
        Posting_List = Find_PostingList(path_to_index_folder, token, field)

        for docID in Posting_List.keys():

            if docID not in Doc_Occurence :
                Doc_Occurence[docID] = [1, Posting_List[docID]]
            else :
                Doc_Occurence[docID][1] = Doc_Occurence[docID][1] + Posting_List[docID]
                Doc_Occurence[docID][0] = Doc_Occurence[docID][0] + 1

    return Doc_Occurence

def RelevantTitles(Doc_Occurence, TopN):

    Top_Docs = nlargest(TopN, Doc_Occurence.items(), key = lambda x: (x[1][0], x[1][1]))

    TitleList = []
    for i in range(0, len(Top_Docs), 1):
        TitleList.append(Page_ID_Title[Top_Docs[i][0]])
    return TitleList

def search(path_to_index, query):
    field_query_flag = False

    if ':' in query:
        query_tokens, fields = Field_Query_Processing(query)
        print("QUERY TOKENS")
        print(query_tokens)
        print("FIELDS")
        print(fields)
    else:
        query_tokens, fields = Query_processing(query)
        print("QUERY TOKENS")
        print(query_tokens)
        print("FIELDS")
        print(fields)

    Doc_Occurence = Search_Pages(path_to_index, query_tokens, fields)
    TitleList = RelevantTitles(Doc_Occurence, 10)

    return TitleList

def main():

    path_to_index = sys.argv[1]
    testfile = sys.argv[2]
    path_to_output = sys.argv[3]

    ## Load Index and Title_ID mapping in Data Structures
    Load_Metadata(path_to_index)

    Query_Input = "Y"
    while Query_Input=="Y":
        query = input("enter query: ")
        start = time.time()
        output = search(path_to_index, query)
        end = time.time()
        for line in output:
            print(line)
        print("SEARCHING TIME: ", end-start)
        Query_Input = input("Y/N : ")

if __name__ == '__main__':

    main()
