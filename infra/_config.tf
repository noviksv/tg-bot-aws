# Set up the backend 
terraform {
  required_version = ">1.8.0"

  required_providers {
    aws = { version = "5.53.0" }
  }

  backend "s3" {
    #9 put your values in .backend.hcl
    # bucket         = ""
    # key            = ""
    # region         = ""
    # dynamodb_table = ""
  }
}
