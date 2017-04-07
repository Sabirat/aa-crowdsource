from app import app
from flask import render_template
from flask import Flask, request, redirect, url_for
from random import randint
from flaskext.mysql import MySQL

from selenium import webdriver
import time
from PIL import Image
#from Pillow import Image
from pytesseract import image_to_string
from PIL import ImageFilter
#from Pillow import ImageFilter
import threading, os, sys, string

from helperFunctions import GetMeetingAddress, GetMeetingDay, GetMeetingTime
from MeetingValidation import SearchDatabaseForRandomMeeting
from CreateLocalDomain import create_local_domain

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'br4cruta'
app.config['MYSQL_DATABASE_DB'] = 'AAmeetings'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/index')
@app.route('/')

def index():
	return render_template('index.html',
                           title='Home')

@app.route('/FindAppropriateTask',methods=['POST'])
def FindAppropriateTask():
	if request.method == 'POST':
		if request.form['submit'] == 'Identify Meeting from Webpage':
			onerecord=LoadOneMeetingRecordFromDB()
			return render_template('MeetingIdentificationPage.html',url=onerecord[0],imagepath="images/"+onerecord[1])

		elif request.form['submit'] == 'Validate Meeting Information':	
			ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
			ts = str(int(time.time()))
			path=ROOT_DIR+'/static/local_files/local'+ts+'.html'
			onemeetingrecord=SearchDatabaseForRandomMeeting(mysql)

			create_local_domain(onemeetingrecord, path)
			return render_template('MeetingValidationPage.html',url='',htmlfilename='local_files/local'+ts+'.html',m_id=onemeetingrecord[0], day=onemeetingrecord[1], time=onemeetingrecord[2], address=onemeetingrecord[3])

		else:
			return render_template('index.html',title='Home')
	else:
		return render_template('index.html',title='Home')

'''assuming that all the cropped images have been saved in appstatic/imaes folder, this function randomly selects
one image to show with jcrop and returns the imagepath and url associated with it'''
def LoadOneMeetingRecordFromDB():
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT url,imagename from urlsbyimage where fullorpartial=0")

	length=cursor.rowcount
	randomRecord=randint(0,length-1)

	contents=[]
	for i in range(length):
		ms = cursor.fetchone()
		contents.append(ms)

	onerecord=contents[randomRecord]
	return onerecord

'''calls LoadOneMeetingRecordFromDB to get a random website image, lets worker crop a meeting portion'''
@app.route("/FindAMeeting")
def FindAMeeting():
	onerecord=LoadOneMeetingRecordFromDB()
	return render_template('MeetingIdentificationPage.html',url=onerecord[0],imagepath="images/"+onerecord[1])

'''when worker hits submit after cropping, this function is called from form submit and gets the portion of image cropped.
This shows something to the user but at the same time creates a new thread to do background processing to the image
(e.g., text extraction, finding matched web element and if found saving to DB)'''
@app.route("/ImageCropFormReturn", methods=['POST','get'])
def ImageCropFormReturn():
	x1=float(request.form['x'])
	y1=float(request.form['y'])
	x2=float(request.form['x2'])
	y2=float(request.form['y2'])
	url=request.form["corr_url"]
	img_path=request.form["img_path"]

	download_thread = threading.Thread(target=DoInBackground, args=(x1,y1,x2,y2,url,img_path))
	download_thread.start()

	return redirect(url_for('FindAMeeting'))
	#return "<div>Thank you. If you want to select another meeting please  <a href='./FindAMeeting'>click here</a></div>"

