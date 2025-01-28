"""An AWS Python Pulumi program"""

import pulumi
from pulumi_aws import s3

# Create an AWS resource (S3 Bucket)
bucket = s3.BucketV2('my-bucket')
bucketObject = s3.BucketObject('index.html',bucket=bucket.id,source=pulumi.FileAsset('./index.html'))

website = s3.BucketWebsiteConfigurationV2("website",
                                          bucket=bucket.id,
                                          index_document={
                                              "suffix": "index.html",
                                          })
# Export the name of the bucket
pulumi.export('bucket_name', bucket.id)
