
# kmsDataKeyCacheBenchmark

kmsDataKeyCacheBenchmark is a solution to make test with Amazon S3 and AWS KMS.
For example, you can verify if all your KMS calls are logged in CloudTrail.

This project uses AWS Cloud Development Kit (CDK).

To deploy the solution, run the following commands:

```
$ source .venv/bin/activate

$ pip install -r requirements.txt

$ cdk deploy
```

At this point, you are ready to make tests.

## Architecture

[Architecture](https://raw.githubusercontent.com/vikingen13/kmsDataKeyCacheBenchmark/main/archi.png)

## How to make tests
Once the project is deployed, you will be invited to execute a command similar to the following one:
```
aws stepfunctions start-execution --input "{\"waitTime\": 300}" --state-machine-arn arn:aws:states:eu-west-1:12345678:stateMachine:myKMSCacheBenchStateMachine12345678-123456789
```

This command will execute the Stepfunction. Each state machine execution will launch 10 time a lambda function that will perform a get_object on a S3 bucket with the server side encryption enabled. The waitTime parameter represents the delay in second between each of the lambda executions.

Once you executed the state machine, you can use CloudTrail to verify if KMS was correctly called to decrypt the object data key. In the solution, the s3 bucket key is enabled but you can try to change this setting to check how the behaviour differs.

Enjoy!
