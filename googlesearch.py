import argparse
import io
import os
from google.cloud import vision
#oschdir

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='/home/selvaprakash/searchthisimg/google.json'

def detect_safe_search_uri(uri):
    """Detects unsafe features in the file located in Google Cloud Storage or
    on the Web."""
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri
    response = client.safe_search_detection(image=image)
    safe = response.safe_search_annotation
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')
    print('Safe search:')
    print('adult: {}'.format(likelihood_name[safe.adult]))
    return likelihood_name[safe.adult]



def annotate(path):
  #Returns web annotations given the path to an image.
    client = vision.ImageAnnotatorClient()
    print('client')

    image = vision.Image()
    image.source.image_uri = path
    print(image.source.image_uri)
    # request = {
    #   image: {
    #     source: {imageUri: path}
    #   }
    # }
    # web_detection  = client.web_detection(request)
    web_detection = client.web_detection(image=image).web_detection
    return web_detection



def report(annotations):
    """Prints detected features in the provided web annotations."""
    if annotations.pages_with_matching_images:
        print('\n{} Pages with matching images retrieved'.format(
            len(annotations.pages_with_matching_images)))

        for page in annotations.pages_with_matching_images:
            print('Url   : {}'.format(page.url))

    if annotations.full_matching_images:
        print('\n{} Full Matches found: '.format(
              len(annotations.full_matching_images)))

        for image in annotations.full_matching_images:
            print('Url  : {}'.format(image.url))

    if annotations.partial_matching_images:
        print('\n{} Partial Matches found: '.format(
              len(annotations.partial_matching_images)))

        for image in annotations.partial_matching_images:
            print('Url  : {}'.format(image.url))

    if annotations.web_entities:
        print('\n{} Web entities found: '.format(
              len(annotations.web_entities)))

        for entity in annotations.web_entities:
            print('Score      : {}'.format(entity.score))
            print('Description: {}'.format(entity.description))


def save_all_url(img_url,last_mentioned_tweet_id):
  os.chdir(HOME_FOLDER+'/save url/')
  with open('all_urls.txt','a') as file:
    now = datetime.datetime.now()

    # current_time = now.strftime("%H:%M:%S")
    print("now =", now)

    #dt_string = now.strftime("%d-/%m-/%Y %H:%M:%S %Z%z")
    now_asia = now.astimezone(timezone('Asia/Kolkata'))
    new_asia=now_asia.strftime("%Y-%m-%d %H:%M:%S")
    print(new_asia)

    file.write((new_asia) + ' - ' +str(last_mentioned_tweet_id) +' - '+   (img_url) + '\n')



if __name__ == '__main__':
    #image_url =
    # parser = argparse.ArgumentParser(
    #     description=__doc__,
    #     formatter_class=argparse.RawDescriptionHelpFormatter)
    # path_help = str('The image to detect, can be web URI, '
    #                 'Google Cloud Storage, or path to local file.')
    # parser.add_argument('image_url', help=path_help)
    # args = parser.parse_args()


    report(annotate('https://pbs.twimg.com/media/FNKZdPTaAAQuai4.jpg'))