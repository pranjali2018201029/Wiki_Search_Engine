from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer

## Tokenizer by using only space as delimiter so punctuations are removed
tokenizer = RegexpTokenizer(r'\w+')

## Class object will store field wise tokens for one WikiPage
class TokenObject():

    def __init__(self):
        self.title = []
        self.infobox = []
        self.category = []
        self.links = []
        self.ref = []
        self.body = []

## Input : Filtered parsed data file
def word_tokenizer(IPFilePath):

    ## List of tokenobjects <--> List of pages
    TokenPages = []
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
                Tokenobj.title = word_tokenize(line[15:])
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

    TokenPages.append(Tokenobj)

word_tokenizer("Phase_1_Result.xml")
