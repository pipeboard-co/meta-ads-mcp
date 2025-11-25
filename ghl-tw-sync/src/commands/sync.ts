/**
 * Sync command - Sync GHL contacts to TripleWhale orders
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { SyncEngine } from '../sync/sync-engine.js';
import { GHLClient } from '../ghl-api/ghl-client.js';
import { TWClient } from '../tw-api/tw-client.js';

export const syncCommand = new Command('sync')
  .description('Sync GoHighLevel contacts to TripleWhale orders')
  .argument('<location-id>', 'GHL Location ID')
  .argument('<shop>', 'Shop identifier (e.g., "rtt.com")')
  .option('-t, --tags <tags...>', 'Filter contacts by tags (e.g., "_customer (rtt any)")')
  .option('-l, --limit <number>', 'Limit number of contacts to sync')
  .option('--platform <platform>', 'Platform identifier (default: gohighlevel)')
  .option('--currency <currency>', 'Default currency (default: USD)')
  .option('--revenue <amount>', 'Default revenue if not in GHL (default: 0)')
  .option('--start-date <date>', 'Start date (YYYY-MM-DD)')
  .option('--end-date <date>', 'End date (YYYY-MM-DD)')
  .option('--dry-run', 'Test sync without pushing to TripleWhale')
  .option('--batch-size <size>', 'Batch size for pushing orders', '100')
  .option('--delay <ms>', 'Delay between batches in milliseconds', '1000')
  .action(async (locationId: string, shop: string, options) => {
    const spinner = ora('Initializing sync...').start();

    try {
      // Parse dates if provided
      let startDate: Date | undefined;
      let endDate: Date | undefined;

      if (options.startDate) {
        startDate = new Date(options.startDate);
        if (isNaN(startDate.getTime())) {
          spinner.fail(chalk.red('Invalid start date format'));
          console.error(chalk.yellow('Use format: YYYY-MM-DD (e.g., 2025-01-01)'));
          process.exit(1);
        }
      }

      if (options.endDate) {
        endDate = new Date(options.endDate);
        if (isNaN(endDate.getTime())) {
          spinner.fail(chalk.red('Invalid end date format'));
          console.error(chalk.yellow('Use format: YYYY-MM-DD (e.g., 2025-01-31)'));
          process.exit(1);
        }
      }

      // Create clients
      const ghlApiKey = process.env.GHL_API_KEY;
      const twApiKey = process.env.TW_API_KEY;

      if (!ghlApiKey) {
        spinner.fail(chalk.red('GHL_API_KEY not found in environment'));
        process.exit(1);
      }

      if (!twApiKey) {
        spinner.fail(chalk.red('TW_API_KEY not found in environment'));
        process.exit(1);
      }

      const ghlClient = new GHLClient({
        apiKey: ghlApiKey,
        baseUrl: process.env.GHL_API_BASE_URL || 'https://rest.gohighlevel.com',
      });

      const twClient = new TWClient({
        apiKey: twApiKey,
        baseUrl: process.env.TW_API_BASE_URL || 'https://api.triplewhale.com',
      });

      const syncEngine = new SyncEngine(ghlClient, twClient);

      spinner.text = options.dryRun
        ? 'Running dry-run sync...'
        : 'Starting sync...';

      // Run sync
      const result = await syncEngine.syncContacts({
        locationId,
        shop,
        tags: options.tags,
        platform: options.platform,
        currency: options.currency,
        defaultRevenue: options.revenue ? parseFloat(options.revenue) : undefined,
        startDate,
        endDate,
        limit: options.limit ? parseInt(options.limit) : undefined,
        dryRun: options.dryRun || false,
        batchSize: parseInt(options.batchSize),
        delayMs: parseInt(options.delay),
      });

      if (result.success) {
        spinner.succeed(chalk.green('Sync completed successfully'));
      } else {
        spinner.fail(chalk.red('Sync failed'));
      }

      // Display results
      console.log(chalk.bold('\n📊 Sync Results:'));
      console.log(`  Duration: ${chalk.cyan((result.duration / 1000).toFixed(2))}s`);
      console.log(`  Contacts Fetched: ${chalk.cyan(result.contactsFetched)}`);
      console.log(`  Orders Created: ${chalk.cyan(result.ordersCreated)}`);
      console.log(`  Orders Pushed: ${chalk.cyan(result.ordersPushed)}`);

      if (result.errors.length > 0) {
        console.log(chalk.red.bold('\n⚠️ Errors:'));
        result.errors.forEach((error) => {
          console.log(chalk.red(`  • ${error}`));
        });
      }

      if (options.dryRun) {
        console.log(chalk.yellow('\n💡 This was a dry run - no orders were actually pushed'));
        console.log(chalk.yellow('   Remove --dry-run to push orders to TripleWhale'));
      }
    } catch (error) {
      spinner.fail(chalk.red('Sync failed'));
      console.error(chalk.red(`\nError: ${error instanceof Error ? error.message : 'Unknown error'}`));
      process.exit(1);
    }
  });
