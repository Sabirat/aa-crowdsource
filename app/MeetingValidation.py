from flaskext.mysql import MySQL
from random import randint

def SearchDatabaseForRandomMeeting(mysql):
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT `meetingid`, `meetingday`, `meetingtime`, `meetingaddress`, `meetingurl`, `meetingcity`, `meetingX`, `meetingY`, `meetingwidth`, `meetingheight`, `meetingfulltext`, `meetingxpath`, `crowdapproved`, `crowddisapproved`, `approvedornot` from meetinginformation where crowdapproved<3")

	length=cursor.rowcount
	randomRecord=randint(0,length-1)
	
	contents=[]
	for i in range(length):
		ms = cursor.fetchone()
		contents.append(ms)

	onerecord=contents[randomRecord]
	return onerecord
