import os
import random
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def create_mock_documents():
    output_dir = "mock_documents"
    os.makedirs(output_dir, exist_ok=True)
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    sub_title = styles['Heading2']
    normal = styles['Normal']
    
    # Text generator helper to ensure 200+ words
    def generate_filler(prefix, count=200):
        words = ["the", "of", "and", "a", "to", "in", "is", "you", "that", "it", "he", "was", "for", "on", "are", "as", "with", "his", "they", "I", "at", "be", "this", "have", "from", "or", "one", "had", "by", "word", "but", "not", "what", "all", "were", "we", "when", "your", "can", "said", "there", "use", "an", "each", "which", "she", "do", "how", "their", "if"]
        filler = " ".join([random.choice(words) for _ in range(count)])
        return prefix + " " + filler

    # 1. GSTR-3B
    doc = SimpleDocTemplate(os.path.join(output_dir, "mock_gstr3b.pdf"), pagesize=A4)
    elements = []
    elements.append(Paragraph("Form GSTR-3B", title_style))
    elements.append(Paragraph("Monthly/Quarterly Return", sub_title))
    elements.append(Spacer(1, 12))
    
    gstr3b_text = (
        "This document serves as the official Form GSTR-3B for the registered taxpayer. "
        "The GSTIN for the entity is 24AABCS1234F1Z3. This return covers the period from April 2024 to March 2025. "
        "Section 3.1 details the outward taxable supplies and other tax liabilities. "
        "The total outward taxable supplies made during this period amount to a quarterly average of 3,85,00,000 INR. "
        "Furthermore, the ITC (Input Tax Credit) claimed by the taxpayer is recorded as 58,00,000 INR. "
    )
    elements.append(Paragraph(generate_filler(gstr3b_text, 250), normal))
    elements.append(Spacer(1, 12))
    
    data = [
        ["Details of Outward Supplies", "Value"],
        ["Outward taxable supplies (Quarterly Average)", "₹ 3,85,00,000"],
        ["Total Output Tax Paid", "₹ 69,30,000"],
        ["Eligible ITC", ""],
        ["ITC Claimed", "₹ 58,00,000"]
    ]
    t = Table(data, colWidths=[300, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT')
    ]))
    elements.append(t)
    doc.build(elements)
    
    # 2. Bank Statement
    doc = SimpleDocTemplate(os.path.join(output_dir, "mock_bank_statement.pdf"), pagesize=A4)
    elements = []
    elements.append(Paragraph("HDFC Bank - Account Statement", title_style))
    elements.append(Spacer(1, 12))
    
    bank_text = (
        "This is an official bank statement generated for Sharma Textile Mills. "
        "The Account Number associated with these records is 50100234567890. "
        "Each transaction date is carefully logged chronologically. "
        "The transaction columns specify whether an amount was a Debit or a Credit. "
        "At the end of the specified period, the closing balance is verified and recorded accurately. "
    )
    elements.append(Paragraph(generate_filler(bank_text, 250), normal))
    elements.append(Spacer(1, 12))
    
    transactions = [["transaction date", "Description", "Debit (₹)", "Credit (₹)", "Balance (₹)"]]
    balance = 0
    start_date = datetime(2024, 4, 1)
    
    credit_amounts = [5000000] * 3 
    remaining_credit = 35500000 - 15000000
    for _ in range(7): credit_amounts.append(random.randint(1000000, 3000000))
    credit_amounts.append(remaining_credit - sum(credit_amounts[3:]))
    
    debit_amounts = []
    remaining_debit = 34254770
    for _ in range(8): debit_amounts.append(random.randint(1000000, 5000000))
    debit_amounts.append(remaining_debit - sum(debit_amounts))
    
    events = [("CR", c) for c in credit_amounts] + [("DR", d) for d in debit_amounts]
    random.shuffle(events)
    
    current_date = start_date
    for type_, amt in events:
        current_date += timedelta(days=random.randint(2, 12))
        date_str = current_date.strftime("%d-%b-%Y")
        if type_ == "CR":
            balance += amt
            transactions.append([date_str, "INWARD REM", "", f"{amt:,.2f}", f"{balance:,.2f}"])
        else:
            balance -= amt
            transactions.append([date_str, "VENDOR PAY", f"{amt:,.2f}", "", f"{balance:,.2f}"])
            
    if round(balance) != 1245230:
        transactions[-1][-1] = f"{1245230:,.2f}"
        
    transactions.append(["", "closing balance", "3,42,54,770.00", "3,55,00,000.00", "12,45,230.00"])

    t = Table(transactions, colWidths=[80, 110, 80, 80, 90])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
    ]))
    elements.append(t)
    doc.build(elements)
    
    # 3. GSTR-2A
    doc = SimpleDocTemplate(os.path.join(output_dir, "mock_gstr2a.pdf"), pagesize=A4)
    elements = []
    elements.append(Paragraph("Form GSTR-2A", title_style))
    elements.append(Spacer(1, 12))
    
    gstr2a_text = (
        "This document is Form GSTR-2A, which provides auto-drafted details of input tax credit. "
        "The GSTIN matching this profile is 24AABCS1234F1Z3 for Sharma Textile Mills Pvt. Ltd. "
        "The total ITC available from suppliers is consolidated here for the period of April 2024 to March 2025. "
        "Each supplier has filed their respective returns, making the ITC available for the recipient. "
    )
    elements.append(Paragraph(generate_filler(gstr2a_text, 250), normal))
    elements.append(Spacer(1, 12))
    
    data = [
        ["Total ITC available", "₹ 42,00,000"],
        ["Total Number of supplier", "34"]
    ]
    t = Table(data, colWidths=[300, 150])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT')
    ]))
    elements.append(t)
    doc.build(elements)

    # 4. Annual Report
    doc = SimpleDocTemplate(os.path.join(output_dir, "mock_annual_report.pdf"), pagesize=A4)
    elements = []
    elements.append(Paragraph("Sharma Textile Mills Pvt. Ltd. - Annual Report", title_style))
    elements.append(Spacer(1, 12))
    
    ar_text = (
        "Welcome to the annual report for the fiscal year. The Board of Directors is pleased to present the financial results. "
        "The Chairman has noted that the overall revenue for the period saw significant improvement. "
        "The Auditor has reviewed the statements and provided an unqualified opinion on the fairness of the reporting. "
        "This annual report aims to give shareholders a transparent look at our operations and financial health. "
    )
    elements.append(Paragraph(generate_filler(ar_text, 250), normal))
    elements.append(Spacer(1, 12))
    
    bs_data = [
        ["Total Assets", "₹ 28,00,00,000"],
        ["Net Worth", "₹ 14,00,00,000"],
        ["Debt", "₹ 8,20,00,000"]
    ]
    t1 = Table(bs_data, colWidths=[200, 150])
    t1.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
    elements.append(t1)
    elements.append(Spacer(1, 12))

    fin_data = [
        ["Metric", "FY2023", "FY2024", "FY2025"],
        ["revenue (Cr)", "₹ 35.0", "₹ 38.0", "₹ 42.5"],
        ["EBITDA (Cr)", "₹ 4.2", "₹ 4.8", "₹ 6.1"],
        ["PAT (Cr)", "₹ 1.8", "₹ 2.1", "₹ 2.8"]
    ]
    t2 = Table(fin_data, colWidths=[150, 80, 80, 80])
    t2.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
    elements.append(t2)
    doc.build(elements)
    
    # 5. Sanction Letter
    doc = SimpleDocTemplate(os.path.join(output_dir, "mock_sanction_letter.pdf"), pagesize=A4)
    elements = []
    elements.append(Paragraph("State Bank of India - SANCTION LETTER", title_style))
    elements.append(Spacer(1, 12))
    
    sl_text = (
        "We are pleased to issue this sanction letter to Sharma Textile Mills Pvt. Ltd. "
        "This letter outlines the terms of the credit facility being offered. "
        "The sanctioned amount is subject to the prime lending rate of interest. "
        "Appropriate collateral must be maintained as security against the facility at all times. "
        "Failure to service the interest can lead to revocation of the sanctioned amount. "
    )
    elements.append(Paragraph(generate_filler(sl_text, 250), normal))
    elements.append(Spacer(1, 12))
    
    data = [
        ["facility Type", "Cash Credit (CC)"],
        ["sanctioned amount", "₹ 5,00,00,000 (Five Crores Only)"],
        ["rate of interest", "11.5% p.a."],
        ["collateral / Security", "Hypothecation of stock and debtors"],
    ]
    t = Table(data, colWidths=[150, 300])
    t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
    elements.append(t)
    doc.build(elements)

if __name__ == "__main__":
    create_mock_documents()
    print("Successfully generated all verbose mock PDFs.")
