/**
 * Contacts command - List and export GHL contacts
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { createGHLClient } from '../api/ghl-client.js';
import { displayContactsTable, displaySummary } from '../utils/formatter.js';
import { exportToJSON, createExport } from '../utils/export.js';

export const contactsCommand = new Command('contacts')
  .description('List contacts from GoHighLevel')
  .argument('<location-id>', 'GHL Location ID')
  .option('-l, --limit <number>', 'Limit number of contacts', '100')
  .option('-q, --query <query>', 'Search query')
  .option('-t, --tags <tags...>', 'Filter by tags')
  .option('-e, --export <file>', 'Export to JSON file')
  .action(async (locationId: string, options) => {
    const spinner = ora('Fetching contacts from GoHighLevel...').start();

    try {
      const client = createGHLClient();

      const contacts = await client.getContacts({
        locationId,
        limit: parseInt(options.limit),
        query: options.query,
      });

      spinner.succeed(chalk.green(`Found ${contacts.length} contacts`));

      // Filter by tags if specified
      let filteredContacts = contacts;
      if (options.tags && options.tags.length > 0) {
        filteredContacts = contacts.filter((contact) =>
          options.tags.some((tag: string) => contact.tags?.includes(tag))
        );
        console.log(chalk.blue(`\nFiltered to ${filteredContacts.length} contacts with tags: ${options.tags.join(', ')}`));
      }

      // Export if requested
      if (options.export) {
        const exportData = createExport(filteredContacts, 'contacts');
        await exportToJSON(exportData, options.export);
      } else {
        // Display in terminal
        displayContactsTable(filteredContacts);

        // Display summary
        displaySummary({
          total: filteredContacts.length,
        });
      }
    } catch (error) {
      spinner.fail(chalk.red('Failed to fetch contacts'));
      console.error(chalk.red(`\nError: ${error instanceof Error ? error.message : 'Unknown error'}`));
      process.exit(1);
    }
  });
