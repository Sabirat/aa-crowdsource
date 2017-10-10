from app import app
from flask import render_template,session
from flask import Flask, request, redirect, url_for, render_template_string
from flask import Blueprint
from .. import db_config
import sys, random,json
#from db_config import config_db
api_app = Blueprint('api_app', __name__)
mysql=db_config.config_db()
######################################################## Function for API Endpoints  ##################################################################################
@api_app.route("/getPageURLs",methods=['post','get'])
def getPageURLs():

	if request.method=='GET': #and request.args.get('imei')=="123456789":
		passcode=request.args.get('passcode')
		getPageURLsWithParams(passcode)
	else:
		return "Error. Not a valid request."

def getPageURLsWithParams(passcode):
	conn = mysql.connect()
	cursor=conn.cursor()
	try:
		cursor.execute("SELECT id,url,pagetype from PageInfoFromAlgo where id not in (select urlid from PageApprovalFromCrowd where crowdid='"+passcode+"') and id not in (select urlid from PageApprovalFromCrowd where approved=1 group by urlid having count(urlid)>2) and id not in (select urlid from PageApprovalFromCrowd where approved=0 group by urlid having count(urlid)>2)")
		length=cursor.rowcount

		tenrandomrows=random.sample(range(1, length-1), 10)
		lst = []
		i=0
		for i in range(length):
			ms = cursor.fetchone()
			if i in tenrandomrows:
				d = {}
				d['urlid']=ms[0]
				d['url']=ms[1]
				d['type']=ms[2]
				lst.append(d)
			i+=1
		return json.dumps(lst,separators=(',',':'))

	except Exception as E:
		print "Exception in getPageURLs..."+format(sys.exc_info()[-1].tb_lineno)
		print E
		return "Error. Exception in Server."

@api_app.route("/setPasscode",methods=['post','get'])
def setPasscode():
	if request.method=='POST':
		passcode=request.args.get('passcode')
		return setPasscodeWithParams(passcode)
	else:
		return "not a POST request"


def setPasscodeWithParams(passcode):
	conn = mysql.connect()
	cursor=conn.cursor()
	try:
		cursor.execute("select * from CrowdInformation where crowdid='"+passcode+"'")
		if cursor.rowcount==0:
			cursor.execute("insert into CrowdInformation (crowdid) values('"+passcode+"')")
			conn.commit()
		return "Success"
	except Exception as E:
		print "Exception in setPasscodeWithParams..."+format(sys.exc_info()[-1].tb_lineno)
		print E
		return "Error"

@api_app.route("/postApprovalResult",methods=['post'])
def postApprovalResult():
	if request.method=='POST':
		passcode=request.args.get('passcode')
		urlid=request.args.get('urlid')
		approved=request.args.get('approved')
		postApprovalResultWthParams(passcode,urlid,approved)

	else:
		return "Not a POST request"

def postApprovalResultWthParams(passcode,urlid,approved):
		conn = mysql.connect()
		cursor=conn.cursor()
		try:
			cursor.execute("""insert into PageApprovalFromCrowd (crowdid,urlid,approved) values(%s,%s,%s)""",(passcode,urlid,approved))
			conn.commit()
			return "Success to post page approval"
		except Exception as E:
			print "Exception in postApprovalResultWthParams..."+format(sys.exc_info()[-1].tb_lineno)
			print E
			return "Error!"
