#!/usr/bin/env node

/**
 * TripleWhale CLI Tool
 * Push offline events and view attribution metrics from the command line
 */

import { Command } from 'commander';
import dotenv from 'dotenv';
import chalk from 'chalk';
import { pushEventCommand } from './commands/push-event.js';
import { pushEventsCommand } from './commands/push-events.js';

// Load environment variables
dotenv.config();

const program = new Command();

program
  .name('tw')
  .description('TripleWhale CLI - Push offline events and view attribution metrics')
  .version('1.0.0');

// Add commands
program.addCommand(pushEventCommand);
program.addCommand(pushEventsCommand);

// Setup command - display configuration and help
program
  .command('setup')
  .description('Show setup information and configuration')
  .action(() => {
    console.log(chalk.bold.cyan('\n🐋 TripleWhale CLI Setup\n'));

    const apiKey = process.env.TW_API_KEY;
    const shopId = process.env.TW_SHOP_ID;
    const baseUrl = process.env.TW_API_BASE_URL || 'https://api.triplewhale.com';

    console.log(chalk.bold('Configuration:'));
    console.log(`  API Key: ${apiKey ? chalk.green('✓ Set') : chalk.red('✗ Not set')}`);
    console.log(`  Shop ID: ${shopId ? chalk.green('✓ Set') : chalk.yellow('Optional')}`);
    console.log(`  Base URL: ${chalk.blue(baseUrl)}`);

    if (!apiKey) {
      console.log(chalk.yellow('\n⚠️  Warning: TW_API_KEY not found in environment variables'));
      console.log(chalk.yellow('   Set it in your .env file or export it in your shell\n'));
    } else {
      console.log(chalk.green('\n✅ Configuration looks good!\n'));
    }

    console.log(chalk.bold('Quick Start:'));
    console.log(chalk.gray('  # Push a single event'));
    console.log(chalk.cyan('  tw push-event --name "Purchase" --source phone_call --email customer@example.com --value 99.99\n'));
    console.log(chalk.gray('  # Push events from a JSON file'));
    console.log(chalk.cyan('  tw push-events events.json\n'));

    console.log(chalk.bold('Event File Format:'));
    console.log(chalk.gray('  JSON file with array of events or object with "data" property'));
    console.log(chalk.blue(`
{
  "data": [
    {
      "event_name": "Purchase",
      "event_time": 1642089600,
      "action_source": "phone_call",
      "user_data": {
        "email": ["customer@example.com"],
        "phone": ["5551234567"]
      },
      "custom_data": {
        "currency": "USD",
        "value": 99.99,
        "order_id": "ORDER-123"
      }
    }
  ]
}
    `));

    console.log(chalk.bold('Documentation:'));
    console.log(chalk.blue('  TripleWhale API: https://triplewhale.com/api-docs'));
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
