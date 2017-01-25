import time ,os ,re
from xml.etree import ElementTree

def GetMeetingTime(text):
	'''arr=["1 pm","2 pm","3 pm","4 pm","5 pm","6 pm","7 pm","8 pm","9 pm","10 pm","11 pm","12 pm","1 am","2 am","3 am","4 am","5 am","6 am","7 am","8 am","9 am","10 am","11 am","12 am", "1pm", "2pm", "3pm", "4pm", "5pm", "6pm", "7pm", "8pm", "9pm", "10pm", "11pm", "12pm", "1am", "2am", "3am", "4am", "5am", "6am", "7am", "8am", "9am", "10am", "11am", "12am"]'''
	text=text.replace("&nbsp;"," ")
	#text=text.replace("<"," ")
	text=text.lower()
	line=text

	#grp=re.finditer('\d{1,2}(:(\d{2})*)\s*(AM|am|PM|pm|a|p)?', line,re.I|re.M)
	grp=re.finditer('(([0-9]|0[0-9]|1[0-9]|2[0-3])(:[0-5][0-9])\s*(AM|am|PM|pm)?)|([0-9]|0[0-9]|1[0-9]|2[0-3])(:[0-5][0-9])?\s*(AM|am|PM|pm)|(([0-9]|0[0-9]|1[0-9]|2[0-3])(:[0-5][0-9])\s*(a|A|p|P))',line,re.I|re.M)

	for pp in grp:
		return text[pp.start():pp.end()]
	return ""

def GetMeetingAddress(text):
	line=text.lower()
	street_address = re.finditer("\d{1,4}(?:[\w\-]{1,2}) [\w\d\s\,\.\-\']{0,100}(?:street|st|avenue|av|ave|road|rd|highway|hwy|square|sq|trail|trl|drive|dr|court|ct|parkway|pkwy|circle|cir|boulevard|blvd|pike|pk|lane)",line,re.I|re.M)

	for pp in street_address:
		return text[pp.start():pp.end()]
	return ""

def GetMeetingDay(text):
	arr=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sun","Mon","Tues","Tue","Wed","Thurs","Thu","Fri","Sat"]
	text=text.lower()

	for el in arr:
		for pp in re.finditer(el.lower(), text,re.I|re.M):
			st=pp.start()
			return text[st:pp.end()]
	return ""
