from google.cloud import storage
import io
import uuid
import datetime

class GCSManager:
    def __init__(self, bucket_name):
        self.client = storage.Client()
        self.bucket_name = bucket_name
        self.bucket = self.client.bucket(bucket_name)

    def upload_image(self, image_obj, folder="memes"):
        """
        Uploads a PIL image to GCS.
        """
        # Convert PIL image to bytes
        img_byte_arr = io.BytesIO()
        image_obj.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)

        # Generate unique filename
        filename = f"{folder}/{uuid.uuid4()}.jpg"
        blob = self.bucket.blob(filename)
        
        # Upload
        blob.upload_from_file(img_byte_arr, content_type='image/jpeg')
        
        # Make public (optional, depending on bucket settings) or return authenticated link
        # For this project, we assume the bucket or service account allows viewing
        return blob.public_url

    def list_images(self, folder="memes"):
        """
        Lists all blobs in the folder.
        """
        blobs = self.client.list_blobs(self.bucket_name, prefix=folder)
        # Sort by time created (newest first)
        sorted_blobs = sorted(blobs, key=lambda x: x.time_created, reverse=True)
        
        image_urls = []
        for blob in sorted_blobs:
            # We use media_link for downloading/displaying within the app authenticated session
            image_urls.append(blob.media_link) 
        
        return image_urls