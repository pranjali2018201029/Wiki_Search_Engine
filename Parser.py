import xml.sax
from xml.sax import make_parser
from xml.sax.saxutils import XMLFilterBase, XMLGenerator
import time
import sys
import re

## Remove URL from the text
URL_RegEx = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',re.DOTALL)
## Remove CSS from the text
CSS_RegEx = re.compile(r'&lt.*&gt;', re.DOTALL)
## Remove html tags
Tags_RegEx = re.compile(r'<(.*?)>',re.DOTALL)

class WikiContenthandler(xml.sax.ContentHandler):

    def __init__(self):

        xml.sax.ContentHandler.__init__(self)

        self.text_tag = False
        self.text = ""

        self.title_tag = False
        self.title = ""

        self.RedirectFlag = False
        self.ResultFile = open("./Phase_1_Result.xml", 'w')

    def startElement(self, name, attrs):

        if name == "text":
            self.text_tag = True

        if name == "title":
            self.title_tag = True

    def endElement(self, name):

        if name == "title":
            self.title_tag = False
            self.ResultFile.write("Title Content: " + self.title + "\n")
            self.title = ""

        if name == "text":
            self.text_tag = False
            self.RedirectFlag = False
            self.text = URL_RegEx.sub('',self.text)
            self.text = CSS_RegEx.sub('',self.text)
            self.text = Tags_RegEx.sub('',self.text)
            self.ResultFile.write("Text Content: " + self.text + "\n")
            self.ResultFile.write("\n")
            self.text = ""

    def characters(self, content):

        if self.title_tag :
            self.title = content

        if self.text_tag :
            if "#REDIRECT" in content:
                self.RedirectFlag = True
            if not self.RedirectFlag:
                self.text = self.text + content

    def __del__(self):
        self.ResultFile.close()

if __name__ == "__main__":

    start = time.time()

    source = open(sys.argv[1])
    xml.sax.parse(source, WikiContenthandler())

    end = time.time()
    print("PARSING TIME: ", end-start)
