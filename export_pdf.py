from fpdf import FPDF
from utils import safe_text
import pypdf

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

    for event in heat_sheet:

        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(
            0, 6,
            safe_text(f"Event {event['number']}: {event['name']}"),
            ln=1
        )

        pdf.set_font("Helvetica", "", 9)

        for heat in event["heats"]:

            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 5, f"Heat {heat['heat_number']}", ln=1)

            # Sort lanes by number
            sorted_lanes = sorted(heat["lanes"].items(), key=lambda x: int(x[0]))
            for lane, s in sorted_lanes:

                fav = "★ " if s["name"] in favorites else ""

                text = f"{fav}Lane {lane} {s['name']} {s['seed_time']} {s['age']}"

                pdf.cell(0, 5, safe_text(text), ln=1)

    
    # output = pdf.output(dest="S")
    # if isinstance(output, (bytes, bytearray)):
    #     return bytes(output)

    return output.encode("latin-1")
