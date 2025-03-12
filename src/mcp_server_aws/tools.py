from mcp.types import Tool


def get_s3_tools() -> list[Tool]:
    return [
        Tool(
            name="s3_bucket_create",
            description="Create a new S3 bucket",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the S3 bucket to create"
                    },
                    "region": {
                        "type": "string",
                        "description": "AWS region where the bucket should be created (e.g., us-west-2)"
                    }
                },
                "required": ["bucket_name"]
            }
        ),
        Tool(
            name="s3_bucket_list",
            description="List all S3 buckets",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="s3_bucket_delete",
            description="Delete an S3 bucket",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the S3 bucket to delete"
                    }
                },
                "required": ["bucket_name"]
            }
        ),
        Tool(
            name="s3_object_upload",
            description="Upload an object to S3",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the S3 bucket"
                    },
                    "object_key": {
                        "type": "string",
                        "description": "Key/path of the object in the bucket"
                    },
                    "file_content": {
                        "type": "string",
                        "description": "Base64 encoded file content for upload"
                    }
                },
                "required": ["bucket_name", "object_key", "file_content"]
            }
        ),
        Tool(
            name="s3_object_delete",
            description="Delete an object from S3",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the S3 bucket"
                    },
                    "object_key": {
                        "type": "string",
                        "description": "Key/path of the object to delete"
                    }
                },
                "required": ["bucket_name", "object_key"]
            }
        ),
        Tool(
            name="s3_object_list",
            description="List objects in an S3 bucket",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the S3 bucket"
                    }
                },
                "required": ["bucket_name"]
            }
        ),
        Tool(
            name="s3_object_read",
            description="Read an object's content from S3",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the S3 bucket"
                    },
                    "object_key": {
                        "type": "string",
                        "description": "Key/path of the object to read"
                    }
                },
                "required": ["bucket_name", "object_key"]
            }
        ),
    ]


