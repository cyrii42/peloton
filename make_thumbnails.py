from PIL import Image
# from pathlib import Path
# from io import BytesIO

from peloton import IMAGES_DIR

# for image_file in IMAGES_DIR.iterdir():
#     print(f"Converting {image_file}...")
#     thumb_filename = image_file.with_stem(f"{image_file.stem}_thumb")
    
#     img = Image.open(image_file)
#     thumb = img.copy()
#     thumb.thumbnail(size=(250, 250))

#     thumb.save(thumb_filename)

image_file = IMAGES_DIR.joinpath('img_1663794305_983716073eca42769ae4598e3118c8c7.png')
print(f"Converting {image_file}...")
thumb_filename = image_file.with_stem(f"{image_file.stem}_thumb")

img = Image.open(image_file)
thumb = img.copy()
thumb.thumbnail(size=(250, 250))

thumb.save(thumb_filename)