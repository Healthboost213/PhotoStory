from io import BytesIO
from botocore.client import Config
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import boto3, os, secrets

class FileStorage:

    def upload(self, filename, file_ext, file_data):
        pass

    def upload_thumbnail(self, filename, file_data):
        pass

    def download(self, filename, file_ext):
        pass

    def download_thumb(self, filename):
        pass

    def delete_func(self, filename, file_ext):
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

    def delete_func(self, filename, file_ext):
        self.s3.delete_object(Bucket=self.bucket_name, Key=f'images/{filename}{file_ext}')
        self.s3.delete_object(Bucket=self.bucket_name, Key=f'thumbnails/{filename}.webp')

class LocalStorage(FileStorage):
    
    def __init__(self):
        self.__ImageDirectory = Path(__file__).resolve().parent / 'PhotoStory' / 'Images'
        self.__ThumbnailDirectory = Path(__file__).resolve().parent / 'PhotoStory' / 'Thumbnails'
        self.__ImageDirectory.mkdir(parents=True, exist_ok=True)
        self.__ThumbnailDirectory.mkdir(parents=True, exist_ok=True)
        if os.getenv('IMAGE_ENCRYPTION_KEY') is not None:
            self.__Encryption = AESGCM(bytes.fromhex(os.getenv('IMAGE_ENCRYPTION_KEY')))
        
    def upload(self, filename, file_ext, file_data):
        creation_path = self.__ImageDirectory / f'{filename}{file_ext}'

        try:
            nonce = secrets.token_bytes(12)
            ciphertext = self.__Encryption.encrypt(nonce, file_data, None)
            payload = b''.join([nonce, ciphertext])
        except:
            payload = file_data

        with open(creation_path, 'wb') as file:
            file.write(payload)
    
    def upload_thumbnail(self, filename, file_data):
        creation_path = self.__ThumbnailDirectory / f'{filename}.webp'

        try:
            nonce = secrets.token_bytes(12)
            ciphertext = self.__Encryption.encrypt(nonce, file_data, None)
            payload = b''.join([nonce, ciphertext])
        except:
            payload = file_data

        with open(creation_path, 'wb') as file:
            file.write(payload)

    def download(self, filename, file_ext):
        current_file_path = self.__ImageDirectory / f'{filename}{file_ext}'
        with open(current_file_path, 'rb') as file:
            data = memoryview(file.read())
            try:
                nonce = data[:12]
                ciphertext = data[12:]
                plaintext = BytesIO(self.__Encryption.decrypt(nonce, ciphertext, None))
            except:
                plaintext = BytesIO(data)

        return plaintext
    
    def download_thumb(self, filename):
        current_file_path = self.__ThumbnailDirectory / f'{filename}.webp'
        with open(current_file_path, 'rb') as file:
            data = memoryview(file.read())
            try:
                nonce = data[:12]
                ciphertext = data[12:]
                plaintext = BytesIO(self.__Encryption.decrypt(nonce, ciphertext, None))
            except:
                plaintext = BytesIO(data)

        return plaintext
    
    def delete_func(self, filename, file_ext):
        im_path = self.__ImageDirectory / (filename + file_ext)
        im_path.unlink()
        thumb_path = self.__ThumbnailDirectory / (filename + '.webp')
        thumb_path.unlink()
 
storage = None
if os.getenv('STORAGE_BACKEND') == 's3':
    storage = S3Storage()
elif os.getenv('STORAGE_BACKEND') == 'local':
    storage = LocalStorage()