import urllib3
from pathlib import Path

IMAGE_URL = 'https://s3.amazonaws.com/peloton-ride-images/e9e4253f78e4877d267b8dbacc47e3da620e70b2/img_1666115383_13232dbbc48d43739b3a0108e71266e5.jpg'
LOCAL_FILENAME = Path.cwd().joinpath('test_image.jpg')

def download_image(image_url: str, local_filename: str) -> None:
    http = urllib3.PoolManager()

    try:
        response: urllib3.response.BaseHTTPResponse = http.request('GET', image_url)           
    except urllib3.exceptions.LocationValueError as e:
        print(e)
    else:
        if response.status == 200:
            with open(local_filename, 'wb') as file:
                file.write(response.data)
        else:
            print(f"ERROR - HTTP Status Code: {response.status}")


def main():
    download_image(IMAGE_URL, LOCAL_FILENAME)


if __name__ == '__main__':
    main()