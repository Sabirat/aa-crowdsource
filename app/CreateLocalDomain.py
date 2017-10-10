# uncompyle6 version 2.11.2
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.12 (default, Jul  1 2016, 15:12:24) 
# [GCC 5.4.0 20160609]
# Embedded file name: /home/grad05/rubya001/AAmeeting/aa-crowdsource/app/CreateLocalDomain.py
# Compiled at: 2017-07-14 18:57:15
from selenium import webdriver
import re
import json
import sys
import string
import MySQLdb
import io
import os
import codecs
from shutil import copyfile
from highlightpdf import HighlightAMeetingInPDF

def create_local_domain(meetingrecord, path):
	try:
	    url = meetingrecord[14]
	    if meetingrecord[15].startswith('10'):
		path=path+".html"
		print >> sys.stderr, 'URL is' + url
		print >> sys.stderr, 'x is' + str(meetingrecord[5])
		print >> sys.stderr, 'y is' + str(meetingrecord[6])
		print >> sys.stderr, 'URL2' + url
		browser = webdriver.PhantomJS(executable_path='/home/grad05/rubya001/AAmeeting/aa-crowdsource/app/phantomjs/bin/phantomjs', service_log_path='/home/grad05/rubya001/AAmeeting/aa-crowdsource/app/ghostdriver.log')
		local_html = open(path, 'w+')
		html_source = ''
		db = MySQLdb.connect('localhost', 'root', 'br4cruta', 'AAmeetings')
		cursor = db.cursor()
		sql = 'SELECT textcontent FROM PageContentFromAlgo WHERE id =' + str(meetingrecord[4]) + ' ORDER BY sequenceofcontent'
		cursor.execute(sql)
		for row in cursor:
		    html_source += row[0]

		cursor.close()
		db.close()
		html_source.decode('string_escape')
		html_source=re.sub(r'[^\x00-\x7F]+','', html_source)
		local_html.write(html_source)
		local_html.close()
		abs_path = os.path.abspath(path)
		print >> sys.stderr, 'log msg' + abs_path
		browser.get(abs_path)
		print >> sys.stderr, 'log msg' + 'opened browser'
		text = meetingrecord[9].encode('utf8').decode('string_escape')
		elems = browser.find_elements_by_xpath('//' + meetingrecord[10])
		print >> sys.stderr, 'element text' + meetingrecord[10]
		local_html = codecs.open(path, 'w+', encoding='utf8')
		local_html.write(browser.page_source)
		print >> sys.stderr, 'loop ended'
		filtered_elemtext = filter(lambda x: x in string.printable, text)
		filtered_elemtext = ''.join(filtered_elemtext.split())
		testvar = '<script>var aTags = document.getElementsByTagName("' + meetingrecord[10] + '"); var searchText = "' + filtered_elemtext + '".replace((/  |\\r\\n|\\n|\\r|\\t|\\ /gm),"").replace(/[^\x20-\x7E]+/g, ""); var found; var count=0; var thatelem; for (var i = 0; i < aTags.length; i++) { var remtext=aTags[i].innerText.replace((/  |\\r\\n|\\n|\\r|\\t|\\ /gm),"").replace(/[^\x20-\x7E]+/g, ""); if (remtext==searchText ||(remtext.length>30 && searchText.indexOf(remtext)!=-1)) { count=count+1; thatelem=aTags[i]; break;}}   window.scroll(0,findPos(thatelem)-10); function findPos(obj) {var curtop = 0; if (obj.offsetParent) { do { curtop += obj.offsetTop; } while (obj = obj.offsetParent); return [curtop]; } } thatelem.style.backgroundColor = \'yellow\'; </script>'
		local_html.write(testvar)
		local_html.close()
		print >> sys.stderr, 'returning'
		return 1
	    elif meetingrecord[15]=='20':
		 #return 'error'
		db = MySQLdb.connect('localhost', 'root', 'br4cruta', 'AAmeetings')
		cursor = db.cursor()
		sql = 'SELECT localpath FROM PageInfoFromAlgo WHERE id =' + str(meetingrecord[4])
		cursor.execute(sql)
		for row in cursor:
		    pathofpdf= row[0]
		outputtemppath=HighlightAMeetingInPDF(meetingrecord,"/home/grad05/rubya001/AAmeeting/aa-crowdsource"+pathofpdf)
		copyfile(outputtemppath,path+".pdf")
		return 2
	    else:
		return 'error'
	except Exception as E:
		print "Exception in CreatelocalDomain..."+format(sys.exc_info()[-1].tb_lineno)
		print E
		return None
		pass
