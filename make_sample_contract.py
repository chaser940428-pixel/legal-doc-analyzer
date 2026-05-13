"""
Run once to generate sample_contract.pdf for demo purposes.
Requires: pip install fpdf2
"""

from fpdf import FPDF


def make():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "SOFTWARE DEVELOPMENT SERVICES AGREEMENT", ln=True, align="C")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Effective Date: January 1, 2025", ln=True, align="C")
    pdf.ln(8)

    sections = [
        ("PARTIES", (
            "This Software Development Services Agreement (the \"Agreement\") is entered into as of "
            "January 1, 2025, by and between:\n\n"
            "CLIENT: NovaTech Solutions Ltd., a company incorporated under the laws of Taiwan, "
            "with its principal office at 12F, No. 88, Xinyi Road, Section 5, Taipei 110 (\"Client\"); and\n\n"
            "CONTRACTOR: ChainLink Software Studio, an individual contractor with principal place "
            "of business at No. 101, Guangfu Road, Hsinchu 300 (\"Contractor\")."
        )),
        ("1. SCOPE OF SERVICES", (
            "Contractor agrees to provide Client with custom software development services, "
            "including but not limited to: backend API design and implementation, cloud infrastructure "
            "setup on AWS, automated testing suite development, and technical documentation. "
            "Detailed deliverables and milestones are set forth in Schedule A, attached hereto and "
            "incorporated by reference. Any changes to the scope of services must be agreed upon in "
            "writing by both parties through a Change Order process."
        )),
        ("2. TERM AND DURATION", (
            "This Agreement shall commence on January 1, 2025 and continue for a period of twelve (12) "
            "months, terminating on December 31, 2025, unless earlier terminated in accordance with "
            "Section 7 of this Agreement. This Agreement may be renewed for successive one-year terms "
            "upon mutual written consent of both parties no later than thirty (30) days prior to the "
            "expiration of the then-current term."
        )),
        ("3. PAYMENT TERMS", (
            "3.1 Fees. Client shall pay Contractor a monthly retainer of TWD 180,000 (New Taiwan Dollars "
            "one hundred eighty thousand), due on the first business day of each calendar month.\n\n"
            "3.2 Project Milestones. In addition to the monthly retainer, Client shall pay milestone "
            "payments as outlined in Schedule A, with each milestone payment due within fourteen (14) "
            "calendar days of written acceptance by Client.\n\n"
            "3.3 Late Payment. Any payment not received within fourteen (14) days of its due date shall "
            "accrue interest at the rate of 1.5% per month (18% per annum) on the outstanding balance. "
            "If payment is overdue by more than thirty (30) days, Contractor may suspend services "
            "without liability until full payment is received.\n\n"
            "3.4 Expenses. Pre-approved third-party expenses (e.g., cloud hosting, software licenses) "
            "shall be reimbursed by Client within fourteen (14) days of invoice with supporting receipts."
        )),
        ("4. INTELLECTUAL PROPERTY OWNERSHIP", (
            "4.1 Work for Hire. All deliverables, code, documentation, and other work product created "
            "by Contractor specifically for Client under this Agreement (\"Deliverables\") shall, upon "
            "full payment of all amounts due, be considered works made for hire and shall be the sole "
            "and exclusive property of Client.\n\n"
            "4.2 Pre-Existing IP. Contractor retains all right, title, and interest in any pre-existing "
            "tools, libraries, frameworks, or methodologies (\"Background IP\") used in the creation of "
            "Deliverables. Contractor hereby grants Client a perpetual, royalty-free, non-exclusive "
            "license to use such Background IP solely as embedded in the Deliverables.\n\n"
            "4.3 Open Source. Where Contractor incorporates open-source components, Contractor shall "
            "disclose such components to Client in writing, including applicable license terms."
        )),
        ("5. CONFIDENTIALITY", (
            "5.1 Definition. \"Confidential Information\" means any non-public information disclosed by "
            "either party to the other, whether orally, in writing, or by any other means, that is "
            "designated as confidential or that reasonably should be understood to be confidential given "
            "the nature of the information and circumstances of disclosure.\n\n"
            "5.2 Obligations. Each party agrees to: (a) hold the other's Confidential Information in "
            "strict confidence; (b) not disclose it to any third party without prior written consent; "
            "and (c) use it solely for purposes of performing obligations under this Agreement.\n\n"
            "5.3 Duration. Confidentiality obligations shall survive termination of this Agreement for "
            "a period of three (3) years.\n\n"
            "5.4 Exceptions. These obligations do not apply to information that: (a) is or becomes "
            "publicly available through no fault of the receiving party; (b) was rightfully known prior "
            "to disclosure; or (c) is required to be disclosed by law or court order, provided the "
            "disclosing party is given reasonable prior notice."
        )),
        ("6. LIABILITY AND INDEMNIFICATION", (
            "6.1 Limitation of Liability. IN NO EVENT SHALL EITHER PARTY BE LIABLE TO THE OTHER FOR "
            "ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING OUT OF OR "
            "RELATED TO THIS AGREEMENT, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.\n\n"
            "6.2 Cap on Liability. Each party's total cumulative liability to the other party arising "
            "out of or related to this Agreement shall not exceed the total fees paid or payable by "
            "Client to Contractor during the three (3) months immediately preceding the event giving "
            "rise to the claim.\n\n"
            "6.3 Indemnification by Contractor. Contractor shall indemnify, defend, and hold harmless "
            "Client from any third-party claims arising from Contractor's gross negligence, willful "
            "misconduct, or infringement of third-party intellectual property rights.\n\n"
            "6.4 Indemnification by Client. Client shall indemnify, defend, and hold harmless "
            "Contractor from any third-party claims arising out of Client's use of the Deliverables "
            "in a manner not contemplated by this Agreement."
        )),
        ("7. TERMINATION", (
            "7.1 Termination for Convenience. Either party may terminate this Agreement without cause "
            "upon thirty (30) days' prior written notice to the other party.\n\n"
            "7.2 Termination for Cause. Either party may terminate this Agreement immediately upon "
            "written notice if the other party: (a) materially breaches this Agreement and fails to "
            "cure such breach within fifteen (15) days after receiving written notice thereof; "
            "(b) becomes insolvent, makes a general assignment for the benefit of creditors, or "
            "files for bankruptcy protection; or (c) engages in fraudulent or illegal conduct.\n\n"
            "7.3 Effect of Termination. Upon termination, Client shall pay Contractor for all work "
            "completed and accepted up to the effective termination date. Contractor shall deliver "
            "all completed Deliverables and work-in-progress to Client within five (5) business days "
            "of termination. Sections 4, 5, 6, and 8 shall survive termination of this Agreement."
        )),
        ("8. GOVERNING LAW AND DISPUTE RESOLUTION", (
            "8.1 Governing Law. This Agreement shall be governed by and construed in accordance with "
            "the laws of the Republic of China (Taiwan), without regard to its conflict of law provisions.\n\n"
            "8.2 Negotiation. The parties agree to attempt to resolve any dispute arising out of or "
            "relating to this Agreement through good-faith negotiation for a period of thirty (30) days "
            "following written notice of the dispute.\n\n"
            "8.3 Arbitration. If the dispute is not resolved through negotiation, it shall be finally "
            "settled by binding arbitration administered by the Chinese Arbitration Association, Taipei, "
            "in accordance with its arbitration rules. The arbitration shall be conducted in Taipei, "
            "Taiwan, in the Chinese language. The arbitral award shall be final and binding.\n\n"
            "8.4 Injunctive Relief. Notwithstanding the foregoing, either party may seek injunctive "
            "or other equitable relief in any court of competent jurisdiction to prevent irreparable harm."
        )),
        ("9. GENERAL PROVISIONS", (
            "9.1 Independent Contractor. Contractor is an independent contractor and not an employee, "
            "partner, or agent of Client. Contractor is solely responsible for all taxes, insurance, "
            "and benefits related to Contractor's personnel.\n\n"
            "9.2 Entire Agreement. This Agreement, together with all Schedules, constitutes the entire "
            "agreement between the parties and supersedes all prior negotiations, representations, or "
            "agreements relating to its subject matter.\n\n"
            "9.3 Amendments. This Agreement may not be amended except by a written instrument signed "
            "by authorized representatives of both parties.\n\n"
            "9.4 Severability. If any provision of this Agreement is found invalid or unenforceable, "
            "the remaining provisions shall remain in full force and effect.\n\n"
            "9.5 Force Majeure. Neither party shall be liable for delays or failures in performance "
            "resulting from circumstances beyond that party's reasonable control."
        )),
    ]

    for title, body in sections:
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, title)
        pdf.ln(1)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, body)
        pdf.ln(5)

    # Signature block
    pdf.set_font("Helvetica", "B", 11)
    pdf.multi_cell(0, 7, "SIGNATURES")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6,
        "IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.\n\n"
        "NovaTech Solutions Ltd. (Client)\n"
        "Authorized Signature: _________________________\n"
        "Name: Chen Wei-Ting, CEO\n"
        "Date: January 1, 2025\n\n"
        "ChainLink Software Studio (Contractor)\n"
        "Authorized Signature: _________________________\n"
        "Name: Lin Jia-Hao\n"
        "Date: January 1, 2025"
    )

    pdf.output("sample_contract.pdf")
    print("sample_contract.pdf generated.")


if __name__ == "__main__":
    make()
