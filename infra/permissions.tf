resource "aws_iam_policy" "read_from_notd_queue" {
  name = "read-queue-${aws_sqs_queue.notd_work_queue.name}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
        Effect = "Allow"
        Action = [
            "sqs:GetQueueUrl",
            "sqs:GetQueueAttributes",
            "sqs:ReceiveMessage",
            "sqs:ChangeMessageVisibility",
            "sqs:ChangeMessageVisibilityBatch",
            "sqs:DeleteMessage",
            "sqs:DeleteMessageBatch",
        ]
        Resource = aws_sqs_queue.notd_work_queue.arn
    }]
  })
}

resource "aws_iam_policy" "write_to_notd_queue" {
  name = "write-queue-${aws_sqs_queue.notd_work_queue.name}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
        Effect = "Allow"
        Action = [
            "sqs:GetQueueUrl",
            "sqs:GetQueueAttributes",
            "sqs:SendMessage",
            "sqs:SendMessageBatch",
        ]
        Resource = aws_sqs_queue.notd_work_queue.arn
    }]
  })
}
