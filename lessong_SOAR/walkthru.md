SOAR + Bedrock — AI Incident Summary Generator

Are you ready?

“We already detect unused tokens. Now we will orchestrate an automated response workflow.”

Now we build:

    Unused Token Detected
    → EventBridge Event
    → Lambda Enrichment
    → SNS Alert
    → Slack Notification
    → Optional Account Disable

AI Incident Summary Generator

Workflow

    Unused Token Detected
    → EventBridge
    → Lambda gathers details
    → Bedrock prompt generated
    → AI creates security summary
    → Send summary to Slack/SNS

Example Input

    {
      "username": "student1",
      "issued_at": "2026-05-19T20:00:00Z",
      "used": false,
      "group": "students",
      "source_ip": "1.2.3.4"
    }

Bedrock Prompt

    You are a SOC analyst assistant.
    
    Analyze this event:
    
    - User authenticated successfully
    - JWT token issued
    - Token never used within 15 minutes
    
    Provide:
    1. Severity
    2. Possible explanations
    3. Recommended analyst actions
    4. Short executive summary

Example Output

    Severity: Low-Medium
    
    Possible Causes:
    - User confusion
    - Automation failure
    - Credential testing activity
    
    Recommended Actions:
    - Verify repeated occurrence
    - Correlate source IP activity
    - Check for abnormal authentication patterns
    
    Executive Summary:
    A Cognito-authenticated user generated a token but did not interact with protected APIs within the expected timeframe.

What is your goal here?

You Demonstrate:

    AI enrichment
    prompt engineering
    event summarization
    SOC augmentation

WITHOUT:

    dangerous automation
    hallucination risks controlling systems

Hey... isn't this why you are in the class in the first place? Besides wanting selfies with Chewbacca?

LAB Objective

When the SOAR workflow detects:

        JWT token issued
        BUT
        never used

the system will:

    Gather event details
    Send the event to Amazon Bedrock
    Generate:
        incident summary
        severity estimate
        possible causes
        analyst recommendations

REMEMBER---> “AI is not making security decisions. AI is assisting analysts with interpretation.”
Don't perform stupid AI SOC decisions!!!

“Humans perform judgment. AI reduces repetitive cognitive load.”---> that's why you still have a job!

New Workflow

        Unused Token Detected
        → Detector Lambda
        → Bedrock Prompt
        → AI Incident Summary
        → CloudWatch / SNS / Slack

What Bedrock Adds

Without Bedrock: ALERT: unused token

Who cares right?

With Bedrock:

        Severity: Low-Medium
        
        Possible Causes:
        - User confusion
        - Automation failure
        - Credential testing behavior
        
        Recommended Actions:
        - Check repeated occurrence
        - Verify source IP activity
        - Review failed login attempts


Why is this dope???

you can  immediately see:

        ✔ AI can summarize
        ✔ AI can explain
        ✔ AI can assist analysts
        ✔ AI works WITH workflows

None of this “AI does security magically” BS 

SpeechOPS: “Bedrock is helping interpret telemetry. It is not replacing human operators.”

Phase 1 — Enable Bedrock Model Access

Navigation

        AWS Console
        Bedrock
        Model Access

Enable:

Recommended:

        ✔ Anthropic Claude (Feel the Dark Side)
        OR
        ✔ Meta Llama

We are doing Claude---> Claude Sonnet

Why:

        cleaner summaries
        easier prompting
        better SOC-style output
        Malgus approves

Phase 2 — Modify Detector Lambda

Now the Lambda becomes:

        detector
        AI enrichment engine

New Flow Inside Lambda

        Unused token found
        → build prompt
        → call Bedrock
        → receive AI analysis
        → print / send alert

Example Bedrock Prompt

        prompt = f"""
        You are a SOC analyst assistant.
        
        Analyze this event:
        
        - User: {username}
        - JWT token issued
        - Token never used within 15 minutes
        - User group: {group}
        
        Provide:
        1. Severity
        2. Possible explanations
        3. Recommended analyst actions
        4. Executive summary
        
        """

Phase 3 — Call Bedrock

First, modify Lambda IAM Role
Add to Lambda role:


        {
          "Effect": "Allow",
          "Action": [
            "bedrock:InvokeModel"
          ],
          "Resource": "*"
        }

Example (Claude)
Moodify Lambda unused-token-detector.py

        #Python
        import boto3
        import json
        
        bedrock = boto3.client("bedrock-runtime")
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-v2",
            body=json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 300
            })
        )

Phase 4 — Parse AI Output

Example Result

        Severity: Low-Medium
        
        Possible Causes:
        - User confusion
        - Token abandonment
        - Automation issue
        
        Recommended Actions:
        - Review repeated behavior
        - Correlate source IP
        - Monitor future activity
        
        Executive Summary:
        A Cognito-authenticated user generated a JWT token but did not access protected APIs within the expected timeframe.

Phase 5 — Generate Alert

Initially:

        CloudWatch logs

Later:

        SNS
        Slack
        Jira

Now you see....

| Service     | Role            |
| ----------- | --------------- |
| Cognito     | identity        |
| DynamoDB    | telemetry state |
| EventBridge | orchestration   |
| Lambda      | automation      |
| Bedrock     | AI enrichment   |

