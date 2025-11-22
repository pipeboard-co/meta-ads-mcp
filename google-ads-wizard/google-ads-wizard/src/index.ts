#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { config } from 'dotenv';
import { createGoogleAdsClient } from './api/google-ads-client.js';
import { analyzeAccount } from './analysis/claude-client.js';
import { generatePDFReport } from './generators/pdf-report.js';
import { saveCursorRules } from './utils/cursor-rules.js';

config();

const program = new Command();

program
  .name('gads')
  .description('🚀 Google Ads Wizard - AI-powered auditing CLI')
  .version('1.0.0');

// Command 1: Comprehensive Audit
program
  .command('audit')
  .description('Generate comprehensive RTT-style audit')
  .argument('<customer-id>', 'Google Ads customer ID (e.g., 8888034950)')
  .option('-o, --output <path>', 'Output file path', './audit-report.pdf')
  .option('--format <type>', 'Output format: pdf, markdown, json', 'pdf')
  .option('--compare-meta', 'Compare with Meta Ads')
  .action(async (customerId, options) => {
    console.log(chalk.blue.bold('\n🔍 Google Ads Wizard - Account Audit\n'));

    const spinner = ora('Connecting to Google Ads API...').start();

    try {
      const client = createGoogleAdsClient();

      // Fetch all data in parallel
      spinner.text = 'Fetching account data...';
      const [accountInfo, campaigns, performance, keywords, conversions] =
        await Promise.all([
          client.getAccountInfo(customerId),
          client.getCampaigns(customerId),
          client.getPerformanceMetrics(customerId),
          client.getKeywordPerformance(customerId),
          client.getConversionTracking(customerId)
        ]);

      spinner.succeed('Account data fetched');

      // Analyze with Claude
      spinner.start('Analyzing with Claude Sonnet 4 (temperature 0)...');
      const analysis = await analyzeAccount({
        accountInfo,
        campaigns,
        performance,
        keywords,
        conversions
      });
      spinner.succeed('AI analysis complete');

      // Generate report based on format
      if (options.format === 'json') {
        spinner.start('Saving JSON report...');
        const fs = await import('fs');
        fs.writeFileSync(options.output.replace('.pdf', '.json'), JSON.stringify({
          accountInfo,
          analysis,
          performance,
          campaigns: campaigns.slice(0, 10)
        }, null, 2));
        spinner.succeed(`JSON report saved to ${options.output.replace('.pdf', '.json')}`);
      } else if (options.format === 'pdf') {
        spinner.start('Generating RTT-style PDF report...');
        await generatePDFReport({
          accountInfo,
          analysis,
          performance,
          campaigns
        }, options.output);
        spinner.succeed(`PDF report saved to ${options.output}`);
      }

      // Generate .cursor/rules (PostHog Wizard pattern)
      spinner.start('Generating .cursor/rules context...');
      const rulesPath = saveCursorRules({
        accountInfo,
        auditDate: new Date().toISOString(),
        keyMetrics: performance,
        criticalIssues: analysis.critical_issues?.map((i: any) => i.title) || [],
        recommendations: analysis.recommendations || [],
        activeCampaigns: campaigns.filter((c: any) => c.campaign?.status === 'ENABLED'),
        accountHealthScore: analysis.account_health_score
      });
      spinner.succeed('.cursor/rules updated');

      // Display summary
      console.log(chalk.green.bold('\n✅ Audit Complete!\n'));
      console.log(chalk.cyan('Account:'), accountInfo.descriptive_name);
      console.log(chalk.cyan('Health Score:'), `${analysis.account_health_score}/10`);
      console.log(chalk.cyan('Critical Issues:'), analysis.critical_issues?.length || 0);
      console.log(chalk.cyan('Recommendations:'), analysis.recommendations?.length || 0);

      console.log(chalk.yellow('\n📁 Files Generated:'));
      console.log(chalk.gray('  • Report:'), options.output);
      console.log(chalk.gray('  • Context:'), rulesPath);

      console.log(chalk.blue('\n💡 Next Steps:'));
      console.log(chalk.gray('  • Review the PDF report'));
      console.log(chalk.gray('  • Check .cursor/rules for AI context'));
      console.log(chalk.gray('  • Run: npm run dev -- campaigns ' + customerId));

    } catch (error) {
      spinner.fail('Audit failed');
      console.error(chalk.red('\n❌ Error:'), (error as Error).message);
      if ((error as Error).message.includes('refresh_token')) {
        console.log(chalk.yellow('\n💡 Tip: Make sure GOOGLE_ADS_REFRESH_TOKEN is set in your .env file'));
      }
      process.exit(1);
    }
  });

