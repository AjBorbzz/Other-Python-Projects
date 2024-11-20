# One Deal A Day Sale Architecture
An ecommerce company wants to launch a one-deal-a-day website on AWS. Each day will feature exactly one product on sale for a period of 24 hours. The company wants to be able to handle millions of requests each hour with millisecond latency during peak hours.

For least operational overhead.
**Use Amazon S3 Bucket to Host the website's static content.**
**Deploy an Amazon CloudFront distribution.**
**Set S3 bucket as Origin**
**Use AWS API Gateway and Lambda Functions for backend API.**
**Store the data to DynamoDb**
