from flask import Flask, jsonify, request, send_file, abort
import mysql.connector
from flask_cors import CORS
#from collections import OrderedDict
import requests, datetime, json,os,sys
from werkzeug import secure_filename
app = Flask(__name__)
CORS(app)

mydb=None
mycursor=None

def connectToDB():
	try:
		# mydb = mysql.connector.connect(host="localhost",user="witest123",password="witest123",database="user_notes")
		mydb_first = mysql.connector.connect(host="localhost", user="root", password="interOP@123")
		mycursor_first = mydb_first.cursor()

		mycursor_first.execute("SHOW DATABASES")
		isdbpresent=0
		for x in mycursor_first:
			if "witestdbfinal" in x:
				isdbpresent=1
				break;

		if not isdbpresent:
			mycursor_first.execute("CREATE DATABASE witestdbfinal")
			mydb_first.commit()

		#mycursor.execute("USE witestdb")

		global mydb
		global mycursor

		mydb = mysql.connector.connect(host="localhost", user="root", password="interOP@123",database="witestdbfinal")
		mycursor = mydb.cursor(buffered=True)
		mycursor.execute("SHOW TABLES")
		is_userinfo_present=0
		is_notesinfo_present = 0
		for x in mycursor:
			if is_userinfo_present==1 and is_notesinfo_present==1:
				break
			if "userinfofinal" in x:
				is_userinfo_present=1
				continue
			if "notesinfofinal" in x:
				is_notesinfo_present=1
				continue

		if is_userinfo_present==0:
			mycursor.execute("CREATE TABLE userinfofinal (userid INT PRIMARY KEY, username VARCHAR(50) , password VARCHAR(50))")
			mydb.commit()

		if is_notesinfo_present==0:
			mycursor.execute("CREATE TABLE notesinfofinal (userid INT, note VARCHAR(255))")
			mydb.commit()

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		print ("Error", e)
		print("SERVER ERROR", e)
		return "SERVER ERROR"


@app.route('/app/user', methods = ['POST'])
def registerUser():
	try:
		connectToDB()
		resp={}
		data = request.get_json()
		username=data["username"]
		password=data["password"]


		mycursor.execute(
			"SELECT username, COUNT(*) FROM userinfofinal WHERE username = %s",
			(username,)
		)

		row_count = mycursor.rowcount
		print(row_count)
		if row_count>0:
			resp["status"]="username already exists"
		else:
			sql = "INSERT INTO userinfofinal (userid, username, password) VALUES (%s, %s, %s)"
			val = (mycursor.lastrowid+1,username, password)
			# val = [username, password]
			mycursor.execute(sql, val)
			mydb.commit()
			resp["status"] = "account created"

		return resp

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		print ("Error", e)
		print("SERVER ERROR", e)
		return "SERVER ERROR"

@app.route('/app/user/auth', methods = ['POST'])
def loginUser():
	try:
		connectToDB()
		resp={}
		data = request.get_json()
		username=data["username"]
		password=data["password"]

		mycursor.execute(
			"SELECT username, COUNT(*) FROM userinfofinal WHERE username = %s AND password = %s",
			(username,password)
		)

		row_count = mycursor.rowcount
		print(row_count)
		if row_count==0:
			resp["status"]="wrong username or password"
		else:
			sql = "SELECT userid FROM userinfofinal WHERE username = %s"
			val = (username,)
			mycursor.execute(sql, val)
			result=mycursor.fetchall()
			userid=result[0]
			resp["status"] = "success"
			resp["userId"] = userid

		return resp

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		print ("Error", e)
		print("SERVER ERROR", e)
		return "SERVER ERROR"

@app.route('/app/sites/list/', methods = ['GET'])
def listNotes():
	try:
		connectToDB()
		resp=[]
		userId = request.args.get('user')
		
		mycursor.execute(
			"SELECT note FROM notesinfofinal Group By userid WHERE userid = %s",
			(userId,)
		)

		result=mycursor.fetchall()
		print(result)
		for x in result:
			resp.append(x)

		return resp

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		print ("Error", e)
		print("SERVER ERROR", e)
		return "SERVER ERROR"

@app.route('/app/sites/', methods = ['POST'])
def addNote():
	try:
		connectToDB()
		resp = {}
		data = request.get_json()
		userId = request.args.get('user')
		note = data["note"]

		mycursor.execute(
			"SELECT COUNT(*) FROM userinfofinal WHERE userid = %s",
			(userId,)
		)

		row_count = mycursor.rowcount
		if row_count == 0:
			resp["status"] = "wrong username or password"
		else:
			sql = "INSERT INTO notesinfofinal (userid, note) VALUES (%s, %s)"
			val = (userId, note)
			mycursor.execute(sql, val)
			mydb.commit()
			resp["status"] = "success"

		return resp

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		print ("Error", e)
		print("SERVER ERROR", e)
		return "SERVER ERROR"


if __name__ == "__main__":
	app.run("0.0.0.0", debug = True, port=5001)
