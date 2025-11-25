/**
 * Test command - Test sync with a small sample
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { SyncEngine } from '../sync/sync-engine.js';
import { GHLClient } from '../ghl-api/ghl-client.js';
import { TWClient } from '../tw-api/tw-client.js';

export const testCommand = new Command('test')
  .description('Test sync with a small sample (dry-run with 10 contacts)')
  .argument('<location-id>', 'GHL Location ID')
  .argument('<shop>', 'Shop identifier (e.g., "rtt.com")')
  .option('-t, --tags <tags...>', 'Filter contacts by tags (e.g., "_customer (rtt any)")')
  .option('-l, --limit <number>', 'Number of contacts to test', '10')
  .action(async (locationId: string, shop: string, options) => {
    const spinner = ora('Initializing test sync...').start();

    try {
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

      spinner.text = `Testing sync with ${options.limit} contacts...`;

      // Run test sync
      const result = await syncEngine.testSync(
        locationId,
        shop,
        options.tags,
        parseInt(options.limit)
      );

      if (result.success) {
        spinner.succeed(chalk.green('Test completed successfully'));
      } else {
        spinner.fail(chalk.red('Test failed'));
      }

      // Display results
      console.log(chalk.bold('\n📊 Test Results:'));
      console.log(`  Duration: ${chalk.cyan((result.duration / 1000).toFixed(2))}s`);
      console.log(`  Contacts Fetched: ${chalk.cyan(result.contactsFetched)}`);
      console.log(`  Orders Created: ${chalk.cyan(result.ordersCreated)}`);

      if (result.errors.length > 0) {
        console.log(chalk.red.bold('\n⚠️ Errors:'));
        result.errors.forEach((error) => {
          console.log(chalk.red(`  • ${error}`));
        });
      } else {
        console.log(chalk.green('\n✅ No errors - ready for production sync'));
        console.log(chalk.blue('\nRun without --dry-run to push orders to TripleWhale:'));

        const tagsOption = options.tags ? ` --tags ${options.tags.join(' ')}` : '';
        console.log(chalk.cyan(`  ghl-tw-sync sync ${locationId} ${shop}${tagsOption}`));
      }
    } catch (error) {
      spinner.fail(chalk.red('Test failed'));
      console.error(chalk.red(`\nError: ${error instanceof Error ? error.message : 'Unknown error'}`));
      process.exit(1);
    }
  });
