# AWS MCP Server

[![smithery badge](https://smithery.ai/badge/mcp-server-aws)](https://smithery.ai/server/mcp-server-aws)

A [Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) server implementation for AWS operations that supports S3, DynamoDB, EC2, Lambda, CloudWatch, and Bedrock services. All operations are automatically logged and can be accessed through the `audit://aws-operations` resource endpoint. Features comprehensive logging support for Bedrock model invocations with both standard and large data handling capabilities.

See a demo video [here](https://www.loom.com/share/99551eeb2e514e7eaf29168c47f297d1?sid=4eb54324-5546-4f44-99a0-947f80b9365c).

Listed as a [Community Server](https://github.com/modelcontextprotocol/servers?tab=readme-ov-file#-community-servers) within the MCP servers repository.

## Running locally with the Claude desktop app

### Installing via Smithery

To install AWS MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/mcp-server-aws):

```bash
npx -y @smithery/cli install mcp-server-aws --client claude
```

### Manual Installation
1. Clone this repository.
2. Set up your AWS credentials via one of the two methods below. Note that this server requires an IAM user with appropriate permissions for:
   - S3 (read/write)
   - DynamoDB (read/write)
   - EC2 (describe, start, stop instances)
   - Lambda (invoke, list, get functions)
   - CloudWatch (get metrics, list metrics, get logs)
   - Bedrock (invoke models, get metrics)
   Additionally, for Bedrock logging:
   - S3 permissions for `bedrock-logs-mcp` and `bedrock-large-data-mcp` buckets
   - CloudWatch Logs permissions for `/aws/bedrock/*` log groups
- Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` (defaults to `us-east-1`)
- Default AWS credential chain (set up via AWS CLI with `aws configure`)
3. Add the following to your `claude_desktop_config.json` file:
- On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
- On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```
"mcpServers": {
  "mcp-server-aws": {
    "command": "uv",
    "args": [
      "--directory",
      "/path/to/repo/mcp-server-aws",
      "run",
      "mcp-server-aws"
    ]
  }
}
```
4. Install and open the [Claude desktop app](https://claude.ai/download).
5. Try asking Claude to do a read/write operation of some sort to confirm the setup (e.g. create an S3 bucket and give it a random name). If there are issues, use the Debugging tools provided in the MCP documentation [here](https://modelcontextprotocol.io/docs/tools/debugging).

## Available Tools

### Bedrock Operations
- **bedrock_get_model_stats**: Get detailed usage statistics for a Bedrock model, including invocations, token counts, and latency metrics
- **bedrock_analyze_requests**: Analyze Bedrock API requests to get detailed token statistics, including:
  - Average input/output tokens per request
  - Total requests and token counts
  - Request patterns over time
- **bedrock_get_token_metrics**: Get detailed TPM (tokens per minute) and RPM (requests per minute) metrics with peak and average values

### Bedrock Operations

#### Model Logging
- **bedrock_get_model_stats**: Get detailed model invocation statistics
- **bedrock_analyze_requests**: Analyze token usage and request patterns
- **bedrock_get_token_metrics**: Get TPM and RPM metrics

#### Log Storage Locations
- **Standard Logs**: `bedrock-logs-mcp` (us-west-2)
- **Large Data**: `bedrock-large-data-mcp` (us-west-2)

See [support-help.md](support-help.md) for detailed information about Bedrock logging configuration and analysis.

### S3 Operations

- **s3_bucket_create**: Create a new S3 bucket
- **s3_bucket_list**: List all S3 buckets
- **s3_bucket_delete**: Delete an S3 bucket
- **s3_object_upload**: Upload an object to S3
- **s3_object_delete**: Delete an object from S3
- **s3_object_list**: List objects in an S3 bucket
- **s3_object_read**: Read an object's content from S3


### DynamoDB Operations

#### Table Operations
- **dynamodb_table_create**: Create a new DynamoDB table
- **dynamodb_table_describe**: Get details about a DynamoDB table
- **dynamodb_table_delete**: Delete a DynamoDB table
- **dynamodb_table_update**: Update a DynamoDB table

#### Item Operations
- **dynamodb_item_put**: Put an item into a DynamoDB table
- **dynamodb_item_get**: Get an item from a DynamoDB table
- **dynamodb_item_update**: Update an item in a DynamoDB table
- **dynamodb_item_delete**: Delete an item from a DynamoDB table
- **dynamodb_item_query**: Query items in a DynamoDB table
- **dynamodb_item_scan**: Scan items in a DynamoDB table
#### Batch Operations
- **dynamodb_batch_get**: Batch get multiple items from DynamoDB tables
- **dynamodb_item_batch_write**: Batch write operations (put/delete) for DynamoDB items
- **dynamodb_batch_execute**: Execute multiple PartiQL statements in a batch

#### TTL Operations
- **dynamodb_describe_ttl**: Get the TTL settings for a table
- **dynamodb_update_ttl**: Update the TTL settings for a table

### EC2 Operations
- **ec2_list_instances**: List EC2 instances and their details with optional filters
- **ec2_start_instances**: Start one or more EC2 instances
- **ec2_stop_instances**: Stop one or more EC2 instances
- **ec2_describe_instance**: Get detailed information about an EC2 instance

### Lambda Operations
- **lambda_list_functions**: List all Lambda functions
- **lambda_invoke**: Invoke a Lambda function with custom payload
- **lambda_get_function**: Get detailed information about a Lambda function

### CloudWatch Operations
#### Metrics
- **cloudwatch_get_metrics**: Get CloudWatch metrics for a resource
- **cloudwatch_list_metrics**: List available CloudWatch metrics

#### Logs
- **cloudwatch_get_logs**: Get CloudWatch logs from a log group with optional filtering
