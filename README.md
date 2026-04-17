# Aws-Cost-Calculator
AWS Serverless Cost Guardian 🛡️
A production-grade FinOps automation tool that monitors AWS spending, identifies cost anomalies using Python, and implements a robust "fail-safe" architecture.

📖 Project Overview
Managing cloud costs isn't just about setting budgets; it's about observability. This project automates the manual task of tracking expenditures and uses custom logic to flag spending spikes before they become financial liabilities.

The system is designed with a "Zero-Loss" mentality—if the monitoring fails, the system alerts the administrator via a Dead Letter Queue (DLQ), ensuring the "watcher" is always being watched.

🚀 Key Engineering Features
Intelligent Anomaly Detection: Custom Python logic that calculates week-over-week variance. It triggers alerts only when spending exceeds a 25% threshold, preventing "alert fatigue."

Fault-Tolerant Architecture: Implemented an Asynchronous SQS Dead Letter Queue (DLQ). Any failed Lambda invocations are preserved for replay and trigger a high-priority CloudWatch alarm.

Secure Configuration: Decoupled infrastructure from code using Lambda Environment Variables, ensuring no sensitive ARNs or bucket names are hardcoded.

Least-Privilege Security: A custom IAM policy restricts the Lambda to specific resource ARNs, adhering to the AWS Well-Architected Framework.

🛠️ Tech Stack
Compute: AWS Lambda (Python 3.x)

Storage: Amazon S3 (JSON Report Archive)

Monitoring: Amazon CloudWatch (Alarms & Metrics)

Orchestration: Amazon EventBridge (Weekly Cron Schedule)

Messaging: Amazon SNS (Alerts) & Amazon SQS (DLQ)

✅ Implementation Proof
1. Execution Success

The Lambda function successfully processes cost data and evaluates anomalies.

2. Automated Archiving

Reports are stored in S3 as timestamped JSON objects for long-term auditing.

3. Secure Environment Configuration

Infrastructure secrets are managed via encrypted environment variables.

⚙️ Manual Setup & Deployment
This project was deployed via the AWS Management Console to master service integrations.

S3 Bucket: Create a bucket (e.g., weekly-cost-report-storage-yogesh) and enable "Block all public access."

SNS Topic: Create a Standard Topic BillingAlerts and subscribe your email.

SQS Queue: Create a queue CostReporter-DLQ to act as the failure destination.

IAM Role: Create a Lambda execution role with the policy found in /iam/lambda-policy.json.

Lambda Function:

Runtime: Python 3.12+

Timeout: 30 seconds

Dead Letter Queue: Set to the SQS queue created in Step 3.

Environment Variables: Add S3_BUCKET_NAME and SNS_TOPIC_ARN.

EventBridge: Set a "Schedule" type trigger for cron(0 9 ? * MON *).
