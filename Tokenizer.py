from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

## Class object will store field wise tokens for one WikiPage
class TokenObject():

    def __init__(self):
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

## Input : Filtered parsed data file
def word_tokenizer(IPFilePath):

    Tokenobj = TokenObject()

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

def StopWordRemoval():

    infobox_stopwords = ['Infobox', 'infobox']
    category_stopwords = ['Category', 'category']
    links_stopwords = ['External links']
    ref_stopwords = ['Reflist', 'reflist', 'Bibliography', 'bibliography']
    body_stopwords = ['REDIRECT']

    ## Stopword removal, Numbers removal and case folding
    for Tokenobj in TokenPages:
        Tokenobj.title = [w.casefold() for w in Tokenobj.title]
        Tokenobj.infobox = [w.casefold() for w in Tokenobj.infobox if w not in infobox_stopwords and w not in stop_words and w.isalpha()]
        Tokenobj.category = [w.casefold() for w in Tokenobj.category if w not in category_stopwords and w not in stop_words and w.isalpha()]
        Tokenobj.links = [w.casefold() for w in Tokenobj.links if w not in links_stopwords and w not in stop_words and w.isalpha()]
        Tokenobj.ref = [w.casefold() for w in Tokenobj.ref if w not in ref_stopwords and w not in stop_words and w.isalpha()]
        Tokenobj.body = [w.casefold() for w in Tokenobj.body if w not in body_stopwords and w not in stop_words and w.isalpha()]

def Stemming():

    for Tokenobj in TokenPages:
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

word_tokenizer("Phase_1_Result.xml")
print("TOKENIZATION DONE")
StopWordRemoval()
print("STOP WORD REMOVAL AND CASE FOLDING DONE")
Stemming()
print("STEMMING DONE")
PrintTokens()