def get_dynamodb_tools() -> list[Tool]:
    return [
        Tool(
            name="dynamodb_table_create",
            description="Create a new DynamoDB table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the DynamoDB table"
                    },
                    "key_schema": {
                        "type": "array",
                        "description": "Key schema for table creation"
                    },
                    "attribute_definitions": {
                        "type": "array",
                        "description": "Attribute definitions for table creation"
                    }
                },
                "required": ["table_name", "key_schema", "attribute_definitions"]
            }
        ),
        Tool(
            name="dynamodb_table_describe",
            description="Get details about a DynamoDB table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the DynamoDB table"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="dynamodb_table_list",
            description="List all DynamoDB tables",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="dynamodb_table_delete",
            description="Delete a DynamoDB table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the DynamoDB table"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="dynamodb_table_update",
            description="Update a DynamoDB table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the DynamoDB table"
                    },
                    "attribute_definitions": {
                        "type": "array",
                        "description": "Updated attribute definitions"
                    }
                },
                "required": ["table_name", "attribute_definitions"]
            }
        ),
        Tool(
            name="dynamodb_item_put",
            description="Put an item into a DynamoDB table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the DynamoDB table"
                    },
                    "item": {
                        "type": "object",
                        "description": "Item data to put"
                    }
                },
                "required": ["table_name", "item"]
            }
        ),
        Tool(
            name="dynamodb_item_get",
            description="Get an item from a DynamoDB table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the DynamoDB table"
                    },
                    "key": {
                        "type": "object",
                        "description": "Key to identify the item"
                    }
                },
                "required": ["table_name", "key"]
            }
        ),
        Tool(
            name="dynamodb_item_update",
            description="Update an item in a DynamoDB table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the DynamoDB table"
                    },
                    "key": {
                        "type": "object",
                        "description": "Key to identify the item"
                    },
                    "item": {
                        "type": "object",
                        "description": "Updated item data"
                    }
                },
                "required": ["table_name", "key", "item"]
            }
        ),
        Tool(
            name="dynamodb_item_delete",
            description="Delete an item from a DynamoDB table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the DynamoDB table"
                    },
                    "key": {
                        "type": "object",
                        "description": "Key to identify the item"
                    }
                },
                "required": ["table_name", "key"]
            }
        ),
        Tool(
            name="dynamodb_item_query",
            description="Query items in a DynamoDB table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the DynamoDB table"
                    },
                    "key_condition": {
                        "type": "string",
                        "description": "Key condition expression"
                    },
                    "expression_values": {
                        "type": "object",
                        "description": "Expression attribute values"
                    }
                },
                "required": ["table_name", "key_condition", "expression_values"]
            }
        ),
        Tool(
            name="dynamodb_item_scan",
            description="Scan items in a DynamoDB table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the DynamoDB table"
                    },
                    "filter_expression": {
                        "type": "string",
                        "description": "Filter expression"
                    },
                    "expression_attributes": {
                        "type": "object",
                        "properties": {
                            "values": {
                                "type": "object",
                                "description": "Expression attribute values"
                            },
                            "names": {
                                "type": "object",
                                "description": "Expression attribute names"
                            }
                        }
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="dynamodb_batch_get",
            description="Batch get multiple items from DynamoDB tables",
            inputSchema={
                "type": "object",
                "properties": {
                    "request_items": {
                        "type": "object",
                        "description": "Map of table names to keys to retrieve",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "Keys": {
                                    "type": "array",
                                    "items": {
                                        "type": "object"
                                    }
                                },
                                "ConsistentRead": {
                                    "type": "boolean"
                                },
                                "ProjectionExpression": {
                                    "type": "string"
                                }
                            },
                            "required": ["Keys"]
                        }
                    }
                },
                "required": ["request_items"]
            }
        ),
        Tool(
            name="dynamodb_item_batch_write",
            description="Batch write operations (put/delete) for DynamoDB items",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the DynamoDB table"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["put", "delete"],
                        "description": "Type of batch operation (put or delete)"
                    },
                    "items": {
                        "type": "array",
                        "description": "Array of items to process"
                    },
                    "key_attributes": {
                        "type": "array",
                        "description": "For delete operations, specify which attributes form the key",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["table_name", "operation", "items"]
            }
        ),
        Tool(
            name="dynamodb_describe_ttl",
            description="Get the TTL settings for a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the DynamoDB table"
                    }
                },
                "required": ["table_name"]
            }
        ),

        Tool(
            name="dynamodb_update_ttl",
            description="Update the TTL settings for a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the DynamoDB table"
                    },
                    "ttl_enabled": {
                        "type": "boolean",
                        "description": "Whether TTL should be enabled"
                    },
                    "ttl_attribute": {
                        "type": "string",
                        "description": "The attribute name to use for TTL"
                    }
                },
                "required": ["table_name", "ttl_enabled", "ttl_attribute"]
            }
        ),
        Tool(
            name="dynamodb_batch_execute",
            description="Execute multiple PartiQL statements in a batch",
            inputSchema={
                "type": "object",
                "properties": {
                    "statements": {
                        "type": "array",
                        "description": "List of PartiQL statements to execute",
                        "items": {
                            "type": "string"
                        }
                    },
                    "parameters": {
                        "type": "array",
                        "description": "List of parameter lists for each statement",
                        "items": {
                            "type": "array"
                        }
                    }
                },
                "required": ["statements", "parameters"]
            }
        ),
    ]


def get_ec2_tools() -> list[Tool]:
    return [
        Tool(
            name="ec2_list_instances",
            description="List EC2 instances and their details",
            inputSchema={
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "array",
                        "description": "Optional filters to apply",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Name": {"type": "string"},
                                "Values": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        ),
        Tool(
            name="ec2_start_instances",
            description="Start one or more EC2 instances",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ids": {
                        "type": "array",
                        "description": "List of instance IDs to start",
                        "items": {"type": "string"}
                    }
                },
                "required": ["instance_ids"]
            }
        ),
        Tool(
            name="ec2_stop_instances",
            description="Stop one or more EC2 instances",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_ids": {
                        "type": "array",
                        "description": "List of instance IDs to stop",
                        "items": {"type": "string"}
                    }
                },
                "required": ["instance_ids"]
            }
        ),
        Tool(
            name="ec2_describe_instance",
            description="Get detailed information about an EC2 instance",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_id": {
                        "type": "string",
                        "description": "ID of the instance to describe"
                    }
                },
                "required": ["instance_id"]
            }
        )
    ]

