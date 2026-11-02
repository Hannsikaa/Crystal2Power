import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=45, bottom=45, left=90, right=90):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for border_name, border_style in borders.items():
        if border_style is not None:
            border = OxmlElement(f'w:{border_name}')
            for key, val in border_style.items():
                border.set(qn(f'w:{key}'), str(val))
            tcBorders.append(border)
        else:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), 'none')
            tcBorders.append(border)
    tcPr.append(tcBorders)

def format_table(table, col_widths, headers, data, alignment=WD_TABLE_ALIGNMENT.CENTER):
    table.alignment = alignment
    table.autofit = False

    # Header Row
    hdr_row = table.rows[0]
    hdr_trPr = hdr_row._tr.get_or_add_trPr()
    hdr_trPr.append(OxmlElement('w:tblHeader'))
    hdr_trPr.append(OxmlElement('w:cantSplit'))

    border_thin = {'val': 'single', 'sz': '4', 'space': '0', 'color': '000000'}

    for idx, heading in enumerate(headers):
        cell = hdr_row.cells[idx]
        cell.text = heading
        cell.width = col_widths[idx]
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        set_cell_borders(cell, top=border_thin, bottom=border_thin, left=border_thin, right=border_thin)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.keep_with_next = True
        for r in p.runs:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0, 0, 0)

    # Data Rows
    for r_idx, row_data in enumerate(data):
        row = table.rows[r_idx + 1]
        row_trPr = row._tr.get_or_add_trPr()
        row_trPr.append(OxmlElement('w:cantSplit'))
        for c_idx, cell_value in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.text = cell_value
            cell.width = col_widths[c_idx]
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            set_cell_borders(cell, top=border_thin, bottom=border_thin, left=border_thin, right=border_thin)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.05
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(9)
                r.font.color.rgb = RGBColor(0, 0, 0)

def add_footer_page_numbers(doc):
    for s in doc.sections:
        footer = s.footer
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run("Page ")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(80, 80, 80)

        # Field for current page
        fldSimple1 = OxmlElement('w:fldSimple')
        fldSimple1.set(qn('w:instr'), 'PAGE')
        p._p.append(fldSimple1)

        run2 = p.add_run(" of ")
        run2.font.name = 'Times New Roman'
        run2.font.size = Pt(9)
        run2.font.color.rgb = RGBColor(80, 80, 80)

        # Field for total pages
        fldSimple2 = OxmlElement('w:fldSimple')
        fldSimple2.set(qn('w:instr'), 'NUMPAGES')
        p._p.append(fldSimple2)
