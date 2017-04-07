from selenium import webdriver
import re
import sys, string
import MySQLdb
import os

def create_local_domain(meetingrecord, pathf):	
	reload(sys)
	sys.setdefaultencoding('utf-8')

	#local_html = open(path, "w+")

        # get source code
        #browser = webdriver.PhantomJS("D:\Research\phantomjs.exe")
        browser = webdriver.PhantomJS(executable_path='/home/grad05/rubya001/AAmeeting/aa-crowdsource/app/phantomjs/bin/phantomjs',
                                service_log_path='/home/grad05/rubya001/AAmeeting/aa-crowdsource/app/ghostdriver.log')
        browser.get(url);


	#path = "app/static/"+pathf
	local_html = open(path, "w+")
	html_source = ""
	
	# connect to the database
	db = MySQLdb.connect("localhost", "root", "", "aameetings")
	cursor = db.cursor()
	# get html source code from the data base
	sql = "SELECT source_code FROM local_domain_source_code WHERE url = " + "'"+ meetingrecord[4] +"' ORDER BY seq"
	cursor.execute(sql)
	for row in cursor:
		html_source += row[0]
	cursor.close()
	db.close()	

	# remove escape characters
	html_source.decode('string_escape')
	
	local_html.write(html_source);	
	local_html.close()

	# load a local html
	#abs_path = os.path.abspath(path)
	#browser = webdriver.PhantomJS()
	#browser.get(abs_path);

	# get full text from the database
	text = meetingrecord[10].decode('string_escape')

	# find the element that contains matched text
	elems = browser.find_elements_by_xpath("//" + meetingrecord[11])
	lists=(o for o in elems if o.text==text)

	# add an id in this element and its children elements
	elem = lists.next()
	script = "return arguments[0].id = 'bittamoni0'"
	browser.execute_script(script, elem)
	k=0
	allchildrenelems=elem.find_elements_by_xpath(".//*")
	for onechild in allchildrenelems:
		k+=1
		id_e='bittamoni'+str(k)
		script = "return arguments[0].id = '"+id_e+"'"
		browser.execute_script(script, onechild)
			
	local_html = open(path, "w+")
	local_html.write(browser.page_source);	
	
	scriptstr='<script>window.scroll(0,findPos(document.getElementById("bittamoni0"))-300); function findPos(obj) {var curtop = 0; if (obj.offsetParent) { do { curtop += obj.offsetTop; } while (obj = obj.offsetParent); return [curtop]; } } var elements = document.querySelectorAll(\'*[id^="bittamoni"]\'); for (var i = 0; i < elements.length; i++) {elements[i].style.backgroundColor = \'yellow\';} </script>'
	local_html.write(scriptstr);
	
	local_html.write('<style> *[id^="bittamoni"] {background-color:yellow;}</style>')
	local_html.close()
	browser.quit()

