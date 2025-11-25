/**
 * Utility functions for exporting data to files
 */

import { writeFile } from 'fs/promises';
import chalk from 'chalk';

/**
 * Export data to JSON file
 * @param data Data to export
 * @param filepath Output file path
 */
export async function exportToJSON(data: any, filepath: string): Promise<void> {
  try {
    const json = JSON.stringify(data, null, 2);
    await writeFile(filepath, json, 'utf-8');
    console.log(chalk.green(`\n✅ Exported to: ${filepath}`));
  } catch (error) {
    console.error(chalk.red(`\n❌ Failed to export: ${error instanceof Error ? error.message : 'Unknown error'}`));
    throw error;
  }
}

/**
 * Create an export object with metadata
 * @param data Main data to export
 * @param type Type of data (e.g., 'contacts', 'opportunities')
 * @returns Export object with metadata
 */
export function createExport(data: any, type: string): any {
  return {
    exportedAt: new Date().toISOString(),
    type,
    count: Array.isArray(data) ? data.length : 1,
    data,
  };
}
