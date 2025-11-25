export const CLAUDE_CONFIG = {
  model: 'claude-sonnet-4-20250514',
  temperature: 0,  // CRITICAL: Deterministic output (PostHog Wizard pattern)
  max_tokens: 4096,
};

export function generateAuditPrompt(data: any): string {
  const accountInfo = data.accountInfo;
  const campaigns = data.campaigns;
  const performance = data.performance;
  const keywords = data.keywords;
  const conversions = data.conversions;

  return `You are a Google Ads expert analyzing account performance. Generate a comprehensive RTT-style audit report.

CRITICAL INSTRUCTIONS:
- Respond with ONLY valid JSON
- DO NOT include markdown code blocks or backticks
- DO NOT include any explanatory text before or after the JSON
- Follow the EXACT schema provided below
- Use the EXACT field names as specified
- All severity and priority values must be lowercase

ACCOUNT DATA:
${JSON.stringify({
  account: accountInfo,
  campaigns_count: campaigns?.length || 0,
  performance_last_30_days: performance,
  top_keywords: keywords?.slice(0, 20) || [],
  conversion_actions: conversions || [],
}, null, 2)}

ANALYSIS REQUIREMENTS:
1. Identify critical issues affecting performance
2. Evaluate account health (1-10 scale)
3. Provide specific, actionable recommendations
4. Focus on RTT methodology: tracking, targeting, testing

Respond with JSON in this EXACT format:
{
  "account_health_score": <number between 1-10>,
  "currency": "<currency code>",
  "total_spend_last_30_days": <number>,
  "executive_summary": "<2-3 sentence overview of account performance>",
  "critical_issues": [
    {
      "severity": "<critical|high|medium|low>",
      "title": "<brief title>",
      "description": "<detailed explanation>",
      "impact": "<business impact description>",
      "category": "<tracking|targeting|testing|budget|quality_score>"
    }
  ],
  "strengths": [
    "<specific strength observed in the account>"
  ],
  "recommendations": [
    {
      "priority": "<high|medium|low>",
      "category": "<tracking|targeting|testing|budget|optimization>",
      "action": "<specific action to take>",
      "expected_impact": "<expected outcome>",
      "implementation_time": "<time estimate>"
    }
  ],
  "tracking_audit": {
    "conversion_tracking_setup": "<assessment>",
    "tracking_issues": ["<issue>"],
    "tracking_score": <number 1-10>
  },
  "targeting_analysis": {
    "audience_coverage": "<assessment>",
    "keyword_quality": "<assessment>",
    "targeting_score": <number 1-10>
  },
  "testing_opportunities": {
    "current_tests": ["<test>"],
    "recommended_tests": ["<test>"],
    "testing_score": <number 1-10>
  }
}

OUTPUT ONLY JSON. NO MARKDOWN. NO EXPLANATION. START WITH { AND END WITH }.`;
}
