/**
 * Push Events command - Push multiple offline events from a JSON file
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { createTWClient } from '../api/tw-client.js';
import { readEventsFromFile, validateEvents, displayValidationErrors } from '../utils/file-reader.js';

export const pushEventsCommand = new Command('push-events')
  .description('Push multiple offline events from a JSON file')
  .argument('<file>', 'Path to JSON file containing events')
  .option('--no-validate', 'Skip validation before pushing')
  .option('--batch-size <size>', 'Batch size for splitting large uploads', '1000')
  .action(async (file: string, options) => {
    let spinner = ora('Reading events from file...').start();

    try {
      const events = await readEventsFromFile(file);
      spinner.succeed(chalk.green(`Loaded ${events.length} events from file`));

      // Validate events if not skipped
      if (options.validate !== false) {
        spinner = ora('Validating events...').start();
        const errors = validateEvents(events);

        if (errors.length > 0) {
          spinner.fail(chalk.red('Validation failed'));
          displayValidationErrors(errors);
          process.exit(1);
        }

        spinner.succeed(chalk.green('All events validated successfully'));
      }

      // Push events
      const client = createTWClient();
      const batchSize = parseInt(options.batchSize);

      if (events.length <= batchSize) {
        // Single batch
        spinner = ora(`Pushing ${events.length} events...`).start();
        const result = await client.pushEvents(events);
        spinner.succeed(chalk.green(`Successfully pushed ${events.length} events`));

        console.log(chalk.bold('\n✅ Response:'));
        console.log(`  Events Received: ${chalk.cyan(result.events_received)}`);
        if (result.fbtrace_id) {
          console.log(`  Trace ID: ${chalk.gray(result.fbtrace_id)}`);
        }
      } else {
        // Multiple batches
        const totalBatches = Math.ceil(events.length / batchSize);
        console.log(chalk.blue(`\n📦 Splitting into ${totalBatches} batches of ${batchSize} events each`));

        let totalPushed = 0;

        for (let i = 0; i < totalBatches; i++) {
          const start = i * batchSize;
          const end = Math.min((i + 1) * batchSize, events.length);
          const batch = events.slice(start, end);

          spinner = ora(`Pushing batch ${i + 1}/${totalBatches} (${batch.length} events)...`).start();

          const result = await client.pushEvents(batch);
          totalPushed += result.events_received;

          spinner.succeed(chalk.green(`Batch ${i + 1}/${totalBatches} complete (${result.events_received} events received)`));

          // Small delay between batches to avoid rate limits
          if (i < totalBatches - 1) {
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
        }

        console.log(chalk.bold.green(`\n✅ All batches complete! Total events pushed: ${totalPushed}`));
      }
    } catch (error) {
      spinner.fail(chalk.red('Failed to push events'));
      console.error(chalk.red(`\nError: ${error instanceof Error ? error.message : 'Unknown error'}`));
      process.exit(1);
    }
  });
