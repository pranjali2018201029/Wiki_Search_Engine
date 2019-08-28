from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import sys
import pickle
from stemming import porter as ps

stop_words = set(stopwords.words('english'))
tokenizer = RegexpTokenizer(r'\w+')
#ps = PorterStemmer()

InvIndex = {}
Page_ID_Title = {}

def LoadIndex(path_to_index_folder):
    global InvIndex
    global Page_ID_Title

    with open(path_to_index_folder+"/index.pkl", 'rb') as file:
        InvIndex = pickle.load(file)

    with open(path_to_index_folder+"/title_id.pkl", 'rb') as file:
        Page_ID_Title = pickle.load(file)

def Query_processing(query):

    query_tokens = tokenizer.tokenize(query)
    query_tokens = [w.casefold() for w in query_tokens]
    query_tokens = [w for w in query_tokens if w not in stop_words]
    query_tokens = [ps.stem(w) for w in query_tokens]

    return query_tokens, []

def Field_Query_Processing(query):

    query_tokens = []
    fields = []
    field_tokens = query.split()

    for field_token in field_tokens:
        tokens = field_token.split(':')
        fields.append(tokens[0][0])
        query_tokens.append(tokens[1])

    query_tokens = [w.casefold() for w in query_tokens]
    query_tokens = [w for w in query_tokens if w not in stop_words]
    query_tokens = [ps.stem(w) for w in query_tokens]

    return query_tokens, fields

def Find_PostingList(token, field="all"):

    PostingList = {}

    if token in InvIndex.keys():
        token_entry = InvIndex[token]

        for docID in token_entry.keys():
            if field=="all" :
                freq = 0
                for key in token_entry[docID].keys():
                    freq = freq + token_entry[docID][key]
                PostingList[docID] = freq
            else:
                if field in token_entry[docID].keys():
                    PostingList[docID] = token_entry[docID][field]

    return PostingList

def Search_Pages(query_tokens, fields=[]):

    ## Dict DocID: [Intersections, Occurences]
    Doc_Occurence = {}

    for i in range(len(query_tokens)):
        token = query_tokens[i]

        if len(fields) == 0:
            field = "all"
        else:
            field = fields[i]
        Posting_List = Find_PostingList(token, field)

        for docID in Posting_List.keys():

            if docID not in Doc_Occurence :
                Doc_Occurence[docID] = [1, Posting_List[docID]]
            else :
                Doc_Occurence[docID][1] = Doc_Occurence[docID][1] + Posting_List[docID]
                Doc_Occurence[docID][0] = Doc_Occurence[docID][0] + 1

    Doc_Occurence = sorted(Doc_Occurence.items(), key = lambda x: (x[1][0], x[1][1]), reverse=True)
    return Doc_Occurence

def RelevantTitles(Doc_Occurence, TopN):

    TitleList = []
    for i in range(0, TopN, 1):
        TitleList.append(Page_ID_Title[Doc_Occurence[i][0]])
    return TitleList

def read_file(testfile):

    with open(testfile, 'r') as file:
        queries = file.readlines()
    return queries

def write_file(outputs, path_to_output):

    with open(path_to_output, 'w') as file:
        for output in outputs:
            for line in output:
                file.write(line.strip() + '\n')
            file.write('\n')

def search(path_to_index, queries):
    outputs = []
    field_query_flag = False

    for query in queries:
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
        Doc_Occurence = Search_Pages(query_tokens, fields)
        TitleList = RelevantTitles(Doc_Occurence, 10)
        outputs.append(TitleList)
    return outputs

def main():

    path_to_index = sys.argv[1]
    testfile = sys.argv[2]
    path_to_output = sys.argv[3]

    ## Load Index and Title_ID mapping in Data Structures
    LoadIndex(path_to_index)

    queries = read_file(testfile)
    outputs = search(path_to_index, queries)
    write_file(outputs, path_to_output)

if __name__ == '__main__':
    main()
    print("TOKEN COUNT: "+ str(len(InvIndex.keys())))
