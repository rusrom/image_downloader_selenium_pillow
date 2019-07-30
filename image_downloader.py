import os.path
import argparse
import sys
import re

from selenium import webdriver
from lxml import html
from urllib.request import urlopen
from PIL import Image


SCRIPT_ROOT = os.path.dirname(os.path.abspath(__file__))


# Arguments from terminal
parser = argparse.ArgumentParser()
parser.add_argument('-url', help='URL for parsing images')
args = parser.parse_args()
url = args.url

# Check URL
if url is None or not url.startswith('http'):
    sys.exit('Must be a valid URL!')

# Create or check auction folder
auction_id = re.search(r'listingid=(\d+)&', url).group(1)
auction_folder = os.path.join(SCRIPT_ROOT, 'downloaded_images', auction_id)
if not os.path.isdir(auction_folder):
    os.makedirs(auction_folder)


# Download all photos
def download_photos(srcs):
    for src in srcs:
        pic_auction_id, pic_num = re.search(r'lid=(\d+).*in=(\d+)', src).groups()
        target_img_url = 'https://www.auctionzip.com/Full-Image/{}/fi{}.cgi'.format(pic_auction_id, pic_num)

        print('Downloading {} ...'.format(target_img_url))
        with urlopen(target_img_url) as auction_image:
            img = Image.open(auction_image)
            img_ext = img.format.lower()
            image_name = '{auction_id}_{pic_num}.{extension}'.format(
                auction_id=pic_auction_id,
                pic_num=pic_num,
                extension=img_ext
            )
            img_path = os.path.join(auction_folder, image_name)
            img.save(img_path)


# WebDriver config
CHROME_DRIVER_PATH = 'D:\\WebDrivers\\chromedriver.exe'
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')

# Render the page
browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, chrome_options=options)
print('Rendering page! Executing JavaScript...')
browser.get(url)
browser.save_screenshot(os.path.join(SCRIPT_ROOT, 'headless_chrome_test.png'))
page_html = browser.page_source
browser.close()

tree = html.fromstring(page_html)

if 'feed=129' in url:
    # Get src from page like
    # http://www.auctionzip.com/cgi-bin/photopanel.cgi?listingid=3203771&feed=129&category=0
    srcs = tree.xpath('//td/img/@src')
else:
    # Get src from page like
    # https://www.auctionzip.com/cgi-bin/photopanel.cgi?listingid=3229232&category=0&zip=&kwd=
    srcs = tree.xpath('//li[@onclick]//a/img/@src')

download_photos(srcs)

print('All images was downloaded!')
