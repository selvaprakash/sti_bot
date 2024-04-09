
#importing keys
import tweepy as twitter
import keys
import time, datetime
from pytz import timezone
from datetime import date
import os
import requests
import shutil
import googlesearch
import csv
import dbops
from requests_oauthlib import OAuth1Session
import openai_nsfw_check

user_limit = 3
ref_tweet_limit = 3


#TWITTER AUTHORIZATION AND TOKENS
auth = twitter.OAuthHandler(keys.API_KEY, keys.API_SECRET_KEY)
auth.set_access_token(keys.ACCESS_TOKEN, keys.SECRET_ACCESS_TOKEN)
api = twitter.API(auth)
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = '/home/selvaprakash/searchthisimg/google.json'
oauth = OAuth1Session(keys.API_KEY, client_secret=keys.API_SECRET_KEY,resource_owner_key=keys.ACCESS_TOKEN, resource_owner_secret=keys.SECRET_ACCESS_TOKEN,)

#CREATING FOLDER IN MACHINE
# HOME_FOLDER = os.getcwd()
# print('HOME_FOLDER',HOME_FOLDER)
HOME_FOLDER = '/home/selvaprakash/searchthisimg'
TWEETS_UPLOADED_FOLDER = HOME_FOLDER + '/infiles/'
BEARER_TOKEN = keys.BEARER_TOKEN
print(TWEETS_UPLOADED_FOLDER)

# GET /2/users/by/username/:username
headers = {"Authorization": "Bearer {}".format(BEARER_TOKEN)}

def search_file(filename):
    for dirpath, dirnames, files in os.walk('/home/selvaprakash/searchresults/results_html'):
        if filename in files:
            return 'existing'

def retrieve_last_mentioned_tweet_id():
	os.chdir(TWEETS_UPLOADED_FOLDER)
	f_read = open('last_mentioned_tweet_id.py', 'r')
	last_mentioned_tweet_id = int(f_read.read().strip())
	f_read.close()
	print(last_mentioned_tweet_id)
	return last_mentioned_tweet_id


def save_last_mention_tweet_id(id):
	os.chdir(HOME_FOLDER + '/infiles/')
	with open('last_mentioned_tweet_id.py', 'w') as file:
		file.write(str(id))
		print('file written')

	#REQUESTS

def save_conv_id(id):
	os.chdir(HOME_FOLDER + '/infiles/')
	with open('conv_id.py', 'a') as file:
		file.write(str(id))
		print('file written')

	#REQUESTS

def check_existing_conv(conv_id):
    os.chdir(HOME_FOLDER + '/infiles/')
    with open('conv_id.py') as conv_file:
        if 'conv_id' in conv_file.read():
            return 'exists'

