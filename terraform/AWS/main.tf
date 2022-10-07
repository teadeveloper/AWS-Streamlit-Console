provider "aws" {
  skip_credentials_validation = true
  skip_requesting_account_id = true
  skip_metadata_api_check = true
  s3_force_path_style = true
}


variable "s3_bucket_names" {
  type = list
  default = ["0001","0002","0003"]
}

resource "aws_s3_bucket" "rugged_buckets" {
  count         = length(var.s3_bucket_names) //count will be 3
  bucket        = var.s3_bucket_names[count.index]
  force_destroy = true
}



resource "aws_instance" "my-machine" {
   count = 3   # Here we are creating identical 4 machines. 
   ami = "ami-026b57f3c383c2eec"
   instance_type = "t2.micro"
   tags = {
      Name = "my-machine-${count.index}"
           }
}