def get_lambda_tools() -> list[Tool]:
    return [
        Tool(
            name="lambda_list_functions",
            description="List all Lambda functions",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_items": {
                        "type": "integer",
                        "description": "Maximum number of functions to return"
                    }
                }
            }
        ),
        Tool(
            name="lambda_invoke",
            description="Invoke a Lambda function",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name or ARN of the Lambda function"
                    },
                    "payload": {
                        "type": "object",
                        "description": "JSON payload to send to the function"
                    },
                    "invocation_type": {
                        "type": "string",
                        "enum": ["RequestResponse", "Event", "DryRun"],
                        "description": "Invocation type for the Lambda function"
                    }
                },
                "required": ["function_name"]
            }
        ),
        Tool(
            name="lambda_get_function",
            description="Get information about a Lambda function",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {
                        "type": "string",
                        "description": "Name or ARN of the Lambda function"
                    }
                },
                "required": ["function_name"]
            }
        )
    ]

def get_cloudwatch_tools() -> list[Tool]:
    return [
        Tool(
            name="cloudwatch_get_metrics",
            description="Get CloudWatch metrics for a resource",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Namespace of the metric (e.g., AWS/EC2)"
                    },
                    "metric_name": {
                        "type": "string",
                        "description": "Name of the metric"
                    },
                    "dimensions": {
                        "type": "array",
                        "description": "Dimensions to filter the metric",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Name": {"type": "string"},
                                "Value": {"type": "string"}
                            }
                        }
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time in ISO format"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time in ISO format"
                    },
                    "period": {
                        "type": "integer",
                        "description": "Period in seconds"
                    }
                },
                "required": ["namespace", "metric_name"]
            }
        ),
        Tool(
            name="cloudwatch_list_metrics",
            description="List available CloudWatch metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Optional namespace to filter metrics"
                    },
                    "metric_name": {
                        "type": "string",
                        "description": "Optional metric name to filter"
                    }
                }
            }
        ),
        Tool(
            name="cloudwatch_get_logs",
            description="Get CloudWatch logs from a log group",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_group_name": {
                        "type": "string",
                        "description": "Name of the log group"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time in ISO format"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time in ISO format"
                    },
                    "filter_pattern": {
                        "type": "string",
                        "description": "Optional filter pattern for the logs"
                    }
                },
                "required": ["log_group_name"]
            }
        )
    ]

def get_bedrock_tools() -> list[Tool]:
    return [
        Tool(
            name="bedrock_get_model_stats",
            description="Get detailed usage statistics for a Bedrock model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_id": {
                        "type": "string",
                        "description": "Bedrock model ID (e.g., anthropic.claude-3-sonnet-20240229-v1:0)"
                    },
                    "region": {
                        "type": "string",
                        "description": "AWS region (e.g., us-west-2)"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time in ISO format"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time in ISO format"
                    }
                },
                "required": ["model_id", "region"]
            }
        ),
        Tool(
            name="bedrock_analyze_requests",
            description="Analyze Bedrock API requests to get token statistics",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_id": {
                        "type": "string",
                        "description": "Bedrock model ID"
                    },
                    "region": {
                        "type": "string",
                        "description": "AWS region"
                    },
                    "time_period_hours": {
                        "type": "integer",
                        "description": "Number of hours to analyze",
                        "default": 24
                    }
                },
                "required": ["model_id", "region"]
            }
        ),
        Tool(
            name="bedrock_get_token_metrics",
            description="Get token usage metrics for a Bedrock model",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_id": {
                        "type": "string",
                        "description": "Bedrock model ID"
                    },
                    "region": {
                        "type": "string",
                        "description": "AWS region"
                    },
                    "period": {
                        "type": "integer",
                        "description": "Period in minutes to analyze",
                        "default": 60
                    }
                },
                "required": ["model_id", "region"]
            }
        )
    ]

def get_aws_tools() -> list[Tool]:
    return [
        *get_s3_tools(),
        *get_dynamodb_tools(),
        *get_ec2_tools(),
        *get_lambda_tools(),
        *get_cloudwatch_tools(),
        *get_bedrock_tools()
    ]
