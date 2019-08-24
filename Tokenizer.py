from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

tokenizer = RegexpTokenizer(r'\w+')

class TokenObject():

    def __init__(self):
        self.title = []
        self.infobox = []
        self.category = []
        self.links = []
        self.ref = []
        self.body = []

def word_tokenizer(IPFilePath):

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
            # print("LINE: "+line)
            if line.startswith("Title Content: "):

                if len(Tokenobj.title) != 0:

                    # print("NewPage")

                    # print("InfoboxText: "+InfoboxText)
                    # print("CategoryText: "+CategoryText)
                    # print("LinksText: "+LinksText)
                    # print("RefText: "+RefText)
                    # print("BodyText: "+BodyText)

                    # Tokenobj.infobox = word_tokenize(InfoboxText)
                    # Tokenobj.category = word_tokenize(CategoryText)
                    # Tokenobj.links = word_tokenize(LinksText)
                    # Tokenobj.ref = word_tokenize(RefText)
                    # Tokenobj.body = word_tokenize(BodyText)

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

                Tokenobj.title = word_tokenize(line[15:])
                continue

            elif line.startswith("Text Content: "):
                # print("TextContent")
                line = line[14:]

            else :
                # print("Pass")
                pass

            if InfoboxFlag or line.startswith("{{Infobox"):
                # print("Inside Infobox")
                if not InfoboxFlag:
                    InfoboxFlag = True
                    line = line[9:]
                if InfoboxFlag and line.startswith("}}"):
                    InfoboxFlag = False
                    # line = line[:-2]
                InfoboxText = InfoboxText + line

            elif CategoryFlag or line.startswith("[[Category:"):
                # print("Inside Cayegory")
                if line.startswith("[[Category:"):
                    line = line[11:]
                    CategoryFlag = True
                if CategoryFlag and line.endswith("]]"):
                    CategoryFlag = False
                    line = line[:-2]
                CategoryText = CategoryText + line

            elif RefFlag or "References" in line:
                # print("Inside References")
                if not RefFlag:
                    RefFlag = True
                    continue
                if RefFlag:
                    if line.startswith("{{"):
                        line = line[2:]
                    if line.endswith("}}"):
                        line = line[:-2]
                        RefFlag = False
                RefText = RefText + line

            elif LinksFlag or "External links" in line:
                # print("Inside Links")
                if not LinksFlag:
                    LinksFlag = True
                    continue
                if LinksFlag:
                    if line.startswith("*{{"):
                        line = line[3:]
                    if line.endswith("}}"):
                        line = line[:-2]
                        LinksFlag = False
                LinksText = LinksText + line

            else:
                # print("Inside Body")
                BodyText = BodyText + line

    # print("InfoboxText: "+InfoboxText)
    # print("CategoryText: "+CategoryText)
    # print("LinksText: "+LinksText)
    # print("RefText: "+RefText)
    # print("BodyText: "+BodyText)

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
