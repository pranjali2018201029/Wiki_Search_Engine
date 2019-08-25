import xml.sax
from xml.sax import make_parser
from xml.sax.saxutils import XMLFilterBase, XMLGenerator

class WikiContentFilter(XMLFilterBase):

    def __init__(self, tag_names_to_exclude, parent=None):
        super().__init__(parent)
        self._tag_names_to_exclude = tag_names_to_exclude
        self._tag_count = 0

    def startElement(self, name, attrs):
        if name in self._tag_names_to_exclude:
            self._tag_count += 1

        if self._forward_events():
            super().startElement(name, attrs)

    def _forward_events(self):
        return self._tag_count == 0

    def endElement(self, name):
        if self._forward_events():
            super().endElement(name)

        if name in self._tag_names_to_exclude:
            self._tag_count -= 1

    def characters(self, content):
        if self._forward_events():
            super().characters(content)

class WikiContenthandler(xml.sax.ContentHandler):

    def __init__(self):

        xml.sax.ContentHandler.__init__(self)

        self.text_tag = False
        self.text = ""

        self.title_tag = False
        self.title = ""

        self.ResultFile = open("Phase_1_Result.xml", 'w')

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
            self.ResultFile.write("Text Content: " + self.text + "\n")
            self.ResultFile.write("\n")
            self.text = ""

    def characters(self, content):

        if self.title_tag :
            self.title = content

        if self.text_tag :
            self.text = self.text + content

    def __del__(self):
        self.ResultFile.close()

def main(tag_names_to_exclude, sourceFileName, FilteredFilePath):

    reader = WikiContentFilter(tag_names_to_exclude, make_parser())

    with open(FilteredFilePath, 'w') as f:
        handler = XMLGenerator(f)
        reader.setContentHandler(handler)
        reader.parse(sourceFileName)

    source = open(FilteredFilePath)
    xml.sax.parse(source, WikiContenthandler())

if __name__ == "__main__":

    tag_names_to_exclude = {'siteinfo', 'ns', 'timestamp', 'contributor', 'model', 'format', 'id', 'redirect', 'comment', 'sha1'}
    main(tag_names_to_exclude, "Phase1_Dump.xml", "Phase_1_Filtered.xml")
    print("PARSING DONE")
