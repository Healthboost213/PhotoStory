# PhotoStory Install Guide

PhotoStory can be installed either manually or automatically using the script. It is recommended to configure manually if you want a custom configuration. The automatic script may be too streamlined for you.


---
### Automatic Configuration

coming soon

---

### Manual Configuration

Firstly, before starting off with the main installation. Ensure you have the prerequisites:

- Python >= 3.12.10
- Node.js >= v24.21.0
- Nginx
- Git 

Next, clone the repository outside of home directory. A recommended location would be `/opt/`
```
git clone https://github.com/Healthboost213/PhotoStory.git
```

Let's configure the backend first. From the root of the PhotoStory directory,
```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file at the root of the backend folder. Change the configuration as you deem fit.
```
# Storage Option (accepts 'local' or 's3')
STORAGE_BACKEND=local

# Flask Configurations. Use Python secrets lib to generate this.
FLASK_SECRET=

# Master key for use in dashboard. Set a secure password for this.
MASTER_KEY=
```

Next, we need to run a production grade WSGI server rather than the built-in Flask Development Server as there are security flaws within Flask Dev Server that can allow for arbitrary code execution. This step is very crucial. Only one thread is used as the SQLite Database cannot handle conccurent requests. 

On Linux, you can run the server using Gunicorn.
```
pip install gunicorn
gunicorn app:app -w 1 --bind 127.0.0.1:8080
```

On Windows and MacOS, Waitress is the only option.
```
pip install waitress
waitress-serve --threads=1 --host=127.0.0.1 --port=8080 app:app
```

Next let's configure the frontend. The frontend requires Nodejs to be installed. From the root of the PhotoStory directory,
```
cd frontend
npm install
npm run build
```
The Svelte app should be built and located inside the `/dist/` folder.

Depending on your Operating system, an appropriate webserver + reverse proxy can be used. I would recommend Nginx. I've left a sample configuration in the configs folder to view as reference. Do make any tweaks necessary to ensure proper security. To enable E2EE, ensure you use proper TLS certificates.

---

### Optional Addons

These are all additonal configurations that can be added to PhotoStory to extend its feature set. However, it can work without these by default.

### S3-Compatible Storage

PhotoStory allows for extending its storage functionality to the cloud via S3-Compatible Storage Interface. This feature was primary tested with RustFS but ideally should work under different providers just the same.

```
# S3 Specific Configurations
STORAGE_BACKEND=s3
ENDPOINT_URL=
BUCKET_NAME=
AWS_ACCESS_KEY=
AWS_SECRET_KEY=
```

### Encryption at Rest

PhotoStory doesn't encrypt images while saving to disk by default. You would need to generate an AES key and supply it in the .env file under the key, 
```
STORAGE_BACKEND=local
IMAGE_ENCRYPTION_KEY=
```
The app will automatically detect the key and encrypt future uploads. Note that this will only work under local storage backend.

### Reverse Geocoding Support

PhotoStory uses the cities500 dataset to provide offline reverse geocoding support. This doesn't right outside the box and requires extra configuration.

```
curl -O https://download.geonames.org/export/dump/cities500.zip
```
Extract and place the resulting file at the root of the scripts folder. Run `geospatial.py`. There should be a pickles file generated. Leave it there. The app should automatically detect it and include definitions for future image uploads.