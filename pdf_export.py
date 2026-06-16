from fpdf import FPDF
from utils import safe_text

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, self.title, ln=1, align="C")


def generate_pdf(meet_title, heat_sheet, favorites):

    pdf = PDF()
    pdf.title = meet_title
    pdf.set_auto_page_break(True, margin=10)

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Heat Sheet", ln=1)

    pdf.set_font("Helvetica", "", 10)

    for event in heat_sheet:
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, f"Event {event['number']}: {event['name']}", ln=1)

        pdf.set_font("Helvetica", "", 9)

        for s in event["swimmers"]:
            fav = "★ " if s["name"] in favorites else ""
            pdf.cell(
                0, 5,
                f"{fav}{s.get('name')} {s.get('seed_time')} {s.get('age')}",
                ln=1
            )

    return bytes(pdf.output(dest="S").encode("latin-1"))
