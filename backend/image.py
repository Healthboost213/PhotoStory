from PIL import Image
from datetime import date
import numpy as np
import cv2, io, hashlib

# Pillow is far more stricter with image formats.
# Therefore I have opted to use cv2 which offers greater compatibility.

def scrape_metadata(file_data, filename):

    image_metadata = {}

    image_metadata['img_id'] = hashlib.sha256(file_data).digest()
    image_metadata['img_name'] = filename
    
    with Image.open(io.BytesIO(file_data)) as img:
        
        image_metadata['img_x_res'] = img.width
        image_metadata['img_y_res'] = img.height

        try:
            date_taken = img.getexif()[306]
            year_var = int(date_taken[0:4])
            month_var = int(date_taken[5:7])
            date_var = int(date_taken[8:10])
            image_metadata['img_date_taken'] = date(year_var, month_var, date_var)
        except:
            image_metadata['img_date_taken'] = date.today()

    return image_metadata

def generate_thumbnails(file_data):

    image_as_array = np.frombuffer(file_data, dtype='uint8')
    image_decoded = cv2.imdecode(image_as_array, cv2.IMREAD_COLOR)
    image_resized = cv2.resize(image_decoded, (300, 300), cv2.INTER_NEAREST)
    thumbnail_encode = cv2.imencode('.webp', image_resized, [cv2.IMWRITE_WEBP_QUALITY, 80])[1]

    return thumbnail_encode.tobytes()