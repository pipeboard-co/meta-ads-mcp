import Anthropic from '@anthropic-ai/sdk';
import { generateAuditPrompt, CLAUDE_CONFIG } from '../prompts/audit.js';

export async function analyzeAccount(data: any) {
  const apiKey = process.env.ANTHROPIC_API_KEY;

  if (!apiKey) {
    throw new Error('ANTHROPIC_API_KEY not found in environment variables');
  }

  const anthropic = new Anthropic({
    apiKey: apiKey
  });

  const prompt = generateAuditPrompt(data);

  try {
    const response = await anthropic.messages.create({
      ...CLAUDE_CONFIG,
      messages: [{
        role: 'user',
        content: prompt
      }]
    });

    const text = response.content[0].type === 'text' ? response.content[0].text : '';

    // Strip any potential markdown if present (PostHog Wizard pattern)
    const cleaned = text
      .replace(/```json\n?/g, '')
      .replace(/```\n?/g, '')
      .trim();

    try {
      const parsed = JSON.parse(cleaned);
      return parsed;
    } catch (parseError) {
      console.error('Failed to parse Claude response:', cleaned.substring(0, 500));
      throw new Error('Invalid JSON response from Claude. Please try again.');
    }
  } catch (error: any) {
    if (error.status === 401) {
      throw new Error('Invalid Anthropic API key. Please check your .env file.');
    }
    throw error;
  }
}

export async function analyzeWithContext(data: any, context: string) {
  const apiKey = process.env.ANTHROPIC_API_KEY;

  if (!apiKey) {
    throw new Error('ANTHROPIC_API_KEY not found in environment variables');
  }

  const anthropic = new Anthropic({
    apiKey: apiKey
  });

  const response = await anthropic.messages.create({
    model: CLAUDE_CONFIG.model,
    temperature: CLAUDE_CONFIG.temperature,
    max_tokens: 2048,
    messages: [{
      role: 'user',
      content: `${context}\n\nData:\n${JSON.stringify(data, null, 2)}`
    }]
  });

  return response.content[0].type === 'text' ? response.content[0].text : '';
}
