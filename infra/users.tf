resource "aws_iam_group" "notd_users" {
  name = "notd-users"
}

resource "aws_iam_group" "notd_readers" {
  name = "notd-readers"
}

resource "aws_iam_user" "notd_api" {
  name = "notd-api"
  tags = {
    app = "notd"
  }
}

resource "aws_iam_access_key" "notd_api" {
  user = aws_iam_user.notd_api.name
}

resource "aws_iam_user_group_membership" "notd_api" {
  user = aws_iam_user.notd_api.name

  groups = [
    aws_iam_group.notd_readers.name,
    aws_iam_group.notd_users.name,
  ]
}

resource "aws_iam_user" "notd_user_obafemi" {
  name = "notd-user-obafemi"
  tags = {
    app = "notd"
  }
}

resource "aws_iam_access_key" "notd_user_obafemi" {
  user = aws_iam_user.notd_user_obafemi.name
}

resource "aws_iam_user_group_membership" "notd_user_obafemi" {
  user = aws_iam_user.notd_user_obafemi.name

  groups = [
    aws_iam_group.notd_readers.name,
  ]
}

output "notd_user_obafemi_name" {
  value     = aws_iam_user.notd_user_obafemi.name
  sensitive = true
}

output "notd_user_obafemi_iam_key" {
  value     = aws_iam_access_key.notd_user_obafemi.id
  sensitive = true
}

output "notd_user_obafemi_iam_secret" {
  value     = aws_iam_access_key.notd_user_obafemi.secret
  sensitive = true
}

resource "aws_iam_group_policy_attachment" "notd_users_read_from_notd_queue_dl" {
  group = aws_iam_group.notd_users.name
  policy_arn = aws_iam_policy.read_from_notd_queue_dl.arn
}

resource "aws_iam_group_policy_attachment" "notd_users_read_from_notd_queue" {
  group = aws_iam_group.notd_users.name
  policy_arn = aws_iam_policy.read_from_notd_queue.arn
}

resource "aws_iam_group_policy_attachment" "notd_users_write_to_notd_queue" {
  group = aws_iam_group.notd_users.name
  policy_arn = aws_iam_policy.write_to_notd_queue.arn
}

resource "aws_iam_group_policy_attachment" "notd_users_read_from_notd_token_queue" {
  group = aws_iam_group.notd_users.name
  policy_arn = aws_iam_policy.read_from_notd_token_queue.arn
}

resource "aws_iam_group_policy_attachment" "notd_users_write_to_notd_token_queue" {
  group = aws_iam_group.notd_users.name
  policy_arn = aws_iam_policy.write_to_notd_token_queue.arn
}

resource "aws_iam_group_policy_attachment" "notd_users_access_ethereum_node" {
  group = aws_iam_group.notd_users.name
  policy_arn = aws_iam_policy.access_ethereum_node.arn
}

resource "aws_iam_group_policy_attachment" "notd_users_read_from_storage" {
  group = aws_iam_group.notd_users.name
  policy_arn = aws_iam_policy.read_from_storage.arn
}

resource "aws_iam_group_policy_attachment" "notd_users_write_to_storage" {
  group = aws_iam_group.notd_users.name
  policy_arn = aws_iam_policy.write_to_storage.arn
}

resource "aws_iam_group_policy_attachment" "notd_readers_read_from_storage" {
  group = aws_iam_group.notd_readers.name
  policy_arn = aws_iam_policy.read_from_storage.arn
}
