from io import BytesIO
from botocore.client import Config
from pathlib import Path
import boto3, os

class FileStorage:

    def upload(self, filename, file_ext, file_data):
        pass

    def upload_thumbnail(self, filename):
        pass

    def download(self, filename, file_ext):
        pass

    def download_thumb(self, filename):
        pass

    def delete_func(self, filename):
        pass

class S3Storage(FileStorage):
    
    def __init__(self):
        
        self.bucket_name = os.getenv('BUCKET_NAME')

        self.s3 = boto3.client(
            service_name='s3',
            endpoint_url= os.getenv('ENDPOINT_URL'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            region_name='us-east-1',
            config=Config(signature_version='s3v4')
        )

    def upload(self, filename, file_ext, file_data):
        self.s3.upload_fileobj(BytesIO(file_data), self.bucket_name, f'images/{filename}{file_ext}')

    def upload_thumbnail(self, filename, file_data):
        self.s3.upload_fileobj(BytesIO(file_data), self.bucket_name, f'thumbnails/{filename}.webp')

    def download(self, filename, file_ext):
        loaded_data = BytesIO()
        downloaded_file = self.s3.download_fileobj(self.bucket_name, f'images/{filename}{file_ext}', loaded_data)
        return loaded_data
    
    def download_thumb(self, filename):
        loaded_data = BytesIO()
        downloaded_File = self.s3.download_fileobj(self.bucket_name, f'thumbnails/{filename}.webp', loaded_data)
        return loaded_data

    def delete_func(self, filename):
        pass

class LocalStorage(FileStorage):
    
    def __init__(self):
        self.__ImageDirectory = Path(__file__).resolve().parent / 'PhotoStory' / 'Images'
        self.__ThumbnailDirectory = Path(__file__).resolve().parent / 'PhotoStory' / 'Thumbnails'
        self.__ImageDirectory.mkdir(parents=True, exist_ok=True)
        self.__ThumbnailDirectory.mkdir(parents=True, exist_ok=True)
        
    def upload(self, filename, file_ext, file_data):
        creation_path = self.__ImageDirectory / f'{filename}{file_ext}'
        with open(creation_path, 'wb') as file:
            file.write(file_data)
    
    def upload_thumbnail(self, filename, file_data):
        creation_path = self.__ThumbnailDirectory / f'{filename}.webp'
        with open(creation_path, 'wb') as file:
            file.write(file_data)

    def download(self, filename, file_ext):
        current_file_path = self.__ImageDirectory / f'{filename}{file_ext}'
        with open(current_file_path, 'rb') as file:
            data = BytesIO(file.read())
        return data
    
    def download_thumb(self, filename):
        current_file_path = self.__ThumbnailDirectory / f'{filename}.webp'
        with open(current_file_path, 'rb') as file:
            data = BytesIO(file.read())
        return data
    
    def delete_func(self, filename):
        for path in self.__ImageDirectory.glob(filename + '*'):
            path.unlink()

        for path in self.__ThumbnailDirectory.glob(filename + '*'):
            path.unlink()
 
storage = None
if os.getenv('STORAGE_BACKEND') == 's3':
    storage = S3Storage()
elif os.getenv('STORAGE_BACKEND') == 'local':
    storage = LocalStorage()