resource "aws_cloudwatch_event_rule" "redshift_snapshot_trigger" {
  name        = "redshift_snapshot_trigger"
  description = "Triggers Lambda when a Redshift serverless snapshot is created."

  event_pattern = <<EOF
  {
    "source": ["redshift-serverless.amazonaws.com"],
    "detail": {
      "eventName": ["CreateSnapshot"]
    }
  }
  EOF
}

# Maybe sourceType instead of snapshotType.