import requests
import re


def upload_image(jellyfin_client, image_id):
    link = jellyfin_client.jellyfin.artwork(image_id, "Primary", 1024)
    r = requests.get(link)
    files = {"file": ("image.jpg", r.content)}
    post = requests.post("https://bashupload.com/", files=files)

    regex = r"https(.*)"
    result = re.search(regex, post.text)
    return result.group(0)
