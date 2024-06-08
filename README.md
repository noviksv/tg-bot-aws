# tg-bot-aws

Create lambda layer and publish it
```
mkdir python-bot-layer
cd python-bot-layer
pip install requests -t ./python
zip -r python-bot-layer.zip .

aws lambda publish-layer-version --layer-name python-bot-layer --zip-file fileb://python-bot-layer.zip --compatible-runtimes python3.12
```
Apply terraform infra
```
terraform apply -var-file=".tfvars"
```