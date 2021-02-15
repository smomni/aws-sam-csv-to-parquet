include stage.env
export


create-venv:
	python3 -m virtualenv venv
	venv/bin/pip install -r requirements.txt

create-image-repo:
	aws ecr describe-repositories --repository-names "${STACK_NAME}" || aws ecr create-repository --repository-name "${STACK_NAME}" --image-tag-mutability IMMUTABLE --image-scanning-configuration scanOnPush=false

build:
	envsubst < "samconfig.toml.template" > "samconfig.toml"
	sam build

deploy:
	sam deploy

tail-logs:
	sam logs -n CsvToParquetFunction --stack-name ${STACK_NAME} --tail

setup-integration-test:
	pytest -m setup

test:
	pytest

destroy:
	aws s3 rb s3://${BUCKET_NAME} --force || true
	aws cloudformation delete-stack --stack-name ${STACK_NAME}
	
delete-image-repo:
	aws ecr delete-repository --repository-name "${STACK_NAME}" --force