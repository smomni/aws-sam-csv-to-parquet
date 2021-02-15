import pytest
import json
import pandas as pd
from lambda_app.app import df_to_parquet, lambda_handler

def test_df_to_parquet_writes_a_dataframe_to_a_parquet_file(df_fake, datadir):
    path = datadir / 'pytest.parquet.snappy'
    # Drop columns with unsupported data types
    unsupported_data_type_columns = ['current_location']
    df = df_fake.drop(labels=unsupported_data_type_columns, axis=1)
    df_to_parquet(df=df, path=path)

    df_read = pd.read_parquet(path)
    assert len(df) == len(df_read)
    assert (df.columns == df_read.columns).all()

def test_lambda_handler_takes_s3_notification_and_converts_put_objects_to_parquet_if_csv(s3_notification_event, bucket_name, mocker):
    context = ""
    result = lambda_handler(event=s3_notification_event, context=context)
    files = result["files"]
    assert len(files) == 1
    for file in files:
        output_path = file["output"]
        input_path = file["input"]
        assert output_path == f"s3://{bucket_name}/transformed/pytest.snappy.parquet"
        assert input_path.startswith(f"s3://{bucket_name}/raw/")
