import boto3
import io

s3 = boto3.client("s3")


def upload(bucket, s3_img_path, in_mem_file):
    s3.put_object(
        Bucket=bucket,
        Key=s3_img_path,
        Body=in_mem_file,
        ContentType="image/png",
        ACL="public-read",
    )


def download(bucket, key):
    buffer_file = io.BytesIO()
    s3.download_fileobj(bucket, key, buffer_file)
    # Why do I have to do this seek operation?
    # https://stackoverflow.com/a/58006156/1723469
    buffer_file.seek(0)
    return buffer_file