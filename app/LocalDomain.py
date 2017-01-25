from selenium import webdriver
import re
import sys, string

# save website url in the variable named website_url and run the python codd
# then a local html file named full_local.html will be saved in the same path

# argv[1] = website address, e.g. "http://www.aawilliamsburg.org/CALENDAR_OF_EVENTS.html"

# MORE CORNER CASES:
# 1. url(xxx.img)
# 2. url(../xxx.img)

def copySourcePage(meetingrecord, pathf):
	path=path = "app/static/"+pathf
	url=meetingrecord[4]
	reload(sys)
	sys.setdefaultencoding('utf-8')
	url_end_by_domain = getDomainUrl(url)
	incomplete_link_pattern = re.compile("\s*=\s*[\"'](?!http).*")
	index = 0; # index of string

	# open html file
	local_html = open(path, "w+")

	# get source code
	#browser = webdriver.PhantomJS("D:\Research\phantomjs.exe")
	browser = webdriver.PhantomJS()
	browser.get(url);


	dbstring=filter(lambda x: x in string.printable,meetingrecord[10])
	dbstring="".join(dbstring.split()).replace("nbsp;","")

	info_elems=browser.find_elements_by_tag_name(meetingrecord[11])
	for elem in info_elems:
		outerhtml=filter(lambda x: x in string.printable, elem.get_attribute("outerHTML"))
		outerhtml="".join(outerhtml.split()).replace("&nbsp;","")

		if outerhtml==dbstring:
			script = "return arguments[0].id = 'bittamoni0'"
			browser.execute_script(script, elem)
			k=0
			allchildrenelems=elem.find_elements_by_xpath(".//*")
			for onechild in allchildrenelems:
				k+=1
				id_e='bittamoni'+str(k)
				script = "return arguments[0].id = '"+id_e+"'"
				browser.execute_script(script, onechild)

			break

	html_page_source = browser.page_source

	lenSource = len(html_page_source)
	srcIndexFound = html_page_source.find("src",index)
	srcIndexFound = srcIndexFound if srcIndexFound!=-1 else lenSource
	hrefIndexFound = html_page_source.find("href",index)
	hrefIndexFound = hrefIndexFound if hrefIndexFound!=-1 else lenSource
	indexFound = min(hrefIndexFound,srcIndexFound)
	local_html.write(html_page_source[index:indexFound])
	index = indexFound
	# scan source code and add  url_end_by_domain in any incomplete src or href links
	while(index<lenSource):
		if(html_page_source[index]=='h'):
			local_html.write("href")
			index += 4
		else:
			local_html.write("src")
			index += 3
		srcIndexFound = html_page_source.find("src",index)
		srcIndexFound = srcIndexFound if srcIndexFound!=-1 else lenSource
		hrefIndexFound = html_page_source.find("href",index)
		hrefIndexFound = hrefIndexFound if hrefIndexFound!=-1 else lenSource
		nextIndexFound = min(hrefIndexFound,srcIndexFound)

		if(incomplete_link_pattern.match(html_page_source[index:nextIndexFound])):
			while(html_page_source[index].isspace()):
				index +=1
			local_html.write("=\"" + url_end_by_domain)
			index += 2
			while(html_page_source[index].isspace()):
				index +=1
			local_html.write("/" + html_page_source[index:nextIndexFound])
		else:
			local_html.write(html_page_source[index:nextIndexFound])
		index = nextIndexFound
	# close browser and html file
	browser.close()

	scriptstr='<script>window.scroll(0,findPos(document.getElementById("bittamoni0"))-300); function findPos(obj) {var curtop = 0; if (obj.offsetParent) { do { curtop += obj.offsetTop; } while (obj = obj.offsetParent); return [curtop]; } } var elements = document.querySelectorAll(\'*[id^="bittamoni"]\'); for (var i = 0; i < elements.length; i++) {elements[i].style.backgroundColor = \'yellow\';} </script>'
	local_html.write(scriptstr);

	local_html.write('<style> *[id^="bittamoni"] {background-color:yellow;}</style>')
	local_html.close()

# input a full website url (with .html at the end) and return its domain url (without .html at the end)

from urlparse import urlparse

def getDomainUrl(url):
	parsed_uri = urlparse( url )
	domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
	return domain