'''From form submit gets the x, y coordinates of images, crops the image and save it as img2.jpg.
Then using pytesseract it tries to extract text information from img2.jpg by calling MatchExtractedTextWithPage.
If it finds a matched element, saves to DB by calling and then deletes img2.jpg'''
def DoInBackground(x1,y1,x2,y2,url,img_path):
	img = Image.open("app/static/"+img_path)
	img2 = img.crop((x1,y1,x2,y2))
	img2.save("app/static/images/img2.jpg")

	imgCropped = Image.open("app/static/images/img2.jpg")		#hardcoded
	imgCropped.filter(ImageFilter.SHARPEN)

	#gray = im.convert('L')
	#bw = gray.point(lambda x: 0 if x<150 else 250, '1')
	#cleaned_image_name ='_cleaned.jpg'
	#bw.save(cleaned_image_name)

	print(imgCropped)
	extracted=image_to_string(imgCropped)

	similarItem=MatchExtractedTextWithPage(extracted,url)
	if similarItem is not None:
		InsertMeetingInDB(similarItem)
	os.remove("app/static/images/img2.jpg")

'''It takes as parameter the extracted text from img2.jpg and the URL of the website the image was cropped from.
At first it looks in the database to find the tags that are associated with meeting records on the particular website.
Then it opens phantomjs browser, finds the elements starting with those tags and see similarity matching with
extracted text by calling string_similarity function. If the percentage matching is more than 60% then saves
this meeting record'''
def MatchExtractedTextWithPage(extracted_text,real_url):
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT distinct meetingxpath,meetingcity from meetinginformation where meetingurl= %s",real_url)

	city=""
	tags_found=[]
	for i in range(cursor.rowcount):
		ms = cursor.fetchone()
		tags_found.append(ms[0])
		city=ms[1]

	allTags="|".join(tags_found)

	browser	= webdriver.PhantomJS("D:\Research\phantomjs.exe")
	browser.get(real_url)

	allTextsOfElements=[]
	info_elems=browser.find_elements_by_tag_name(allTags)
	for elem in info_elems:
		one_record={}
		text=elem.text
		tag=elem.tag_name

		fulltext=filter(lambda x: x in string.printable, text)
		outerhtml=filter(lambda x: x in string.printable, elem.get_attribute("outerHTML"))
		outerhtml="".join(outerhtml.split()).replace("&nbsp;","")

		outerhtml="".join(outerhtml.split()).replace("&nbsp;","")
		one_record['fulltext']=fulltext
		one_record['outerHTML']=outerhtml
		one_record['tag']=tag
		one_record['x']=elem.location['x']
		one_record['y']=elem.location['y']
		one_record['width']=elem.size['width']
		one_record['height']=elem.size['height']
		one_record['city']=city
		one_record['tag']=tag
		allTextsOfElements.append(one_record)

	max_similarity=0
	max_similar_elem={}

	for w2 in allTextsOfElements:
		percentage=string_similarity(extracted_text, w2['fulltext'])
		if percentage>max_similarity:
			max_similarity=percentage
			max_similar_elem=w2

	if max_similarity>0.4:
		max_similar_elem['url']=real_url
		max_similar_elem['time']= GetMeetingTime(max_similar_elem['fulltext'])
		max_similar_elem['day']=GetMeetingDay(max_similar_elem['fulltext'])
		max_similar_elem['address']=GetMeetingAddress(max_similar_elem['fulltext'])
		return max_similar_elem
	else:
		return None

'''the following two functions are needed for comparing strings for similarity percentage'''
def get_bigrams(string):
    '''
    Takes a string and returns a list of bigrams
    '''
    s = string.lower()
    return [s[i:i+2] for i in xrange(len(s) - 1)]

def string_similarity(str1, str2):
    '''
    Perform bigram comparison between two strings
    and return a percentage match in decimal form
    '''
    pairs1 = get_bigrams(str1)
    pairs2 = get_bigrams(str2)
    union  = len(pairs1) + len(pairs2)
    hit_count = 0
    for x in pairs1:
        for y in pairs2:
            if x == y:
                hit_count += 1
                break
    return (2.0 * hit_count) / union

