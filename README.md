# csv-to-parquet-serverless

This is a simple serverless application for converting CSV files to Parquet using the AWS Serverless Application Model (SAM). 
The conversion is executed by a dockerized Lambda function which is triggered by an `s3:ObjectCreated:*` event. 
All the necessary commands and scripts are wrapped in a [Makefile](Makefile) to make building, testing and deploying the application a matter of running one command.

## Getting started

These instructions will get you a copy of the project up and running on your local machine and AWS.

### Prerequisites

* Python>=3.6
* Docker
* awscli
* [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)


### Customizing the environment

Configure the AWS profiles and regions in [stage.env](stage.env) and [prod.env](prod.env) to match your staging and production environments in AWS, respectively. Also change the `BUCKET_NAME` variable. `IMAGE_REPOSITORY` variable will be customized in the next step. Note that [stage.env](stage.env) is included by default in the [Makefile](Makefile). If you want to deploy to production, replace `include stage.env` with `include prod.env`.

### Building and deploying the application

Start by creating an AWS ECR repository for the Lambda docker image:
    
    make create-image-repo

The command prints out the repository details. Take the `repositoryUri` value and use it as `IMAGE_REPOSITORY` in [stage.env](stage.env).

Next, build the application image:

    make build

This command generates a [samconfig.toml](samconfig.toml) file from a template and runs `sam build` which in turn builds a Docker image for the Lambda function. The Lambda function is implemented in [lambda_app/app.py](lambda_app/app.py) and the image is defined in [lambda_app/Dockerfile](lambda_app/Dockerfile).

Next, deploy the application to AWS:

    make deploy

This command creates an AWS Elastic Container Registry (ECR) repository if it doesn't exist yet and runs `sam deploy` which pushes the freshly built Docker image to ECR and deploys the application stack as defined in [template.yaml](template.yaml) to AWS.


### Testing the application in AWS

First, create a Python virtual environment:

    make create-venv

Next, activate the environment and upload an example CSV file to `s3://<bucket>/raw/pytest.csv` using `make`:

    source venv/bin/activate
    make setup-integration-test

You can follow the Lambda function logs live by `make tail-logs`. 
The Lambda should now have created a parquet file `s3://<bucket>/transformed/pytest.snappy.parquet`.

### Testing the application locally

Run the unit tests in a local Python virtual environment:

    source venv/bin/activate
    make test

### Cleanup

Delete the stack and all its resources (including S3 bucket and ECR repository):

    make destroy

Also delete the ECR repository:

    make delete-image-repo

## Further reading

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)