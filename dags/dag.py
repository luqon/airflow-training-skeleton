import datetime as dt

from airflow import DAG
# from airflow.operators.python_operator import PythonOperator
from godatadriven.operators.postgres_to_gcs import PostgresToGoogleCloudStorageOperator
from airflow.contrib.operators.dataproc_operator imort (
    DataprocClusterCreateOperator,
    DataprocClusterDeleteOperator,
    DataProcPySparkOperator
)


dag = DAG(
    dag_id="my_second_dag",
    schedule_interval="30 7 * * *",
    default_args={
        "owner": "airflow",
        "start_date": dt.datetime(2018, 10, 1),
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
    cluster_name="dataproc_cluster_dag_training_{{ds}}",
    project_id="airflowbolcom-b9aabd6971d488d9",
    num_workers=2,
    zone="europe-west1-d",
    dag=dag
)

compute_aggregates = DataProcPySparkOperator(
    task_id="compute_aggregates",
    main='gs://gdd-training/build_statistics.py',
    cluster_name="dataproc_cluster_dag_training_{{ds}}",
    arguments=["{{ ds_nodash }}"],
    dag=dag
)

from airflow.utils.trigger_rule import TriggerRule

dataproc_delete_cluster = DataprocClusterDeleteOperator(
    task_id="delete_dataproc_cluster",
    cluster_name="dataproc_cluster_dag_training_{{ds}}",
    project_id="airflowbolcom-b9aabd6971d488d9",
    trigger_rule=TriggerRule.ALL_DONE,
    dag=dag
)

pgsl_to_gcs >> dataproc_create_cluster >> compute_aggregates >> dataproc_delete_cluster