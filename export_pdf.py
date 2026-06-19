from fpdf import FPDF
from utils import safe_text


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, self.title, ln=1, align="C")
        self.ln(2)


def generate_pdf(meet_title, heat_sheet, favorites):

    pdf = PDF()
    pdf.title = meet_title
    pdf.set_auto_page_break(True, margin=10)

    pdf.add_page()

    # -------------------------
    # Title
    # -------------------------
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, safe_text("Heat Sheet"), ln=1)
    pdf.ln(2)

    # -------------------------
    # Two-column layout setup
    # -------------------------
    col_width = pdf.w / 2 - 10
    left_x = 10
    right_x = pdf.w / 2 + 5
    y_start = pdf.get_y()

    col = 0
    x = left_x
    y = y_start

    def switch_column():
        nonlocal col, x, y
        if col == 0:
            col = 1
            x = right_x
            y = y_start
        else:
            col = 0
            x = left_x
            pdf.add_page()
            y_start_new = pdf.get_y()
            y = y_start_new

    # -------------------------
    # Content
    # -------------------------
    pdf.set_font("Helvetica", "", 9)

    for event in heat_sheet:

        event_header = safe_text(
            f"Event {event['event_number']}: {event['event_name']}"
        )

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_xy(x, y)
        pdf.multi_cell(col_width, 5, event_header)

        y = pdf.get_y()

        pdf.set_font("Helvetica", "", 9)

        for heat in event["heats"]:

            heat_header = safe_text(f"Heat {heat.heat_number}")

            pdf.set_font("Helvetica", "B", 9)
            pdf.set_xy(x, y)
            pdf.cell(col_width, 5, heat_header, ln=1)

            y = pdf.get_y()

            # IMPORTANT FIX: lanes is list of Lane objects OR dict fallback
            lanes = heat.lanes

            if isinstance(lanes, dict):
                sorted_lanes = sorted(lanes.items(), key=lambda x: int(x[0]))
                lane_iter = [(lane, entry) for lane, entry in sorted_lanes]
            else:
                lane_iter = sorted(
                    lanes,
                    key=lambda l: l.lane_number
                )
                lane_iter = [
                    (l.lane_number, l.entry)
                    for l in lane_iter
                ]

            for lane, entry in lane_iter:

                swimmer = entry.swimmer
                fav = "★ " if swimmer.name in favorites else ""

                text = safe_text(
                    f"{fav}Lane {lane} "
                    f"{swimmer.name} "
                    f"{entry.entry_time} "
                    f"{swimmer.age}"
                )

                pdf.set_xy(x, y)
                pdf.cell(col_width, 5, text, ln=1)

                y = pdf.get_y()

                # column switch if space runs out
                if y > 260:
                    switch_column()
                    y = pdf.get_y()

    output = pdf.output(dest="S")

    if isinstance(output, (bytes, bytearray)):
        return bytes(output)

    return output.encode("latin-1")
