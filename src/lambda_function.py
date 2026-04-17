import boto3
import os
import json
from datetime import datetime, timedelta

def lambda_handler(event, context):
    ce = boto3.client('ce')
    sns = boto3.client('sns')
    s3 = boto3.client('s3')
    
    # 1. Get Environment Variables (Set these in the Configuration tab!)
    topic_arn = os.environ.get('SNS_TOPIC_ARN')
    bucket_name = os.environ.get('S3_BUCKET_NAME')

    # 2. Define Time Ranges
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    seven_days_ago = (now - timedelta(days=7)).strftime('%Y-%m-%d')
    fourteen_days_ago = (now - timedelta(days=14)).strftime('%Y-%m-%d')

    # Helper function to get cost data
    def get_cost_sum(start, end):
        results = ce.get_cost_and_usage(
            TimePeriod={'Start': start, 'End': end},
            Granularity='DAILY',
            Metrics=['UnblendedCost']
        )
        return sum(float(day['Total']['UnblendedCost']['Amount']) for day in results['ResultsByTime'])

    # 3. Calculate Current vs. Previous Week
    try:
        current_week_cost = get_cost_sum(seven_days_ago, today)
        previous_week_cost = get_cost_sum(fourteen_days_ago, seven_days_ago)
    except Exception as e:
        print(f"Error fetching cost data: {e}")
        return {'statusCode': 500, 'body': str(e)}

    # 4. Anomaly Logic (25% increase and spend > $1.00)
    is_anomaly = False
    if previous_week_cost > 0:
        if current_week_cost > (previous_week_cost * 1.25) and current_week_cost > 1.0:
            is_anomaly = True

    # 5. Send Alert if Anomaly Found
    if is_anomaly:
        sns.publish(
            TopicArn=topic_arn,
            Subject="⚠️ AWS COST ANOMALY DETECTED",
            Message=(f"Significant cost increase detected!\n\n"
                     f"This Week: ${current_week_cost:.2f}\n"
                     f"Last Week: ${previous_week_cost:.2f}\n"
                     f"Increase: {((current_week_cost/previous_week_cost)-1)*100:.1f}%")
        )

    # 6. Save JSON Report to S3 for Audit Trail
    report = {
        "date": today,
        "current_week_total": current_week_cost,
        "previous_week_total": previous_week_cost,
        "anomaly_detected": is_anomaly
    }
    
    s3.put_object(
        Bucket=bucket_name,
        Key=f"cost-reports/{today}-report.json",
        Body=json.dumps(report)
    )

    return {
        'statusCode': 200,
        'body': json.dumps(f"Process complete. Anomaly: {is_anomaly}")
    }