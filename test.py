import tweepy as twitter
import keys
import time, datetime
from pytz import timezone
from datetime import date
import os
import requests
import shutil
import googlesearch

#TWITTER AUTHORIZATION AND TOKENS
auth = twitter.OAuthHandler(keys.API_KEY, keys.API_SECRET_KEY)
auth.set_access_token(keys.ACCESS_TOKEN, keys.SECRET_ACCESS_TOKEN)
api = twitter.API(auth)
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = 'google.json'

#CREATING FOLDER IN MACHINE
HOME_FOLDER = os.getcwd()
print(HOME_FOLDER)
# HOME_FOLDER = '/home/SelvaPrakash/searchthisimage'
TWEETS_UPLOADED_FOLDER = HOME_FOLDER + '/infiles/'
GDOC_BEARER_TOKEN = keys.GDOC_BEARER_TOKEN
BEARER_TOKEN = keys.BEARER_TOKEN
print(TWEETS_UPLOADED_FOLDER)

# GET /2/users/by/username/:username
headers = {"Authorization": "Bearer {}".format(BEARER_TOKEN)}


def retrieve_last_mentioned_tweet_id():
	os.chdir(TWEETS_UPLOADED_FOLDER)
	f_read = open('last_mentioned_tweet_id.py', 'r')
	last_mentioned_tweet_id = int(f_read.read().strip())
	f_read.close()
	print(last_mentioned_tweet_id)
	return last_mentioned_tweet_id

def process(last_mentioned_tweet_id):
    params = {
	    'expansions': 'referenced_tweets.id,author_id',
	    'since_id': last_mentioned_tweet_id,
	    'user.fields': 'username'
	}

	# REQUESTSTO GET NEW_ID

    r_men = requests.request(
	    "GET",
	    'https://api.twitter.com/2/users/4449919873/mentions',
	    headers=headers,
	    params=params)
    print('r_men', r_men.json())

    mention_count =  (r_men.json()['meta']['result_count'])
    if mention_count <1 :
        return 0
	
    for i in range(0,mention_count):
        try:
            men_tweet_id = (r_men.json()['data'][i]['id'])
            men_tweet_text = (r_men.json()['data'][i]['text'])
            men_user =  (r_men.json()['includes']['users'][0]['username'])

            replied_to_tweet_id =(r_men.json()['data'][i]['referenced_tweets'][0]['id'])
            # prev_tweet = (r_men.json()['data'][0]['referenced_tweets'][0]['id'])
            orig_tweet_url = "https://api.twitter.com/2/tweets/{}?expansions=attachments.media_keys&media.fields=url".format(replied_to_tweet_id)
                                
            r_tweet = requests.request("GET", orig_tweet_url, headers=headers)
            # tweet=requests.get(orig_tweet_url)
            
            img_url = (r_tweet.json()['includes']['media'][0]['url'])
            print('Mentioned Tweet Details', men_tweet_id,men_user,men_tweet_text,orig_tweet_url,img_url)
            media_pos = img_url.index('media/')
            jpg_pos = img_url.rfind('.')
	    
            print(img_url.rfind('.jpg'))
            img_filename = img_url[media_pos + 6:jpg_pos]
            if img_url:
               result  = googleurl(img_url)
        except Exception as e:
            print ('Not Mentioned')
            # save_last_mention_tweet_id(men_tweet_id)
            return 0


def googleurl(img_url):

	nsfw = googlesearch.detect_safe_search_uri(img_url)
	if nsfw == 'VERY_LIKELY' or nsfw == 'LIKELY' or nsfw == 'POSSIBLE':
		return 'NSFW_Skip'

	annotations = (googlesearch.annotate(img_url))

	print((annotations.pages_with_matching_images))
	#save_google_url_all(img_url, annotations.pages_with_matching_images)
	# for page in annotations.pages_with_matching_images:

	#  print(' Searched Url   : {}'.format(page.url))

	result_len = len((annotations.pages_with_matching_images))
	print('result_len', result_len)
	if result_len == 0:
		print('No Result Found')
		return "No Result Found"
	
	elif len(annotations.pages_with_matching_images[i].
			         full_matching_images) == 0 and len(
			             annotations.pages_with_matching_images[i].
			             partial_matching_images) == 0:
				print("No Matching Images")
				

	else:
				print('google_search_img_url  : {}',
				      annotations.pages_with_matching_images[i].url)
				google_url = annotations.pages_with_matching_images[i].url
				print(google_url)
				
	return google_url
	
	
def reply2tweet(img_url, searched_url, men_tweet_id, men_userid):

	media_pos = img_url.index('media/')
	jpg_pos = img_url.rfind('.')

	print(img_url.rfind('.jpg'))
	links_filename = img_url[media_pos + 6:jpg_pos]

	if searched_url or searched_url != 'No Result Found':
		try:
			api.update_status('@' + men_userid + ' ' + searched_url + ' \n',
			                  (men_tweet_id))
		except Exception as e:
			print(e)
			pass

if __name__ == '__main__':

	while (True):

		last_mentioned_tweet_id = retrieve_last_mentioned_tweet_id()

		try:
			process(last_mentioned_tweet_id)
		except Exception as e:
			print(e)
			time.sleep(15)
			continue
	# while (True):

	# 	last_mentioned_tweet_id = retrieve_last_mentioned_tweet_id()
	# 	# last_mentioned_id = last_mentioned_tweet_id
	# 	print('in main', last_mentioned_tweet_id)
    #     try:
    #         img_url, men_userid, new_id = get_id(last_mentioned_tweet_id)
    #     except Exception as e:
    #         print(e)
    #         time.sleep(15)
    #         continue