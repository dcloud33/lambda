
WAF LAB A

Let's work on WAF.

1. WAF logs are already going to CloudWatch.
2. A Lambda reads the last few minutes of WAF log events.
3. Lambda extracts:

    source IP
    country
    URI
    HTTP method
    WAF action
    terminating rule
    
4. Lambda sends those details to Bedrock.
5. Bedrock returns a SOC-style summary.
6. Lambda prints the summary to CloudWatch.

No DynamoDB yet. No EventBridge yet. First, prove Bedrock can analyze the WAF event.

Required IAM permissions

The Lambda execution role needs:

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
            }
          ]
        }


Lambda environment variables

Use these:

WAF_LOG_GROUP=/aws/waf/chewbacca-waf
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
LOOKBACK_MINUTES=10

WAF Lambda---> Make this: Python Lambda: waf_bedrock_analyzer.py
HERE--->>>> https://github.com/BalericaAI/lambda/blob/main/lessonh_WAF/python/waf_bedrock_analyzer.py

Test flow
1. Generate a WAF event: Use the API endpoint and send something suspicious:

        curl "https://<api-id>.execute-api.<region>.amazonaws.com/prod/python?name=<script>alert(1)</script>"

Expected result: 403 Forbidden

2. Invoke the analyzer Lambda --> Run it manually first from Lambda Console:
3. Check analyzer logs ---> Go to: CloudWatch Logs → /aws/lambda/waf-bedrock-analyzer

Expected output:

        Structured WAF Event:
        {
          "action": "BLOCK",
          "client_ip": "...",
          "uri": "/prod/python",
          "terminating_rule_id": "..."
        }
        
        ===== BEDROCK SOC SUMMARY =====
        Severity:
        Possible Attack Type:
        Why This Was Flagged:
        Recommended Analyst Actions:
        Short Executive Summary:




WAF LAB B WAF Telemetry Database

Objective

Store WAF security events in DynamoDB so they can later be:

        searched
        correlated
        enriched
        analyzed by Bedrock
        used for SOAR workflows

Concept

CloudWatch Logs are excellent for:

        troubleshooting
        operational visibility

But terrible for:

        correlation
        analytics
        threat history


From Lab A we have: Current State---> WAF Event → CloudWatch 

New State

        WAF Event
        → CloudWatch Log
        → Lambda Parser
        → DynamoDB

Why We Need DynamoDB

Imagine: IP 1.2.3.4 hits your API: 
Monday: XSS attempt
Tuesday:  SQL Injection
Wednesday: Credential stuffing
Thursday: Lizzo Injection

CloudWatch sees individual events.

DynamoDB lets us build: ---> Attack History

DynamoDB Table Design

You need a new Table: waf-events
Partition Key:  event_id
Type: String

How your record should look in JSON

        {
          "event_id": "123456",
          "timestamp": "2026-06-23T18:00:00Z",
          "source_ip": "1.2.3.4",
          "country": "RU",
          "uri": "/python",
          "method": "GET",
          "action": "BLOCK",
          "rule": "AWSManagedRulesCommonRuleSet"
        }

Lambda Enhancement

Currently: print(ai_summary)
Now: table.put_item(...)












