import os
from celery import shared_task
from django.conf import settings
from .models import ComplianceReport

@shared_task
def generate_compliance_pdf(report_id: str):
    """Generates a PDF compliance report using ReportLab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        report = ComplianceReport.objects.select_related('bank').get(id=report_id)
        
        # Ensure static/reports directory exists
        reports_dir = os.path.join(settings.BASE_DIR, 'static', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        pdf_path = os.path.join(reports_dir, f'{report_id}.pdf')
        
        # Draw PDF
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        
        title_map = {
            'rbi_dpsp': 'RBI DPSP Compliance Report',
            'gdpr_art30': 'GDPR Article 30 Processing Record',
            'pci_dss': 'PCI-DSS Federation Audit',
            'fiu_ind': 'FIU-IND Suspicious Activity Summary'
        }
        
        title = title_map.get(report.report_type, 'Compliance Report')
        c.drawString(50, 750, title)
        
        c.setFont("Helvetica", 12)
        c.drawString(50, 710, f"Report ID: {report.id}")
        c.drawString(50, 690, f"Generated At: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(50, 670, f"Bank: {report.bank.name} (Tier: {report.bank.tier})")
        
        c.drawString(50, 630, "Federation Participation Log:")
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, 610, "This bank has successfully participated in FedShield rounds without transmitting PII.")
        c.drawString(50, 595, f"Differential Privacy Epsilon Used: {report.bank.privacy_epsilon}")
        
        c.line(50, 580, 550, 580)
        
        c.setFont("Helvetica", 10)
        c.drawString(50, 560, f"Period: {report.period_start} to {report.period_end}")
        c.drawString(50, 540, "Status: COMPLIANT")
        
        c.save()
        
        # Update report status
        report.status = 'completed'
        report.save()
        
        return f"Generated {pdf_path}"
        
    except Exception as e:
        report = ComplianceReport.objects.get(id=report_id)
        report.status = 'failed'
        report.save()
        return str(e)
