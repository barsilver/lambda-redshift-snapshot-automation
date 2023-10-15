resource "aws_cloudwatch_event_rule" "redshift_snapshot_trigger" {
  name        = "redshift_snapshot_trigger"
  description = ""

  event_pattern = <<EOF
  {
    "source": ["aws.redshift"],
    "detail": {
      "eventName": ["CreateSnapshot"]
    },
    "requestParameters": {
      "snapshotType": ["serverless"]
    }
  }
  EOF
}

# Maybe sourceType instead of snapshotType.