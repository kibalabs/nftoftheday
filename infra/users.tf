resource "aws_iam_group" "notd_users" {
  name = "notd-users"
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
    aws_iam_group.notd_users.name,
  ]
}

resource "aws_iam_group_policy_attachment" "notd_users_read_from_notd_queue" {
  group = aws_iam_group.notd_users.name
  policy_arn = aws_iam_policy.read_from_notd_queue.arn
}

resource "aws_iam_group_policy_attachment" "notd_users_read_from_notd_queue_dl" {
  group = aws_iam_group.notd_users.name
  policy_arn = aws_iam_policy.read_from_notd_queue_dl.arn
}

resource "aws_iam_group_policy_attachment" "notd_users_write_to_notd_queue" {
  group = aws_iam_group.notd_users.name
  policy_arn = aws_iam_policy.write_to_notd_queue.arn
}

resource "aws_iam_group_policy_attachment" "notd_users_access_ethereum_node" {
  group = aws_iam_group.notd_users.name
  policy_arn = aws_iam_policy.access_ethereum_node.arn
}
