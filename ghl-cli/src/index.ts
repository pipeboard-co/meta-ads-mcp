#!/usr/bin/env node

/**
 * GoHighLevel CLI Tool
 * Manage contacts and opportunities from the command line
 */

import { Command } from 'commander';
import dotenv from 'dotenv';
import chalk from 'chalk';
import { contactsCommand } from './commands/contacts.js';
import { opportunitiesCommand } from './commands/opportunities.js';

// Load environment variables
dotenv.config();

const program = new Command();

program
  .name('ghl')
  .description('GoHighLevel CLI - Manage contacts and opportunities')
  .version('1.0.0');

// Add commands
program.addCommand(contactsCommand);
program.addCommand(opportunitiesCommand);

// Setup command - display configuration and help
program
  .command('setup')
  .description('Show setup information and configuration')
  .action(() => {
    console.log(chalk.bold.cyan('\n🚀 GoHighLevel CLI Setup\n'));

    const apiKey = process.env.GHL_API_KEY;
    const locationId = process.env.GHL_LOCATION_ID;
    const baseUrl = process.env.GHL_API_BASE_URL || 'https://rest.gohighlevel.com';

    console.log(chalk.bold('Configuration:'));
    console.log(`  API Key: ${apiKey ? chalk.green('✓ Set') : chalk.red('✗ Not set')}`);
    console.log(`  Location ID: ${locationId ? chalk.green('✓ Set') : chalk.yellow('Optional')}`);
    console.log(`  Base URL: ${chalk.blue(baseUrl)}`);

    if (!apiKey) {
      console.log(chalk.yellow('\n⚠️  Warning: GHL_API_KEY not found in environment variables'));
      console.log(chalk.yellow('   Set it in your .env file or export it in your shell\n'));
    } else {
      console.log(chalk.green('\n✅ Configuration looks good!\n'));
    }

    console.log(chalk.bold('Quick Start:'));
    console.log(chalk.gray('  # List contacts'));
    console.log(chalk.cyan('  ghl contacts <location-id>\n'));
    console.log(chalk.gray('  # List opportunities'));
    console.log(chalk.cyan('  ghl opportunities <location-id>\n'));
    console.log(chalk.gray('  # Export contacts to JSON'));
    console.log(chalk.cyan('  ghl contacts <location-id> --export contacts.json\n'));

    console.log(chalk.bold('Documentation:'));
    console.log(chalk.blue('  GoHighLevel API: https://highlevel.stoplight.io/docs/integrations'));
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
