import requests
import shutil
import os
import boto3

def download_mp3(url, save_path):
    try:
        # Ensure the target directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Open a local file with write-binary mode
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"MP3 file downloaded successfully and saved to {save_path}")
        else:
            raise SystemError(f"Failed to download file. Status code: {response.status_code}")
    except requests.RequestException as e:
        raise SystemError(f"Request error: {e}")
    except Exception as e:
        raise SystemError(f"An error occurred: {e}")
    
def delete_path(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
            print(f"File {path} deleted successfully.")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"Directory {path} and all its contents deleted successfully.")
        else:
            raise FileNotFoundError(f"Path {path} not found.")
    except FileNotFoundError:
        raise FileNotFoundError(f"Path {path} not found.")
    except PermissionError:
        raise PermissionError(f"Permission denied: cannot delete {path}.")
    except Exception as e:
        raise SystemError(f"Error deleting path {path}: {e}")

    
def upload_file(file_path, key):
    try:
        # Create an S3 client
        s3 = boto3.client(
            service_name='s3',
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        bucket_name = os.getenv("AWS_BUCKET_NAME")

        # Upload the file to the specified bucket with the specified key
        s3.upload_file(
            Filename=file_path,
            Bucket=bucket_name,
            Key=key,
            ExtraArgs={'ACL': 'public-read'}
        )
        print(f"File {file_path} uploaded to S3 bucket {bucket_name} with key {key}")

        # Construct the S3 URL
        region = os.getenv("AWS_REGION")
        url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"
        return url
    except Exception as e:
        raise SystemError(f"Error uploading file {file_path} to S3: {e}")