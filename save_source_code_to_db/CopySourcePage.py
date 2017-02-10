from selenium import webdriver
import re
import sys, string
import MySQLdb
from urlparse import urlparse

# running "python CopySourcePage.py" will save all meeting page source codes into the database


# save one meeting page souce code into the database
# MORE CORNER CASES that has not been covered:
# 1. url(xxx.img)
# 2. url(../xxx.img)
def copy_source_page(url):
	reload(sys)
	sys.setdefaultencoding('utf-8')
	url_end_by_domain = getDomainUrl(url)
	incomplete_link_pattern = re.compile("\s*=\s*[\"'](?!http).*")
	index = 0; # index of string

	# get source code
	browser = webdriver.PhantomJS()
	browser.get(url)
	html_source = browser.page_source
	
	corrected_html_source = ""

	lens = len(html_source)
	src_index_found = html_source.find("src",index)
	src_index_found = src_index_found if src_index_found!=-1 else lens
	href_index_found = html_source.find("href",index)
	href_index_found = href_index_found if href_index_found!=-1 else lens
	index_found = min(href_index_found,src_index_found)
	
	corrected_html_source += html_source[index:index_found]
	index = index_found
	
	# scan source code and add  url_end_by_domain in any incomplete src or href links
	while(index<lens):
		if(html_source[index]=='h'):
			corrected_html_source += "href"
			index += 4
		else:
			corrected_html_source += "src"
			index += 3
		src_index_found = html_source.find("src",index)
		src_index_found = src_index_found if src_index_found!=-1 else lens
		href_index_found = html_source.find("href",index)
		href_index_found = href_index_found if href_index_found!=-1 else lens
		next_index_found = min(href_index_found,src_index_found)

		if(incomplete_link_pattern.match(html_source[index:next_index_found])):
			while(html_source[index].isspace()):
				index += 1
			corrected_html_source += "=\"" + url_end_by_domain
			index += 2
			while(html_source[index].isspace()):
				index += 1
			corrected_html_source += "/" + html_source[index:next_index_found]
		else:
			corrected_html_source += html_source[index:next_index_found]
		index = next_index_found
	
	browser.close()
		

	# deal with escape characters
	corrected_html_source = MySQLdb.escape_string(corrected_html_source)

	seq = 0
	index = 0
	lens = len(corrected_html_source)

	# connect to the database
	db = MySQLdb.connect("localhost", "root", "", "aameetings")
	cursor = db.cursor()
	
	while(index<lens):
		end = index+40960 if index+40960<=lens else lens
		while(corrected_html_source[end-1]=='\\'):
			end -= 1

		sql = "INSERT INTO local_domain_source_code (url, seq, source_code) VALUES " + "('" + url + "'," + str(seq) + ", '" + corrected_html_source[index:end] + "');"
		cursor.execute(sql)
		db.commit()

		seq += 1
		index = end
	
	cursor.close()
	db.close()

# input a full website url (with .html at the end) and return its domain url (without .html at the end)
def getDomainUrl(url):
	parsed_uri = urlparse(url)
	domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
	return domain

# main function
def main():
	#connect to the database
	db = MySQLdb.connect("localhost", "root", "", "aameetings")
	cursor = db.cursor()
	sql = "SELECT meetingurl FROM meetinginformation GROUP BY meetingurl"
	cursor.execute(sql)

	for row in cursor:
		copy_source_page(row[0])
		
main() # Invoke the main function
