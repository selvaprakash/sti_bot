import mysql.connector
from datetime import datetime
import csv


def check_user_usage (twit_user):
    with open('/home/selvaprakash/searchthisimg/infiles/subscribers.csv','r') as csvfile:
        subs_list = csv.reader(csvfile)
        for row in subs_list:
            print (row[0])
            if row[0]==twit_user:
                print ('subscriber')
                return 0
        # print (subs_list)

    mydb = mysql.connector.connect(
    host="selvaprakash.mysql.pythonanywhere-services.com",
    user="selvaprakash",
    password="pythonmysql1",
    database="selvaprakash$STI",
    port ="3306"
    )
    mycursor = mydb.cursor()
    # user="'TheCryptoDog'"
    twit_user = "'"+twit_user+"'"
    user_search_count = 0
    mycursor.execute("SELECT COUNT(*) FROM twit_search WHERE twit_user= {} and tweet_time > now() - INTERVAL 1 DAY".format(twit_user) )
    records = mycursor.fetchall()
    for record in records:
        user_search_count =  record[0]

    print ('Search Count for User',twit_user,user_search_count)
    return user_search_count


def check_ref_tweet (ref_tweet_id ):
    mydb = mysql.connector.connect(
    host="selvaprakash.mysql.pythonanywhere-services.com",
    user="selvaprakash",
    password="pythonmysql1",
    database="selvaprakash$STI",
    port ="3306"
    )
    mycursor = mydb.cursor()
    # user="'TheCryptoDog'"
    ref_tweet_count = 0
    mycursor.execute("SELECT COUNT(*) FROM twit_search WHERE ref_tweet_id = {}".format(ref_tweet_id) )
    records = mycursor.fetchall()
    for record in records:
        ref_tweet_count =  record[0]

    print ('Search Count for Referred Tweet',ref_tweet_id,ref_tweet_count)
    return ref_tweet_count


def insert_twit_search(twit_user,tweet_id,ref_tweet_id,img_url):
    mydb = mysql.connector.connect(
      host="selvaprakash.mysql.pythonanywhere-services.com",
      user="selvaprakash",
      password="pythonmysql1",
    database="selvaprakash$STI"
    )
    mycursor = mydb.cursor()
    # user="'TheCryptoDog'"
    media_pos = img_url.index('media/')
    jpg_pos = img_url.rfind('.')

    img_filename = img_url[media_pos + 6:jpg_pos]
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ins_query = ("INSERT INTO twit_search (twit_user,tweet_id,ref_tweet_id,tweet_time,img_url,img_name) VALUES (%s,%s, %s, %s, %s,%s)")
    mycursor.execute(ins_query, (twit_user,tweet_id,ref_tweet_id,now,img_url,img_filename,))
    print ('inserted twit_search')

    mydb.commit()
    mydb.close()

def insert_google_search(img_url,img_name,google_results):
    mycursor = mydb.cursor()

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ins_query = ("INSERT INTO search_results (img_url,img_name,search_time,google_results) VALUES (%s,%s, %s, %s)")
    mycursor.execute(ins_query, ('dummy_img_url','img_name',now,'json','img_name','search_results_json'))

    mydb.commit()
    mydb.close()


def check_usage ():
    with open('infiles/subscribers.csv','r') as file:
        subs_list = file.read()
        print (subs_list)
    mycursor = mydb.cursor()
    mycursor.execute("SELECT DATE_FORMAT(tweet_time,'%Y-%m-%d') tweet_date,COUNT(*) FROM twit_search WHERE tweet_time > now() - INTERVAL 32 DAY GROUP BY 1 DESC")
    records = mycursor.fetchall()
    for record in records:
        print (record)
    print (records)
    return records



if __name__=='__main__':
    check_user_usage('123456')