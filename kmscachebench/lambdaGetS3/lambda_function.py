# -*- coding: utf-8 -*-

import logging
import boto3
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#lambda handler
def lambda_handler(event, context):
    #read a file on an s3 bucket
    s3 = boto3.resource('s3')

    #read the s3 bucket name from the environment variable
    myBucketName = os.environ['BUCKET_NAME']

    myBucket = s3.Bucket(myBucketName)

    myObjectName = os.environ['OBJECT_NAME']

    myObject = myBucket.Object(myObjectName)

    #read the file contents
    fileContents = myObject.get()['Body'].read()


    