import mysql.connector

mydb = mysql.connector.connect(
    host="selvaprakash.mysql.pythonanywhere-services.com",
    user="selvaprakash",
    password="pythonmysql1",
    database="selvaprakash$STI",
    port ="3306"
    )
mycursor = mydb.cursor()

mycursor.execute("SELECT twit_user,COUNT(*) FROM twit_search WHERE tweet_time > now() - INTERVAL 1 DAY group by 1" )
records = mycursor.fetchall()
print (records)
for record in records:
    user_search_count =  record[0]