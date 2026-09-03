from datetime import date
import hashlib, pyvips

# Pillow is far more stricter with image formats.
# Therefore I have opted to use cv2 which offers greater compatibility.

def scrape_metadata(file_data, filename):

    image_metadata = {}

    image_metadata['img_id'] = hashlib.sha256(file_data).digest()
    image_metadata['img_name'] = filename

    img = pyvips.Image.new_from_buffer(file_data, '')
    image_metadata['img_x_res'] = img.width
    image_metadata['img_y_res'] = img.height

    try:
        date_taken = img.get('exif-ifd0-DateTime')
        year_var = int(date_taken[0:4])
        month_var = int(date_taken[5:7])
        date_var = int(date_taken[8:10])
        image_metadata['img_date_taken'] = date(year_var, month_var, date_var)
    except:
        image_metadata['img_date_taken'] = date.today()
        
    return image_metadata

def generate_thumbnails(file_data):
    image = pyvips.Image.thumbnail_buffer(file_data, 600, height=600)
    return image.write_to_buffer('.webp', Q=100)