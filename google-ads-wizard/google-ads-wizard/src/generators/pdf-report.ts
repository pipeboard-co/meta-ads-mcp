import PDFDocument from 'pdfkit';
import fs from 'fs';

export interface PDFReportData {
  accountInfo: any;
  analysis: any;
  performance: any;
  campaigns: any[];
}

export async function generatePDFReport(data: PDFReportData, outputPath: string) {
  return new Promise<void>((resolve, reject) => {
    const doc = new PDFDocument({ margin: 50 });
    const stream = fs.createWriteStream(outputPath);

    doc.pipe(stream);

    // Helper function for formatting currency
    const formatCurrency = (micros: number, currency: string) => {
      return `${currency} ${(micros / 1000000).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}`;
    };

    // Title Page
    doc.fontSize(28).font('Helvetica-Bold').text('Google Ads Account Audit', { align: 'center' });
    doc.moveDown(0.5);

    doc.fontSize(18).font('Helvetica').text(data.accountInfo.descriptive_name || 'Account', { align: 'center' });
    doc.fontSize(12).text(`Customer ID: ${data.accountInfo.id}`, { align: 'center' });
    doc.moveDown(0.3);
    doc.fontSize(10).fillColor('#666666').text(`Generated: ${new Date().toLocaleString()}`, { align: 'center' });

    // Account Health Score Box
    doc.moveDown(2);
    doc.roundedRect(150, doc.y, 300, 80, 10).fillAndStroke('#f0f0f0', '#cccccc');
    doc.fillColor('#000000');
    doc.fontSize(14).font('Helvetica-Bold').text('Account Health Score', 150, doc.y + 20, { width: 300, align: 'center' });
    doc.fontSize(36).font('Helvetica-Bold').fillColor('#2196F3').text(
      `${data.analysis.account_health_score}/10`,
      150,
      doc.y + 10,
      { width: 300, align: 'center' }
    );

    // Executive Summary
    doc.addPage();
    doc.fillColor('#000000').fontSize(20).font('Helvetica-Bold').text('Executive Summary');
    doc.moveDown(0.5);
    doc.fontSize(11).font('Helvetica').text(data.analysis.executive_summary);

    // Performance Overview
    doc.moveDown(1.5);
    doc.fontSize(16).font('Helvetica-Bold').text('Performance Overview (Last 30 Days)');
    doc.moveDown(0.5);

    const perf = data.performance;
    doc.fontSize(11).font('Helvetica');
    doc.text(`• Total Spend: ${formatCurrency(perf.cost_micros || 0, data.analysis.currency)}`);
    doc.text(`• Impressions: ${(perf.impressions || 0).toLocaleString()}`);
    doc.text(`• Clicks: ${(perf.clicks || 0).toLocaleString()}`);
    doc.text(`• CTR: ${((perf.ctr || 0) * 100).toFixed(2)}%`);
    doc.text(`• Conversions: ${perf.conversions || 0}`);
    if (perf.conversions > 0) {
      doc.text(`• Cost per Conversion: ${formatCurrency((perf.cost_micros || 0) / perf.conversions, data.analysis.currency)}`);
    }

    // Critical Issues
    doc.addPage();
    doc.fontSize(20).font('Helvetica-Bold').fillColor('#d32f2f').text('🔴 Critical Issues');
    doc.fillColor('#000000');
    doc.moveDown(0.5);

    if (data.analysis.critical_issues && data.analysis.critical_issues.length > 0) {
      data.analysis.critical_issues.forEach((issue: any, idx: number) => {
        doc.fontSize(14).font('Helvetica-Bold').text(`${idx + 1}. ${issue.title}`);
        doc.moveDown(0.3);
        doc.fontSize(10).font('Helvetica').fillColor('#666666').text(`Severity: ${issue.severity.toUpperCase()} | Category: ${issue.category || 'General'}`);
        doc.moveDown(0.3);
        doc.fontSize(11).fillColor('#000000').text(issue.description);
        doc.moveDown(0.3);
        doc.fontSize(10).font('Helvetica-Bold').text('Impact: ', { continued: true });
        doc.font('Helvetica').text(issue.impact);
        doc.moveDown(1);
      });
    } else {
      doc.fontSize(11).font('Helvetica').text('No critical issues identified.');
    }

    // Strengths
    doc.addPage();
    doc.fontSize(20).font('Helvetica-Bold').fillColor('#2e7d32').text('✅ Account Strengths');
    doc.fillColor('#000000');
    doc.moveDown(0.5);

    if (data.analysis.strengths && data.analysis.strengths.length > 0) {
      data.analysis.strengths.forEach((strength: string, idx: number) => {
        doc.fontSize(11).font('Helvetica').text(`${idx + 1}. ${strength}`);
        doc.moveDown(0.3);
      });
    } else {
      doc.fontSize(11).font('Helvetica').text('No specific strengths identified.');
    }

    // Recommendations
    doc.addPage();
    doc.fontSize(20).font('Helvetica-Bold').fillColor('#1976d2').text('💡 Recommendations');
    doc.fillColor('#000000');
    doc.moveDown(0.5);

    if (data.analysis.recommendations && data.analysis.recommendations.length > 0) {
      data.analysis.recommendations.forEach((rec: any, idx: number) => {
        doc.fontSize(12).font('Helvetica-Bold').text(`${idx + 1}. [${rec.priority.toUpperCase()}] ${rec.action}`);
        doc.moveDown(0.3);
        doc.fontSize(10).fillColor('#666666').text(`Category: ${rec.category} | Time: ${rec.implementation_time}`);
        doc.moveDown(0.3);
        doc.fontSize(11).fillColor('#000000').font('Helvetica').text(`Expected Impact: ${rec.expected_impact}`);
        doc.moveDown(1);
      });
    } else {
      doc.fontSize(11).font('Helvetica').text('No recommendations available.');
    }

    // RTT Analysis
    if (data.analysis.tracking_audit || data.analysis.targeting_analysis || data.analysis.testing_opportunities) {
      doc.addPage();
      doc.fontSize(20).font('Helvetica-Bold').text('RTT Analysis Framework');
      doc.moveDown(0.5);

      // Tracking
      if (data.analysis.tracking_audit) {
        doc.fontSize(16).font('Helvetica-Bold').fillColor('#ff6f00').text('Tracking');
        doc.fillColor('#000000');
        doc.moveDown(0.3);
        doc.fontSize(11).font('Helvetica').text(`Score: ${data.analysis.tracking_audit.tracking_score}/10`);
        doc.text(`Setup: ${data.analysis.tracking_audit.conversion_tracking_setup}`);
        doc.moveDown(0.5);
      }

      // Targeting
      if (data.analysis.targeting_analysis) {
        doc.fontSize(16).font('Helvetica-Bold').fillColor('#1976d2').text('Targeting');
        doc.fillColor('#000000');
        doc.moveDown(0.3);
        doc.fontSize(11).font('Helvetica').text(`Score: ${data.analysis.targeting_analysis.targeting_score}/10`);
        doc.text(`Audience Coverage: ${data.analysis.targeting_analysis.audience_coverage}`);
        doc.text(`Keyword Quality: ${data.analysis.targeting_analysis.keyword_quality}`);
        doc.moveDown(0.5);
      }

      // Testing
      if (data.analysis.testing_opportunities) {
        doc.fontSize(16).font('Helvetica-Bold').fillColor('#2e7d32').text('Testing');
        doc.fillColor('#000000');
        doc.moveDown(0.3);
        doc.fontSize(11).font('Helvetica').text(`Score: ${data.analysis.testing_opportunities.testing_score}/10`);
        if (data.analysis.testing_opportunities.recommended_tests?.length > 0) {
          doc.text('Recommended Tests:');
          data.analysis.testing_opportunities.recommended_tests.forEach((test: string) => {
            doc.text(`  • ${test}`);
          });
        }
      }
    }

    // Footer on last page
    doc.moveDown(2);
    doc.fontSize(9).fillColor('#999999').text(
      'Generated by Google Ads Wizard CLI | Following RTT Methodology',
      { align: 'center' }
    );

    doc.end();

    stream.on('finish', () => resolve());
    stream.on('error', reject);
  });
}
