from flaskext.mysql import MySQL
from random import randint

def SearchDatabaseForRandomMeeting(mysql):
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT `meetingid`, `day`, `time`, `address`, `urlid`, `xcoord`, `ycoord`, `width`, `height`, `meetingtext`, `firsttag`, `crowdapproved`, `crowddisapproved`, `approvedornot` from MeetingInfoFromAlgo where crowdapproved<3 and meetingid in (select meetingid from PageInfoFromAlgo where pagetype='20')")

	length=cursor.rowcount
	randomRecord=randint(0,length-1)
	
	contents=[]
	for i in range(length):
		ms = cursor.fetchone()
		contents.append(ms)

	onerecord=contents[randomRecord]
	recordaslist=list(onerecord)

	mid=recordaslist[4]
	cursor.execute("SELECT `id`, `url`, `pagetype` from PageInfoFromAlgo where id="+str(mid))
	urlrow=cursor.fetchone()
	recordaslist.append(urlrow[1])
	recordaslist.append(urlrow[2])
	return recordaslist
