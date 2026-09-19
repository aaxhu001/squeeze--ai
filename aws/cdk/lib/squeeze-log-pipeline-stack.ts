import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as destinations from 'aws-cdk-lib/aws-logs-destinations';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import * as path from 'path';

export interface SqueezeLogPipelineStackProps extends cdk.StackProps {
  bedrockModelId?: string;
}

export class SqueezeLogPipelineStack extends cdk.Stack {
  public readonly reportsBucket: s3.Bucket;
  public readonly noisyLoggerFunction: lambda.Function;
  public readonly logProcessorFunction: lambda.Function;

  constructor(scope: Construct, id: string, props?: SqueezeLogPipelineStackProps) {
    super(scope, id, props);

    const modelId = props?.bedrockModelId || 'anthropic.claude-3-5-sonnet-20241022-v2:0';

    // ------------------------------------------------------------------------
    // 1. S3 Incident Reports Bucket (with auto-delete on destroy)
    // ------------------------------------------------------------------------
    this.reportsBucket = new s3.Bucket(this, 'SqueezeIncidentReportsBucket', {
      bucketName: `squeeze-incident-reports-${this.account}-${this.region}`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      lifecycleRules: [
        {
          expiration: cdk.Duration.days(7),
          id: 'ExpireOldReports',
        },
      ],
    });

    // ------------------------------------------------------------------------
    // 2. Demo Noisy Logger Lambda (Simulates high-volume microservice)
    // ------------------------------------------------------------------------
    const noisyLogGroup = new logs.LogGroup(this, 'NoisyLoggerLogGroup', {
      logGroupName: '/aws/lambda/squeeze-demo-noisy-logger',
      retention: logs.RetentionDays.ONE_DAY,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    this.noisyLoggerFunction = new lambda.Function(this, 'NoisyLoggerFunction', {
      functionName: 'squeeze-demo-noisy-logger',
      description: 'Emits repetitive error logs and credentials to CloudWatch for Squeeze demo',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../lambdas/noisy-logger')),
      memorySize: 256,
      timeout: cdk.Duration.seconds(30),
      logGroup: noisyLogGroup,
    });

    // ------------------------------------------------------------------------
    // 3. Squeeze CloudWatch Log Processor Lambda
    // ------------------------------------------------------------------------
    this.logProcessorFunction = new lambda.Function(this, 'SqueezeLogProcessorFunction', {
      functionName: 'squeeze-cloudwatch-log-processor',
      description: 'Intercepts CloudWatch logs, collapses lines via Squeeze, emits metrics, and triggers Bedrock',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../lambdas/log-processor')),
      memorySize: 512,
      timeout: cdk.Duration.seconds(60),
      environment: {
        REPORTS_BUCKET_NAME: this.reportsBucket.bucketName,
        BEDROCK_MODEL_ID: modelId,
        FALLBACK_MODEL_ID: 'anthropic.claude-3-haiku-20240307-v1:0',
        PYTHONUNBUFFERED: '1',
      },
    });

    // Grant permissions: S3 write, CloudWatch metrics, Bedrock InvokeModel
    this.reportsBucket.grantPut(this.logProcessorFunction);

    this.logProcessorFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['cloudwatch:PutMetricData'],
        resources: ['*'],
      })
    );

    this.logProcessorFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['bedrock:InvokeModel'],
        resources: [`arn:aws:bedrock:${this.region}::foundation-model/*`],
      })
    );

    // ------------------------------------------------------------------------
    // 4. CloudWatch Subscription Filter
    // ------------------------------------------------------------------------
    new logs.SubscriptionFilter(this, 'SqueezeLogSubscriptionFilter', {
      logGroup: noisyLogGroup,
      destination: new destinations.LambdaDestination(this.logProcessorFunction),
      filterPattern: logs.FilterPattern.allEvents(),
    });

    // ------------------------------------------------------------------------
    // Outputs
    // ------------------------------------------------------------------------
    new cdk.CfnOutput(this, 'IncidentReportsBucketOutput', {
      value: this.reportsBucket.bucketName,
      description: 'S3 Bucket holding Squeeze AI Incident Summaries',
    });

    new cdk.CfnOutput(this, 'NoisyLoggerFunctionNameOutput', {
      value: this.noisyLoggerFunction.functionName,
      description: 'Trigger this Lambda to generate live noisy logs and feed Squeeze pipeline',
    });
  }
}
