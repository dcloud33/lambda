import boto3
import json
import os
import time
import uuid
from datetime import datetime, timedelta, timezone

# for the second part of the lab
dynamodb = boto3.resource("dynamodb")
#table = dynamodb.Table("waf-events")
DYNAMODB_TABLE = os.environ["DYNAMODB_TABLE"]
table = dynamodb.Table(DYNAMODB_TABLE)

logs = boto3.client("logs")
bedrock = boto3.client("bedrock-runtime")

WAF_LOG_GROUP = os.environ["WAF_LOG_GROUP"]
MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID",
    "anthropic.claude-3-haiku-20240307-v1:0"
)
LOOKBACK_MINUTES = int(os.environ.get("LOOKBACK_MINUTES", "10"))


def get_recent_waf_events():
    end_time = int(time.time() * 1000)
    start_time = int(
        (datetime.now(timezone.utc) - timedelta(minutes=LOOKBACK_MINUTES)).timestamp() * 1000
    )

    response = logs.filter_log_events(
        logGroupName=WAF_LOG_GROUP,
        startTime=start_time,
        endTime=end_time,
        limit=10
    )

    events = []

    for event in response.get("events", []):
        try:
            waf_event = json.loads(event["message"])
            events.append(waf_event)
        except json.JSONDecodeError:
            print("Skipping non-JSON log event")

    return events


def summarize_waf_event(waf_event):
    http_request = waf_event.get("httpRequest", {})

    summary = {
        "timestamp": waf_event.get("timestamp"),
        "action": waf_event.get("action"),
        "terminating_rule_id": waf_event.get("terminatingRuleId"),
        "terminating_rule_type": waf_event.get("terminatingRuleType"),
        "client_ip": http_request.get("clientIp"),
        "country": http_request.get("country"),
        "method": http_request.get("httpMethod"),
        "uri": http_request.get("uri"),
        "args": http_request.get("args"),
        "headers": http_request.get("headers", [])[:5]
    }

    return summary


    
def call_bedrock(waf_summary):
    prompt = f"""
You are a SOC analyst assistant.

Analyze the following AWS WAF event.

Event:
{json.dumps(waf_summary, indent=2)}

Return the answer in this format:

Severity:
Possible Attack Type:
Why This Was Flagged:
Recommended Analyst Actions:
Short Executive Summary:

Keep the answer concise and practical.
"""

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    print("Invoking Bedrock...")
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body)
    )

    response_body = json.loads(response["body"].read())
    return response_body["content"][0]["text"]
    
    print("Bedrock invocation successful")
    
# For the second part of the lab

def save_to_dynamodb(waf_summary):
    print(f"Saving WAF event for IP {waf_summary.get('client_ip')}") 
    table.put_item(
        Item={
            "event_id": str(uuid.uuid4()),
            "timestamp": str(waf_summary.get("timestamp")),
            "source_ip": waf_summary.get("client_ip"),
            "country": waf_summary.get("country"),
            "uri": waf_summary.get("uri"),
            "method": waf_summary.get("method"),
            "action": waf_summary.get("action"),
            "rule": waf_summary.get("terminating_rule_id")
        }
    )

     print("Successfully saved event to DynamoDB")
    
def lambda_handler(event, context):
    print("Starting WAF Bedrock analyzer")

    waf_events = get_recent_waf_events()

    if not waf_events:
        print("No recent WAF events found")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "No recent WAF events found"})
        }

    for waf_event in waf_events:

        if "httpRequest" not in waf_event:
            print("Malformed WAF record")
            continue
            
        waf_summary = summarize_waf_event(waf_event)

        print("Structured WAF Event:")
        print(json.dumps(waf_summary, indent=2))
        save_to_dynamodb(waf_summary)
    try:
        
        ai_summary = call_bedrock(waf_summary)

        print("\n===== BEDROCK SOC SUMMARY =====")
        print(ai_summary)
        print("================================\n")

    except Exception as e:
        print(f"Bedrock error: {e}")
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "WAF events analyzed",
            "events_analyzed": len(waf_events)
        })
    }
