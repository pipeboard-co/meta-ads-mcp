#!/usr/bin/env node

/**
 * GHL-TW Sync Tool
 * Sync GoHighLevel data to TripleWhale attribution dashboard
 */

import { Command } from 'commander';
import dotenv from 'dotenv';
import chalk from 'chalk';
import { syncCommand } from './commands/sync.js';
import { testCommand } from './commands/test.js';
import { importCsvCommand } from './commands/import-csv.js';

// Load environment variables
dotenv.config();

const program = new Command();

program
  .name('ghl-tw-sync')
  .description('Sync GoHighLevel data to TripleWhale attribution dashboard')
  .version('1.0.0');

// Add commands
program.addCommand(syncCommand);
program.addCommand(testCommand);
program.addCommand(importCsvCommand);

// Setup command - display configuration and help
program
  .command('setup')
  .description('Show setup information and configuration')
  .action(() => {
    console.log(chalk.bold.cyan('\n🔄 GHL-TW Sync Tool Setup\n'));

    const ghlApiKey = process.env.GHL_API_KEY;
    const ghlLocationId = process.env.GHL_LOCATION_ID;
    const twApiKey = process.env.TW_API_KEY;
    const twShop = process.env.TW_SHOP || process.env.TW_SHOP_ID;

    console.log(chalk.bold('GoHighLevel Configuration:'));
    console.log(`  API Key: ${ghlApiKey ? chalk.green('✓ Set') : chalk.red('✗ Not set')}`);
    console.log(`  Location ID: ${ghlLocationId ? chalk.green('✓ Set') : chalk.yellow('Optional (can specify in command)')}`);

    console.log(chalk.bold('\nTripleWhale Configuration:'));
    console.log(`  API Key: ${twApiKey ? chalk.green('✓ Set') : chalk.red('✗ Not set')}`);
    console.log(`  Shop: ${twShop ? chalk.green(`✓ Set (${twShop})`) : chalk.yellow('Required (specify in command or .env)')}`);

    if (!ghlApiKey || !twApiKey) {
      console.log(chalk.yellow('\n⚠️  Warning: Missing required API keys'));
      console.log(chalk.yellow('   Set them in your .env file\n'));
    } else {
      console.log(chalk.green('\n✅ Configuration looks good!\n'));
    }

    console.log(chalk.bold('Quick Start:'));
    console.log(chalk.gray('  # Test sync with tagged contacts'));
    console.log(chalk.cyan('  ghl-tw-sync test <location-id> <shop> --tags "_customer (rtt any)"\n'));
    console.log(chalk.gray('  # Dry-run sync (no data pushed)'));
    console.log(chalk.cyan('  ghl-tw-sync sync <location-id> <shop> --tags "_customer (rtt any)" --dry-run\n'));
    console.log(chalk.gray('  # Full sync with multiple tags'));
    console.log(chalk.cyan('  ghl-tw-sync sync <location-id> <shop> --tags "_customer (rtt any)" "_customer (rtc any)"\n'));
    console.log(chalk.gray('  # Sync with custom currency and revenue'));
    console.log(chalk.cyan('  ghl-tw-sync sync <location-id> <shop> --currency GBP --revenue 150.75\n'));

    console.log(chalk.bold('Data Flow:'));
    console.log(chalk.blue(`
  1. Fetch contacts from GoHighLevel (filtered by tags)
  2. Transform to TripleWhale order records
     - Contact info → Customer data
     - Contact date → Order created_at
     - Custom fields → Order revenue (if available)
  3. Push orders to TripleWhale data-in/orders endpoint
    `));

    console.log(chalk.bold('Customer Tags:'));
    console.log(chalk.cyan('  • _customer (rtt any)'));
    console.log(chalk.cyan('  • _customer (rtc any)'));
    console.log(chalk.cyan('  • _customer (ciah)'));
    console.log(chalk.cyan('  • _customer (rtt integrated)\n'));

    console.log(chalk.bold('Documentation:'));
    console.log(chalk.blue('  GHL API: https://highlevel.stoplight.io/docs/integrations'));
    console.log(chalk.blue('  TripleWhale API: https://triplewhale.readme.io/reference'));
    console.log(chalk.blue('  GitHub: [Coming Soon]\n'));
  });

// Error handling
program.exitOverride();

try {
  program.parse(process.argv);
} catch (error: any) {
  if (error.code === 'commander.helpDisplayed') {
    // Help was displayed, exit normally
    process.exit(0);
  } else if (error.code === 'commander.missingArgument') {
    console.error(chalk.red(`\nError: ${error.message}`));
    console.log(chalk.yellow('\nRun with --help for usage information'));
    process.exit(1);
  } else {
    console.error(chalk.red(`\nUnexpected error: ${error.message}`));
    process.exit(1);
  }
}