def get_id(last_mentioned_tweet_id):
	r = requests.request("GET",
						 'https://api.twitter.com/2/users/by/username/TWITTER',
						 headers=headers)
	myid = r.json()['data']['id']
	print(myid)
	r_text = r.json()['data']
	print(r_text)
	# porn_ids = ["@Reahub1_1"]
	# r_text = r.json()['data']['text']
	# if any([x in r_text for x in porn_ids]):
	#   print ('Got Porn ID')
	#   return (None,username, new_id)

	params = {
		'expansions': 'referenced_tweets.id,author_id',
		'since_id': last_mentioned_tweet_id,
		'user.fields': 'username',
		'tweet.fields':'conversation_id'
	}

	# REQUESTSTO GET NEW_ID

	r_men = requests.request(
		"GET",
		'https://api.twitter.com/2/users/4449919873/mentions',
		headers=headers,
		params=params)
	print('r_men', r_men.json())
	new_id = (r_men.json()['meta']['newest_id'])
	print('newest_id=', new_id)
	#new_id='1654219117828931584'


	# def use_name(username):

	username = (r_men.json()['includes']['users'][0]['username'])

	print('USERNAME=', username)

	#GET THE PREVIOUS TWEET

	prev_tweet = (r_men.json()['data'][0]['referenced_tweets'][0]['id'])
	print('replied to=', prev_tweet)
	tweet_text = r_men.json()['data'][0]['text']
	no_of_mentions = tweet_text.count('@')
	if no_of_mentions > 4:
		print ('Too many mentions in one tweet')
		return (None, username, new_id)
	# print('r_men text',r_men.json()['data']['text'])

	# REQUEST TO GET THE ORIGINAL TWEET
	if dbops.check_user_usage(username) >=user_limit:
	    return (None,username,new_id)
	if dbops.check_ref_tweet(prev_tweet) >=ref_tweet_limit:
	    print ('Replied Multiple Times to same ref tweet')
	    return (None,username,new_id)

	orig_tweet_url = "https://api.twitter.com/2/tweets/{}?expansions=attachments.media_keys&media.fields=url".format(
		prev_tweet)
	r_tweet = requests.request("GET", orig_tweet_url, headers=headers)
	# tweet=requests.get(orig_tweet_url)
	print('r_tweet=', r_tweet.json())

	# def image(image_url,username) :
	#  TO GET THE IMG_URL
	words_to_watch = ["Gama", "is the video you’re searching:", "Video You are Looking","@Reahub1_1"]
	users_to_watch = ["GoldyC83","LmaoGPT"]
	r_tweet_text = r_tweet.json()['data']['text']
	if any([x in (r_tweet_text) for x in words_to_watch]):
		print('Got Watched Words')
		return (None, username, new_id)
	elif any  ([x in username for x in users_to_watch]):
		print ('watched user')
		return (None, username, new_id)
	img_url = (r_tweet.json()['includes']['media'][0]['url'])
	print('IMAGE', img_url, username, new_id)
	dbops.insert_twit_search(username,new_id,prev_tweet,img_url)
	return img_url, username, new_id

	#ANNOTATIONS BY GOOGLE


def googleurl(img_url):

	nsfw = googlesearch.detect_safe_search_uri(img_url)

	if nsfw == 'VERY_LIKELY' or nsfw == 'LIKELY' or nsfw == 'POSSIBLE':
		return 'NSFW_Skip'
	openai_nsfw = openai_nsfw_check.check_nsfw(img_url)
	if openai_nsfw != 'N':
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

	else:
		google_url = ""  #annotations.pages_with_matching_images[0].url
		for i in range(0, result_len):
			try:
				print(
					'print img url', annotations.pages_with_matching_images[i].
					full_matching_images[0].url)
			except:
				pass
			if len(annotations.pages_with_matching_images[i].
					 full_matching_images) == 0 and len(
						 annotations.pages_with_matching_images[i].
						 partial_matching_images) == 0  :
				print("No Matching Images")
				continue
			elif annotations.pages_with_matching_images[i].full_matching_images == img_url:
				continue

			# elif img_url == annotations.pages_with_matching_images[i].full_matching_images[0]:
			#   continue

			else:
				print('google_search_img_url  : {}',
					  annotations.pages_with_matching_images[i].url)
				google_url = annotations.pages_with_matching_images[i].url
				print(google_url)
				break

		return google_url


def save_google_url(img_url, last_mentioned_tweet_id):
	os.chdir(HOME_FOLDER + '/save url/')
	with open('google_url', 'a') as file:
		now = datetime.datetime.now()

		# current_time = now.strftime("%H:%M:%S")
		print("now =", now)

		#dt_string = now.strftime("%d-/%m-/%Y %H:%M:%S %Z%z")
		now_asia = now.astimezone(timezone('Asia/Kolkata'))
		new_asia = now_asia.strftime("%Y-%m-%d %H:%M:%S")
		print(new_asia)

		file.write((new_asia) + ' - ' + str(last_mentioned_tweet_id) + ' - ' +
				   (img_url) + '\n')

		file.close()

		print('written url and id')


