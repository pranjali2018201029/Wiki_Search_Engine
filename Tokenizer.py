from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import json

## Class object will store field wise tokens for one WikiPage
class TokenObject():

    def __init__(self):
        self.id = 0
        self.title = []
        self.infobox = []
        self.category = []
        self.links = []
        self.ref = []
        self.body = []

## List of stop words, words that not need to be indexed in Wikidata
stop_words = set(stopwords.words('english'))
## Tokenizer by using only space as delimiter so punctuations are removed
tokenizer = RegexpTokenizer(r'\w+')
## PorterStemmer
ps = PorterStemmer()
## List of tokenobjects <--> List of pages
TokenPages = []
## Inverted Index Data Structure
InvIndex = {}
## Data Structure with mapping of PageID and PageTitle for search results
Page_ID_Title = {}

## Input : Filtered parsed data file
def word_tokenizer(IPFilePath):

    Tokenobj = TokenObject()
    PageID = 0

    InfoboxText = ""
    CategoryText = ""
    LinksText = ""
    RefText = ""
    BodyText = ""

    InfoboxFlag = False
    CategoryFlag = False
    LinksFlag = False
    RefFlag = False

    with open(IPFilePath, 'r') as f:

        for line in f:

            if line.startswith("Title Content: "):
                ## If line is title line

                if len(Tokenobj.title) != 0:
                    ## If this is not first page, Tokenobj is not empty
                    ## Tokenize each field content for previous page

                    Tokenobj.infobox = tokenizer.tokenize(InfoboxText)
                    Tokenobj.category = tokenizer.tokenize(CategoryText)
                    Tokenobj.links = tokenizer.tokenize(LinksText)
                    Tokenobj.ref = tokenizer.tokenize(RefText)
                    Tokenobj.body = tokenizer.tokenize(BodyText)

                    ## Append previous page obj to objlist
                    ## and Create new empty object for new page
                    TokenPages.append(Tokenobj)
                    Tokenobj = TokenObject()

                    ## Initialize all variables and flags for new page
                    InfoboxText = ""
                    CategoryText = ""
                    LinksText = ""
                    RefText = ""
                    BodyText = ""

                    InfoboxFlag = False
                    CategoryFlag = False
                    LinksFlag = False
                    RefFlag = False

                ## Continue reading next line after processing for this title line
                PageID = PageID + 1
                Tokenobj.id = PageID
                Page_ID_Title[PageID] = line[15:]
                Tokenobj.title = tokenizer.tokenize(line[15:])
                continue

            elif line.startswith("Text Content: "):
                ## If line is part of text content of page
                line = line[14:]

            else :
                pass

            if LinksFlag or "==External" in line:
                ## External links : *{{}} or *[] or *
                if not LinksFlag:
                    LinksFlag = True
                elif (not line.startswith("*{{")) and (not line.startswith("*[")):
                    LinksFlag = False
                else:
                    LinksText = LinksText + line

            if RefFlag or "References" in line:
                if not RefFlag:
                    ## References starts
                    RefFlag = True
                else:
                    ## References are represented in multiple formats (Not-uniform)
                    ## References ends when External links or Category field starts
                    if ("External links" in line) or (line.startswith("[[Category:")):
                        RefFlag = False
                        continue
                    RefText = RefText + line

            elif InfoboxFlag or line.startswith("{{Infobox"):
                if not InfoboxFlag:
                    ## Infobox content started
                    InfoboxFlag = True
                    line = line[9:]
                if InfoboxFlag and line.startswith("}}"):
                    ## Infobox content ends
                    InfoboxFlag = False
                ## Append all content inside infobox
                ## which will be tokenize once title of next page is read
                InfoboxText = InfoboxText + line

            elif CategoryFlag or line.startswith("[[Category:"):
                ## Category field is list of [[Category:text]] entries
                if line.startswith("[[Category:"):
                    ## Category entry starts
                    line = line[11:]
                    CategoryFlag = True
                if CategoryFlag and line.endswith("]]"):
                    ## Category entry ends
                    CategoryFlag = False
                    line = line[:-2]
                CategoryText = CategoryText + line

            else:
                ## Text not inside any of the above fields conidered as body
                if not LinksFlag:
                    BodyText = BodyText + line

    ## Precossing for last page
    Tokenobj.infobox = tokenizer.tokenize(InfoboxText)
    Tokenobj.category = tokenizer.tokenize(CategoryText)
    Tokenobj.links = tokenizer.tokenize(LinksText)
    Tokenobj.ref = tokenizer.tokenize(RefText)
    Tokenobj.body = tokenizer.tokenize(BodyText)

    TokenPages.append(Tokenobj)

def CaseFolding():

    for Tokenobj in TokenPages:
        Tokenobj.title = [w.casefold() for w in Tokenobj.title]
        Tokenobj.infobox = [w.casefold() for w in Tokenobj.infobox]
        Tokenobj.category = [w.casefold() for w in Tokenobj.category]
        Tokenobj.links = [w.casefold() for w in Tokenobj.links]
        Tokenobj.ref = [w.casefold() for w in Tokenobj.ref]
        Tokenobj.body = [w.casefold() for w in Tokenobj.body]


