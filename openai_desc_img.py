from openai import OpenAI
from dotenv import load_dotenv
import os

print (os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def check_nsfw(img_url):
    print (img_url)
    response = client.chat.completions.create(
      model="gpt-4-vision-preview",
      messages=[
        {
          "role": "user",
          "content": [
            {"type": "text", "text": "Read the Image provide title and description in JSON format. keys should be 'img_title' and 'img_desc'"},
            {
              "type": "image_url",
              "image_url": {
                "url": img_url,
              },
            },
          ],
        }
      ],
      max_tokens=300,
    )

    print(response.choices[0].message.content)
    return (response.choices[0].message.content)

if __name__ == '__main__':
    print (check_nsfw("https://pbs.twimg.com/media/GBEWg-IaMAAcVDP?format=jpg&name=large"))