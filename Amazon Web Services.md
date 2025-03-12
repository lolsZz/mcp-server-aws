Amazon Web Services

Tue Mar 11 2025
02:37:08 GMT+0000 (Greenwich Mean Time)

Hi there,

Hope you're doing well today. Adams here from AWS Accounts and Billings support.

Thank you for reaching out with regard to your quota increase request.

I understand you have requested for a limit increase on Bedrock, anthropic.claude-3-sonnet-20240229-v1:0:200k Provisioned Throughput Model Units in the US West (Oregon) region. I'm glad to review your request and assist you further.

=====================================

Request Summary:

Service: Bedrock
Model Name: anthropic.claude-3-sonnet-20240229-v1:0:200k
Region: US West (Oregon)
Limit name: Provisioned Throughput Model Units
New limit value: 1000000

=====================================

I’m happy to inform you that I have submitted the request for you. For a quota increase of this nature, I will need to collaborate with our service teams to get approval. Please note that it can take some time for the service team to review your request. This is to ensure that we can meet your needs while keeping existing infrastructure safe.

Rest assured, I will insist on regular updates and keep you posted!

In the meantime, if there's anything else we can assist you with, please let us know, and we'll be happy to help!

Your patience, time and comprehension are greatly appreciated since we truly value your business with us.

Have a great day ahead! 

We value your feedback. Please share your experience by rating this and other correspondences in the AWS Support Center. You can rate a correspondence by selecting the stars in the top right corner of the correspondence.

Best regards,
Adams J P 
Amazon Web Services

Martin M
Tue Mar 11 2025
07:24:44 GMT+0000 (Greenwich Mean Time)

Thank's for the quick response Adams. 

I need to clarify two important points regarding this quota increase request:

The ticket system required selecting 'Provisioned Throughput Model Units', our request is specifically for increasing the on-demand inference quotas for the following Claude models in US-West-2 as well as investigating the cross region inference for (US East (Virginia) us-east-1, US West (Oregon)):
Standard Models Tested:

anthropic.claude-3-7-sonnet-20250219-v1:0
anthropic.claude-3-5-sonnet-20240620-v1:0
anthropic.claude-3-5-sonnet-20241022-v2:0

The Cross-Region Inference Issue (US East (Virginia) us-east-1, US West (Oregon):
We have specifically tested cross-region inference using the following Inference Profile IDs:
us.anthropic.claude-3-7-sonnet-20250219-v1:0
us.anthropic.claude-3-5-sonnet-20240620-v1:0
us.anthropic.claude-3-5-sonnet-20241022-v2:0

However, contrary to the expected behavior, cross-region inference configuration is not providing the anticipated increased throughput. 
We are still experiencing the same rate limiting issues across all configurations.

Our request specifically needs to address:

RPM (Requests per Minute) increases
TPM (Tokens per Minute) increases
Daily token limit adjustments

Could you please:
Ensure this request is routed to the appropriate team for on-demand model quota increases
Maybe investigate why cross-region inference is not providing the expected throughput improvements ?

Consider our quota increase request in light of the fact that the standard mitigation strategy (cross-region inference) is not resolving our severly stringent token limitations
As mentioned in our original request, we are currently experiencing:

Rate limits after a single chat with Claude 3.7 Sonnet (under 10,000 tokens)
Only approximately 2 messages possible with Claude 3.5 Sonnet v2 before hitting limits
Consistent 'Too many tokens, please wait before trying again' errors
These limitations are severely impacting our ability to conduct proper testing and development.

Martin M

Amazon Web Services

Tue Mar 11 2025
10:09:59 GMT+0000 (Greenwich Mean Time)

Hello there, 

Adams here from AWS Accounts and Billing team! 

I understand that you have  two important points regarding this quota increase request. Thank you for letting us know that ticket system required selecting 'Provisioned Throughput Model Units' eventhough your request is specifically for increasing the on-demand inference quotas for the following Claude models in US-West-2 as well as investigating the cross region inference for (US East (Virginia) us-east-1, US West (Oregon)). 

I also understand that you have Cross-Region Inference Issue  in the  US East (Virginia) and US West (Oregon) region. I understand that contrary to the expected behavior, cross-region inference configuration is not providing the anticipated increased throughput and you are still experiencing the same rate limiting issues across all configurations. 

Hence before to proceed with the limit increase, first we will check with the concerned team why these issue are still occurring. Hence I am transferring the support case to the concerned technical Sagemaker team and they will help you further in figuring out the issue. Once the issue has been resolved and they find out the exact region, we can surely work on the Sagemaker limits. They will soon reply to you via email soon.

Meanwhile if you have any queries related to this, please let us know and we would be happy to help you! Have a nice day ahead!

We value your feedback. Please share your experience by rating this and other correspondences in the AWS Support Center. You can rate a correspondence by selecting the stars in the top right corner of the correspondence.

Best regards,
Adams J P 
Amazon Web Services

Martin M
Tue Mar 11 2025
16:53:46 GMT+0000 (Greenwich Mean Time)

Excellent, 

Well done Adams, Ill wait for them to get back to me then.
Thank you so much for your input

Sincerely
Martin M

Amazon Web Services

Tue Mar 11 2025
18:20:22 GMT+0000 (Greenwich Mean Time)
Hello Martin,

Greetings from AWS Premium Support. My name is Isaac from the AI/ML team, and I will be assisting you with this case.

From the case description, I understand that you are facing throttling issues in your Bedrock invocation workflows (even after using cross-region inference), and you are seeking a limit increase for the Bedrock quotas in your account. Adams (the engineer from the AWS Accounts and Billing team) transferred this case to the Premium Support queue, for further assistance regarding this issue. Please correct me if I have not captured your query correctly.

To better assist in this issue, I will need to create an escalation ticket to the internal service team (who are the Bedrock service owners) to action the limit increase request. To achieve this, kindly provide the following details as a response to this case (fill the details separately for each model that you are seeking a limit increase):

-------------------------------------------------------------------------
1. Detailed description of the use case:
2. Model ID:
3. Region:
4. Limit type (RPM and/or TPM):
5. Requested TPM (tokens per minute) for Steady-state:          and Peak:
6. Requested RPM (requests per minute) for Steady-state:       and Peak: 
7. Average input tokens per request: 
8. Average output tokens per request:
9. Percentage of requests with input tokens greater than 25k:
10. Are you open to use cross-region inference?
-------------------------------------------------------------------------

Looking forward to your feedback of the requested information.

If you have any further questions, please feel free to add it to your response and I will be more than happy to assist you further.

We value your feedback. Please share your experience by rating this and other correspondences in the AWS Support Center. You can rate a correspondence by selecting the stars in the top right corner of the correspondence.

Best regards,
Isaac A.
Amazon Web Services