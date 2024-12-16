from google.cloud import storage
import os

# Initialize Google Cloud Storage client
storage_client = storage.Client()
bucket_name = 'jigglypuff-images'

def upload_image(file_path):
    try:
        # Get the bucket
        bucket = storage_client.bucket(bucket_name)
        
        # Extract the file name
        file_name = os.path.basename(file_path)
        
        # Create a blob (object) in the bucket
        blob = bucket.blob(file_name)
        
        # Upload the file
        blob.upload_from_filename(file_path)
        
        # Make the file publicly accessible (optional)
        blob.make_public()
        
        print(f"{file_name} uploaded successfully.")
        return blob.public_url
    except Exception as e:
        print(f"Failed to upload {file_path}: {e}")
        raise