'''given that a record has been found to match text extracted from crpped image this function saves that meeting to DB. These all
are done as background process'''
def InsertMeetingInDB(OneMeeting):
	conn = mysql.connect()
	cursor=conn.cursor()
	try:
	   cursor.execute("""INSERT INTO meetinginformation(meetingday,meetingtime,meetingaddress,
	   meetingurl,meetingcity,meetingX,meetingY,meetingwidth,meetingheight,meetingfulltext,meetingxpath)
	   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(OneMeeting['day'],OneMeeting['time'],OneMeeting['address'],
	   OneMeeting['url'],OneMeeting['city'],OneMeeting['x'],OneMeeting['y'],OneMeeting['width'],
	   OneMeeting['height'],OneMeeting['outerHTML'],OneMeeting['tag']))
	   conn.commit()
	except Exception as e:
		print "exception in db "+str(e)

########################here starts the functions/routes for meeting validation page#################################
'''if there is "no" selected in dropdown then we need to increase crowddisapproved in db, otherwise update the corresponding meeting information from form data'''
'''work on this function to split the db work in other functions'''
@app.route("/MeetingValidationFormReturn", methods=['POST','get'])
def MeetingValidationFormReturn():
	print request.method
	if request.method=='GET':
		dropdownvalue=request.args.get('dropdownvalue')
		print dropdownvalue
		if dropdownvalue=="no":
			mid_fromhtml_no=request.args.get('mId')
			UpdateDisapproval(mid_fromhtml_no)
			#return redirect(url_for('index'))

			ts = str(int(time.time()))
			path='local_files/local'+ts+'.html'
			onemeetingrecord=SearchDatabaseForRandomMeeting(mysql)
			create_local_domain(onemeetingrecord, path)
			return render_template('MeetingValidationPage.html',url='',htmlfilename=path,m_id=onemeetingrecord[0], day=onemeetingrecord[1], time=onemeetingrecord[2], address=onemeetingrecord[3])

		return "<div>Thank you2.</div>"
	elif request.method=='POST':
		mTime=request.form['mTime']
		mDay=request.form['mDay']
		mAddress=request.form['mAddress']
		mid_fromhtml_no=request.form['mId']

		UpdateApproval(mid_fromhtml_no,mTime, mDay, mAddress)
		#return redirect(url_for('index'))
		ts = str(int(time.time()))
		path='local_files/local'+ts+'.html'
		onemeetingrecord=SearchDatabaseForRandomMeeting(mysql)
		create_local_domain(onemeetingrecord, path)
		return render_template('MeetingValidationPage.html',url='',htmlfilename=path,m_id=onemeetingrecord[0], day=onemeetingrecord[1], time=onemeetingrecord[2], address=onemeetingrecord[3])
	else:
		return redirect(url_for('index'))

def UpdateDisapproval(mid_fromhtml_no):
	conn = mysql.connect()
	cursor=conn.cursor()
	try:
		'''cursor.execute("SELECT crowddisapproved from meetinginformation where meetingid= %d",mid_fromhtml_no)
		disapprove_count=cursor.fetchone()[0]
		disapprove_count+=1'''
		midint=int(mid_fromhtml_no)
		cursor.execute("""update meetinginformation set crowddisapproved=crowddisapproved+1 where meetingid=%s""",midint)
		conn.commit()
	except Exception as e:
		print "exception in db "+str(e)

def UpdateApproval(mid_fromhtml_no,timeForm,dayForm,addressForm):
	conn = mysql.connect()
	cursor=conn.cursor()
	try:
		'''cursor.execute("SELECT crowddisapproved from meetinginformation where meetingid= %d",mid_fromhtml_no)
		disapprove_count=cursor.fetchone()[0]
		disapprove_count+=1'''
		midint=int(mid_fromhtml_no)
		cursor.execute("""update meetinginformation set meetingtime=%s, meetingday=%s, meetingaddress=%s, crowdapproved=crowdapproved+1 where meetingid=%s""",(timeForm,dayForm,addressForm,midint))
		conn.commit()
	except Exception as e:
		print "exception in db "+str(e)
