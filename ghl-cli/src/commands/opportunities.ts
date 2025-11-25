/**
 * Opportunities command - List and export GHL opportunities
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { createGHLClient } from '../api/ghl-client.js';
import { displayOpportunitiesTable, displaySummary } from '../utils/formatter.js';
import { exportToJSON, createExport } from '../utils/export.js';
import type { GHLOpportunity } from '../types/ghl.js';

export const opportunitiesCommand = new Command('opportunities')
  .description('List opportunities from GoHighLevel')
  .argument('<location-id>', 'GHL Location ID')
  .option('-l, --limit <number>', 'Limit number of opportunities', '100')
  .option('-p, --pipeline <pipeline-id>', 'Filter by pipeline ID')
  .option('-s, --status <status>', 'Filter by status (open, won, lost, abandoned, all)', 'all')
  .option('-e, --export <file>', 'Export to JSON file')
  .action(async (locationId: string, options) => {
    const spinner = ora('Fetching opportunities from GoHighLevel...').start();

    try {
      const client = createGHLClient();

      // Validate status
      const validStatuses = ['open', 'won', 'lost', 'abandoned', 'all'];
      if (!validStatuses.includes(options.status)) {
        spinner.fail(chalk.red(`Invalid status: ${options.status}`));
        console.error(chalk.yellow(`Valid statuses: ${validStatuses.join(', ')}`));
        process.exit(1);
      }

      const opportunities = await client.getOpportunities({
        locationId,
        limit: parseInt(options.limit),
        pipelineId: options.pipeline,
        status: options.status,
      });

      spinner.succeed(chalk.green(`Found ${opportunities.length} opportunities`));

      // Export if requested
      if (options.export) {
        const exportData = createExport(opportunities, 'opportunities');
        await exportToJSON(exportData, options.export);
      } else {
        // Display in terminal
        displayOpportunitiesTable(opportunities);

        // Calculate summary statistics
        const stats = calculateStats(opportunities);
        displaySummary(stats);
      }
    } catch (error) {
      spinner.fail(chalk.red('Failed to fetch opportunities'));
      console.error(chalk.red(`\nError: ${error instanceof Error ? error.message : 'Unknown error'}`));
      process.exit(1);
    }
  });

/**
 * Calculate summary statistics for opportunities
 */
function calculateStats(opportunities: GHLOpportunity[]): {
  total: number;
  open: number;
  won: number;
  lost: number;
  totalValue: number;
} {
  const stats = {
    total: opportunities.length,
    open: 0,
    won: 0,
    lost: 0,
    totalValue: 0,
  };

  opportunities.forEach((opp) => {
    if (opp.status === 'open') stats.open++;
    if (opp.status === 'won') stats.won++;
    if (opp.status === 'lost') stats.lost++;
    stats.totalValue += opp.monetaryValue || 0;
  });

  return stats;
}
