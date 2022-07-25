from getpass import getpass
from mysql.connector import connect, Error
import os


if (os.environ.get("DB_TYPE") == None):
	from dotenv import load_dotenv
	load_dotenv(os.getcwd()+str("/.env"))

#sample_dict={"Manga's URL": 'https://m.manganelo.com/manga-bc115996', "Manga's Genre": "Comedy - Shounen - Slice of life", "Manga's Name": 'liudgfhlaiugbvkj', 'SA_Rating': 8.3456, "Manga's Summary": 'testing sample to test sorting in json!'}



def view_db():
	try:
	    with connect(
	        host=os.environ.get("DB_HOST"),
	        user=os.environ.get("DB_USER"),
	        password=os.environ.get("DB_PASS"),
	        database=os.environ.get("DB_NAME"),
	    ) as connection:
	        print(connection)
	        query="SELECT * FROM manga_list"
	        with connection.cursor() as cursor:
	        	cursor.execute(query)
	        	result = cursor.fetchall()
	        	for row in result:
	        		print(row)
	except Error as e:
	    print(e)


def clear_db():
	try:
	    with connect(
	        host=os.environ.get("DB_HOST"),
	        user=os.environ.get("DB_USER"),
	        password=os.environ.get("DB_PASS"),
	        database=os.environ.get("DB_NAME"),
	    ) as connection:
	        print(connection)
	        query="TRUNCATE TABLE manga_list"
	        with connection.cursor() as cursor:
	        	cursor.execute(query)
	except Error as e:
	    print(e)		

def update_db(manga,sa_rating):
	try:
	    with connect(
	        host=os.environ.get("DB_HOST"),
	        user=os.environ.get("DB_USER"),
	        password=os.environ.get("DB_PASS"),
	        database=os.environ.get("DB_NAME"),
	    ) as connection:
	        print(connection)
	        query="UPDATE manga_list SET SA_RATING='{rating}' where MANGA_NAME='{name}' ".format(rating=sa_rating,name=manga)
	        print("SQL Query: "+ query)
	        with connection.cursor() as cursor:
	        	cursor.execute(query)
	        	connection.commit()
	except Error as e:
	    print(e)

def alter_db():
	try:
	    with connect(
	        host=os.environ.get("DB_HOST"),
	        user=os.environ.get("DB_USER"),
	        password=os.environ.get("DB_PASS"),
	        database=os.environ.get("DB_NAME"),
	    ) as connection:
	        print(connection)
	        query="ALTER TABLE manga_list DROP PRIMARY KEY,ADD PRIMARY KEY(Manga_Name(500)) "
	        with connection.cursor() as cursor:
	        	cursor.execute(query)
	except Error as e:
	    print(e)	


def save_db(data_dict):
	data_dict["Manga's Genre"]=data_dict["Manga's Genre"].split(' - ')
	genre_list=data_dict["Manga's Genre"]
	manga=data_dict["Manga's Name"]
	sa_rating=data_dict["SA_Rating"]

	for i in range(len(genre_list)):
		genre=genre_list[i]
		genre = genre.replace('\t', '') 
		genre = genre.replace('\n', '')
		genre = genre.replace(' ', '')
		
		genre = genre.lower()
		genre=genre.capitalize()	
		
		genre = genre.replace('Sliceoflife', 'Slice_Of_Life') 
		genre = genre.replace('Shounenai', 'Shounen_Ai') 
		genre = genre.replace('Shoujoai', 'Shoujo_Ai') 
		genre = genre.replace('Scifi', 'Sci_Fi') 
		genre = genre.replace('Schoollife', 'School_Life') 
		genre = genre.replace('Oneshot', 'One_Shot') 
		genre = genre.replace('Martialarts', 'Martial_Arts') 
		genre = genre.replace('Genderbender', 'Gender_Bender') 
		genre_list[i]=genre
		
	final_dict={}
	final_dict.update({"Manga_Link":data_dict["Manga's URL"]})
	final_dict.update({"SA_Rating":sa_rating})
	final_dict.update({"Manga_Name":manga})
	final_dict.update({"Manga_Summary":data_dict["Manga's Summary"]})

	for genre in genre_list:
		final_dict.update({genre:1})		
		
	cols = ','.join([f'`{k}`' for k in final_dict.keys()])
	vals = ','.join(['%s'] * len(final_dict))
	query = f'INSERT INTO manga_list ({cols}) VALUES ({vals})'
	print("\n\n")
	print("SQL query: "+query)
	print("\n\n")

	try:
	    with connect(
	        host=os.environ.get("DB_HOST"),
	        user=os.environ.get("DB_USER"),
	        password=os.environ.get("DB_PASS"),
	        database=os.environ.get("DB_NAME"),
	    ) as connection:
	        print(connection)
	        check_element="SELECT SA_RATING FROM manga_list WHERE Manga_Name='{name}'".format(name=manga) 
	        with connection.cursor() as cursor:
	        	cursor.execute(check_element)
	        	msg=cursor.fetchone()
	        	if not msg:
	        		cursor.execute(query,tuple(final_dict.values()))
	        		connection.commit()
	        	else:
	        		update_db(manga,sa_rating)
	except Error as e:
	    print(e)

