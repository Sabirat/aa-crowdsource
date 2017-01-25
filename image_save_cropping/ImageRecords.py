from selenium import webdriver
import MySQLdb, sys
import string
import random
from PIL import Image

browser	= webdriver.PhantomJS("D:\Research\phantomjs.exe")
conn = MySQLdb.connect (host = "localhost",user = "root", passwd = "",db = "AAMeetings")
cursor = conn.cursor()
cursor2 = conn.cursor()

cursor.execute("DELETE FROM urlsbyimage")
conn.commit()

def rand_generator(size=10, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

g_url=""
def LoadPageAndTakeScreenShot(url,contents):
		elements=[]
		browser.get(url)

		alldict={}
		for row in contents:
			tagtofind=row[11]
			if alldict.get(tagtofind) is None:

				elemdict={}
				info_elems=browser.find_elements_by_tag_name(row[11])
				for elem in info_elems:
					outerhtml=filter(lambda x: x in string.printable, elem.get_attribute("outerHTML"))
					outerhtml="".join(outerhtml.split()).replace("&nbsp;","")
					elemdict[outerhtml]=elem

				alldict[tagtofind]=elemdict

		for row in contents:
			tagtofind=row[11]
			dbstring=filter(lambda x: x in string.printable,row[10])
			dbstring="".join(dbstring.split()).replace("nbsp;","")

			tagdict=alldict.get(tagtofind)
			element=tagdict.get(dbstring)
			elements.append(element)

			#print browser.title
		for e in elements:
			if e is not None:
				highlight(e)

		imagerand= 'multiMeetingScreenshot'+str(rand_generator())+'.png'
		browser.save_screenshot("../Step2 (crowd interface)/crowdImage/app/static/images/"+imagerand)
		cursor2.execute("""INSERT INTO urlsbyimage(url,fullorpartial,imagename) values(%s,%s,%s)""",(url,1,imagerand))
		return "../Step2 (crowd interface)/crowdImage/app/static/images/"+imagerand

def highlight(element):
    """Highlights (blinks) a Selenium Webdriver element"""
    #print("highlighting element")
    driver = element._parent
    def apply_style(s):
        driver.execute_script("arguments[0].style.background='yellow'",
                              element)
    original_style = element.get_attribute('style')
    apply_style("background: yellow; border: 5px solid red;")
    apply_style("border: 5px solid red;")

cursor.execute("SELECT distinct meetingurl from meetinginformation")
for i in range(cursor.rowcount):
	row = cursor.fetchone()
	g_url = row[0]

	if g_url is None:
		continue
	else:
		cursor2.execute("SELECT * from meetinginformation where meetingurl= %s",g_url)
		contents=[]
		for i in range(cursor2.rowcount):
			ms = cursor2.fetchone()
			contents.append(ms)

		retval=LoadPageAndTakeScreenShot(g_url,contents)
		if retval is not None:
			img=Image.open(retval)
			img_width=int(img.size[0])
			img_height=int(img.size[1])
			crop_y=0
			while crop_y<img_height:
				img2 = img.crop((0,crop_y,img_width,crop_y+400))
				path="img"+str(rand_generator())+".png"
				img2.save("../Step2 (crowd interface)/crowdImage/app/static/images/"+path)
				crop_y=crop_y+400
				cursor2.execute("""INSERT INTO urlsbyimage(url,fullorpartial,imagename) values(%s,%s,%s)""",(g_url,0,path))

conn.commit()