def save_google_url_all(img_url, all_matching_urls):
	os.chdir(HOME_FOLDER + '/save url/')
	with open('all_urls.txt', 'a') as file:
		now = datetime.datetime.now()

		# current_time = now.strftime("%H:%M:%S")
		print("now =", now)

		#dt_string = now.strftime("%d-/%m-/%Y %H:%M:%S %Z%z")
		now_asia = now.astimezone(timezone('Asia/Kolkata'))
		new_asia = now_asia.strftime("%Y-%m-%d %H:%M:%S")
		print(new_asia)

		file.write((new_asia) + ' - ' + str(img_url) + '\n')
		file.write('\n' + str(all_matching_urls) + '\n')
		file.write('----------------------\n\n')
		file.close()

	media_pos = img_url.index('media/')
	jpg_pos = img_url.rfind('.')

	print(img_url.rfind('.jpg'))
	links_filename = img_url[media_pos + 6:jpg_pos]
	print('links_filename', links_filename)
	with open(links_filename + '.csv', 'w') as file1:
		file1.write(str(all_matching_urls))
		print('created new file')
		file1.close()

	print('written url and id')


def save_images(img_url):
	os.chdir(HOME_FOLDER + '/tweet_images/')
	res = requests.get(img_url, stream=True)

	media_pos = img_url.index('media/')
	jpg_pos = img_url.rfind('.')

	print(img_url.rfind('.jpg'))
	img_filename = img_url[media_pos + 6:jpg_pos]
	print('img_filename', img_filename)

	if res.status_code == 200:
		with open(img_filename + '.jpg', 'wb') as f:
			shutil.copyfileobj(res.raw, f)
		print('Image sucessfully Downloaded: ', img_filename + '.jpg')
	else:
		print('Image Couldn\'t be retrieved')

	print('Saved image')
	return img_filename


def reply2tweet(img_url, searched_url, men_tweet_id, men_userid):

	media_pos = img_url.index('media/')
	jpg_pos = img_url.rfind('.')

	print(img_url.rfind('.jpg'))
	links_filename = img_url[media_pos + 6:jpg_pos]
	reply_msg = searched_url
	reply_payload = {"text": reply_msg, "reply": {"in_reply_to_tweet_id": men_tweet_id}}

 # reply_msg = '@' + men_userid + ' ' + searched_url + ' \n'

	if searched_url or searched_url != 'No Result Found':
		try:

			response = oauth.post("https://api.twitter.com/2/tweets", json=reply_payload)
		except Exception as e:
			print(e)
			pass


# api.update_status(

#		'@' + men_userid + ' ' +
#		' \n\nClick the link for more results \n   https://lens.google.com/uploadbyurl?url='
#		+ img_url, (men_tweet_id)) # changed from https://www.google.com/searchbyimage?image_url= to https://lens.google.com/uploadbyurl?url= on 11-11-2022
	print('Replied')


def upload_search(imgfile):
	os.chdir(HOME_FOLDER + '/tweet_images/')
	searchUrl = 'http://www.google.com/searchbyimage/upload'
	multipart = {
		'encoded_image':
		(HOME_FOLDER + '/tweet_images/', open(imgfile + '.jpg', 'rb')),
		'image_content':
		''
	}
	response = requests.post(searchUrl, files=multipart, allow_redirects=False)
	fetchUrl = response.headers['Location']
	return (fetchUrl)


