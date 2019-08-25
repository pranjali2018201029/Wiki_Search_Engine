from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import sys
import pickle

stop_words = set(stopwords.words('english'))
tokenizer = RegexpTokenizer(r'\w+')
ps = PorterStemmer()

InvIndex = {}
Page_ID_Title = {}

def LoadIndex(path_to_index):

    with open(path_to_index, 'rb') as file:
        InvIndex = pickle.load(file)

    # for key in InvIndex.keys():
    #     print(key)

    with open('title_id.pkl', 'rb') as file:
        Page_ID_Title = pickle.load(file)

def Query_processing(query):

    query_tokens = tokenizer.tokenize(query)
    query_tokens = [w.casefold() for w in query_tokens]
    query_tokens = [w for w in query_tokens if w not in stop_words and w.isalpha()]
    query_tokens = [ps.stem(w) for w in query_tokens]

    return query_tokens

def Find_PostingList(token, field="all"):

    PostingList = {}

    # if 'ice' in InvIndex.keys():
    #     print("ICE TRUE")

    if token in InvIndex.keys():
        print("TRUE: "+ token)
        token_entry = InvIndex[token]

        for docID in token_entry.keys():
            if field=="all" :
                freq = 0
                for field in token_entry[docID]:
                    freq = freq + token_entry[docID][field]
            else:
                freq = token_entry[docID][field]
            PostingList[docID] = freq

    return PostingList

def Search_Pages(query_tokens):

    Doc_Occurence = {}

    for token in query_tokens:
        Posting_List = Find_PostingList(token)
        print("POSTINGLIST: "+ token)
        print(Posting_List)
        for docID in Posting_List.keys():
            if docID not in Doc_Occurence :
                Doc_Occurence[docID] = 1
            else :
                Doc_Occurence[docID] = Doc_Occurence[docID] + 1

    Doc_Occurence = sorted(Doc_Occurence.items(), key=lambda kv: kv[1])
    return Doc_Occurence

def RelevantTitles(Doc_Occurence):

    TitleList = []
    for i in range(len(Doc_Occurence), 0, -1):
        TitleList.append(Page_ID_Title[Doc_Occurence[i-1]])
    print("TitleList: ")
    print(TitleList)
    return TitleList

def read_file(testfile):
    with open(testfile, 'r') as file:
        queries = file.readlines()
    return queries

def write_file(outputs, path_to_output):
    '''outputs should be a list of lists.
        len(outputs) = number of queries
        Each element in outputs should be a list of titles corresponding to a particular query.'''
    with open(path_to_output, 'w') as file:
        for output in outputs:
            for line in output:
                file.write(line.strip() + '\n')
            file.write('\n')

def search(path_to_index, queries):

    LoadIndex(path_to_index)
    outputs = []

    for query in queries:
        query_tokens = Query_processing(query)
        print("query_tokens: ")
        print(query_tokens)
        Doc_Occurence = Search_Pages(query_tokens)
        print("Doc_Occurence: ")
        print(Doc_Occurence)
        TitleList = RelevantTitles(Doc_Occurence)
        outputs.append(TitleList)
    return outputs

def main():
    # path_to_index = sys.argv[1]
    # testfile = sys.argv[2]
    # path_to_output = sys.argv[3]
    path_to_index = "index.pkl"
    testfile = "test.txt"
    path_to_output = "SearchResults.txt"

    queries = read_file(testfile)
    print("QUERIES :")
    print(queries)
    outputs = search(path_to_index, queries)
    write_file(outputs, path_to_output)

if __name__ == '__main__':
    main()
