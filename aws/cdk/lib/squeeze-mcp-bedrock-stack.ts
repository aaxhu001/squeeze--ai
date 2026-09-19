import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as bedrock from 'aws-cdk-lib/aws-bedrock';
import { Construct } from 'constructs';
import * as path from 'path';
import * as fs from 'fs';

export interface SqueezeMcpBedrockStackProps extends cdk.StackProps {
  bedrockModelId?: string;
}

export class SqueezeMcpBedrockStack extends cdk.Stack {
  public readonly mcpEndpointUrl: string;
  public readonly actionGroupFunctionArn: string;
  public readonly agentId: string;

  constructor(scope: Construct, id: string, props?: SqueezeMcpBedrockStackProps) {
    super(scope, id, props);

    const modelId = props?.bedrockModelId || 'anthropic.claude-3-5-sonnet-20241022-v2:0';

    // ------------------------------------------------------------------------
    // 1. Squeeze Remote MCP Server (Lambda Function URL for HTTP/SSE & JSON-RPC)
    // ------------------------------------------------------------------------
    const mcpFunction = new lambda.Function(this, 'SqueezeMcpServerFunction', {
      functionName: 'squeeze-aws-mcp-server',
      description: 'Squeeze AI Remote MCP & REST context compression server',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'app.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../mcp-server')),
      memorySize: 512,
      timeout: cdk.Duration.seconds(30),
      environment: {
        PYTHONUNBUFFERED: '1',
      },
    });

    // Add public Function URL with CORS enabled for remote MCP client connections
    const fnUrl = mcpFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedOrigins: ['*'],
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ['*'],
        maxAge: cdk.Duration.days(1),
      },
    });

    this.mcpEndpointUrl = fnUrl.url;

    // ------------------------------------------------------------------------
    // 2. Bedrock Agent Action Group Handler Lambda
    // ------------------------------------------------------------------------
    const actionGroupFunction = new lambda.Function(this, 'SqueezeActionGroupFunction', {
      functionName: 'squeeze-bedrock-action-handler',
      description: 'Executes Squeeze context compression tools for Bedrock Agents',
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../../lambdas/bedrock-action-handler')),
      memorySize: 512,
      timeout: cdk.Duration.seconds(30),
      environment: {
        PYTHONUNBUFFERED: '1',
      },
    });

    // Allow CloudWatch metric publishing
    actionGroupFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['cloudwatch:PutMetricData'],
        resources: ['*'],
      })
    );

    // Permission for Bedrock service principal to invoke the Action Group Lambda
    actionGroupFunction.addPermission('AllowBedrockInvocation', {
      principal: new iam.ServicePrincipal('bedrock.amazonaws.com'),
      action: 'lambda:InvokeFunction',
      sourceAccount: this.account,
    });

    this.actionGroupFunctionArn = actionGroupFunction.functionArn;

    // ------------------------------------------------------------------------
    // 3. Bedrock Agent Execution IAM Role
    // ------------------------------------------------------------------------
    const agentRole = new iam.Role(this, 'SqueezeBedrockAgentRole', {
      roleName: `squeeze-bedrock-agent-role-${this.region}`,
      assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
      description: 'IAM execution role for Squeeze AI Bedrock Agent',
    });

    agentRole.addToPolicy(
      new iam.PolicyStatement({
        actions: ['bedrock:InvokeModel'],
        resources: [`arn:aws:bedrock:${this.region}::foundation-model/*`],
      })
    );

    agentRole.addToPolicy(
      new iam.PolicyStatement({
        actions: ['lambda:InvokeFunction'],
        resources: [actionGroupFunction.functionArn, `${actionGroupFunction.functionArn}:*`],
      })
    );

    // ------------------------------------------------------------------------
    // 4. Amazon Bedrock Agent with Squeeze Action Group
    // ------------------------------------------------------------------------
    const schemaPath = path.join(__dirname, '../../mcp-server/openapi-schema.json');
    const openApiSchema = fs.readFileSync(schemaPath, 'utf8');

    const agent = new bedrock.CfnAgent(this, 'SqueezeBedrockAgent', {
      agentName: 'Squeeze-Bedrock-Optimizer',
      description: 'Autonomous AWS Agent with Squeeze context compression and DLP Secret Shield tools',
      foundationModel: modelId,
      agentResourceRoleArn: agentRole.roleArn,
      instruction:
        'You are the Squeeze-Bedrock-Optimizer Agent. Before analyzing large logs, massive JSON structures, or source code, ' +
        'ALWAYS call the appropriate Squeeze action (squeeze_shrink_logs, squeeze_shrink_json, squeeze_skeleton, squeeze_compress, squeeze_codebase_graph) ' +
        'to compress the context window and prevent token bloat. Then synthesize your findings and report the compression savings.',
      actionGroups: [
        {
          actionGroupName: 'SqueezeOptimizerActions',
          description: 'Squeeze context compression, log deduplication, AST skeletonization, and secret masking tools',
          actionGroupExecutor: {
            lambda: actionGroupFunction.functionArn,
          },
          apiSchema: {
            payload: openApiSchema,
          },
        },
      ],
      autoPrepare: true,
    });

    this.agentId = agent.attrAgentId;

    const agentAlias = new bedrock.CfnAgentAlias(this, 'SqueezeAgentAlias', {
      agentId: agent.attrAgentId,
      agentAliasName: 'live',
      description: 'Live production alias for Squeeze Bedrock Agent',
    });

    agentAlias.addResourceDependency(agent);

    // ------------------------------------------------------------------------
    // Outputs
    // ------------------------------------------------------------------------
    new cdk.CfnOutput(this, 'SqueezeMcpEndpointUrl', {
      value: this.mcpEndpointUrl,
      description: 'Public HTTP/SSE Remote MCP Endpoint for Squeeze (compatible with Cursor, Claude Code, Bedrock)',
    });

    new cdk.CfnOutput(this, 'BedrockAgentId', {
      value: agent.attrAgentId,
      description: 'Amazon Bedrock Agent ID equipped with Squeeze Action Group',
    });

    new cdk.CfnOutput(this, 'BedrockAgentAliasId', {
      value: agentAlias.attrAgentAliasId,
      description: 'Amazon Bedrock Agent Live Alias ID',
    });
  }
}
