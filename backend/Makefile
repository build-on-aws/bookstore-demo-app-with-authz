all: build deploy
ORIGIN ?= http://localhost:8080
STACKNAME ?= bookstore-demo-app-with-authz

build:
	@echo "Building template $(TEMPLATE).yaml..."
	@sam build -t $(TEMPLATE).yaml

deploy:
	@echo "Deploying stack $(STACKNAME)-$(TEMPLATE)..."
	@sam deploy --capabilities CAPABILITY_NAMED_IAM --stack-name $(STACKNAME)-$(TEMPLATE) --s3-bucket $(S3_BUCKET) --parameter-overrides AllowedOrigin=$(ORIGIN) --no-fail-on-empty-changeset

delete:
	@aws cloudformation delete-stack --stack-name $(STACKNAME)-$(TEMPLATE)
	@echo "Waiting for stack $(STACKNAME)-$(TEMPLATE) to be deleted..."
	@aws cloudformation wait stack-delete-complete --stack-name $(STACKNAME)-$(TEMPLATE)

.PHONY: build package deploy delete
