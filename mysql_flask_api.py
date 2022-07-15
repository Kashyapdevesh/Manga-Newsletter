from flask import Flask,request,jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import json
import os

if (os.environ.get("DB_TYPE") == None):
	from dotenv import load_dotenv
	load_dotenv(os.getcwd()+str("/.env"))
	
print(os.environ.get("DB_TYPE"))

app = Flask(__name__)

app.config['MYSQL_DB'] = os.environ.get("DB_NAME")
app.config['MYSQL_PASSWORD'] = os.environ.get("DB_PASS")
app.config['MYSQL_USER'] = os.environ.get("DB_USER")
app.config['MYSQL_HOST'] = os.environ.get("DB_HOST")

mysql = MySQL(app)


@app.route('/manga',methods=['GET'])
def getdata():

    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    args = request.args.to_dict()
    cols = '=1 OR '.join([f'`{k}`' for k in args.keys()])
    if cols!='':
    	query=f"SELECT * FROM manga_list WHERE {cols}=1 ORDER BY SA_Rating"
    	query=query.replace("`","")
    else:
    	query="SELECT * FROM manga_list ORDER BY SA_Rating"
    print("\n\n")
    print(query)
    print("\n\n")
    cursor.execute(query)

    data=cursor.fetchall()
    output={}
    count=0
    for row in data:
    	output.update({count:row})
    	count+=1
    json_output=json.dumps(output,indent =4)

    return json_output
    

@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone
    
if __name__ == '__main__':
    app.run(port=5000,debug=True)