// Command 2: List Campaigns
program
  .command('campaigns')
  .description('List campaigns with performance')
  .argument('<customer-id>', 'Google Ads customer ID')
  .option('--status <status>', 'Filter: active, paused, all', 'all')
  .action(async (customerId, options) => {
    console.log(chalk.blue.bold('\n📊 Google Ads Campaigns\n'));

    const spinner = ora('Fetching campaigns...').start();

    try {
      const client = createGoogleAdsClient();

      const [accountInfo, campaigns] = await Promise.all([
        client.getAccountInfo(customerId),
        client.getCampaigns(customerId)
      ]);

      spinner.succeed(`Found ${campaigns.length} campaigns`);

      // Filter by status
      let filteredCampaigns = campaigns;
      if (options.status !== 'all') {
        const statusFilter = options.status.toUpperCase();
        filteredCampaigns = campaigns.filter((c: any) =>
          statusFilter === 'ACTIVE' ? c.campaign?.status === 'ENABLED' :
          statusFilter === 'PAUSED' ? c.campaign?.status === 'PAUSED' :
          true
        );
      }

      // Display account info
      console.log(chalk.cyan('\nAccount:'), accountInfo.descriptive_name);
      console.log(chalk.cyan('Customer ID:'), accountInfo.id);
      console.log(chalk.cyan('Currency:'), accountInfo.currency_code);
      console.log(chalk.gray('─'.repeat(80)));

      // Display campaigns
      if (filteredCampaigns.length === 0) {
        console.log(chalk.yellow('\nNo campaigns found matching the filter.'));
      } else {
        filteredCampaigns.forEach((c: any, idx: number) => {
          const campaign = c.campaign;
          const metrics = c.metrics;
          const budget = c.campaign_budget;

          console.log(chalk.bold(`\n${idx + 1}. ${campaign?.name || 'Unnamed Campaign'}`));

          // Status
          const status = campaign?.status || 'UNKNOWN';
          const statusColor = status === 'ENABLED' ? chalk.green : status === 'PAUSED' ? chalk.yellow : chalk.gray;
          console.log(`   Status: ${statusColor(status)}`);

          // Type
          console.log(`   Type: ${campaign?.advertising_channel_type || 'Unknown'}`);

          // Budget
          if (budget?.amount_micros) {
            const budgetAmount = (budget.amount_micros / 1000000).toFixed(2);
            console.log(`   Budget: ${accountInfo.currency_code} ${budgetAmount}`);
          }

          // Performance
          if (metrics) {
            const spend = (metrics.cost_micros / 1000000).toFixed(2);
            const ctr = ((metrics.ctr || 0) * 100).toFixed(2);
            const cpc = (metrics.average_cpc / 1000000).toFixed(2);

            console.log(`   Performance (Last 30 days):`);
            console.log(`     • Spend: ${accountInfo.currency_code} ${spend}`);
            console.log(`     • Impressions: ${(metrics.impressions || 0).toLocaleString()}`);
            console.log(`     • Clicks: ${(metrics.clicks || 0).toLocaleString()}`);
            console.log(`     • CTR: ${ctr}%`);
            console.log(`     • Avg CPC: ${accountInfo.currency_code} ${cpc}`);
            console.log(`     • Conversions: ${metrics.conversions || 0}`);
          }
        });

        console.log(chalk.gray('\n' + '─'.repeat(80)));
        console.log(chalk.green(`\nTotal: ${filteredCampaigns.length} campaigns`));
      }

      console.log(chalk.blue('\n💡 Next Steps:'));
      console.log(chalk.gray('  • Run full audit: npm run dev -- audit ' + customerId));
      console.log(chalk.gray('  • Filter active: npm run dev -- campaigns ' + customerId + ' --status active'));

    } catch (error) {
      spinner.fail('Failed to fetch campaigns');
      console.error(chalk.red('\n❌ Error:'), (error as Error).message);
      if ((error as Error).message.includes('refresh_token')) {
        console.log(chalk.yellow('\n💡 Tip: Make sure GOOGLE_ADS_REFRESH_TOKEN is set in your .env file'));
      }
      process.exit(1);
    }
  });

// Command 3: Cross-Platform Comparison
program
  .command('compare')
  .description('Compare Google Ads vs Meta Ads')
  .argument('<google-id>', 'Google Ads customer ID')
  .argument('<meta-id>', 'Meta Ads account ID')
  .action(async (googleId, metaId) => {
    console.log(chalk.blue.bold('\n🔄 Cross-Platform Comparison\n'));

    const spinner = ora('Comparing platforms...').start();

    try {
      // TODO: Implement cross-platform comparison
      spinner.info('Comparison functionality coming in Phase 3');

      console.log(chalk.gray('Google Ads ID:'), googleId);
      console.log(chalk.gray('Meta Ads ID:'), metaId);

    } catch (error) {
      spinner.fail('Comparison failed');
      console.error(chalk.red('\nError:'), (error as Error).message);
      process.exit(1);
    }
  });

// Command 4: Setup Wizard
program
  .command('setup')
  .description('Interactive credential setup')
  .action(async () => {
    console.log(chalk.blue.bold('\n⚙️  Google Ads Wizard Setup\n'));

    console.log(chalk.yellow('Setup steps:'));
    console.log(chalk.gray('1. Copy .env.example to .env'));
    console.log(chalk.gray('2. Add your Google Ads API credentials'));
    console.log(chalk.gray('3. Add your Anthropic API key'));
    console.log(chalk.gray('4. Run: gads campaigns <customer-id> to test'));

    console.log(chalk.blue('\n📖 Documentation:'));
    console.log(chalk.gray('Google Ads API: https://developers.google.com/google-ads/api/docs/start'));
    console.log(chalk.gray('Anthropic API: https://docs.anthropic.com/en/api/getting-started'));
  });

// Show help if no command provided
if (process.argv.length === 2) {
  program.help();
}

program.parse(process.argv);
