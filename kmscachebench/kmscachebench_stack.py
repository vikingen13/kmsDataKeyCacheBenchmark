from aws_cdk import (
    Duration,
    Stack,
    # aws_sqs as sqs,
    aws_kms as kms,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_lambda as _lambda,
    aws_events,
    aws_events_targets,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks        
)
import aws_cdk
from constructs import Construct

class KmscachebenchStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #create the kms key
        myKMSKey = kms.Key(self, "Key",
               enable_key_rotation=True
        )

        #create a bucket encrypted with a bucket key encrypted with the kms key
        myBucket = s3.Bucket(self, "MyBucket",
             encryption=s3.BucketEncryption.KMS,
             encryption_key=myKMSKey,
             bucket_key_enabled=True
        )

        #deploy the test files        
        s3deploy.BucketDeployment(self, "DeployTestFiles",
           sources=[s3deploy.Source.asset("./kmscachebench/tmpfile")],
            destination_bucket=myBucket,
            destination_key_prefix=""
        )

        #create a lambda function to iterate in the step function
        myLambdaIteratorFunction = _lambda.Function(self, "LambdaIteratorFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("kmscachebench/lambdaIterator"),
            handler="lambda_function.lambda_handler",
            timeout=Duration.seconds(20)
        )


        #create the lambda function that will be triggered every minute
        myLambdaGetObjectFunction = _lambda.Function(self, "LambdaGetObjectFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("kmscachebench/lambdaGetS3"),
            handler="lambda_function.lambda_handler",
            environment={
                "BUCKET_NAME": myBucket.bucket_name,
                "OBJECT_NAME": "fileLambda"
            },
            timeout=Duration.seconds(20)
        )

        #allow the lambda function to access the bucket
        myBucket.grant_read(myLambdaGetObjectFunction)


        #-------------------StepFunctions------------------#
        #create a pass state for the step function
        myInitializeIteratorStep = sfn.Pass(self, "InitializeIteratorStep",
            result=sfn.Result.from_object({
                    "count": 10,
                    "index": 0,
                    "continue": True
                }),                    
                result_path="$.iterator"
        )
        
        #create the iterator lambda state
        myIteratorStep = sfn_tasks.LambdaInvoke(self, "Iterator",
                lambda_function=myLambdaIteratorFunction,
                payload_response_only=True)
        
        myInitializeIteratorStep.next(myIteratorStep)

        #create the get object lambda state
        myGetObjectStep = sfn_tasks.LambdaInvoke(self, "GetObject",
                lambda_function=myLambdaGetObjectFunction,
                result_path=sfn.JsonPath.DISCARD
                )
        
        myIteratorStep.next(myGetObjectStep)

        #create the wait state
        myWaitStep = sfn.Wait(self, "Wait",
            time=sfn.WaitTime.seconds_path("$.waitTime"))
        
        myGetObjectStep.next(myWaitStep)

        #create the choice state
        myChoiceStep = sfn.Choice(self, "isOver")
        myChoiceStep.when(sfn.Condition.boolean_equals("$.iterator.continue", True), myIteratorStep)
        myChoiceStep.otherwise(sfn.Succeed(self, "Success"))
        myWaitStep.next(myChoiceStep)

        #create a state machine to iterate the lambda function
        myStateMachine = sfn.StateMachine(self, "myKMSCacheBenchStateMachine",
            definition=myInitializeIteratorStep)                                           
        
        #write the ouput of the stack
        aws_cdk.CfnOutput(
            self, "Lauch a StepFunction running 10 times a Lambda function that perform a getObject at a regular interval",
            value='aws stepfunctions start-execution --input "\{"waitTime": 60\}" --state-machine-arn ' + myStateMachine.state_machine_arn,
            description="Please run this command to lauch a StepFunction running 10 times a Lambda function that perform a getObject at a regular interval"
        )
