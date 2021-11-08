resource "aws_s3_bucket" "storage" {
  bucket = "kiba-${local.project}"
  acl = "private"
  lifecycle {
    prevent_destroy = false
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  tags = {
    app = local.project
  }
}

resource "aws_s3_bucket_public_access_block" "storage" {
  bucket = aws_s3_bucket.storage.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}
