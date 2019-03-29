"""
Generates a post from the most liked comment
of the most recent post on a instagram account and posts it.

IDEAS:
    Choose a random font for each post
    Choose a random background/text color
"""
from datetime import datetime
from pytz import timezone
from textwrap import wrap
from time import sleep
from os import environ
from InstagramAPI import InstagramAPI
from PIL import Image, ImageDraw, ImageFont


def main():
    USERNAME = environ['INSTAGRAM_USERNAME']
    PASSWORD = environ['INSTAGRAM_PASSWORD']
    API = InstagramAPI(USERNAME, PASSWORD)
    API.login()

    last_posted_day = None
    tz = timezone('EST')
    while True:
        t = datetime.now()
        # Post every day at 10am
        if t.day != last_posted_day:
            try:
                text, username = most_liked_comment(API, most_recent_post_id(API))
                img = comment_to_image(text)
                API.uploadPhoto(img, caption=f'Submitted by @{username}')

                last_posted_day = t.day
                sleep(20*60*60) # 20 hours
            except:
                pass

        sleep(2*60) # 2 Minutes


def most_recent_post_id(api):
    """Return id of most recent post. Return None on failure"""
    if not api.getSelfUserFeed():
        return None

    json = api.LastJson
    if len(json['items']) == 0:
        return None

    return json['items'][0]['id']


def most_liked_comment(api, media_id):
    """Return (text, username) of most recent post.
       Return None on failure"""
    if not api.getMediaComments(media_id):
        return None
    comments = api.LastJson['comments']

    if len(comments) == 0:
        return None

    # Sort by likes
    comments.sort(key=lambda c: c['comment_like_count'])
    return comments[0]['text'], comments[0]['user']['username']


def comment_to_image(comment_text):
    """Return path to square image containing the text.
       Return None on failure."""
    IMAGE_DIMENSIONS = (1080, 1080)
    COLOR = (255, 255, 255) # White
    IMAGE_PATH = 'newest_comment_image.jpg'
    TEXT_COLOR = (0, 0, 0, 0) # Black

    img = Image.new('RGB', IMAGE_DIMENSIONS, COLOR)
    d = ImageDraw.Draw(img)
    fnt = ImageFont.truetype(
            './fonts/dejavu_dejavu-sans/DejaVuSans.ttf',
            100, encoding='unic')


    wrapped = wrap(comment_text, width=15)
    pad = 10
    current_h = (IMAGE_DIMENSIONS[1] - (sum([fnt.getsize(w)[1] for w in wrapped]) + pad*(len(wrapped)-1)))/2 # TODO: Refactor
    for line in wrapped:
        w, h = d.textsize(line, font=fnt)
        d.text(((IMAGE_DIMENSIONS[0]-w)/2, current_h), line,
                font=fnt, fill=TEXT_COLOR)

        current_h += h + pad


    img.save(IMAGE_PATH, "JPEG", quality=80)

    return IMAGE_PATH


if __name__ == '__main__':
    main()
