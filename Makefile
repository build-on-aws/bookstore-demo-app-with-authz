all: install backend frontend-build

TEMPLATES = authentication authorization product

REGION := $(shell python3 -c 'import boto3; print(boto3.Session().region_name)')
ifndef S3_BUCKET
ACCOUNT_ID := $(shell aws sts get-caller-identity --query Account --output text)
S3_BUCKET = bookstore-demo-app-with-authz-src-$(ACCOUNT_ID)-$(REGION)
endif

install:
	virtualenv .env --python=python3
	curl -sS https://bootstrap.pypa.io/get-pip.py | .env/bin/python
	.env/bin/python -m pip install -r requirements.txt

backend: create-bucket
	$(MAKE) -C backend TEMPLATE=authentication S3_BUCKET=$(S3_BUCKET)
	$(MAKE) -C backend TEMPLATE=authorization S3_BUCKET=$(S3_BUCKET)
	$(MAKE) -C backend TEMPLATE=product S3_BUCKET=$(S3_BUCKET)

backend-delete:
	$(MAKE) -C backend delete TEMPLATE=authentication
	$(MAKE) -C backend delete TEMPLATE=authorization
	$(MAKE) -C backend delete TEMPLATE=product

create-bucket:
	@echo "S3 Bucket: Checking if s3://$(S3_BUCKET) exists ..."
	@aws s3api head-bucket --bucket $(S3_BUCKET) || (echo "S3 Bucket: Bucket s3://$(S3_BUCKET) doest not exist, creating it ..." ; aws s3 mb s3://$(S3_BUCKET) --region $(REGION))

frontend-serve:
	$(MAKE) -C frontend serve

frontend-build:
	$(MAKE) -C frontend build

.PHONY: all backend backend-delete create-bucket amplify-deploy frontend-serve frontend-build
