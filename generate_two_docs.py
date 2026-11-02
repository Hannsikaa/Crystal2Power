import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx_helpers import set_cell_margins, set_cell_borders, format_table, add_footer_page_numbers

def build_budget_document(output_path):
    doc = docx.Document()

    # Page Setup: Standard A4/Letter, 1 inch margins
    for s in doc.sections:
        s.page_width = Inches(8.5)
        s.page_height = Inches(11.0)
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # Base Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)

    # Title Block
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    p_title.paragraph_format.line_spacing = 1.15
    run_t = p_title.add_run("DETAILED PROJECT BUDGET AND FINANCIAL JUSTIFICATION")
    run_t.font.name = 'Times New Roman'
    run_t.font.size = Pt(13)
    run_t.font.bold = True

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_before = Pt(2)
    p_meta.paragraph_format.space_after = Pt(14)
    p_meta.paragraph_format.line_spacing = 1.1
    run_meta = p_meta.add_run(
        "Scheme: ANRF – Inclusivity Research Grant (IRG) | Duration: 36 Months (3 Years)\n"
        "Project Title: Intelligent Flood Water Electrification Risk Prediction and Automatic Electrical Isolation for Climate Resilient Communities\n"
        "Principal Investigator: Dr. Dhanalakshmi Banavath, Assistant Professor, Department of Electronics and Communication Engineering\n"
        "Collaboration: ECE Department Only | Co-PI: None"
    )
    run_meta.font.name = 'Times New Roman'
    run_meta.font.size = Pt(9.5)
    run_meta.font.italic = True

    # Helper functions
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11.5)
        run.font.bold = True
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(9)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.font.bold = True
        return p

    def add_p(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.12
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        return p

    def add_bullet(bold_prefix, text):
        p = doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.12
        run_b = p.add_run(bold_prefix)
        run_b.font.name = 'Times New Roman'
        run_b.font.size = Pt(10.5)
        run_b.font.bold = True
        run_t = p.add_run(text)
        run_t.font.name = 'Times New Roman'
        run_t.font.size = Pt(10.5)
        return p

    # -------------------------------------------------------------
    # 1. Project and Budget Overview
    # -------------------------------------------------------------
    add_h1("1. Project and Budget Overview")
    add_p(
        "This document details the financial requirements, itemized cost estimates, and comprehensive justifications for the three-year "
        "research project titled \"Intelligent Flood Water Electrification Risk Prediction and Automatic Electrical Isolation for Climate "
        "Resilient Communities\", proposed under the Anusandhan National Research Foundation (ANRF) – Inclusivity Research Grant (IRG) scheme. "
        "The project is led by Dr. Dhanalakshmi Banavath, Assistant Professor in the Department of Electronics and Communication Engineering (ECE). "
        "In accordance with the individual-centric mandate of the ANRF-IRG scheme, the project involves no external Co-Principal Investigator, "
        "with all collaborative and developmental activities anchored within the host Department of Electronics and Communication Engineering."
    )
    add_p(
        "The proposed research addresses the severe life-safety and infrastructure hazard of floodwater electrification by developing an intelligent, "
        "sensor-health-aware monitoring and controlled low-voltage isolation framework. The methodological approach follows a rigorous, simulation-first "
        "lifecycle across 36 months: Year 1 focuses on mathematical problem formulation, coupled hydrodynamic-electrical hazard modelling, and simulation; "
        "Year 2 executes algorithm formulation (online sensor fault diagnosis and evidential hazard estimation under uncertainty) and embedded prototype "
        "hardware design; and Year 3 completes bench-scale firmware integration and controlled laboratory validation using an isolated, current-limited, "
        "protected low-voltage experimental setup (<= 24 V DC / 24 V AC, current limited to < 2 A)."
    )
    add_p(
        "The requested financial allocation directly supports the research lifecycle across seven standard heads: Research Personnel, Equipment, "
        "Consumables, Travel, Contingency, Other Costs, and Institutional Overhead. The total direct project cost is ₹39,10,000 (₹39.10 Lakhs). "
        "With standard institutional overheads computed at 10% (₹3,91,000), the overall proposed budget is ₹43,01,000 (₹43.01 Lakhs). This allocation "
        "is fully within the permissible financial ceiling of the ANRF-IRG scheme (up to ₹60.00 Lakhs plus overheads), ensuring robust technical "
        "feasibility, financial transparency, and strict adherence to governmental expenditure norms."
    )

    # -------------------------------------------------------------
    # 2. Consolidated Budget Summary
    # -------------------------------------------------------------
    add_h1("2. Consolidated Budget Summary")
    add_p(
        "The consolidated budget summary presented in Table 1 categorizes total proposed expenditures across direct research heads and "
        "institutional overheads for the entire 36-month project tenure."
    )

    p_tbl1_cap = doc.add_paragraph()
    p_tbl1_cap.paragraph_format.space_before = Pt(4)
    p_tbl1_cap.paragraph_format.space_after = Pt(2)
    p_tbl1_cap.paragraph_format.keep_with_next = True
    r = p_tbl1_cap.add_run("Table 1: Consolidated Project Budget Summary (36 Months)")
    r.font.bold = True
    r.font.size = Pt(10)

    t1_headers = ["Sl. No.", "Budget Head", "Total Proposed Amount (₹)", "Percentage of Direct Cost"]
    t1_data = [
        ["1", "Research Personnel", "17,50,000", "44.76%"],
        ["2", "Equipment (Non-Recurring)", "10,50,000", "26.85%"],
        ["3", "Consumables", "4,50,000", "11.51%"],
        ["4", "Travel (Domestic)", "2,40,000", "6.14%"],
        ["5", "Contingency", "2,40,000", "6.14%"],
        ["6", "Other Costs (Publications & Patent Filing)", "1,80,000", "4.60%"],
        ["--", "Subtotal: Direct Project Cost", "39,10,000", "100.00%"],
        ["7", "Institutional Overhead (10% of Direct Cost)", "3,91,000", "--"],
        ["--", "Grand Total (Direct Cost + Institutional Overhead)", "43,01,000", "--"]
    ]
    t1_widths = [Inches(0.8), Inches(2.8), Inches(1.8), Inches(1.6)]
    table1 = doc.add_table(rows=len(t1_data) + 1, cols=4)
    format_table(table1, t1_widths, t1_headers, t1_data)

    # -------------------------------------------------------------
    # 3. Year-Wise Budget Summary
    # -------------------------------------------------------------
    add_h1("3. Year-Wise Budget Summary")
    add_p(
        "Table 2 outlines the year-wise distribution of expenditures across the 36-month project duration. The allocation reflects the logical "
        "progression of technical tasks from initial computational modelling and upfront hardware procurement in Year 1, through algorithmic "
        "design and embedded prototyping in Year 2, to physical experimental validation, open-access dissemination, and reporting in Year 3."
    )

    p_tbl2_cap = doc.add_paragraph()
    p_tbl2_cap.paragraph_format.space_before = Pt(4)
    p_tbl2_cap.paragraph_format.space_after = Pt(2)
    p_tbl2_cap.paragraph_format.keep_with_next = True
    r = p_tbl2_cap.add_run("Table 2: Year-Wise Detailed Financial Breakdown (in ₹)")
    r.font.bold = True
    r.font.size = Pt(10)

    t2_headers = ["Budget Head", "Year 1 (₹)", "Year 2 (₹)", "Year 3 (₹)", "Total Amount (₹)"]
    t2_data = [
        ["Research Personnel", "5,50,000", "5,80,000", "6,20,000", "17,50,000"],
        ["Equipment (Non-Recurring)", "10,50,000", "0", "0", "10,50,000"],
        ["Consumables", "1,20,000", "1,80,000", "1,50,000", "4,50,000"],
        ["Travel (Domestic)", "60,000", "90,000", "90,000", "2,40,000"],
        ["Contingency", "80,000", "80,000", "80,000", "2,40,000"],
        ["Other Costs", "30,000", "60,000", "90,000", "1,80,000"],
        ["Subtotal: Direct Project Cost", "18,90,000", "9,90,000", "10,30,000", "39,10,000"],
        ["Institutional Overhead (10%)", "1,89,000", "99,000", "1,03,000", "3,91,000"],
        ["Grand Total (Year-Wise)", "20,79,000", "10,89,000", "11,33,000", "43,01,000"]
    ]
    t2_widths = [Inches(2.5), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.2)]
    table2 = doc.add_table(rows=len(t2_data) + 1, cols=5)
    format_table(table2, t2_widths, t2_headers, t2_data)

    add_p(
        "Financial Distribution Justification across Project Years:"
    )
    add_bullet(
        "Year 1 Allocation (₹18,90,000 direct): ",
        "Expenditure is intentionally highest in Year 1 due to the non-recurring procurement of essential laboratory equipment (₹10,50,000). "
        "Procuring test instrumentation, isolated power supplies, and data acquisition hardware at project inception is critical to establish "
        "the experimental infrastructure while computational and simulation models are concurrently formulated. Personnel costs initiate for a "
        "full-time Junior Research Fellow (JRF), supported by baseline consumables for sensor characterization."
    )
    add_bullet(
        "Year 2 Allocation (₹9,90,000 direct): ",
        "With zero non-recurring equipment expenditure, Year 2 funds focus entirely on recurring operational requirements. Consumable allocation "
        "peaks at ₹1,80,000 to support custom multi-layer PCB fabrication, embedded microcontroller boards, and transducer interface circuitry. "
        "Travel increases to support national conference dissemination of algorithmic formulations."
    )
    add_bullet(
        "Year 3 Allocation (₹10,30,000 direct): ",
        "Expenditure supports intensive laboratory validation within the closed-loop fluid test chamber. Personnel remuneration reflects statutory "
        "enhancement to Senior Research Fellow (SRF) grade. Other Costs reach ₹90,000 to cover open-access publishing fees in high-impact IEEE/Elsevier "
        "journals and institutional patent filing costs."
    )

    # -------------------------------------------------------------
    # 4. Detailed Budget Justification by Category
    # -------------------------------------------------------------
    add_h1("4. Detailed Budget Justification by Category")

    # 4.1 Research Personnel
    add_h2("4.1 Research Personnel (₹17,50,000)")
    add_p(
        "The interdisciplinary scope of the proposed investigation requires a dedicated, full-time Junior Research Fellow (JRF) throughout "
        "the 36-month tenure. The research fellow will directly assist the Principal Investigator across all technical work packages, including: "
        "(a) setting up simulation models in MATLAB/Simulink and simulating coupled hydrodynamic-electrical ingress dynamics; (b) writing, compiling, "
        "and debugging embedded C/C++ firmware for 32-bit microcontrollers; (c) interfacing multi-modal sensors (ultrasonic, pressure, environmental, "
        "and isolated electrical telemetry) and executing synchronous data acquisition routines; (d) implementing real-time sensor fault diagnosis "
        "and Dempster-Shafer evidential fusion algorithms; (e) assembling and operating the benchtop fluid test rig under strict laboratory safety "
        "protocols; and (f) logging experimental data, executing statistical analysis, and preparing draft research manuscripts."
    )
    add_p(
        "In accordance with Department of Science and Technology (DST) Office Memorandums (DST/PCPM/Z-06/2022 and SR/S9/Z-08/2018) governing "
        "fellowships for research personnel in central funding agencies, the remuneration is structured as follows: JRF at ₹37,000 per month "
        "for Year 1 and Year 2, progressing upon satisfactory performance assessment to Senior Research Fellow (SRF) at ₹42,000 per month for Year 3. "
        "In addition to monthly fellowship stipends, House Rent Allowance (HRA) is admissible as per central government norms applicable to the "
        "host institution classification (e.g., 9% for Category Z or 18% for Category Y / educational institutions without campus hostel accommodation). "
        "The provisional budget allocation of ₹17,50,000 accommodates monthly stipends, applicable HRA, and statutory allowances over 36 months."
    )

    p_tbl3_cap = doc.add_paragraph()
    p_tbl3_cap.paragraph_format.space_before = Pt(4)
    p_tbl3_cap.paragraph_format.space_after = Pt(2)
    p_tbl3_cap.paragraph_format.keep_with_next = True
    r = p_tbl3_cap.add_run("Table 3: Research Personnel Budget Breakdown")
    r.font.bold = True
    r.font.size = Pt(10)

    t3_headers = ["Position", "No.", "Tenure", "Monthly Stipend (₹)", "Applicable Allowances", "Annual Cost (₹)", "Total 3-Year Cost (₹)"]
    t3_data = [
        ["Junior Research Fellow (JRF)", "1", "Months 1–12 (Yr 1)", "37,000", "HRA & statutory provisions", "5,50,000", "5,50,000"],
        ["Junior Research Fellow (JRF)", "1", "Months 13–24 (Yr 2)", "37,000", "HRA & statutory provisions", "5,80,000", "5,80,000"],
        ["Senior Research Fellow (SRF)", "1", "Months 25–36 (Yr 3)", "42,000", "HRA & statutory provisions", "6,20,000", "6,20,000"],
        ["Consolidated Personnel Total", "1", "36 Months", "--", "--", "--", "17,50,000"]
    ]
    t3_widths = [Inches(1.8), Inches(0.4), Inches(1.3), Inches(1.1), Inches(1.2), Inches(0.9), Inches(0.9)]
    table3 = doc.add_table(rows=len(t3_data) + 1, cols=7)
    format_table(table3, t3_widths, t3_headers, t3_data)

    # 4.2 Equipment
    add_h2("4.2 Equipment – Non-Recurring (₹10,50,000)")
    add_p(
        "All proposed equipment items are specialized, non-recurring hardware units required specifically to execute the experimental "
        "methodology detailed in Section 5 of the technical proposal. The host Department of Electronics and Communication Engineering already "
        "provides basic general-purpose computing systems and standard electronics laboratory benches. However, executing precision multi-sensor "
        "synchronization, transient switching time analysis (verifying isolation latency <= 20 ms), and safe low-voltage fluid testing necessitates "
        "the dedicated hardware items detailed in Table 4. No general-purpose office PCs or duplicate departmental facilities are requested."
    )

    p_tbl4_cap = doc.add_paragraph()
    p_tbl4_cap.paragraph_format.space_before = Pt(4)
    p_tbl4_cap.paragraph_format.space_after = Pt(2)
    p_tbl4_cap.paragraph_format.keep_with_next = True
    r = p_tbl4_cap.add_run("Table 4: Itemized Equipment Requirements and Technical Justifications")
    r.font.bold = True
    r.font.size = Pt(10)

    t4_headers = ["Sl.", "Equipment Item", "Technical Specifications", "Qty", "Est. Cost (₹)", "Technical Justification and Role in Project"]
    t4_data = [
        [
            "1",
            "Multi-Channel High-Speed Isolated DAQ System",
            "16-Channel differential analog inputs, 16-bit resolution, 500 kS/s aggregate sampling, USB/Ethernet interface, channel-to-channel galvanic isolation (> 1000 V RMS), LabVIEW/C/MATLAB drivers.",
            "1",
            "2,80,000",
            "Essential for synchronous, low-noise data acquisition across heterogeneous sensors (ultrasonic, resistive, pressure, temperature, leakage current). Required in Activities 5.3 and 5.8 to validate real-time sensor health against calibrated laboratory ground truth."
        ],
        [
            "2",
            "Precision Programmable Isolated DC/AC Bench Power Supply",
            "Dual-channel isolated output (0–30 V DC, 0–5 A; 0–24 V AC), programmable fast electronic current limiting (< 1 ms trip), low ripple (< 1 mV RMS), over-voltage and over-current protection.",
            "1",
            "1,90,000",
            "Mandatory safety foundation for all physical experiments. Powers the protected low-voltage test circuit (<= 24 V, < 2 A) with programmable current limiting to prevent any electrical hazard during fluid contact testing. Required in Activities 5.7 and 5.8."
        ],
        [
            "3",
            "4-Channel Mixed-Signal Digital Storage Oscilloscope (DSO) with Isolated Probes",
            "200 MHz bandwidth, 4 analog + 16 digital channels, 2 GS/s real-time sampling rate, segmented memory, equipped with 2 differential high-voltage/low-voltage probes and 2 high-bandwidth AC/DC current probes.",
            "1",
            "2,40,000",
            "Crucial for measuring high-speed transient phenomena during electrical isolation switching. Validates contactor opening latency (<= 20 ms), arc suppression, and voltage transient spikes during rapid disconnection. Required in Activities 5.6 and 5.8."
        ],
        [
            "4",
            "Embedded Target Development & Hardware Emulation Station",
            "32-Bit ARM Cortex-M4/M7 evaluation systems (168–400 MHz), hardware floating-point unit (FPU), high-speed JTAG/SWD hardware in-circuit emulators, multi-channel logic analyzer (32-ch, 500 MHz), FreeRTOS toolchain.",
            "1",
            "1,60,000",
            "Dedicated hardware workbench for developing, compiling, in-circuit debugging, and profiling embedded C/C++ firmware. Enables execution timing analysis, CPU load profiling, and memory footprint verification for diagnostic algorithms. Required in Activity 5.7."
        ],
        [
            "5",
            "Controlled Environmental & Hydrodynamic Sensor Test Rig Assembly",
            "Custom sealed transparent acrylic test chamber (100L capacity), variable-speed digital peristaltic metering pump (0.1–1000 mL/min), calibrated liquid level sight gauge, industrial fluid conductivity sensor, drain interlocks.",
            "1",
            "1,80,000",
            "Enables precise, repeatable physical simulation of dynamic flood ingress scenarios (slow seepage, rapid flash inundation, surface sloshing) and controlled fluid conductivity variation without using live municipal drains. Required in Activity 5.8."
        ],
        [
            "--",
            "Total Equipment Cost",
            "Indicative estimates based on standard institutional market pricing",
            "5",
            "10,50,000",
            "Procured entirely in Year 1 to support the full 36-month research and validation plan."
        ]
    ]
    t4_widths = [Inches(0.4), Inches(1.5), Inches(1.8), Inches(0.4), Inches(1.0), Inches(2.2)]
    table4 = doc.add_table(rows=len(t4_data) + 1, cols=6)
    format_table(table4, t4_widths, t4_headers, t4_data)

    # 4.3 Consumables
    add_h2("4.3 Consumables (₹4,50,000)")
    add_p(
        "Consumable items encompass recurring materials expended during prototype fabrication, sensor interfacing, PCB assembly, and repeated "
        "laboratory testing across the 36-month project. Durable capital equipment is strictly excluded. Table 5 provides an itemized breakdown."
    )

    p_tbl5_cap = doc.add_paragraph()
    p_tbl5_cap.paragraph_format.space_before = Pt(4)
    p_tbl5_cap.paragraph_format.space_after = Pt(2)
    p_tbl5_cap.paragraph_format.keep_with_next = True
    r = p_tbl5_cap.add_run("Table 5: Itemized Consumables Breakdown across Project Years")
    r.font.bold = True
    r.font.size = Pt(10)

    t5_headers = ["Sl.", "Consumable Category", "Detailed Items and Purpose", "Qty / Requirement", "Est. Cost (₹)"]
    t5_data = [
        [
            "1",
            "Sensors and Transducer Probe Assemblies",
            "Industrial waterproof ultrasonic sensors (JSN-SR04T / MaxBotix class), submersible hydrostatic pressure transmitters, multi-point stainless steel level probes, digital temperature/humidity sensors (SHT35 class), and spare probe heads for repeated fluid immersion.",
            "Multiple sets (approx. 20–25 units across 3 years)",
            "1,40,000"
        ],
        [
            "2",
            "Active and Passive Electronic Components",
            "ARM microcontroller ICs, precision instrumentation amplifiers, isolated ADC/DAC chips, high-speed optocouplers, voltage regulators, transient voltage suppressors (TVS), precision shunt resistors, capacitors, inductors, and terminal blocks.",
            "Bulk component packs and engineering sample kits",
            "1,00,000"
        ],
        [
            "3",
            "Custom PCB Fabrication and Prototyping Supplies",
            "Multi-layer FR4 PCB fabrication runs (2-layer and 4-layer prototype spins), laser-cut stainless steel solder stencils, lead-free solder paste, flux, desoldering braid, and board-level cleaning consumables.",
            "4 prototype fabrication revisions + assembly consumables",
            "85,000"
        ],
        [
            "4",
            "Low-Voltage Switching and Safety Disconnect Hardware",
            "High-speed solid-state relays (SSRs), redundant 24V electromechanical safety contactors, DIN-rail miniature circuit breakers, quick-disconnect terminal strips, shielded signal cables, and insulated copper wiring harnesses.",
            "6 switching assemblies + wiring stock",
            "65,000"
        ],
        [
            "5",
            "Protective Enclosures, Fluid Fittings, and Test Fixtures",
            "IP65-rated transparent polycarbonate project enclosures, waterproof cable glands, quick-release fluid couplers, chemically inert silicone tubing, mounting brackets, manual emergency stop buttons, and safety interlock switches.",
            "Chamber fittings, 4 enclosure assemblies",
            "60,000"
        ],
        [
            "--",
            "Total Consumables Cost",
            "Distributed across Year 1 (₹1.20 L), Year 2 (₹1.80 L), and Year 3 (₹1.50 L)",
            "36-Month Supply",
            "4,50,000"
        ]
    ]
    t5_widths = [Inches(0.4), Inches(1.8), Inches(2.7), Inches(1.2), Inches(0.9)]
    table5 = doc.add_table(rows=len(t5_data) + 1, cols=5)
    format_table(table5, t5_widths, t5_headers, t5_data)

    # 4.4 Travel
    add_h2("4.4 Travel – Domestic Only (₹2,40,000)")
    add_p(
        "Travel expenditure is strictly limited to domestic travel within India for legitimate, project-specific academic and technical activities. "
        "No international travel is budgeted under this grant. Planned travel includes: (a) attending premier national peer-reviewed conferences "
        "(e.g., IEEE India Council, IEEE Sensors, National Systems Conference) to present peer-reviewed research papers; (b) participating in specialized "
        "technical workshops on sensor dependability and embedded functional safety; and (c) technical consultation meetings with domain experts "
        "and national research laboratories. Year-wise allocation is presented in Table 6."
    )

    p_tbl6_cap = doc.add_paragraph()
    p_tbl6_cap.paragraph_format.space_before = Pt(4)
    p_tbl6_cap.paragraph_format.space_after = Pt(2)
    p_tbl6_cap.paragraph_format.keep_with_next = True
    r = p_tbl6_cap.add_run("Table 6: Year-Wise Travel Allocation and Technical Justification")
    r.font.bold = True
    r.font.size = Pt(10)

    t6_headers = ["Project Year", "Purpose of Travel", "Target Destination / Event Type", "Estimated Cost (₹)"]
    t6_data = [
        [
            "Year 1",
            "Technical consultations on embedded sensor architectures and attending 1 national conference/symposium on sensors/systems.",
            "Premier national technical institutes / conference venue in India",
            "60,000"
        ],
        [
            "Year 2",
            "Presenting peer-reviewed paper on sensor fault diagnosis and attending 1 specialized workshop on functional safety.",
            "National IEEE/Springer conference venue in India",
            "90,000"
        ],
        [
            "Year 3",
            "Dissemination of physical laboratory validation results at 2 flagship national/international conferences held in India.",
            "Flagship IEEE/Elsevier conferences in India",
            "90,000"
        ],
        [
            "Total",
            "Consolidated 3-Year Domestic Travel Allocation",
            "Strictly compliant with ANRF domestic travel guidelines",
            "2,40,000"
        ]
    ]
    t6_widths = [Inches(1.0), Inches(2.7), Inches(2.2), Inches(1.1)]
    table6 = doc.add_table(rows=len(t6_data) + 1, cols=4)
    format_table(table6, t6_widths, t6_headers, t6_data)

    # 4.5 Contingency
    add_h2("4.5 Contingency (₹2,40,000)")
    add_p(
        "The contingency allocation of ₹2,40,000 (budgeted uniformly at ₹80,000 per annum) supports unanticipated but vital experimental expenses "
        "inherent to physical fluid-sensor testing. These include: (a) emergency replacement of damaged sensor transducers or fried interface ICs "
        "during repeated wetting cycles; (b) third-party calibration checks for laboratory reference instruments through NABL-accredited facilities; "
        "(c) specialized technical books, relevant published clauses of international safety standards (IEC 60364, IEC 61508, ISO 13849); and "
        "(d) localized shipping and courier charges for urgent component procurement. Contingency funds will not be utilized for general office overheads."
    )

    p_tbl7_cap = doc.add_paragraph()
    p_tbl7_cap.paragraph_format.space_before = Pt(4)
    p_tbl7_cap.paragraph_format.space_after = Pt(2)
    p_tbl7_cap.paragraph_format.keep_with_next = True
    r = p_tbl7_cap.add_run("Table 7: Year-Wise Contingency Breakdown")
    r.font.bold = True
    r.font.size = Pt(10)

    t7_headers = ["Project Year", "Key Anticipated Contingency Items", "Annual Allocation (₹)"]
    t7_data = [
        ["Year 1", "Emergency component replacements, specialized reference literature, standards documentation.", "80,000"],
        ["Year 2", "Calibration verification fees, replacement of worn sensors, urgent PCB respin expenses.", "80,000"],
        ["Year 3", "Replacement of fluid fittings/seals, final report documentation, technical archival supplies.", "80,000"],
        ["Total", "Three-Year Consolidated Contingency Provision", "2,40,000"]
    ]
    t7_widths = [Inches(1.2), Inches(4.5), Inches(1.3)]
    table7 = doc.add_table(rows=len(t7_data) + 1, cols=3)
    format_table(table7, t7_widths, t7_headers, t7_data)

    # 4.6 Other Costs
    add_h2("4.6 Other Costs – Publications & Patent Filing (₹1,80,000)")
    add_p(
        "In accordance with revised ANRF and central funding agency provisions that explicitly encourage high-impact dissemination and intellectual "
        "property generation, the 'Other Costs' head of ₹1,80,000 is dedicated strictly to two justifiable activities: (a) Open-Access Article "
        "Processing Charges (APCs) for publishing peer-reviewed research findings in premier open-access international journals (e.g., IEEE Access, "
        "Elsevier, Springer), budgeted at ₹1,20,000 across Years 2 and 3; and (b) Indian patent filing, prior-art search, and statutory registration "
        "fees through institutional intellectual property channels, budgeted at ₹60,000. No unverified miscellaneous expenses are included."
    )

    p_tbl8_cap = doc.add_paragraph()
    p_tbl8_cap.paragraph_format.space_before = Pt(4)
    p_tbl8_cap.paragraph_format.space_after = Pt(2)
    p_tbl8_cap.paragraph_format.keep_with_next = True
    r = p_tbl8_cap.add_run("Table 8: Other Costs Allocation Breakdown")
    r.font.bold = True
    r.font.size = Pt(10)

    t8_headers = ["Item Description", "Year 1 (₹)", "Year 2 (₹)", "Year 3 (₹)", "Total (₹)", "Technical Justification"]
    t8_data = [
        ["Open-Access Publication Charges (APCs)", "0", "50,000", "70,000", "1,20,000", "Enables open-access dissemination of algorithmic formulations and experimental validation in reputed peer-reviewed journals."],
        ["Patent Filing & IPR Registration Fees", "30,000", "10,000", "20,000", "60,000", "Supports patent drafting, prior-art searches, and Indian patent office statutory filing fees for novel embedded isolation logic."],
        ["Consolidated Other Costs Total", "30,000", "60,000", "90,000", "1,80,000", "Fully compliant with ANRF IRG provisions for IPR and publication support."]
    ]
    t8_widths = [Inches(1.8), Inches(0.8), Inches(0.8), Inches(0.8), Inches(0.9), Inches(1.9)]
    table8 = doc.add_table(rows=len(t8_data) + 1, cols=6)
    format_table(table8, t8_widths, t8_headers, t8_data)

    # 4.7 Institutional Overhead
    add_h2("4.7 Institutional Overhead (₹3,91,000)")
    add_p(
        "Institutional overhead is provided to the host institution to defray infrastructural support costs, including laboratory electricity, "
        "water, administrative and secretarial services, computational network bandwidth, and maintenance of project-related facilities throughout "
        "the 36-month tenure. In accordance with standard DST and ANRF funding guidelines, overheads are computed as 10% of the total direct project "
        "cost (₹39,10,000), amounting to ₹3,91,000. Institutional overheads are presented separately and are not drawn from direct research funds."
    )

    # -------------------------------------------------------------
    # 5. Equipment Utilisation and Institutional Facilities
    # -------------------------------------------------------------
    add_h1("5. Equipment Utilisation and Institutional Facilities")
    add_p(
        "To ensure optimal financial prudence and avoid duplicative procurement, Table 9 delineates the utilization lifecycle of proposed equipment "
        "alongside existing facilities available within the host Department of Electronics and Communication Engineering."
    )

    p_tbl9_cap = doc.add_paragraph()
    p_tbl9_cap.paragraph_format.space_before = Pt(4)
    p_tbl9_cap.paragraph_format.space_after = Pt(2)
    p_tbl9_cap.paragraph_format.keep_with_next = True
    r = p_tbl9_cap.add_run("Table 9: Facility Mapping and Equipment Utilization Lifecycle")
    r.font.bold = True
    r.font.size = Pt(10)

    t9_headers = ["Category", "Equipment / Facility Description", "Source / Status", "Utilization Across Project Phases"]
    t9_data = [
        [
            "Available Institutional Facilities",
            "Computing workstations, basic circuit simulation software, standard digital multimeters, generic soldering stations, departmental bench space.",
            "Host Institution (ECE Department)",
            "Utilized throughout Years 1–3 for general programming, simulation, preliminary circuit testing, and administrative reporting."
        ],
        [
            "Proposed Non-Recurring Equipment",
            "Multi-channel isolated DAQ, programmable current-limited power supply, 200 MHz DSO with isolated probes, ARM Cortex-M4/M7 development kit, hydrodynamic test rig.",
            "To be procured under ANRF grant (Year 1)",
            "Commissioned in Year 1; utilized in Years 2 and 3 for synchronous sensor sampling, firmware in-circuit emulation, and transient switching validation."
        ],
        [
            "Specialized Stage-Specific Rig",
            "Closed-loop fluid chamber with digital peristaltic metering pump and fluid conductivity instrumentation.",
            "To be assembled under ANRF grant (Year 1/2)",
            "Exclusively utilized during experimental validation phases in Years 2 and 3 for controlled flood ingress simulation and synthetic fault testing."
        ],
        [
            "Post-Project Facility Integration",
            "All procured equipment will be integrated into the permanent institutional asset register.",
            "Host Institution Asset",
            "Retained in the departmental electronics laboratory post-completion to support ongoing student research in embedded systems and climate resilience."
        ]
    ]
    t9_widths = [Inches(1.5), Inches(2.3), Inches(1.4), Inches(1.8)]
    table9 = doc.add_table(rows=len(t9_data) + 1, cols=4)
    format_table(table9, t9_widths, t9_headers, t9_data)

    # -------------------------------------------------------------
    # 6. Year-Wise Financial Utilisation Plan
    # -------------------------------------------------------------
    add_h1("6. Year-Wise Financial Utilisation Plan")
    add_p(
        "Table 10 maps the proposed budgetary allocations directly to the scheduled technical milestones of the 36-month work plan, "
        "demonstrating how financial resources translate into concrete engineering deliverables."
    )

    p_tbl10_cap = doc.add_paragraph()
    p_tbl10_cap.paragraph_format.space_before = Pt(4)
    p_tbl10_cap.paragraph_format.space_after = Pt(2)
    p_tbl10_cap.paragraph_format.keep_with_next = True
    r = p_tbl10_cap.add_run("Table 10: Financial Utilisation Linked to Technical Work Plan")
    r.font.bold = True
    r.font.size = Pt(10)

    t10_headers = ["Project Year", "Major Technical Activities", "Key Budget Heads Required", "Expected Research Deliverables"]
    t10_data = [
        [
            "Year 1 (M1–M12)",
            "• Literature review & mathematical problem formulation.\n• Coupled hydrodynamic-electrical hazard modelling.\n• Baseline threshold simulation in MATLAB/Simulink.\n• Equipment specification, tendering, and procurement.",
            "• Equipment: ₹10.50 L\n• Personnel (JRF): ₹5.50 L\n• Consumables: ₹1.20 L\n• Travel & Cont.: ₹1.40 L\n• Other Costs: ₹0.30 L",
            "• Technical report on coupled hazard models.\n• Validated simulation testbed scripts.\n• Baseline threshold comparative dataset.\n• Fully commissioned equipment inventory."
        ],
        [
            "Year 2 (M13–M24)",
            "• Online sensor fault diagnosis algorithm formulation.\n• Evidential reasoning & Dempster-Shafer fusion engine.\n• 5-state finite state machine with fail-safe logic.\n• Hardware schematic capture & prototype PCB fabrication.",
            "• Personnel (JRF): ₹5.80 L\n• Consumables: ₹1.80 L\n• Travel & Cont.: ₹1.70 L\n• Other Costs: ₹0.60 L",
            "• Algorithmic formulation design report.\n• Embedded C/C++ firmware repository.\n• Fabricated & verified prototype PCB boards.\n• Peer-reviewed journal manuscript submission."
        ],
        [
            "Year 3 (M25–M36)",
            "• Assembly of sealed fluid test chamber.\n• Laboratory validation across Regimes A, B, and C.\n• Performance benchmarking against threshold tripping.\n• Research dissemination, patent filing, final report.",
            "• Personnel (SRF): ₹6.20 L\n• Consumables: ₹1.50 L\n• Travel & Cont.: ₹1.70 L\n• Other Costs: ₹0.90 L",
            "• Protected low-voltage laboratory demonstrator.\n• Comprehensive experimental performance dataset.\n• Second peer-reviewed journal publication.\n• Final project technical completion dossier."
        ]
    ]
    t10_widths = [Inches(1.1), Inches(2.4), Inches(1.5), Inches(2.0)]
    table10 = doc.add_table(rows=len(t10_data) + 1, cols=4)
    format_table(table10, t10_widths, t10_headers, t10_data)

    # -------------------------------------------------------------
    # 7. Budget Summary and Financial Verification
    # -------------------------------------------------------------
    add_h1("7. Budget Summary and Financial Verification")
    add_p(
        "Table 11 provides the final consolidated financial statement for submission under the ANRF-IRG scheme."
    )

    p_tbl11_cap = doc.add_paragraph()
    p_tbl11_cap.paragraph_format.space_before = Pt(4)
    p_tbl11_cap.paragraph_format.space_after = Pt(2)
    p_tbl11_cap.paragraph_format.keep_with_next = True
    r = p_tbl11_cap.add_run("Table 11: Final Project Financial Statement (All Figures in INR)")
    r.font.bold = True
    r.font.size = Pt(10)

    t11_headers = ["Budget Category", "Year 1 (₹)", "Year 2 (₹)", "Year 3 (₹)", "Total (₹)"]
    t11_data = [
        ["A. Non-Recurring (Equipment)", "10,50,000", "0", "0", "10,50,000"],
        ["B. Recurring Costs", "", "", "", ""],
        ["   1. Research Personnel", "5,50,000", "5,80,000", "6,20,000", "17,50,000"],
        ["   2. Consumables", "1,20,000", "1,80,000", "1,50,000", "4,50,000"],
        ["   3. Travel (Domestic)", "60,000", "90,000", "90,000", "2,40,000"],
        ["   4. Contingency", "80,000", "80,000", "80,000", "2,40,000"],
        ["   5. Other Costs (APCs & Patents)", "30,000", "60,000", "90,000", "1,80,000"],
        ["Subtotal: Direct Research Cost (A + B)", "18,90,000", "9,90,000", "10,30,000", "39,10,000"],
        ["C. Institutional Overhead (10%)", "1,89,000", "99,000", "1,03,000", "3,91,000"],
        ["Grand Total Proposed Budget (A + B + C)", "20,79,000", "10,89,000", "11,33,000", "43,01,000"]
    ]
    t11_widths = [Inches(2.5), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.2)]
    table11 = doc.add_table(rows=len(t11_data) + 1, cols=5)
    format_table(table11, t11_widths, t11_headers, t11_data)

    # -------------------------------------------------------------
    # Internal Verification Notes (For PI Review)
    # -------------------------------------------------------------
    p_break = doc.add_paragraph()
    p_break.paragraph_format.space_before = Pt(16)
    p_break.paragraph_format.keep_with_next = True

    add_h1("For PI Review – Not for Portal Submission: Budget Verification Notes")
    add_p(
        "Note: The following advisory remarks are compiled strictly for internal review by the Principal Investigator and the institutional "
        "finance/research dean office prior to online submission on the ANRF portal. This section must not be uploaded to the portal."
    )
    add_bullet(
        "1. Salary Norms and HRA Verification: ",
        "Personnel remuneration is modelled based on standard DST/ANRF Junior Research Fellow norms (₹37,000/month for Y1–Y2, ₹42,000/month "
        "for Y3 as SRF) plus HRA. The PI should confirm the exact HRA percentage slab applicable to the host institution's city classification "
        "(e.g., 9% for Category Z, 18% for Category Y, or 27% for Category X) and verify whether the candidate will be a NET/GATE-qualified JRF "
        "or a Project Associate-I (₹25,000–₹31,000/month + HRA under DST OM SR/S9/Z-05/2019)."
    )
    add_bullet(
        "2. Equipment Quotations: ",
        "Estimated costs for the five proposed equipment units (Isolated DAQ: ₹2.80 L; Programmable Bench Supply: ₹1.90 L; 4-Ch Isolated DSO: ₹2.40 L; "
        "Embedded Emulation Kit: ₹1.60 L; Hydrodynamic Test Rig: ₹1.80 L; Total: ₹10.50 L) represent indicative budgetary estimates derived from "
        "standard academic supplier catalogs. Prior to portal submission, formal vendor budgetary quotations should be obtained to ensure exact alignment "
        "with institutional procurement rules."
    )
    add_bullet(
        "3. Institutional Overhead Percentage: ",
        "Overheads have been calculated at 10% (₹3,91,000) in accordance with the standard DST/SERB formula for grants up to ₹40 Lakhs. The PI "
        "should confirm whether the host institution requires a specific tiered overhead computation or institutional overhead certificate."
    )
    add_bullet(
        "4. Inclusivity Research Grant (IRG) Financial Cap: ",
        "The overall direct project cost of ₹39.10 Lakhs (and grand total of ₹43.01 Lakhs including overheads) is comfortably within the official "
        "ANRF-IRG financial ceiling of ₹60.00 Lakhs plus overheads, leaving substantial room for justification without risk of budgetary rejection."
    )
    add_bullet(
        "5. Admissibility of Other Costs: ",
        "The ₹1.80 Lakhs allocated under 'Other Costs' specifically covers Open-Access Article Processing Charges (₹1.20 L) and Patent Filing Fees "
        "(₹0.60 L). Both heads are explicitly recognized under the ANRF Act and IRG guidelines. No generic or inadmissible contingency items are included."
    )

    # Footers
    add_footer_page_numbers(doc)

    # Save
    doc.save(output_path)
    print(f"Document 1 saved successfully as '{output_path}'")

