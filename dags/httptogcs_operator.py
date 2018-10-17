from airflow.hooks.http_hook import HttpHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.gcs_hook import GoogleCloudStorageHook

class HttpToGcsOperator(BaseOperator):

    template_fields = ('endpoint', 'bucket', 'bucket_path')
    def __init__(self, endpoint, bucket, bucket_path, method='GET', *args, **kwargs):
        self.endpoint = endpoint
        self.bucket = bucket
        self.bucket_path = bucket_path
        self.method = method

    def execute(self):
        http_hook = HttpHook()
        response = http_hook.run(self.endpoint, self.method)

        #gcs_hook = GoogleCloudStorageHook()
        #gcs_hook.upload_file(response, self.bucket, self.bucket_path)