if __name__ == '__main__':

	while (True):
		now = datetime.datetime.now()
		print (now)
		last_mentioned_tweet_id = retrieve_last_mentioned_tweet_id()
		# last_mentioned_id = last_mentioned_tweet_id
		print('in main', last_mentioned_tweet_id)

		params = {
		'expansions': 'referenced_tweets.id,author_id',
		'since_id': last_mentioned_tweet_id,
		'user.fields': 'username',
		'tweet.fields': 'conversation_id'
	}

	# REQUESTSTO GET NEW_ID
		try:
			r_men = requests.request(
				"GET",
				'https://api.twitter.com/2/users/4449919873/mentions',
				headers=headers,
				params=params)
			print('r_men', r_men.json())

			mention_count =  (r_men.json()['meta']['result_count'])
			print ('mention_count',mention_count)
			if mention_count <1 :
				time.sleep(90)
				continue

			for i in range(mention_count):
				try:
					men_tweet_id = (r_men.json()['data'][i]['id'])
					conv_id = (r_men.json()['data'][i]['conversation_id'])
					if check_existing_conv(conv_id) =='exists':
					    continue
					save_last_mention_tweet_id(men_tweet_id)
					save_conv_id(conv_id)
					men_tweet_text = (r_men.json()['data'][i]['text'])
					men_tweet_author_id = (r_men.json()['data'][i]['author_id'])
					# r_user = requests.request("GET",
					# 			'https://api.twitter.com/2/users/'+men_tweet_author_id,
					# 			headers=headers)
					print ('Processing tweet id',men_tweet_id)
					print ('Processing tweet text',men_tweet_text)
					# print (r_user.json())
					# men_user = r_user.json()['data']['username']
					men_user = men_tweet_author_id
					replied_to_tweet_id =(r_men.json()['data'][i]['referenced_tweets'][0]['id'])
					print(men_user)
					if dbops.check_user_usage(men_user) >=user_limit:
						print ('user limit exceeded')
						save_last_mention_tweet_id(men_tweet_id)
						continue

					if dbops.check_ref_tweet(replied_to_tweet_id) >=ref_tweet_limit:
						print ('Replied Multiple Times to same ref tweet')
						save_last_mention_tweet_id(men_tweet_id)
						continue
					no_of_mentions = men_tweet_text.count('@')
					if no_of_mentions > 4:
						print ('Too many Mentions - spam')
						save_last_mention_tweet_id(men_tweet_id)
						continue


				# prev_tweet = (r_men.json()['data'][0]['referenced_tweets'][0]['id'])
					orig_tweet_url = "https://api.twitter.com/2/tweets/{}?expansions=attachments.media_keys&media.fields=url".format(replied_to_tweet_id)

					r_tweet = requests.request("GET", orig_tweet_url, headers=headers)
					print (r_tweet)
					img_url = (r_tweet.json()['includes']['media'][0]['url'])
					dbops.insert_twit_search(men_user,men_tweet_id,replied_to_tweet_id,img_url)
					print ('Processing',men_tweet_id,men_tweet_text,men_user)

			# # SAVE THE LAST MENTION TWEET ID
			# save_last_mention_tweet_id (last_mentioned_tweet_id)
			#try:
					# img_url, men_userid, new_id = get_id(last_mentioned_tweet_id)


					save_last_mention_tweet_id(men_tweet_id)
					img_filename = save_images(img_url)

					# save_last_mention_tweet_id (new_id)
					if img_url:
						search_url = 'https://results.searchthisimage.com/tweetnew?img=' + img_filename
						if search_file (img_filename) == 'existing':
							replied = reply2tweet( img_url,	'Click the link for results \n' + search_url,men_tweet_id, men_user)
							continue

						google_url = googleurl(img_url)




					# 	upload_search_url = upload_search(img_filename)




						search_url = 'https://results.searchthisimage.com/tweetnew?img=' + img_filename
						now = datetime.datetime.now()
						now_asia = now.astimezone(timezone('Asia/Kolkata'))
						new_asia = now_asia.strftime("%Y-%m-%d %H:%M:%S")
						# google_url = googleurl(img_url)
						#	now = datetime.datetime.now()
						#	now_asia = now.astimezone(timezone('Asia/Kolkata'))
						#  new_asia = now_asia.strftime("%Y-%m-%d %H:%M:%S")

						save_google_url(google_url, last_mentioned_tweet_id)
						print(search_url)

						if google_url == 'NSFW_Skip':
							print('Skip')
							with open('NSFW.txt', 'a') as file1:
								file1.write('\n' + str(men_user + '|' + img_url + '|' +
													new_asia))
							pass
						else:
							try:
								if google_url =='No Result Found' or  google_url=="":
									replied = reply2tweet(img_url, 'No Results Found.', men_tweet_id, men_user)


								else:
									replied = reply2tweet( img_url,	'Click the link for results \n' + search_url,men_tweet_id, men_user)


					# with open('img_urls.csv', 'a') as file1:
					# 	file1.write()
							except Exception as e:
								print(e)
								continue
					else:
						save_last_mention_tweet_id(men_tweet_id)
				except Exception as e:
					print(e)
					# time.sleep(15)
					continue
		except Exception as e:
			print(e)
			time.sleep(90)
			continue
		time.sleep(90)
