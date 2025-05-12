import boto3
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from botocore.exceptions import ClientError
from django.conf import settings


def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url = settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
        aws_session_token = None,
        config = boto3.session.Config(signature_version='s3v4'),
        verify = False
    )

def upload_files(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        default_storage.save(file.name, ContentFile(file.read()))
    return redirect('file_list')
    
def file_list(request):
    s3_client = get_s3_client()
    files = []
    continuation_token = None
    errors_list = []

    try:
        while True:
            params = {'Bucket': settings.AWS_STORAGE_BUCKET_NAME}
            if continuation_token:
                params['ContinuationToken'] = continuation_token

            response = s3_client.list_objects_v2(**params)
            for file in response.get('Contents', []):
                file_name = file['Key']
                try:
                    file_params = params.copy()
                    file_params['Key'] = file_name
                    file_url = s3_client.generate_presigned_url(
                        'get_object',
                        Params=file_params,
                        ExpiresIn=30
                    )

                    files.append({
                        'file_name': file_name,
                        'file_url': file_url,
                        'size': file['Size'],
                        'last_modified': file['LastModified']
                    })
                except ClientError as e:
                    errors_list.append(e)
            if response.get('IsTruncated'):
                continuation_token = response.get('NextContinuationToken')
            else:
                break
    except ClientError as e:
        errors_list.append(e)

    return render(request, 'files_list.html', {'files': files, 'errors': errors_list})