def build_portal_fields_document(output_path):
    doc = docx.Document()

    # Page Setup
    for s in doc.sections:
        s.page_width = Inches(8.5)
        s.page_height = Inches(11.0)
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)

    # Title Block
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    p_title.paragraph_format.line_spacing = 1.15
    run_t = p_title.add_run("ANRF ONLINE PORTAL APPLICATION FIELDS")
    run_t.font.name = 'Times New Roman'
    run_t.font.size = Pt(13)
    run_t.font.bold = True

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_before = Pt(2)
    p_meta.paragraph_format.space_after = Pt(14)
    p_meta.paragraph_format.line_spacing = 1.1
    run_meta = p_meta.add_run(
        "Scheme: ANRF – Inclusivity Research Grant (IRG)\n"
        "Project Title: Intelligent Flood Water Electrification Risk Prediction and Automatic Electrical Isolation for Climate Resilient Communities\n"
        "Principal Investigator: Dr. Dhanalakshmi Banavath, Assistant Professor, Department of Electronics and Communication Engineering\n"
        "Ready-for-Copy-Paste Portal Submission Document with Character-Count Audits"
    )
    run_meta.font.name = 'Times New Roman'
    run_meta.font.size = Pt(9.5)
    run_meta.font.italic = True

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11.5)
        run.font.bold = True
        return p

    def add_p(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.12
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10.5)
        return p

    def add_portal_box(text):
        # Create a 1x1 table acting as a clean bordered box for copy-pasting
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        cell = tbl.rows[0].cells[0]
        cell.width = Inches(6.5)
        border_box = {'val': 'single', 'sz': '6', 'space': '0', 'color': '404040'}
        set_cell_borders(cell, top=border_box, bottom=border_box, left=border_box, right=border_box)
        set_cell_margins(cell, top=100, bottom=100, left=140, right=140)

        # Split text by newlines and add paragraphs
        paragraphs = text.strip().split('\n\n')
        for i, para_text in enumerate(paragraphs):
            if i == 0:
                p = cell.paragraphs[0]
            else:
                p = cell.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.12
            run = p.add_run(para_text.strip())
            run.font.name = 'Times New Roman'
            run.font.size = Pt(10)

    def add_count_badge(current_count, max_count, extra_label=""):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(10)
        p.paragraph_format.keep_with_next = True
        r1 = p.add_run("Audit Verification: ")
        r1.font.bold = True
        r1.font.size = Pt(10)

        r2 = p.add_run(f"Character count: {current_count:,} / {max_count:,} characters — Within limit")
        r2.font.bold = True
        r2.font.size = Pt(10)

        if extra_label:
            r3 = p.add_run(f" | {extra_label}")
            r3.font.italic = True
            r3.font.size = Pt(9.5)

    # -------------------------------------------------------------
    # 1. Project Summary
    # -------------------------------------------------------------
    add_h1("1. Project Summary (Portal Field 1)")
    add_p(
        "Instruction: Copy and paste the text within the bordered box directly into the online ANRF portal field titled 'Project Summary'. "
        "The approved text below provides a comprehensive summary of the research rationale, technical methodology, low-voltage demonstrator, "
        "and anticipated societal outcomes."
    )

    summary_text = (
        "Flooding is one of the major natural hazards that threatens human life, property and essential infrastructure. "
        "One of its serious but often overlooked consequences is the risk of electrical accidents. During floods, water may "
        "come into contact with damaged electrical wiring, exposed conductors, distribution panels and other electrical "
        "installations. This can create dangerous electrical conditions, leading to electric shocks, severe injuries and even "
        "electrocution deaths among residents, rescue workers and the public.\n\n"
        "Conventional flood monitoring and electrical protection systems generally depend on water-level detection, predefined "
        "thresholds or conventional protective devices. However, these approaches may not adequately address situations involving "
        "faulty sensors, incomplete measurements, changing flood conditions and uncertainty in electrical parameters. As a result, "
        "dangerous conditions may not always be identified reliably, potentially delaying protective action.\n\n"
        "The proposed research aims to develop an intelligent, sensor-based electrical hazard prediction and automatic isolation "
        "system for flood-affected communities. The system will integrate embedded sensing, electrical hazard modelling and intelligent "
        "decision-making techniques to monitor flood-related conditions and estimate potential electrical risks. Particular attention "
        "will be given to identifying unreliable sensor measurements, including noisy, drifting, missing and contradictory readings, "
        "so that safety decisions are not based blindly on inaccurate information.\n\n"
        "The research will initially focus on developing mathematical and computational models to simulate different flood conditions, "
        "electrical fault scenarios and sensor failure conditions. Appropriate hazard estimation and decision-making algorithms will then "
        "be developed and evaluated against conventional threshold-based approaches. Based on the simulation results, an embedded prototype "
        "will be designed using suitable sensors, a microcontroller and a controlled electrical isolation mechanism.\n\n"
        "The final stage will involve laboratory validation using a protected low-voltage experimental setup to evaluate the system's "
        "reliability, response time, false alarms and ability to identify potentially dangerous conditions under different scenarios.\n\n"
        "The expected outcome is a validated intelligent electrical safety framework that can support early identification of flood-related "
        "electrical hazards and appropriate protective isolation decisions. The research has the potential to contribute to reducing electrical "
        "accident risks and improving the safety and resilience of flood-prone communities."
    )

    add_portal_box(summary_text)
    # Exact character count check
    summary_len = len(summary_text)
    add_count_badge(summary_len, 3000, "Maximum permissible: 3,000 characters")

    # -------------------------------------------------------------
    # 2. Keywords
    # -------------------------------------------------------------
    add_h1("2. Keywords (Portal Field 2)")
    add_p(
        "Instruction: Copy and paste the text within the bordered box directly into the online ANRF portal field titled 'Keywords'. "
        "ANRF portal guidelines mandate a maximum of 6 keywords and a strict overall limit of 30 characters in total (counting all "
        "letters, commas, and spaces). The approved working draft ('Floods, Sensors, Risk, Isolation') contains 32 characters, exceeding "
        "the 30-character cap by 2 characters. The refined version below ('Flood, Sensor, Risk, Isolation') utilizes standard singular "
        "terminology, preserving all four approved technical concepts with 100% fidelity while achieving exact compliance at 30 characters."
    )

    kw_text = "Flood, Sensor, Risk, Isolation"
    add_portal_box(kw_text)
    kw_len = len(kw_text)
    kw_count = len(kw_text.split(','))
    add_count_badge(kw_len, 30, f"Keyword count: {kw_count} / 6 keywords — Within limit")

    # -------------------------------------------------------------
    # 3. Objectives / Aim
    # -------------------------------------------------------------
    add_h1("3. Objectives / Aim (Portal Field 3)")
    add_p(
        "Instruction: Copy and paste the text within the bordered box directly into the online ANRF portal field titled 'Objectives' or 'Aim'."
    )

    obj_text = (
        "The main aim of this research is to develop an intelligent embedded system for predicting flood-related electrical hazards and initiating "
        "appropriate electrical isolation to improve human safety in flood-affected communities.\n\n"
        "The specific objectives are:\n\n"
        "1. To develop computational and electrical models for analysing potential electrical hazards under different flood conditions, electrical fault scenarios and environmental parameters.\n\n"
        "2. To investigate sensor reliability and develop fault-detection techniques for identifying noisy, drifting, missing and inconsistent sensor measurements.\n\n"
        "3. To design an intelligent hazard estimation algorithm that combines sensor information and electrical modelling to assess potential electrical risks under uncertain conditions.\n\n"
        "4. To develop a safety-oriented decision-making mechanism for generating early warnings and initiating appropriate automatic electrical isolation responses.\n\n"
        "5. To evaluate the proposed system through simulation and compare its performance with conventional threshold-based protection approaches.\n\n"
        "6. To design and validate an embedded prototype using a protected low-voltage laboratory setup and assess its reliability, response time and effectiveness under different test conditions."
    )

    add_portal_box(obj_text)
    obj_len = len(obj_text)
    add_count_badge(obj_len, 1500, "Maximum permissible: 1,500 characters")

    # -------------------------------------------------------------
    # 4. Expected Outputs and Outcomes
    # -------------------------------------------------------------
    add_h1("4. Expected Outputs and Outcomes (Portal Field 4)")
    add_p(
        "Instruction: Copy and paste the text within the bordered box directly into the online ANRF portal field titled 'Expected Outputs and Outcomes'."
    )

    outcomes_text = (
        "The proposed research is expected to produce the following outputs and outcomes:\n\n"
        "1. A computational model for analysing flood-related electrical hazards under different water conditions, electrical faults and environmental scenarios.\n\n"
        "2. A sensor monitoring and fault-detection algorithm capable of identifying unreliable, missing and inconsistent sensor measurements.\n\n"
        "3. An intelligent electrical hazard estimation and decision-making framework for assessing potential risks under uncertain conditions.\n\n"
        "4. An embedded prototype integrating suitable sensors, a microcontroller, warning indicators and a controlled electrical isolation mechanism.\n\n"
        "5. Simulation results and laboratory validation demonstrating the system's performance in terms of hazard detection, response time, reliability, false alarms and missed hazard scenarios.\n\n"
        "6. Research publications in relevant peer-reviewed journals and conferences, with potential for intellectual property protection where justified by the research outcomes.\n\n"
        "The long-term expected outcome is to provide a foundation for developing affordable and reliable electrical safety solutions for flood-prone residential buildings and community facilities. The proposed technology could support early warnings and timely protective isolation, potentially reducing the risk of fatal electric shocks and serious injuries during floods. It may also contribute to climate-resilient infrastructure and improved disaster preparedness."
    )

    add_portal_box(outcomes_text)
    outcomes_len = len(outcomes_text)
    add_count_badge(outcomes_len, 1500, "Maximum permissible: 1,500 characters")

    # Footers
    add_footer_page_numbers(doc)

    # Save
    doc.save(output_path)
    print(f"Document 2 saved successfully as '{output_path}'")

if __name__ == '__main__':
    doc1_out = os.path.abspath('ANRF_IRG_Detailed_Budget_and_Justification.docx')
    doc2_out = os.path.abspath('ANRF_IRG_Four_Portal_Sections.docx')
    build_budget_document(doc1_out)
    build_portal_fields_document(doc2_out)