def StopWordRemoval():

    infobox_stopwords = ['infobox']
    category_stopwords = ['category']
    links_stopwords = ['external links']
    ref_stopwords = ['reflist','bibliography']
    body_stopwords = ['redirect']

    ## Stopword removal, Numbers removal and case folding
    for Tokenobj in TokenPages:
        Tokenobj.title = [w for w in Tokenobj.title if w not in stop_words and w.isalpha()]
        Tokenobj.infobox = [w for w in Tokenobj.infobox if w not in infobox_stopwords and w not in stop_words and w.isalpha()]
        Tokenobj.category = [w for w in Tokenobj.category if w not in category_stopwords and w not in stop_words and w.isalpha()]
        Tokenobj.links = [w for w in Tokenobj.links if w not in links_stopwords and w not in stop_words and w.isalpha()]
        Tokenobj.ref = [w for w in Tokenobj.ref if w not in ref_stopwords and w not in stop_words and w.isalpha()]
        Tokenobj.body = [w for w in Tokenobj.body if w not in body_stopwords and w not in stop_words and w.isalpha()]

def Stemming():

    for Tokenobj in TokenPages:
        Tokenobj.title = [ps.stem(w) for w in Tokenobj.title]
        Tokenobj.infobox = [ps.stem(w) for w in Tokenobj.infobox]
        Tokenobj.category = [ps.stem(w) for w in Tokenobj.category]
        Tokenobj.links = [ps.stem(w) for w in Tokenobj.links]
        Tokenobj.ref = [ps.stem(w) for w in Tokenobj.ref]
        Tokenobj.body = [ps.stem(w) for w in Tokenobj.body]

def PrintTokens():

    for Tokenobj in TokenPages:
        print("\nTITLE TOKENS")
        print(Tokenobj.title)
        print("INFOBOX TOKENS")
        print(Tokenobj.infobox)
        print("CATEGORY TOKENS")
        print(Tokenobj.category)
        print("LINKS TOKENS")
        print(Tokenobj.links)
        print("REFERENCES TOKENS")
        print(Tokenobj.ref)
        print("BODY TOKENS")
        print(Tokenobj.body)

def Check_Index(word, doc_id):

    if word not in InvIndex.keys():
        InvIndex[word] = {}
    if doc_id not in InvIndex[word].keys():
        InvIndex[word][doc_id] = {}

def Create_Index():

    for TokenObj in TokenPages:

        for w in TokenObj.title:
            Check_Index(w, TokenObj.id)
            if 't' not in InvIndex[w][TokenObj.id].keys():
                 InvIndex[w][TokenObj.id]['t'] = 1
            else:
                InvIndex[w][TokenObj.id]['t'] = InvIndex[w][TokenObj.id]['t'] + 1

        for w in TokenObj.infobox:
            Check_Index(w, TokenObj.id)
            if 'i' not in InvIndex[w][TokenObj.id].keys():
                 InvIndex[w][TokenObj.id]['i'] = 1
            else:
                InvIndex[w][TokenObj.id]['i'] = InvIndex[w][TokenObj.id]['i'] + 1

        for w in TokenObj.category:
            Check_Index(w, TokenObj.id)
            if 'c' not in InvIndex[w][TokenObj.id].keys():
                 InvIndex[w][TokenObj.id]['c'] = 1
            else:
                InvIndex[w][TokenObj.id]['c'] = InvIndex[w][TokenObj.id]['c'] + 1

        for w in TokenObj.links:
            Check_Index(w, TokenObj.id)
            if 'l' not in InvIndex[w][TokenObj.id].keys():
                 InvIndex[w][TokenObj.id]['l'] = 1
            else:
                InvIndex[w][TokenObj.id]['l'] = InvIndex[w][TokenObj.id]['l'] + 1

        for w in TokenObj.ref:
            Check_Index(w, TokenObj.id)
            if 'r' not in InvIndex[w][TokenObj.id].keys():
                 InvIndex[w][TokenObj.id]['r'] = 1
            else:
                InvIndex[w][TokenObj.id]['r'] = InvIndex[w][TokenObj.id]['r'] + 1

        for w in TokenObj.body:
            Check_Index(w, TokenObj.id)
            if 'b' not in InvIndex[w][TokenObj.id].keys():
                 InvIndex[w][TokenObj.id]['b'] = 1
            else:
                InvIndex[w][TokenObj.id]['b'] = InvIndex[w][TokenObj.id]['b'] + 1

def Store_Index():
    with open('index.json', 'w') as file:
     file.write(json.dumps(InvIndex))

word_tokenizer("Phase_1_Result.xml")
print("TOKENIZATION DONE")
CaseFolding()
StopWordRemoval()
print("STOP WORD REMOVAL AND CASE FOLDING DONE")
Stemming()
print("STEMMING DONE")
Create_Index()
print("INDEX CREATION DONE")
Store_Index()
print("INDEX STORED")
