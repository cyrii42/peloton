import urllib3
import io
from pathlib import Path
from PIL import Image

def download_image(image_url: str) -> io.BytesIO | None:
    http = urllib3.PoolManager()
    try:
        response = http.request('GET', image_url)           
    except urllib3.exceptions.LocationValueError as e:
        print(e)
    else:
        if response.status == 200:
            return io.BytesIO(response.data)
        else:
            print(f"ERROR - HTTP Status Code: {response.status}")
            return None


def save_image(image_data: io.BytesIO, image_filename: str, local_dir: Path) -> None: 
    local_filename = local_dir.joinpath(image_filename)
    image = Image.open(image_data)
    image.save(local_filename)


def create_thumbnail(image_data: io.BytesIO, image_filename: str, local_dir: Path):
    local_filename = local_dir.joinpath(image_filename)
    thumb_filename = local_filename.with_stem(f"{local_filename.stem}_thumb")
    
    image = Image.open(image_data)
    image.thumbnail(size=(250, 250))
    image.save(thumb_filename)



def main():
    ...

if __name__ == '__main__':
    main()