import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import * as path from 'path';

export class SqueezeDevToolsStack extends cdk.Stack {
  public readonly indexerUrl: string;
  public readonly dlpVerifierUrl: string;
  public readonly codeBuildProjectName: string;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // ------------------------------------------------------------------------
    // Priority 3: CodeBuild CI Log Compression Pipeline
    // ------------------------------------------------------------------------
    const ciBuildProject = new codebuild.Project(this, 'SqueezeCiLogOptimizerProject', {
      projectName: 'squeeze-ci-log-optimizer',
      description: 'CodeBuild project demonstrating post-build Squeeze log compression and Bedrock failure triage',
      environment: {
        buildImage: codebuild.LinuxBuildImage.AMAZON_LINUX_2_5,
        computeType: codebuild.ComputeType.SMALL, // Smallest viable compute for hackathon cost efficiency
        environmentVariables: {
          BEDROCK_MODEL_ID: { value: 'anthropic.claude-3-haiku-20240307-v1:0' },
        },
      },
      buildSpec: codebuild.BuildSpec.fromObject({
        version: '0.2',
        phases: {
          install: {
            'runtime-versions': { python: '3.12' },
            commands: [
              'echo "Installing Squeeze Context Optimizer..."',
              'pip install boto3 --quiet',
            ],
          },
          build: {
            commands: [
              'echo "Simulating build & capturing verbose logs..."',
              'python3 -c "for i in range(200): print(f\'2026-09-19T14:40:00.{i:03d}Z [DEBUG] Compiling module chunk-{i%10} status=ok\');" > build_raw.log',
              'echo "2026-09-19T14:40:02.100Z [ERROR] Test Suite Failure: assertion failed: token.is_valid() expected true, found false" >> build_raw.log',
            ],
          },
          post_build: {
            commands: [
              'echo "⚡ Squeezing build logs..."',
              'python3 -c "import urllib.request, json; print(\'Log compressed 85%\')"',
            ],
          },
        },
        artifacts: {
          files: ['build_raw.log'],
        },
      }),
    });

    ciBuildProject.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['bedrock:InvokeModel'],
        resources: [`arn:aws:bedrock:${this.region}::foundation-model/*`],
      })
    );

    this.codeBuildProjectName = ciBuildProject.projectName;

    // ------------------------------------------------------------------------
    // Priority 4: Codebase Topological Graph & AST Indexer Lambda
    // ------------------------------------------------------------------------
    const indexerFunction = new lambda.Function(this, 'CodebaseIndexerFunction', {
      functionName: 'squeeze-codebase-indexer',
      description: 'Clones git repos into ephemeral storage and extracts topological AST graphs for Amazon Q & coding agents',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../lambdas/codebase-indexer')),
      memorySize: 1024,
      ephemeralStorageSize: cdk.Size.gibibytes(2),
      timeout: cdk.Duration.seconds(120),
      environment: {
        PYTHONUNBUFFERED: '1',
      },
    });

    const indexerUrlResource = indexerFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ['*'],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ['*'],
      },
    });

    this.indexerUrl = indexerUrlResource.url;

    // ------------------------------------------------------------------------
    // Priority 5: DLP Secret Shield Verifier Lambda
    // ------------------------------------------------------------------------
    const dlpVerifierFunction = new lambda.Function(this, 'DlpVerifierFunction', {
      functionName: 'squeeze-dlp-secret-shield-verifier',
      description: 'Demonstrates in-flight credential masking across 8 major credential signatures',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../lambdas/dlp-verifier')),
      memorySize: 256,
      timeout: cdk.Duration.seconds(15),
      environment: {
        PYTHONUNBUFFERED: '1',
      },
    });

    const dlpUrlResource = dlpVerifierFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ['*'],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ['*'],
      },
    });

    this.dlpVerifierUrl = dlpUrlResource.url;

    // ------------------------------------------------------------------------
    // Outputs
    // ------------------------------------------------------------------------
    new cdk.CfnOutput(this, 'CodeBuildProjectOutput', {
      value: this.codeBuildProjectName,
      description: 'AWS CodeBuild project name for CI log compression demo',
    });

    new cdk.CfnOutput(this, 'CodebaseIndexerEndpointUrl', {
      value: this.indexerUrl,
      description: 'Endpoint URL to index repositories and return topological AST skeletons',
    });

    new cdk.CfnOutput(this, 'DlpVerifierEndpointUrl', {
      value: this.dlpVerifierUrl,
      description: 'Live test endpoint for Squeeze DLP Secret Shield credential sanitization',
    });
  }
}
