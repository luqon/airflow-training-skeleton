import datetime as dt

from airflow import DAG
# from airflow.operators.python_operator import PythonOperator
from godatadriven.operators.postgres_to_gcs import PostgresToGoogleCloudStorageOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.contrib.operators.gcs_to_bq import GoogleCloudStorageToBigQueryOperator
from airflow.contrib.operators.dataproc_operator import (
    DataprocClusterCreateOperator,
    DataprocClusterDeleteOperator,
    DataProcPySparkOperator
)


dag = DAG(
    dag_id="my_third_dag",
    schedule_interval="30 7 * * *",
    default_args={
        "owner": "airflow",
        "start_date": dt.datetime(2018, 10, 10),
        "depends_on_past": True,
        "email_on_failure": True,
        "email": "airflow_errors@myorganisation.com",
    },
)


def print_exec_date(**context):
    print(context["execution_date"])


# my_task = PythonOperator(
#     task_id="task_name", python_callable=print_exec_date, provide_context=True, dag=dag
# )

pgsl_to_gcs = PostgresToGoogleCloudStorageOperator(
    task_id="export_data_to_bucket",
    postgres_conn_id="training_postgres",
    sql="SELECT * FROM land_registry_price_paid_uk WHERE transfer_date = '{{ ds }}'",
    bucket="airflow_training_data",
    filename="data_{{ds_nodash}}/land_registry_price.json",
    dag=dag
)

dataproc_create_cluster = DataprocClusterCreateOperator(
    task_id="create_dataproc_cluster",
    cluster_name="dataproc-cluster-dag-training-{{ ds }}",
    project_id="airflowbolcom-b9aabd6971d488d9",
    num_workers=2,
    zone="europe-west1-d",
    dag=dag
)

compute_aggregates = DataProcPySparkOperator(
    task_id="compute_aggregates",
    main='gs://europe-west1-training-airfl-68071199-bucket/other/build_statistics_simple.py',
    cluster_name="dataproc-cluster-dag-training-{{ ds }}",
    arguments=["{{ ds_nodash }}"],
    dag=dag
)


dataproc_delete_cluster = DataprocClusterDeleteOperator(
    task_id="delete_dataproc_cluster",
    cluster_name="dataproc-cluster-dag-training-{{ ds }}",
    project_id="airflowbolcom-b9aabd6971d488d9",
    trigger_rule=TriggerRule.ALL_DONE,
    dag=dag
)

bucket_to_bq = GoogleCloudStorageToBigQueryOperator(
    task_id="gcs_to_bq",
    bucket="airflow_training_data",
    source_objects="average_prices/transfer_date={{ds_nodash}}/",
    destination_project_dataset_table=\
        "airflowbolcom-b9aabd6971d488d9:airflow_training_dataset.land_registry_${{ ds_nodash }}",
    source_format="parquet",
    write_disposition="WRITE_TRUNCATE",
    dag=dag
)


pgsl_to_gcs >> dataproc_create_cluster >> compute_aggregates >> dataproc_delete_cluster >> bucket_to_bq