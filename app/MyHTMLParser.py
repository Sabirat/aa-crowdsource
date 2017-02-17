from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):
	def __init__(self):
	    HTMLParser.__init__(self)
	    self.data = []
	def handle_data(self, data):
	    self.data.append(data)

# this function will extract all texts from the html source code
# @param html - given html source code
def extract_text(html):
	parser = MyHTMLParser()
	parser.feed(html)
	return ''.join(parser.data)
