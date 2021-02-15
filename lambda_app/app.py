import logging
import sys
import pandas as pd
from pythonjsonlogger import jsonlogger
from typing import Any, List

logger = logging.getLogger(__name__)
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)

DEFAULT_SEP = ';'

def df_to_parquet(df: pd.DataFrame, path: str):
    df.to_parquet(path, engine='pyarrow', compression='snappy', index=None)


def yield_objects_from_records(records: List[dict]):
    for record in records:
        bucket_name = record["s3"]["bucket"]["name"]
        object_name = record["s3"]["object"]["key"]
        yield bucket_name, object_name


def lambda_handler(event: dict, context: Any):
    """
    :param event: S3 notification event
    :param context: Lambda Context runtime methods and attributes
    """
    input_prefix = 'raw/'
    input_suffix = '.csv'
    output_prefix = 'transformed/'
    output_suffix = '.snappy.parquet'
    return_values = []

    records = event["Records"]
    for bucket_name, object_name in yield_objects_from_records(records):
        path = f"s3://{bucket_name}/{object_name}"
        logger.info('Read CSV', extra={"input_uri": path})
        df = pd.read_csv(path, sep=DEFAULT_SEP)
        assert object_name.startswith(input_prefix)
        assert object_name.endswith(input_suffix)
        output_object_name = output_prefix + object_name[len(input_prefix):len(object_name)-len(input_suffix)] + output_suffix
        output_path = f"s3://{bucket_name}/{output_object_name}"
        logger.info('Write Parquet', extra={"output_uri": output_path, "row_count": len(df), "column_count": len(df.columns)})
        df_to_parquet(df, output_path)
        return_values.append(
            {
                "input": path,
                "output": output_path
            }
        )

    return {"files": return_values}
