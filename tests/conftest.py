import os
import pytest
import boto3
import pandas as pd
import numpy as np
from faker import Faker
from lambda_app.app import DEFAULT_SEP


@pytest.fixture
def bucket_name():
    return os.environ['BUCKET_NAME']


@pytest.fixture
def bucket(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    return bucket


@pytest.fixture
def data_file_local_path(shared_datadir):
    return shared_datadir / 'pytest.csv'

@pytest.fixture
def df_fake():
    seed = 1
    Faker.seed(seed)
    np.random.seed(seed)
    faker = Faker()
    df = pd.DataFrame()

    row_count = 100
    for i in range(row_count):
        df = df.append(faker.profile(), ignore_index=True)

    df['numeric_attribute'] = np.random.rand(row_count)
    df['numeric_attribute_with_missing_values'] = df['numeric_attribute']
    df.loc[df['numeric_attribute'] < 0.5, 'numeric_attribute_with_missing_values'] = np.NaN

    return df


@pytest.fixture
def data_file_local_path(df_fake, datadir):
    path = datadir / 'pytest.csv'
    df_fake.to_csv(path, sep=DEFAULT_SEP, index=False)
    return path


@pytest.fixture
def data_file_s3_key():
    return 'raw/pytest.csv'


@pytest.fixture
def s3_notification_event(bucket_name, data_file_s3_key):
    return {
        "Records": [
            {
            "eventVersion": "2.1",
            "eventSource": "aws:s3",
            "awsRegion": "us-east-2",
            "eventTime": "2019-09-03T19:37:27.192Z",
            "eventName": "ObjectCreated",
            "userIdentity": {
                "principalId": "AWS:AIDAINPONIXQXHT3IKHL2"
            },
            "requestParameters": {
                "sourceIPAddress": "205.255.255.255"
            },
            "responseElements": {
                "x-amz-request-id": "D82B88E5F771F645",
                "x-amz-id-2": "vlR7PnpV2Ce81l0PRw6jlUpck7Jo5ZsQjryTjKlc5aLWGVHPZLj5NeC6qMa0emYBDXOo6QBU0Wo="
            },
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "828aa6fc-f7b5-4305-8584-487c791949c1",
                "bucket": {
                "name": bucket_name,
                "ownerIdentity": {
                    "principalId": "A3I5XTEXAMAI3E"
                },
                "arn": "arn:aws:s3:::lambda-artifacts-deafc19498e3f2df"
                },
                "object": {
                "key": data_file_s3_key,
                "size": 1305107,
                "eTag": "b21b84d653bb07b05b1e6b33684dc11b",
                "sequencer": "0C0F6F405D6ED209E1"
                }
            }
            }
        ]
    }

@pytest.mark.setup
def test_upload_file_to_s3(bucket, data_file_local_path, data_file_s3_key):
    s3_object = bucket.Object(data_file_s3_key)
    s3_object.upload_file(data_file_local_path.as_posix())