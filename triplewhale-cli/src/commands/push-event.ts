/**
 * Push Event command - Push a single offline event to TripleWhale
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { createTWClient } from '../api/tw-client.js';
import type { PushEventOptions } from '../types/triplewhale.js';

export const pushEventCommand = new Command('push-event')
  .description('Push a single offline event to TripleWhale')
  .requiredOption('-n, --name <event-name>', 'Event name (e.g., "Purchase", "Lead", "Contact")')
  .requiredOption('-s, --source <action-source>', 'Action source (physical_store, phone_call, email, system_generated, other)')
  .option('-e, --email <email>', 'Customer email')
  .option('-p, --phone <phone>', 'Customer phone number')
  .option('--first-name <name>', 'Customer first name')
  .option('--last-name <name>', 'Customer last name')
  .option('--city <city>', 'Customer city')
  .option('--state <state>', 'Customer state')
  .option('--zip <zip>', 'Customer zip code')
  .option('--country <country>', 'Customer country')
  .option('--external-id <id>', 'Customer ID from your system')
  .option('--value <value>', 'Event value (e.g., order total)')
  .option('--currency <currency>', 'Currency code (default: USD)', 'USD')
  .option('--content-name <name>', 'Product or content name')
  .option('--order-id <id>', 'Order ID')
  .action(async (options) => {
    const spinner = ora('Pushing event to TripleWhale...').start();

    try {
      const client = createTWClient();

      // Validate at least one user identifier
      if (!options.email && !options.phone && !options.externalId) {
        spinner.fail(chalk.red('Must provide at least one user identifier'));
        console.error(chalk.yellow('\nRequired: --email, --phone, or --external-id'));
        process.exit(1);
      }

      // Validate action source
      const validSources = ['physical_store', 'phone_call', 'email', 'system_generated', 'other'];
      if (!validSources.includes(options.source)) {
        spinner.fail(chalk.red(`Invalid action source: ${options.source}`));
        console.error(chalk.yellow(`\nValid sources: ${validSources.join(', ')}`));
        process.exit(1);
      }

      const pushOptions: PushEventOptions = {
        eventName: options.name,
        actionSource: options.source,
        userData: {
          email: options.email,
          phone: options.phone,
          firstName: options.firstName,
          lastName: options.lastName,
          city: options.city,
          state: options.state,
          zipCode: options.zip,
          country: options.country,
          externalId: options.externalId,
        },
      };

      if (options.value || options.currency || options.contentName || options.orderId) {
        pushOptions.customData = {
          value: options.value ? parseFloat(options.value) : undefined,
          currency: options.currency,
          contentName: options.contentName,
          orderId: options.orderId,
        };
      }

      const result = await client.pushEvent(pushOptions);

      spinner.succeed(chalk.green('Event pushed successfully'));

      console.log(chalk.bold('\n✅ Response:'));
      console.log(`  Events Received: ${chalk.cyan(result.events_received)}`);
      if (result.fbtrace_id) {
        console.log(`  Trace ID: ${chalk.gray(result.fbtrace_id)}`);
      }
      if (result.messages && result.messages.length > 0) {
        console.log(`  Messages: ${result.messages.join(', ')}`);
      }

      console.log(chalk.bold('\n📊 Event Details:'));
      console.log(`  Name: ${chalk.cyan(options.name)}`);
      console.log(`  Source: ${chalk.cyan(options.source)}`);
      if (options.email) console.log(`  Email: ${options.email}`);
      if (options.phone) console.log(`  Phone: ${options.phone}`);
      if (options.value) console.log(`  Value: ${options.currency} ${options.value}`);
    } catch (error) {
      spinner.fail(chalk.red('Failed to push event'));
      console.error(chalk.red(`\nError: ${error instanceof Error ? error.message : 'Unknown error'}`));
      process.exit(1);
    }
  });
