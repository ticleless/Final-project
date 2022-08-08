data "aws_region" "current" {}

data "aws_caller_identity" "current" {}


resource "aws_s3_bucket" "main" {
  bucket = "backup-s3-teamd"

  tags = {
    Name = "backup-s3-teamd"
  }
}


resource "aws_kinesis_stream" "test_stream" {
  name             = "data-stream"
  shard_count      = 1

  shard_level_metrics = [
    "IncomingBytes",
    "OutgoingBytes",
  ]

  stream_mode_details {
    stream_mode = "PROVISIONED"
  }
}

resource "aws_cloudwatch_log_group" "s3backuplog" {
  name = "/aws/s3/firehose_to_s3"

  retention_in_days = 7
}
resource "aws_cloudwatch_log_stream" "s3backupstream" {
  name           = "/aws/s3/firehose_to_s3_stream"
  log_group_name = aws_cloudwatch_log_group.s3backuplog.name
}
resource "aws_cloudwatch_log_group" "opensearchlog" {
  name = "/aws/opensearch/firehose_to_opensearch"

  retention_in_days = 7
}
resource "aws_cloudwatch_log_stream" "opensearchstream" {
  name           = "/aws/opensearch/firehose_to_opensearch_stream"
  log_group_name = aws_cloudwatch_log_group.opensearchlog.name
}
resource "aws_kinesis_firehose_delivery_stream" "test_stream" {
  name        = "firehose-opensearch"
  destination = "elasticsearch"
  kinesis_source_configuration {
    kinesis_stream_arn = aws_kinesis_stream.test_stream.arn
    role_arn = aws_iam_role.firehose_role.arn
  }
  s3_configuration {
    role_arn           = aws_iam_role.firehose_role.arn
    bucket_arn         = aws_s3_bucket.main.arn
    buffer_size        = 5
    buffer_interval    = 60
    cloudwatch_logging_options {
      enabled = true
      log_group_name = aws_cloudwatch_log_group.s3backuplog.name
      log_stream_name =aws_cloudwatch_log_stream.s3backupstream.name
    }
  }

  elasticsearch_configuration {
    domain_arn = aws_opensearch_domain.test_cluster.arn
    role_arn   = aws_iam_role.firehose_role.arn
    index_name = "weather"
    s3_backup_mode = "AllDocuments"
    cloudwatch_logging_options {
      log_group_name = aws_cloudwatch_log_group.opensearchlog.name
      log_stream_name = aws_cloudwatch_log_stream.opensearchstream.name
      enabled = true
    }
  }
}

resource "aws_iam_role" "firehose_role" {
  name = "firehose_test_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "firehose.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
  inline_policy {
    name = "my_inline_policy"

    policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Action": [
                "s3:AbortMultipartUpload",
                "s3:GetBucketLocation",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:ListBucketMultipartUploads",
                "s3:PutObject"
            ],
            "Resource": "*"
        },
        {
            "Sid": "",
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction",
                "lambda:GetFunctionConfiguration"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "kms:GenerateDataKey",
                "kms:Decrypt"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "kms:ViaService": "s3.ap-northeast-2.amazonaws.com"
                },
                "StringLike": {
                    "kms:EncryptionContext:aws:s3:arn": [
                        "arn:aws:s3:::%FIREHOSE_POLICY_TEMPLATE_PLACEHOLDER%/*",
                        "arn:aws:s3:::%FIREHOSE_POLICY_TEMPLATE_PLACEHOLDER%"
                    ]
                }
            }
        },
        {
            "Sid": "",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeVpcs",
                "ec2:DescribeVpcAttribute",
                "ec2:DescribeSubnets",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeNetworkInterfaces",
                "ec2:CreateNetworkInterface",
                "ec2:CreateNetworkInterfacePermission",
                "ec2:DeleteNetworkInterface"
            ],
            "Resource": "*"
        },
        {
            "Sid": "",
            "Effect": "Allow",
            "Action": [
                "es:DescribeElasticsearchDomain",
                "es:DescribeElasticsearchDomains",
                "es:DescribeElasticsearchDomainConfig",
                "es:ESHttpPost",
                "es:ESHttpPut"
            ],
            "Resource": "*"
        },
        {
            "Sid": "",
            "Effect": "Allow",
            "Action": [
                "es:ESHttpGet"
            ],
            "Resource": "*"
        },
        {
            "Sid": "",
            "Effect": "Allow",
            "Action": [
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        },
        {
            "Sid": "",
            "Effect": "Allow",
            "Action": [
                "kinesis:DescribeStream",
                "kinesis:GetShardIterator",
                "kinesis:GetRecords",
                "kinesis:ListShards"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "kms:ViaService": "kinesis.ap-northeast-2.amazonaws.com"
                },
                "StringLike": {
                    "kms:EncryptionContext:aws:kinesis:arn": "arn:aws:kinesis:ap-northeast-2:*"
                }
            }
        }
    ]
}
EOF
  }
}

resource "aws_iam_role_policy_attachment" "firehose_policy" {
  role       = aws_iam_role.firehose_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

#open search service

resource "aws_opensearch_domain" "test_cluster" {
  domain_name = var.domain
  engine_version = "OpenSearch_1.3"
  
  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }
  auto_tune_options{
    desired_state = "DISABLED"
  }
  cluster_config {
    instance_type = "t3.small.search"
  }
  encrypt_at_rest{
    enabled = true
  }
  node_to_node_encryption{
    enabled = true
  }
  domain_endpoint_options{
    enforce_https = true
    tls_security_policy = "Policy-Min-TLS-1-0-2019-07"
  }
  advanced_security_options{
    enabled = true
    internal_user_database_enabled = true
    master_user_options {
      master_user_name = var.user
      master_user_password = var.password
    }
  }
    access_policies = <<CONFIG
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "es:*",
            "Principal": "*",
            "Effect": "Allow",
            "Resource": "arn:aws:es:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:domain/${var.domain}/*"
        }
    ]
}
CONFIG

}
