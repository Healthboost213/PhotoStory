from datetime import date
from enum import Enum
from scipy.spatial import cKDTree
from pathlib import Path
import hashlib, pyvips, exif, pickle

hasGeocoding = False
world_data_path = Path(__file__).resolve().parent / 'db' / 'world_data.pkl'
try:
    with open(world_data_path, 'rb') as f:
        kd_tree, city_data = pickle.load(f)
        hasGeocoding = True
except FileNotFoundError:
    hasGeocoding = False

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

def coord_converter(coord, ref): 
    if (ref == 'N') or (ref == 'E'):
        final = round((coord[0] + (coord[1] / 60) + (coord[2] / 3600)), 4)
        return final
    elif (ref == 'S') or (ref == 'W'):
        final = round((coord[0] + (coord[1] / 60) + (coord[2] / 3600)), 4)
        return -final
    else:
        return None

def geospatial_location_finder(x_coord, y_coord):
    _, index = kd_tree.query((x_coord, y_coord))
    baseStr = city_data[index]['name'] + ', ' + city_data[index]['country_code']
    return baseStr

def scrape_exif(file_data):

    exif_metadata = {'camera' : {}, 'gps' : {}}

    try:

        img = exif.Image(file_data)

        exif_metadata['camera']['make'] = img.get('make', default='')
        exif_metadata['camera']['model'] = img.get('model', default='')
        exif_metadata['camera']['shutter_speed'] = img.get('exposure_time', default='')
        exif_metadata['camera']['aperture_size'] = img.get('f_number', default='')
        exif_metadata['camera']['iso'] = img.get('photographic_sensitivity', default='')

        exif_metadata['gps']['latitude'] = img.get('gps_latitude', default='')
        exif_metadata['gps']['latitude_ref'] = img.get('gps_latitude_ref', default='')
        exif_metadata['gps']['longitude'] = img.get('gps_longitude', default='')
        exif_metadata['gps']['longitude_ref'] = img.get('gps_longitude_ref', default='')

        lat_coord = coord_converter(img.get('gps_latitude', default=0), img.get('gps_latitude_ref', default=''))
        long_coord = coord_converter(img.get('gps_longitude', default=0), img.get('gps_longitude_ref', default=''))

        if hasGeocoding:
            exif_metadata['gps']['location'] = geospatial_location_finder(lat_coord, long_coord)
        else:
            exif_metadata['gps']['location'] = ''
        
    except Exception as e:
        pass

    return exif_metadata

def generate_thumbnails(file_data):
    image = pyvips.Image.thumbnail_buffer(file_data, 600, height=600)
    return image.write_to_buffer('.webp', Q=100)

def validate_image(file_data):

    # jpeg
    if file_data[0:3] == 0xFFD8FF.to_bytes(length=3, byteorder="big"):
        print('isjpeg')
        return True

    # png
    if file_data[0:8] == 0x89504E470D0A1A0A.to_bytes(length=8, byteorder="big"):
        print('ispng')
        return True

    # gif
    if file_data[0:6] == 0x474946383761.to_bytes(length=8, byteorder="big") or file_data[0:6] == 0x474946383961.to_bytes(length=8, byteorder="big"):
        print('isgif')
        return True

    # webp
    if file_data[0:4] == 0x52494646.to_bytes(length=4, byteorder="big"):
        print("iswebp")
        return True

    # avif
    if file_data[4:8] == 0x66747970.to_bytes(length=4, byteorder="big"):
        print("isavif")
        return True

    return False