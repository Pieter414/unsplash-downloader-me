import requests
import os
import time
import image_downloader
from dotenv import load_dotenv

load_dotenv()
ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")

class UnsplashImageDownloader:
    def __init__(self, query):
        self.querystring = {"query": f"{query}", "per_page": "20"}
        self.headers = {"Authorization": f"Client-ID {ACCESS_KEY}"}
        self.url = "https://api.unsplash.com/search/photos"

        self.query = query

    def get_total_images(self):
        with requests.request("GET", self.url, headers=self.headers, params=self.querystring) as rs:
            # Check if request succeeded
            if rs.status_code != 200:
                raise Exception(f"Request failed: {rs.status_code} - {rs.text}")

            try:
                json_data = rs.json()
            except ValueError:
                raise Exception(f"Response is not valid JSON: {rs.text[:200]}")  # show first 200 chars

        return json_data.get("total", 0)

    def get_links(self, pages_, quality_):
        all_links = []
        for page in range(1, int(pages_) + 1):
            self.querystring["page"] = f"{page}"

            response = requests.request("GET", self.url, headers=self.headers, params=self.querystring)
            response_json = response.json()
            all_data = response_json["results"]

            for data in all_data:
                name = None
                try:
                    name = data["sponsorship"]["tagline"]
                except:
                    pass
                if not name:
                    try:
                        name = data['alt_description']
                    except:
                        pass
                if not name:
                    name = data['description']
                try:
                    image_urls = data["urls"]
                    required_link = image_urls[quality_]
                    print("name     : ", name)
                    print(f"url : {required_link}\n")
                    all_links.append(required_link)
                except:
                    pass

        return all_links


if __name__ == '__main__':
    folder = "unsplash"
    if not os.path.exists(folder):
        os.mkdir(folder)

    search = input("What you want to search for ?")

    unsplash = UnsplashImageDownloader(search)

    total_image = unsplash.get_total_images()
    print("\ntotal images available : ", total_image)

    if total_image == 0:
        print("sorry, no image available for this search")
        exit()

    number_of_images = int(input("enter number of images you want to download : "))

    if number_of_images == 0 or number_of_images > total_image:
        print("not a valid number")
        exit()

    pages = float(number_of_images / 20)
    if pages != int(pages):
        pages = int(pages) + 1

    print("\nAvailable image quality.\nraw\nfull\nregular\nsmall\nthumb\nsmall_s3\n")

    quality = input("enter the quality  : ")
    image_links = unsplash.get_links(pages, quality)

    start = time.time()
    print("download started....\n")
    image_downloader.folder = folder
    image_downloader.download(image_links)

    print("\ndownloading finished.")
    print("time took ", time.time() - start)
