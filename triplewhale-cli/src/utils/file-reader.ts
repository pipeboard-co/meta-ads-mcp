/**
 * Utility functions for reading and parsing event files
 */

import { readFile } from 'fs/promises';
import chalk from 'chalk';
import type { TWOfflineEvent } from '../types/triplewhale.js';

/**
 * Read events from a JSON file
 * @param filepath Path to JSON file
 * @returns Array of offline events
 */
export async function readEventsFromFile(filepath: string): Promise<TWOfflineEvent[]> {
  try {
    const content = await readFile(filepath, 'utf-8');
    const parsed = JSON.parse(content);

    // Handle both array format and object with data property
    let events: TWOfflineEvent[];

    if (Array.isArray(parsed)) {
      events = parsed;
    } else if (parsed.data && Array.isArray(parsed.data)) {
      events = parsed.data;
    } else if (parsed.events && Array.isArray(parsed.events)) {
      events = parsed.events;
    } else {
      throw new Error('Invalid file format. Expected array of events or object with "data" property');
    }

    return events;
  } catch (error) {
    if (error instanceof SyntaxError) {
      throw new Error(`Invalid JSON in file: ${filepath}`);
    }
    throw new Error(`Failed to read events from file: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Validate events array
 * @param events Array of events to validate
 * @returns Validation errors (empty if valid)
 */
export function validateEvents(events: any[]): string[] {
  const errors: string[] = [];

  if (!Array.isArray(events)) {
    errors.push('Events must be an array');
    return errors;
  }

  events.forEach((event, index) => {
    const eventNum = index + 1;

    if (!event.event_name) {
      errors.push(`Event #${eventNum}: Missing event_name`);
    }

    if (!event.event_time) {
      errors.push(`Event #${eventNum}: Missing event_time`);
    } else if (typeof event.event_time !== 'number') {
      errors.push(`Event #${eventNum}: event_time must be a Unix timestamp (number)`);
    }

    if (!event.action_source) {
      errors.push(`Event #${eventNum}: Missing action_source`);
    }

    if (!event.user_data) {
      errors.push(`Event #${eventNum}: Missing user_data`);
    } else {
      const hasIdentifier =
        event.user_data.email ||
        event.user_data.phone ||
        event.user_data.external_id;

      if (!hasIdentifier) {
        errors.push(`Event #${eventNum}: Must have at least one user identifier (email, phone, or external_id)`);
      }
    }
  });

  return errors;
}

/**
 * Display validation errors
 * @param errors Array of error messages
 */
export function displayValidationErrors(errors: string[]): void {
  console.log(chalk.red.bold('\n❌ Validation Errors:\n'));
  errors.forEach((error) => {
    console.log(chalk.red(`  • ${error}`));
  });
  console.log('');
}
