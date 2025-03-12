# AWS Bedrock Support Helper

This guide explains how to use the AWS MCP tools to gather metrics and information needed for AWS Bedrock support tickets, particularly for quota increase requests.

## Table of Contents
1. [Collecting Required Information](#collecting-required-information)
2. [Using the Tools](#using-the-tools)
3. [Example Usage](#example-usage)
4. [Understanding the Results](#understanding-the-results)

## Collecting Required Information

When requesting a quota increase for AWS Bedrock, you need to provide the following information:

1. Detailed description of the use case
2. Model ID
3. Region
4. Limit type (RPM and/or TPM)
5. Requested TPM (tokens per minute) for Steady-state and Peak
6. Requested RPM (requests per minute) for Steady-state and Peak
7. Average input tokens per request
8. Average output tokens per request
9. Percentage of requests with input tokens greater than 25k

## Using the Tools

### 1. Getting Model Statistics
Use `bedrock_get_model_stats` to get comprehensive usage statistics:

```python
{
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
    "region": "us-west-2",
    "start_time": "2024-03-11T00:00:00Z",  # Optional
    "end_time": "2024-03-12T00:00:00Z"     # Optional
}
```

This provides:
- Invocation counts
- Latency metrics
- Token usage patterns
- Error rates

### 2. Analyzing Request Patterns
Use `bedrock_analyze_requests` for detailed request analysis:

```python
{
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
    "region": "us-west-2",
    "time_period_hours": 24  # Analyze last 24 hours
}
```

This gives you:
- Total requests and token counts
- Average tokens per request (input and output)
- Request distribution over time

### 3. Getting Token Metrics
Use `bedrock_get_token_metrics` for TPM and RPM analysis:

```python
{
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
    "region": "us-west-2",
    "period": 60  # Analysis period in minutes
}
```

This provides:
- Tokens per minute (TPM) metrics
  - Average TPM
  - Peak TPM
  - Time series data
- Requests per minute (RPM) metrics
  - Average RPM
  - Peak RPM
  - Time series data

## Example Usage

Here's a complete example of gathering all necessary information for a support ticket:

1. First, get basic model statistics:
```python
await use_mcp_tool("aws", "bedrock_get_model_stats", {
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
    "region": "us-west-2"
})
```

2. Then analyze request patterns:
```python
await use_mcp_tool("aws", "bedrock_analyze_requests", {
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
    "region": "us-west-2",
    "time_period_hours": 24
})
```

3. Finally, get detailed token metrics:
```python
await use_mcp_tool("aws", "bedrock_get_token_metrics", {
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
    "region": "us-west-2",
    "period": 1440  # 24 hours in minutes
})
```

## Understanding the Results

### Model Statistics
The `bedrock_get_model_stats` response includes:
```json
{
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
    "time_range": {
        "start": "2024-03-11T00:00:00Z",
        "end": "2024-03-12T00:00:00Z"
    },
    "metrics": {
        "invocations": [...],
        "latency": [...],
        "input_tokens": [...],
        "output_tokens": [...]
    }
}
```

### Request Analysis
The `bedrock_analyze_requests` response includes:
```json
{
    "statistics": {
        "total_requests": 1000,
        "total_input_tokens": 50000,
        "total_output_tokens": 30000,
        "average_input_tokens_per_request": 50,
        "average_output_tokens_per_request": 30
    }
}
```

### Token Metrics
The `bedrock_get_token_metrics` response includes:
```json
{
    "tokens_per_minute": {
        "average": 1000,
        "peak": 2000,
        "data_points": [...]
    },
    "requests_per_minute": {
        "average": 20,
        "peak": 40,
        "data_points": [...]
    }
}
```

Use these metrics to fill out your support ticket request, providing concrete data to justify your quota increase needs.

## Bedrock Model Invocation Logging

Model invocation logging has been enabled to collect detailed metrics and logs for all Bedrock model invocations. The logs are stored in both CloudWatch and S3.

### S3 Logging Configuration

Two S3 buckets have been configured for comprehensive Bedrock logging:

#### 1. Standard Logging Bucket
- **Name**: `bedrock-logs-mcp`
- **Region**: `us-west-2`
- **Purpose**: Standard model invocation logs and metadata
- **Content Size Limit**: Up to 100KB per entry
- **Log Types**:
  - Model invocations (small payloads)
  - Metadata
  - Request headers
  - Response status
  - Performance metrics

#### 2. Large Data Bucket
- **Name**: `bedrock-large-data-mcp`
- **Region**: `us-west-2`
- **Purpose**: Storage for large payloads and binary data
- **Use Cases**:
  - Model inputs exceeding 100KB
  - Large response payloads
  - Binary content (images, documents)
  - High-token-count responses

> **Note**: The system automatically routes data to the appropriate bucket based on size and content type. References to large data entries are maintained in the standard logs for correlation.

### Automated Metrics Collection

The following metrics are automatically collected and can be used in support tickets:

#### CloudWatch Metrics
- Invocation counts (per minute, hour, day)
- Token usage (input and output)
- Latency percentiles (p50, p90, p99)
- Error rates and throttling events
- Cross-region performance metrics

#### S3 Log Analytics
- Large payload frequencies
- Binary content distribution
- High-token request patterns
- Cross-region request patterns

### Storage Management

#### Lifecycle Policies
Both buckets are configured with lifecycle policies to manage storage costs:

1. **Standard Logs Bucket** (`bedrock-logs-mcp`):
   - Logs are kept for 30 days in standard storage
   - After 30 days, logs are automatically deleted

2. **Large Data Bucket** (`bedrock-large-data-mcp`):
   - Data is kept for 30 days in standard storage
   - After 30 days, data is moved to Glacier storage
   - After 90 days, data is automatically deleted

To retrieve historical data older than 30 days, use:
```python
# For data in Glacier storage
await use_mcp_tool("aws", "s3_restore_object", {
    "bucket_name": "bedrock-large-data-mcp",
    "object_key": "path/to/archived/data",
    "days": 7  # Number of days to keep restored copy available
})
```

### Required Permissions
Ensure the following permissions are set for Bedrock logging:

1. **Bucket Policy**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockLoggingPermissions",
            "Effect": "Allow",
            "Principal": {
                "Service": "bedrock.amazonaws.com"
            },
            "Action": [
                "s3:PutObject",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::bedrock-logs-mcp",
                "arn:aws:s3:::bedrock-logs-mcp/*"
            ]
        }
    ]
}
```

2. **Required IAM Role Permissions**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::bedrock-logs-mcp",
                "arn:aws:s3:::bedrock-logs-mcp/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:us-west-2:*:log-group:/aws/bedrock/*"
        }
    ]
}
```

### Log Structure and Analysis

#### Cross-Bucket Log Analysis
When analyzing Bedrock model invocations that involve large data:

1. **Finding Related Entries**:
```python
# First, get the standard log entry
await use_mcp_tool("aws", "cloudwatch_get_logs", {
    "log_group_name": "/aws/bedrock/model-invocation",
    "filter_pattern": "requestId: your-request-id"
})

# Then retrieve the associated large data using the reference
await use_mcp_tool("aws", "s3_object_read", {
    "bucket_name": "bedrock-large-data-mcp",
    "object_key": "YYYY/MM/DD/requestId/payload.json"
})
```

2. **Bulk Analysis Pattern**:
```python
# List all large data entries for a specific date
await use_mcp_tool("aws", "s3_object_list", {
    "bucket_name": "bedrock-large-data-mcp",
    "prefix": datetime.now().strftime("%Y/%m/%d")
})
```

#### Log Organization
Logs are organized in the following structure:
```
bedrock-logs-mcp/
├── YYYY/MM/DD/HH/
│   ├── model-invocations/
│   │   └── [request-id]-invocation.json
│   ├── metadata/
│   │   └── [request-id]-metadata.json
│   ├── requests/
│   │   └── [request-id]-request.json
│   └── responses/
│       └── [request-id]-response.json
```

#### Key Metrics Collection
1. **Real-time Metrics (CloudWatch)**:
   - Invocation rates (RPM)
   - Token usage (TPM)
   - Error rates and throttling events
   - Latency statistics

2. **Detailed Analysis (S3 Logs)**:
   - Input/output token counts per request
   - Request payload sizes
   - Response characteristics
   - Error details and stack traces

#### Log Retention
- S3 logs: 30 days retention
- CloudWatch logs: Configurable retention period
- CloudWatch metrics: 15 months retention

### Accessing the Logs
1. **S3 Logs**: Use the AWS MCP tools to access logs in the S3 bucket:
```python
await use_mcp_tool("aws", "s3_object_list", {
    "bucket_name": "bedrock-logs-mcp"
})
```

2. **CloudWatch Logs**: Use the CloudWatch tools to query logs:
```python
await use_mcp_tool("aws", "cloudwatch_get_logs", {
    "log_group_name": "/aws/bedrock/model-invocation",
    "filter_pattern": "your_filter_here"
})
```

## Tips for Support Tickets

1. Use the metrics from `bedrock_get_token_metrics` to determine your current usage patterns and justify your requested TPM/RPM increases.

2. Include model invocation logs from both S3 and CloudWatch to provide detailed evidence of:
   - Token usage patterns
   - Request frequency
   - Error rates
   - Throttling events

2. Use `bedrock_analyze_requests` data to show your average token usage and justify any increases needed for handling larger context windows.

3. If you're experiencing throttling or rate limits, the error rates from `bedrock_get_model_stats` can help demonstrate the impact on your workload.

4. When specifying time ranges, try to capture both typical usage (steady-state) and high-load periods (peak) to provide a complete picture of your needs.