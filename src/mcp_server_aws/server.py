import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence
from functools import lru_cache
import base64
import io
import boto3
import asyncio
from dotenv import load_dotenv
import mcp.server.stdio
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import AnyUrl
from .tools import get_aws_tools
from .utils import get_dynamodb_type

# Configure root logger and all other loggers to WARNING
logging.basicConfig(level=logging.WARNING)
for logger_name in logging.root.manager.loggerDict:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

# Configure our specific logger
logger = logging.getLogger("aws-mcp-server")
logger.setLevel(logging.WARNING)

def custom_json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

class AWSManager:
    def __init__(self):
        self.audit_entries: list[dict] = []

    @lru_cache(maxsize=None)
    def get_boto3_client(self, service_name: str, region_name: str = None):
        """Get a boto3 client using explicit credentials if available"""
        try:
            region_name = region_name or os.getenv("AWS_REGION", "us-east-1")
            if not region_name:
                raise ValueError(
                    "AWS region is not specified and not set in the environment.")

            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

            if aws_access_key and aws_secret_key:
                logger.debug("Using explicit AWS credentials")
                session = boto3.Session(
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=region_name
                )
            else:
                logger.debug("Using default AWS credential chain")
                session = boto3.Session(region_name=region_name)

            return session.client(service_name)
        except Exception as e:
            logger.error(f"Failed to create boto3 client for {service_name}: {e}")
            raise RuntimeError(f"Failed to create boto3 client: {e}")

    def _synthesize_audit_log(self) -> str:
        """Generate formatted audit log from entries"""
        if not self.audit_entries:
            return "No AWS operations have been performed yet."

        report = "📋 AWS Operations Audit Log 📋\n\n"
        for entry in self.audit_entries:
            report += f"[{entry['timestamp']}]\n"
            report += f"Service: {entry['service']}\n"
            report += f"Operation: {entry['operation']}\n"
            report += f"Parameters: {json.dumps(entry['parameters'], indent=2)}\n"
            report += "-" * 50 + "\n"

        return report

    def log_operation(self, service: str, operation: str, parameters: dict) -> None:
        """Log an AWS operation to the audit log"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": service,
            "operation": operation,
            "parameters": parameters
        }
        self.audit_entries.append(audit_entry)

def _get_server():
    aws = AWSManager()
    server = Server("aws-mcp-server")

    @server.list_resources()
    async def handle_list_resources() -> list[Resource]:
        return [
            Resource(
                uri=AnyUrl("audit://aws-operations"),
                name="AWS Operations Audit Log",
                description="A log of all AWS operations performed through this server",
                mimeType="text/plain",
            )
        ]

    @server.read_resource()
    async def handle_read_resource(uri: AnyUrl) -> str:
        if uri.scheme != "audit":
            logger.error(f"Unsupported URI scheme: {uri.scheme}")
            raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

        path = str(uri).replace("audit://", "")
        if path != "aws-operations":
            logger.error(f"Unknown resource path: {path}")
            raise ValueError(f"Unknown resource path: {path}")

        return aws._synthesize_audit_log()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available AWS tools"""
        return get_aws_tools()

    async def handle_s3_operations(aws: AWSManager, name: str, arguments: dict) -> list[TextContent]:
        """Handle S3-specific operations"""
        s3_client = aws.get_boto3_client('s3', region_name=arguments.get("region"))
        response = None

        if name == "s3_bucket_create":
            import subprocess
            bucket_name = arguments["bucket_name"]
            region = arguments.get("region")
            
            # Use AWS CLI by default for bucket creation
            cli_command = ["aws", "s3api", "create-bucket", "--bucket", bucket_name]
            if region:
                cli_command.extend(["--region", region])
                if region != 'us-east-1':
                    cli_command.extend(["--create-bucket-configuration", f"LocationConstraint={region}"])
            
            try:
                cli_result = subprocess.run(cli_command, capture_output=True, text=True, check=True)
                response = json.loads(cli_result.stdout)
                logger.info(f"Successfully created bucket using AWS CLI: {bucket_name}")
            except subprocess.CalledProcessError as e:
                logger.error(f"AWS CLI bucket creation failed: {e.stderr}")
                raise RuntimeError(f"Failed to create bucket: {e.stderr}")
        elif name == "s3_bucket_list":
            response = s3_client.list_buckets()
        elif name == "s3_bucket_delete":
            response = s3_client.delete_bucket(Bucket=arguments["bucket_name"])
        elif name == "s3_object_upload":
            import subprocess, tempfile
            bucket_name = arguments["bucket_name"]
            object_key = arguments["object_key"]
            content = base64.b64decode(arguments["file_content"])
            
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            try:
                cli_command = [
                    "aws", "s3api", "put-object",
                    "--bucket", bucket_name,
                    "--key", object_key,
                    "--body", tmp_path
                ]
                cli_result = subprocess.run(cli_command, capture_output=True, text=True, check=True)
                response = json.loads(cli_result.stdout) if cli_result.stdout else {"Status": "Success"}
            finally:
                os.unlink(tmp_path)
                
        elif name == "s3_object_delete":
            import subprocess
            cli_command = [
                "aws", "s3api", "delete-object",
                "--bucket", arguments["bucket_name"],
                "--key", arguments["object_key"]
            ]
            cli_result = subprocess.run(cli_command, capture_output=True, text=True, check=True)
            response = json.loads(cli_result.stdout) if cli_result.stdout else {"Status": "Success"}
            
        elif name == "s3_object_list":
            import subprocess
            cli_command = [
                "aws", "s3api", "list-objects-v2",
                "--bucket", arguments["bucket_name"]
            ]
            cli_result = subprocess.run(cli_command, capture_output=True, text=True, check=True)
            response = json.loads(cli_result.stdout)
            
        elif name == "s3_object_read":
            import subprocess
            cli_command = [
                "aws", "s3api", "get-object",
                "--bucket", arguments["bucket_name"],
                "--key", arguments["object_key"],
                "--output", "text"
            ]
            cli_result = subprocess.run(cli_command, capture_output=True, text=True, check=True)
            content = cli_result.stdout
            return [TextContent(type="text", text=content)]
        else:
            raise ValueError(f"Unknown S3 operation: {name}")

        aws.log_operation("s3", name.replace("s3_", ""), arguments)
        return [TextContent(type="text", text=f"Operation Result:\n{json.dumps(response, indent=2, default=custom_json_serializer)}")]

    async def handle_dynamodb_operations(aws: AWSManager, name: str, arguments: dict) -> list[TextContent]:
        """Handle DynamoDB-specific operations"""
        dynamodb_client = aws.get_boto3_client('dynamodb')
        response = None

        if name == "dynamodb_table_create":
            response = dynamodb_client.create_table(
                TableName=arguments["table_name"],
                KeySchema=arguments["key_schema"],
                AttributeDefinitions=arguments["attribute_definitions"],
                BillingMode="PAY_PER_REQUEST"
            )
        elif name == "dynamodb_table_describe":
            response = dynamodb_client.describe_table(
                TableName=arguments["table_name"])
        elif name == "dynamodb_table_list":
            response = dynamodb_client.list_tables()
        elif name == "dynamodb_table_delete":
            response = dynamodb_client.delete_table(
                TableName=arguments["table_name"])
        elif name == "dynamodb_table_update":
            update_params = {
                "TableName": arguments["table_name"],
                "AttributeDefinitions": arguments["attribute_definitions"]
            }
            response = dynamodb_client.update_table(**update_params)
        elif name == "dynamodb_describe_ttl":
            response = dynamodb_client.describe_time_to_live(
                TableName=arguments["table_name"]
            )
        elif name == "dynamodb_update_ttl":
            response = dynamodb_client.update_time_to_live(
                TableName=arguments["table_name"],
                TimeToLiveSpecification={
                    'Enabled': arguments["ttl_enabled"],
                    'AttributeName': arguments["ttl_attribute"]
                }
            )
        elif name == "dynamodb_item_put":
            response = dynamodb_client.put_item(
                TableName=arguments["table_name"],
                Item=arguments["item"]
            )
        elif name == "dynamodb_item_get":
            response = dynamodb_client.get_item(
                TableName=arguments["table_name"],
                Key=arguments["key"]
            )
        elif name == "dynamodb_item_update":
            response = dynamodb_client.update_item(
                TableName=arguments["table_name"],
                Key=arguments["key"],
                AttributeUpdates=arguments["item"]
            )
        elif name == "dynamodb_item_delete":
            response = dynamodb_client.delete_item(
                TableName=arguments["table_name"],
                Key=arguments["key"]
            )
        elif name == "dynamodb_item_query":
            response = dynamodb_client.query(
                TableName=arguments["table_name"],
                KeyConditionExpression=arguments["key_condition"],
                ExpressionAttributeValues=arguments["expression_values"]
            )
        elif name == "dynamodb_item_scan":
            scan_params = {"TableName": arguments["table_name"]}

            if "filter_expression" in arguments:
                scan_params["FilterExpression"] = arguments["filter_expression"]

                if "expression_attributes" in arguments:
                    attrs = arguments["expression_attributes"]
                    if "names" in attrs:
                        scan_params["ExpressionAttributeNames"] = attrs["names"]
                    if "values" in attrs:
                        scan_params["ExpressionAttributeValues"] = attrs["values"]

            response = dynamodb_client.scan(**scan_params)
        elif name == "dynamodb_batch_get":
            response = dynamodb_client.batch_get_item(
                RequestItems=arguments["request_items"]
            )
        elif name == "dynamodb_item_batch_write":
            table_name = arguments["table_name"]
            operation = arguments["operation"]
            items = arguments["items"]

            if not items:
                raise ValueError("No items provided for batch operation")

            batch_size = 25
            total_items = len(items)
            processed_items = 0
            failed_items = []

            for i in range(0, total_items, batch_size):
                batch = items[i:i + batch_size]
                request_items = {table_name: []}

                for item in batch:
                    if operation == "put":
                        formatted_item = {k: get_dynamodb_type(
                            v) for k, v in item.items()}
                        request_items[table_name].append({
                            'PutRequest': {'Item': formatted_item}
                        })
                    elif operation == "delete":
                        key_attrs = arguments.get(
                            "key_attributes", list(item.keys()))
                        formatted_key = {k: get_dynamodb_type(
                            item[k]) for k in key_attrs}
                        request_items[table_name].append({
                            'DeleteRequest': {'Key': formatted_key}
                        })

                try:
                    response = dynamodb_client.batch_write_item(
                        RequestItems=request_items)
                    processed_items += len(batch) - len(
                        response.get('UnprocessedItems', {}).get(table_name, [])
                    )

                    unprocessed = response.get('UnprocessedItems', {})
                    retry_count = 0
                    max_retries = 3
                    while unprocessed and retry_count < max_retries:
                        await asyncio.sleep(2 ** retry_count)
                        retry_response = dynamodb_client.batch_write_item(
                            RequestItems=unprocessed)
                        unprocessed = retry_response.get('UnprocessedItems', {})
                        retry_count += 1

                    if unprocessed:
                        failed_items.extend([
                            item['PutRequest']['Item'] if 'PutRequest' in item else item['DeleteRequest']['Key']
                            for item in unprocessed.get(table_name, [])
                        ])

                except Exception as e:
                    logger.error(f"Error processing batch: {str(e)}")
                    failed_items.extend(batch)

            response = {
                "total_items": total_items,
                "processed_items": processed_items,
                "failed_items": len(failed_items),
                "failed_items_details": failed_items if failed_items else None
            }
        elif name == "dynamodb_batch_execute":
            response = dynamodb_client.batch_execute_statement(
                Statements=[{
                    'Statement': statement,
                    'Parameters': params
                } for statement, params in zip(arguments["statements"], arguments["parameters"])]
            )
        else:
            raise ValueError(f"Unknown DynamoDB operation: {name}")

        aws.log_operation("dynamodb", name.replace("dynamodb_", ""), arguments)
        return [TextContent(type="text", text=f"Operation Result:\n{json.dumps(response, indent=2, default=custom_json_serializer)}")]

    @server.call_tool()
    async def handle_ec2_operations(aws: AWSManager, name: str, arguments: dict) -> list[TextContent]:
        """Handle EC2-specific operations"""
        ec2_client = aws.get_boto3_client('ec2')
        response = None

        if name == "ec2_list_instances":
            filters = arguments.get("filters", [])
            response = ec2_client.describe_instances(Filters=filters)
        elif name == "ec2_start_instances":
            response = ec2_client.start_instances(InstanceIds=arguments["instance_ids"])
        elif name == "ec2_stop_instances":
            response = ec2_client.stop_instances(InstanceIds=arguments["instance_ids"])
        elif name == "ec2_describe_instance":
            response = ec2_client.describe_instances(InstanceIds=[arguments["instance_id"]])
        else:
            raise ValueError(f"Unknown EC2 operation: {name}")

        aws.log_operation("ec2", name.replace("ec2_", ""), arguments)
        return [TextContent(type="text", text=f"Operation Result:\n{json.dumps(response, indent=2, default=custom_json_serializer)}")]

    async def handle_lambda_operations(aws: AWSManager, name: str, arguments: dict) -> list[TextContent]:
        """Handle Lambda-specific operations"""
        lambda_client = aws.get_boto3_client('lambda')
        response = None

        if name == "lambda_list_functions":
            params = {}
            if "max_items" in arguments:
                params["MaxItems"] = arguments["max_items"]
            response = lambda_client.list_functions(**params)
        elif name == "lambda_invoke":
            params = {
                "FunctionName": arguments["function_name"],
                "Payload": json.dumps(arguments.get("payload", {})).encode()
            }
            if "invocation_type" in arguments:
                params["InvocationType"] = arguments["invocation_type"]
            response = lambda_client.invoke(**params)
            # Handle binary payload in response
            if "Payload" in response:
                response["Payload"] = json.loads(response["Payload"].read().decode())
        elif name == "lambda_get_function":
            response = lambda_client.get_function(FunctionName=arguments["function_name"])
        else:
            raise ValueError(f"Unknown Lambda operation: {name}")

        aws.log_operation("lambda", name.replace("lambda_", ""), arguments)
        return [TextContent(type="text", text=f"Operation Result:\n{json.dumps(response, indent=2, default=custom_json_serializer)}")]

    async def handle_cloudwatch_operations(aws: AWSManager, name: str, arguments: dict) -> list[TextContent]:
        """Handle CloudWatch-specific operations"""
        cloudwatch_client = aws.get_boto3_client('cloudwatch')
        logs_client = aws.get_boto3_client('logs')
        response = None

        if name == "cloudwatch_get_metrics":
            params = {
                "Namespace": arguments["namespace"],
                "MetricName": arguments["metric_name"]
            }
            if "dimensions" in arguments:
                params["Dimensions"] = arguments["dimensions"]
            if "start_time" in arguments:
                params["StartTime"] = datetime.fromisoformat(arguments["start_time"])
            if "end_time" in arguments:
                params["EndTime"] = datetime.fromisoformat(arguments["end_time"])
            if "period" in arguments:
                params["Period"] = arguments["period"]
            
            response = cloudwatch_client.get_metric_data(**params)
        elif name == "cloudwatch_list_metrics":
            params = {}
            if "namespace" in arguments:
                params["Namespace"] = arguments["namespace"]
            if "metric_name" in arguments:
                params["MetricName"] = arguments["metric_name"]
            
            response = cloudwatch_client.list_metrics(**params)
        elif name == "cloudwatch_get_logs":
            params = {
                "logGroupName": arguments["log_group_name"]
            }
            if "start_time" in arguments:
                params["startTime"] = int(datetime.fromisoformat(arguments["start_time"]).timestamp() * 1000)
            if "end_time" in arguments:
                params["endTime"] = int(datetime.fromisoformat(arguments["end_time"]).timestamp() * 1000)
            if "filter_pattern" in arguments:
                params["filterPattern"] = arguments["filter_pattern"]
            
            response = logs_client.filter_log_events(**params)
        else:
            raise ValueError(f"Unknown CloudWatch operation: {name}")

        aws.log_operation("cloudwatch", name.replace("cloudwatch_", ""), arguments)
        return [TextContent(type="text", text=f"Operation Result:\n{json.dumps(response, indent=2, default=custom_json_serializer)}")]

    async def handle_bedrock_operations(aws: AWSManager, name: str, arguments: dict) -> list[TextContent]:
        """Handle Bedrock-specific operations"""
        bedrock_client = aws.get_boto3_client('bedrock-runtime', region_name=arguments.get("region"))
        cloudwatch_client = aws.get_boto3_client('cloudwatch', region_name=arguments.get("region"))
        response = None

        if name == "bedrock_get_model_stats":
            # Get model usage statistics from CloudWatch metrics
            model_id = arguments["model_id"]
            dimensions = [
                {'Name': 'ModelId', 'Value': model_id},
                {'Name': 'Operation', 'Value': 'InvokeModel'}
            ]
            
            start_time = datetime.fromisoformat(arguments.get("start_time", (datetime.now() - timedelta(hours=24)).isoformat()))
            end_time = datetime.fromisoformat(arguments.get("end_time", datetime.now().isoformat()))
            
            metrics_response = cloudwatch_client.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'invocations',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Bedrock',
                                'MetricName': 'Invocations',
                                'Dimensions': dimensions
                            },
                            'Period': 300,  # 5-minute periods
                            'Stat': 'Sum'
                        }
                    },
                    {
                        'Id': 'latency',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Bedrock',
                                'MetricName': 'Latency',
                                'Dimensions': dimensions
                            },
                            'Period': 300,
                            'Stat': 'Average'
                        }
                    },
                    {
                        'Id': 'input_tokens',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Bedrock',
                                'MetricName': 'InputTokenCount',
                                'Dimensions': dimensions
                            },
                            'Period': 300,
                            'Stat': 'Sum'
                        }
                    },
                    {
                        'Id': 'output_tokens',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Bedrock',
                                'MetricName': 'OutputTokenCount',
                                'Dimensions': dimensions
                            },
                            'Period': 300,
                            'Stat': 'Sum'
                        }
                    }
                ],
                StartTime=start_time,
                EndTime=end_time
            )

            response = {
                'model_id': model_id,
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'metrics': metrics_response['MetricDataResults']
            }

        elif name == "bedrock_analyze_requests":
            # Analyze recent requests to get statistics
            time_period = arguments.get("time_period_hours", 24)
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_period)
            
            # Get invocations and token counts
            metrics_response = cloudwatch_client.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'invocations',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Bedrock',
                                'MetricName': 'Invocations',
                                'Dimensions': [
                                    {'Name': 'ModelId', 'Value': arguments["model_id"]},
                                    {'Name': 'Operation', 'Value': 'InvokeModel'}
                                ]
                            },
                            'Period': 3600,  # 1-hour periods
                            'Stat': 'Sum'
                        }
                    },
                    {
                        'Id': 'input_tokens',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Bedrock',
                                'MetricName': 'InputTokenCount',
                                'Dimensions': [
                                    {'Name': 'ModelId', 'Value': arguments["model_id"]},
                                    {'Name': 'Operation', 'Value': 'InvokeModel'}
                                ]
                            },
                            'Period': 3600,
                            'Stat': 'Sum'
                        }
                    },
                    {
                        'Id': 'output_tokens',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Bedrock',
                                'MetricName': 'OutputTokenCount',
                                'Dimensions': [
                                    {'Name': 'ModelId', 'Value': arguments["model_id"]},
                                    {'Name': 'Operation', 'Value': 'InvokeModel'}
                                ]
                            },
                            'Period': 3600,
                            'Stat': 'Sum'
                        }
                    }
                ],
                StartTime=start_time,
                EndTime=end_time
            )

            # Calculate statistics
            total_invocations = sum(metrics_response['MetricDataResults'][0]['Values'])
            total_input_tokens = sum(metrics_response['MetricDataResults'][1]['Values'])
            total_output_tokens = sum(metrics_response['MetricDataResults'][2]['Values'])

            response = {
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'statistics': {
                    'total_requests': total_invocations,
                    'total_input_tokens': total_input_tokens,
                    'total_output_tokens': total_output_tokens,
                    'average_input_tokens_per_request': total_input_tokens / total_invocations if total_invocations > 0 else 0,
                    'average_output_tokens_per_request': total_output_tokens / total_invocations if total_invocations > 0 else 0
                },
                'raw_metrics': metrics_response['MetricDataResults']
            }

        elif name == "bedrock_get_token_metrics":
            # Get TPM and RPM metrics
            period_minutes = arguments.get("period", 60)
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=period_minutes)
            
            metrics_response = cloudwatch_client.get_metric_data(
                MetricDataQueries=[
                    {
                        'Id': 'input_tpm',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Bedrock',
                                'MetricName': 'InputTokenCount',
                                'Dimensions': [
                                    {'Name': 'ModelId', 'Value': arguments["model_id"]},
                                    {'Name': 'Operation', 'Value': 'InvokeModel'}
                                ]
                            },
                            'Period': 60,  # 1-minute periods
                            'Stat': 'Sum'
                        }
                    },
                    {
                        'Id': 'rpm',
                        'MetricStat': {
                            'Metric': {
                                'Namespace': 'AWS/Bedrock',
                                'MetricName': 'Invocations',
                                'Dimensions': [
                                    {'Name': 'ModelId', 'Value': arguments["model_id"]},
                                    {'Name': 'Operation', 'Value': 'InvokeModel'}
                                ]
                            },
                            'Period': 60,
                            'Stat': 'Sum'
                        }
                    }
                ],
                StartTime=start_time,
                EndTime=end_time
            )

            tpm_data = metrics_response['MetricDataResults'][0]['Values']
            rpm_data = metrics_response['MetricDataResults'][1]['Values']

            response = {
                'time_range': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat()
                },
                'tokens_per_minute': {
                    'average': sum(tpm_data) / len(tpm_data) if tpm_data else 0,
                    'peak': max(tpm_data) if tpm_data else 0,
                    'data_points': tpm_data
                },
                'requests_per_minute': {
                    'average': sum(rpm_data) / len(rpm_data) if rpm_data else 0,
                    'peak': max(rpm_data) if rpm_data else 0,
                    'data_points': rpm_data
                }
            }

        else:
            raise ValueError(f"Unknown Bedrock operation: {name}")

        aws.log_operation("bedrock", name.replace("bedrock_", ""), arguments)
        return [TextContent(type="text", text=f"Operation Result:\n{json.dumps(response, indent=2, default=custom_json_serializer)}")]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle AWS tool operations"""
        if not isinstance(arguments, dict):
            logger.error("Invalid arguments: not a dictionary")
            raise ValueError("Invalid arguments")

        try:
            if name.startswith("s3_"):
                return await handle_s3_operations(aws, name, arguments)
            elif name.startswith("dynamodb_"):
                return await handle_dynamodb_operations(aws, name, arguments)
            elif name.startswith("ec2_"):
                return await handle_ec2_operations(aws, name, arguments)
            elif name.startswith("lambda_"):
                return await handle_lambda_operations(aws, name, arguments)
            elif name.startswith("cloudwatch_"):
                return await handle_cloudwatch_operations(aws, name, arguments)
            elif name.startswith("bedrock_"):
                return await handle_bedrock_operations(aws, name, arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            logger.error(f"Operation failed: {str(e)}")
            raise RuntimeError(f"Operation failed: {str(e)}")

    return server, aws

async def main():
    server, aws = _get_server()
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-server-aws",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
