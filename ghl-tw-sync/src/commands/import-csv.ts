/**
 * Import CSV command - Sync contacts from a CSV export
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import fs from 'fs';
import { parse } from 'csv-parse/sync';
import { SyncEngine } from '../sync/sync-engine.js';
import { GHLClient } from '../ghl-api/ghl-client.js';
import { TWClient } from '../tw-api/tw-client.js';
import type { GHLContact } from '../types/ghl.js';

interface CSVContact {
  'Contact Id': string;
  'First Name': string;
  'Last Name': string;
  'Name': string;
  'Phone': string;
  'Email': string;
  'Created': string;
  'Last Activity': string;
  'Tags': string;
}

export const importCsvCommand = new Command('import-csv')
  .description('Sync contacts from a GHL CSV export file')
  .argument('<csv-file>', 'Path to CSV file exported from GHL')
  .argument('<shop>', 'Shop identifier (e.g., "rtt.com")')
  .option('--platform <platform>', 'Platform identifier (default: gohighlevel)')
  .option('--currency <currency>', 'Default currency (default: USD)')
  .option('--revenue <amount>', 'Default revenue if not in GHL (default: 0)')
  .option('--dry-run', 'Test sync without pushing to TripleWhale')
  .option('--batch-size <size>', 'Batch size for pushing orders', '100')
  .option('--delay <ms>', 'Delay between batches in milliseconds', '1000')
  .option('-l, --limit <number>', 'Limit number of contacts to sync (for testing)')
  .action(async (csvFile: string, shop: string, options) => {
    const spinner = ora('Reading CSV file...').start();

    try {
      // Check if file exists
      if (!fs.existsSync(csvFile)) {
        spinner.fail(chalk.red(`CSV file not found: ${csvFile}`));
        process.exit(1);
      }

      // Read and parse CSV
      const fileContent = fs.readFileSync(csvFile, 'utf-8');
      const records = parse(fileContent, {
        columns: true,
        skip_empty_lines: true,
      }) as CSVContact[];

      spinner.succeed(chalk.green(`Found ${records.length} contacts in CSV`));

      // Apply limit if specified
      const contactsToSync = options.limit
        ? records.slice(0, parseInt(options.limit))
        : records;

      if (options.limit) {
        console.log(chalk.yellow(`Limiting to ${contactsToSync.length} contacts for testing`));
      }

      // Convert CSV records to GHLContact format
      spinner.start('Converting CSV contacts to GHL format...');
      const contacts: GHLContact[] = contactsToSync.map((record) => ({
        id: record['Contact Id'],
        firstName: record['First Name'],
        lastName: record['Last Name'],
        name: record['Name'],
        email: record['Email'],
        phone: record['Phone'],
        dateAdded: record['Created'],
        tags: record['Tags'] ? record['Tags'].split(', ').map(tag => tag.trim()) : [],
        // Add other fields as needed
      }));

      spinner.succeed(chalk.green(`Converted ${contacts.length} contacts`));

      // Initialize clients
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

      // Run sync with CSV contacts
      spinner.start('Syncing contacts to TripleWhale...');

      const result = await syncEngine.syncFromCSV({
        contacts,
        shop,
        platform: options.platform || 'gohighlevel',
        currency: options.currency || 'USD',
        defaultRevenue: options.revenue ? parseFloat(options.revenue) : 0,
        dryRun: options.dryRun || false,
        batchSize: parseInt(options.batchSize),
        batchDelay: parseInt(options.delay),
      });

      if (result.success) {
        spinner.succeed(chalk.green('Sync completed successfully'));
      } else {
        spinner.fail(chalk.red('Sync completed with errors'));
      }

      // Display results
      console.log(chalk.bold('\n📊 Sync Results:'));
      console.log(`  Duration: ${chalk.cyan((result.duration / 1000).toFixed(2))}s`);
      console.log(`  Contacts Processed: ${chalk.cyan(result.contactsFetched)}`);
      console.log(`  Orders Created: ${chalk.cyan(result.ordersCreated)}`);

      if (options.dryRun) {
        console.log(chalk.yellow('\n⚠️  DRY RUN - No data was pushed to TripleWhale'));
        console.log(chalk.blue('\nRun without --dry-run to push orders:'));
        console.log(chalk.cyan(`  ghl-tw-sync import-csv "${csvFile}" ${shop}`));
      }

      if (result.errors.length > 0) {
        console.log(chalk.red.bold('\n⚠️ Errors:'));
        result.errors.slice(0, 10).forEach((error) => {
          console.log(chalk.red(`  • ${error}`));
        });
        if (result.errors.length > 10) {
          console.log(chalk.red(`  ... and ${result.errors.length - 10} more errors`));
        }
      } else {
        console.log(chalk.green('\n✅ No errors'));
      }
    } catch (error) {
      spinner.fail(chalk.red('Import failed'));
      console.error(chalk.red(`\nError: ${error instanceof Error ? error.message : 'Unknown error'}`));
      process.exit(1);
    }
  });
