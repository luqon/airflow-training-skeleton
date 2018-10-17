from airflow.hooks.http_hook import HttpHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.gcs_hook import GoogleCloudStorageHook

class HttpToGcsOperator(BaseOperator):

    template_fields = ('endpoint', 'bucket', 'bucket_path')
    def __init__(self, endpoint, bucket, bucket_path, method='GET'):
        self.endpoint = endpoint
        self.bucket = bucket
        self.bucket_path = bucket_path
        self.method = method

    def execute(self):
        http_hook = HttpHook()
        response = http_hook.run(self.endpoint, self,method)

        #gcs_hook = GoogleCloudStorageHook()
        #gcs_hook.upload_file(response, self.bucket, self.bucket_path)

endpoint='https://europe-west1-gdd-airflow-training.cloudfunctions.net/airflow-training-transform-valutas'

bla = HttpToGcsOperator(endpoint=endpoint,
                        bucket="airflow_training_data",
                        bucket_path="currencies/{{ds_nodash}}_{from_currency}_{to_currency}.json"
                        )
bla.execute()