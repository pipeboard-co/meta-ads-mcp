/**
 * Utility functions for formatting and displaying data
 */

import chalk from 'chalk';
import type { GHLContact, GHLOpportunity } from '../types/ghl.js';

/**
 * Format a contact for display in the terminal
 */
export function formatContact(contact: GHLContact): string {
  const name = contact.contactName || `${contact.firstName || ''} ${contact.lastName || ''}`.trim();
  const email = contact.email || 'No email';
  const phone = contact.phone || 'No phone';
  const tags = contact.tags && contact.tags.length > 0 ? contact.tags.join(', ') : 'No tags';

  return `
${chalk.bold.cyan('Contact ID:')} ${contact.id}
${chalk.bold('Name:')} ${name}
${chalk.bold('Email:')} ${email}
${chalk.bold('Phone:')} ${phone}
${chalk.bold('Tags:')} ${tags}
${chalk.bold('Added:')} ${contact.dateAdded ? new Date(contact.dateAdded).toLocaleDateString() : 'Unknown'}
${chalk.gray('─'.repeat(60))}`;
}

/**
 * Format a contact for table display
 */
export function formatContactRow(contact: GHLContact): string {
  const name = contact.contactName || `${contact.firstName || ''} ${contact.lastName || ''}`.trim() || 'N/A';
  const email = contact.email || 'N/A';
  const phone = contact.phone || 'N/A';
  const tags = contact.tags && contact.tags.length > 0 ? contact.tags.slice(0, 2).join(', ') : 'None';

  return `${contact.id.padEnd(24)} | ${name.padEnd(25)} | ${email.padEnd(30)} | ${phone.padEnd(15)} | ${tags}`;
}

/**
 * Format an opportunity for display in the terminal
 */
export function formatOpportunity(opportunity: GHLOpportunity): string {
  const value = opportunity.monetaryValue
    ? `$${opportunity.monetaryValue.toLocaleString()}`
    : 'No value';
  const status = getStatusColor(opportunity.status);

  return `
${chalk.bold.cyan('Opportunity ID:')} ${opportunity.id}
${chalk.bold('Name:')} ${opportunity.name}
${chalk.bold('Status:')} ${status}
${chalk.bold('Value:')} ${value}
${chalk.bold('Contact ID:')} ${opportunity.contactId}
${chalk.bold('Added:')} ${opportunity.dateAdded ? new Date(opportunity.dateAdded).toLocaleDateString() : 'Unknown'}
${chalk.gray('─'.repeat(60))}`;
}

/**
 * Format an opportunity for table display
 */
export function formatOpportunityRow(opportunity: GHLOpportunity): string {
  const name = opportunity.name.padEnd(30);
  const status = opportunity.status.padEnd(10);
  const value = opportunity.monetaryValue
    ? `$${opportunity.monetaryValue.toLocaleString()}`.padEnd(12)
    : 'N/A'.padEnd(12);
  const contact = opportunity.contactId.substring(0, 20).padEnd(20);

  return `${opportunity.id.padEnd(24)} | ${name} | ${status} | ${value} | ${contact}`;
}

/**
 * Get colored status text
 */
function getStatusColor(status: string): string {
  switch (status) {
    case 'open':
      return chalk.blue(status);
    case 'won':
      return chalk.green(status);
    case 'lost':
      return chalk.red(status);
    case 'abandoned':
      return chalk.gray(status);
    default:
      return status;
  }
}

/**
 * Display contacts table
 */
export function displayContactsTable(contacts: GHLContact[]): void {
  console.log(chalk.bold('\nContacts:'));
  console.log(chalk.gray('─'.repeat(120)));
  console.log(
    chalk.bold(
      'ID'.padEnd(24) +
        ' | ' +
        'Name'.padEnd(25) +
        ' | ' +
        'Email'.padEnd(30) +
        ' | ' +
        'Phone'.padEnd(15) +
        ' | ' +
        'Tags'
    )
  );
  console.log(chalk.gray('─'.repeat(120)));

  contacts.forEach((contact) => {
    console.log(formatContactRow(contact));
  });

  console.log(chalk.gray('─'.repeat(120)));
  console.log(chalk.bold(`\nTotal Contacts: ${contacts.length}`));
}

/**
 * Display opportunities table
 */
export function displayOpportunitiesTable(opportunities: GHLOpportunity[]): void {
  console.log(chalk.bold('\nOpportunities:'));
  console.log(chalk.gray('─'.repeat(120)));
  console.log(
    chalk.bold(
      'ID'.padEnd(24) +
        ' | ' +
        'Name'.padEnd(30) +
        ' | ' +
        'Status'.padEnd(10) +
        ' | ' +
        'Value'.padEnd(12) +
        ' | ' +
        'Contact'
    )
  );
  console.log(chalk.gray('─'.repeat(120)));

  opportunities.forEach((opp) => {
    console.log(formatOpportunityRow(opp));
  });

  console.log(chalk.gray('─'.repeat(120)));

  // Calculate total value
  const totalValue = opportunities.reduce(
    (sum, opp) => sum + (opp.monetaryValue || 0),
    0
  );
  console.log(chalk.bold(`\nTotal Opportunities: ${opportunities.length}`));
  console.log(chalk.bold(`Total Value: $${totalValue.toLocaleString()}`));
}

/**
 * Format summary statistics
 */
export function displaySummary(data: {
  total: number;
  open?: number;
  won?: number;
  lost?: number;
  totalValue?: number;
}): void {
  console.log(chalk.bold('\n📊 Summary:'));
  console.log(`  Total: ${chalk.cyan(data.total)}`);

  if (data.open !== undefined) {
    console.log(`  Open: ${chalk.blue(data.open)}`);
  }

  if (data.won !== undefined) {
    console.log(`  Won: ${chalk.green(data.won)}`);
  }

  if (data.lost !== undefined) {
    console.log(`  Lost: ${chalk.red(data.lost)}`);
  }

  if (data.totalValue !== undefined) {
    console.log(`  Total Value: ${chalk.green(`$${data.totalValue.toLocaleString()}`)}`);
  }
}
