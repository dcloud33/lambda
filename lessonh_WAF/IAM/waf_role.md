You need IAM Policy this the WAF Lambda..
this is for both parts of the lab

      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Action": [
              "logs:FilterLogEvents"
            ],
            "Resource": "*"
          },
          {
            "Effect": "Allow",
            "Action": [
              "bedrock:InvokeModel"
            ],
            "Resource": "*"
          },
          {
            "Effect": "Allow",
            "Action": [
              "dynamodb:PutItem"
            ],
            "Resource": "arn:aws:dynamodb:<region>:<account-id>:table/waf-events"
          }
        ]
      }
