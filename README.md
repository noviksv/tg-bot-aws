## Project Description

This project is implementation telegram bot on aws serverless stack.

## AWS Technologies Used

- **AWS Lambda**: For running the serverless functions.
- **Amazon API Gateway**: To expose the Lambda functions as HTTP endpoints.
- **Amazon DynamoDB**: For storing user settings and data.
- **Amazon CloudWatch**: For scheduling events and monitoring.
- **AWS IAM**: For managing access and permissions.
- **Amazon S3**: For storing Terraform state files.

## C4 Diagrams

### System Context

![alt](docs/tg-bot-system_context.png)

### Container Diagram
![alt](docs/tg-bot-container_diagram.png)

# tg-bot-aws

Create lambda layer and publish it
```
mkdir python-bot-layer
cd python-bot-layer
pip install requests -t ./python
zip -r python-bot-layer.zip .

aws lambda publish-layer-version --layer-name python-bot-layer --zip-file fileb://python-bot-layer.zip --compatible-runtimes python3.12
```
## Infrastructure
Initialize backend
```
terraform init -backend-config=.terraform.backend.hcl
```
Apply terraform infra
```
terraform apply -var-file=".tfvars"
```
Trigger lambda from local environment

```
aws lambda invoke --function-name weather_bot --payload file://events/event.json --cli-binary-format raw-in-base64-out outfile.txt
```

Run some tests
```
cd src ;python -m unittest 
```

## telegram bot settings

Set webhook to telegram bot
```
curl https://api.telegram.org/bot{my_bot_token}/setWebhook?url={url_to_send_updates_to}
```


## CI/CD Pipelines

### Terraform CI/CD Pipeline

The CI/CD pipeline for Terraform is defined in [`.github/workflows/pipeline.yml`](.github/workflows/pipeline.yml). It includes the following steps:

1. **Checkout**: Checks out the repository code.
2. **Setup Terraform**: Sets up Terraform with the specified version.
3. **Configure AWS Credentials**: Configures AWS credentials using secrets stored in GitHub.
4. **Terraform Init**: Initializes Terraform with backend configuration.
5. **Terraform Format**: Checks the formatting of Terraform files.
6. **Terraform Plan**: Creates an execution plan for Terraform.
7. **Terraform Apply**: Applies the Terraform plan if the branch is `main` and the event is a push.
