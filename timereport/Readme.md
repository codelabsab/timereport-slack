#####
```
.
├── Readme.md
├── requirements.txt
├── timereport
│   ├── __init__.py
│   ├── __main__.py
│   ├── api.py
│   └── validator.py
├── static
├── templates
├── terraform
│   ├── 01-tags.tf
│   ├── api_gateway.tf
│   ├── iam.tf
│   ├── lambda.tf
│   ├── main.tf
│   └── variables.tf
└── test
    ├── __init__.py
        └── test_validator.py

        5 directories, 14 files

```
in project dir run:

```
python -m unittest test/test_validator.py -v

```

```
# to deploy to aws use terraform directory
# requires ssm parameter store variable set
# aws credentials configured
# variables.tf:  updated with your values
# main.tf : update backend s3 storage values

terraform init
terraform plan
terraform deploy
```
####
