import * as cdk from 'aws-cdk-lib';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import { Construct } from 'constructs';

export class SqueezeDashboardStack extends cdk.Stack {
  public readonly dashboardName: string;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.dashboardName = 'Squeeze-AI-Token-Optimizer';

    const dashboard = new cloudwatch.Dashboard(this, 'SqueezeCloudWatchDashboard', {
      dashboardName: this.dashboardName,
      defaultInterval: cdk.Duration.hours(1),
    });

    // ------------------------------------------------------------------------
    // CloudWatch Metrics Definition (Namespace: SqueezeAI)
    // ------------------------------------------------------------------------
    const tokensBeforeMetric = new cloudwatch.Metric({
      namespace: 'SqueezeAI',
      metricName: 'TokensBefore',
      statistic: 'Sum',
      period: cdk.Duration.minutes(1),
      label: 'Raw Tokens Ingested',
      color: '#FF6384',
    });

    const tokensAfterMetric = new cloudwatch.Metric({
      namespace: 'SqueezeAI',
      metricName: 'TokensAfter',
      statistic: 'Sum',
      period: cdk.Duration.minutes(1),
      label: 'Squeezed Tokens Sent to Bedrock',
      color: '#36A2EB',
    });

    const tokensSavedMetric = new cloudwatch.Metric({
      namespace: 'SqueezeAI',
      metricName: 'TokensSaved',
      statistic: 'Sum',
      period: cdk.Duration.minutes(1),
      label: 'Tokens Saved',
      color: '#4BC0C0',
    });

    const costSavedMetric = new cloudwatch.Metric({
      namespace: 'SqueezeAI',
      metricName: 'EstimatedCostSavedUSD',
      statistic: 'Sum',
      period: cdk.Duration.minutes(1),
      label: 'Cost Saved (USD @ Sonnet $3/M)',
      color: '#FFCE56',
    });

    const secretsMaskedMetric = new cloudwatch.Metric({
      namespace: 'SqueezeAI',
      metricName: 'SecretsMasked',
      statistic: 'Sum',
      period: cdk.Duration.minutes(1),
      label: 'DLP Credentials Masked',
      color: '#9966FF',
    });

    // Compression Ratio Math Expression: ((TokensBefore - TokensAfter) / TokensBefore) * 100
    const compressionRatioMetric = new cloudwatch.MathExpression({
      expression: '((m1 - m2) / m1) * 100',
      usingMetrics: {
        m1: tokensBeforeMetric,
        m2: tokensAfterMetric,
      },
      label: 'Compression Ratio (%)',
      period: cdk.Duration.minutes(1),
      color: '#2ECC71',
    });

    // ------------------------------------------------------------------------
    // Dashboard Layout & Widgets
    // ------------------------------------------------------------------------
    dashboard.addWidgets(
      new cloudwatch.TextWidget({
        markdown:
          '# ⚡ SQUEEZE AI - LIVE CONTEXT OPTIMIZATION & DLP MONITOR\n' +
          'Universal LLM context compressor running natively on AWS Bedrock, Lambda, and CloudWatch.\n' +
          '**Deduplicates logs • Skeletons AST • Folds JSON • Masks secrets • Cuts token costs by 80–95%**',
        width: 24,
        height: 2,
      })
    );

    // Row 1: KPI Gauges & Counters
    dashboard.addWidgets(
      new cloudwatch.SingleValueWidget({
        title: '💎 Cumulative Tokens Saved',
        metrics: [tokensSavedMetric],
        width: 6,
        height: 4,
      }),
      new cloudwatch.SingleValueWidget({
        title: '💵 Estimated Cost Saved ($ USD)',
        metrics: [costSavedMetric],
        width: 6,
        height: 4,
      }),
      new cloudwatch.SingleValueWidget({
        title: '🛡️ DLP Secrets Intercepted',
        metrics: [secretsMaskedMetric],
        width: 6,
        height: 4,
      }),
      new cloudwatch.SingleValueWidget({
        title: '📉 Real-Time Compression Ratio',
        metrics: [compressionRatioMetric],
        width: 6,
        height: 4,
      })
    );

    // Row 2: Ingestion vs Squeezed Time Series
    dashboard.addWidgets(
      new cloudwatch.GraphWidget({
        title: '📊 Raw Tokens vs Squeezed Tokens Ingested Over Time',
        left: [tokensBeforeMetric, tokensAfterMetric],
        width: 16,
        height: 6,
      }),
      new cloudwatch.GraphWidget({
        title: '📈 Token Compression % Efficiency',
        left: [compressionRatioMetric],
        leftYAxis: { min: 0, max: 100 },
        width: 8,
        height: 6,
      })
    );

    new cdk.CfnOutput(this, 'CloudWatchDashboardNameOutput', {
      value: this.dashboardName,
      description: 'Access the Squeeze AI metrics dashboard in AWS CloudWatch Console',
    });
  }
}
