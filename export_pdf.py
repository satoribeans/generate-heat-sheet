from fpdf import FPDF
from utils import safe_text
from models import Meet


class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
        self.add_font("DejaVu", "B", "fonts/DejaVuSansCondensed-Bold.ttf", uni=True)

    def header(self):
        self.set_font("DejaVu", "B", 12)
        self.cell(0, 8, self.title, ln=1, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)  # <-- this is the key
        self.set_font("DejaVu", "B", 8)
        footer_text = (
            f"For entertainment only — generated from the psych sheet; not an official meet document. Good luck swimmers!       "
            f"Page {self.page_no()} of {{nb}}"
        )
        self.cell(0, 8, footer_text, ln=1, align="C")
        self.ln(2)

    def print_event_header(self, event, x, y, width):
        self.set_xy(x, y)

        self.set_font("DejaVu", "B", 9)

        self.multi_cell(
            width,
            5,
            f"Event {event.event_number}: {event.name}",
        )
        # st.write("printed event header at: ", self.get_y())
        return self.get_y()


    def print_heat(self, heat, event_total_heats, x, y):
        self.set_xy(x, y)
        # Heat 2 of 15
        self.set_font("DejaVu", "B", 9)
        self.cell(
            0,
            5,
            f"Heat {heat.heat_number} of {event_total_heats}",
            ln=1
        )

        # 1 John Doe 15 NCAC 1:23.45
        self.set_font("DejaVu", "", 9)
        for lane in sorted(heat.lanes, key=lambda l: l.lane_number):
            entry = lane.entry
            if not entry:
                continue
            swimmer = entry.swimmer
            self.set_x(x)
            self.cell(5, 5, str(lane.lane_number), 0, 0, "C")
            self.cell(40, 5, swimmer.name[:22], 0, 0, "L")
            self.cell(10, 5, str(swimmer.age), 0, 0, "C")
            self.cell(15, 5, swimmer.team[:8], 0, 0, "L")
            self.cell(20, 5, entry.entry_time, 0, 1, "R")
        return self.get_y()

def generate_pdf(meet, favorites_entries):

    pdf = PDF(
        orientation="P",
        unit="mm",
        format="Letter"
    )

    pdf.alias_nb_pages()  # enables {nb} replacement
    pdf.title = meet.name

    # --------------------------------------------------
    # FAVORITES PAGE
    # --------------------------------------------------
    if len(favorites_entries) > 0:
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 14)
        pdf.cell(0, 20, "Favorite Swimmers", ln=1)
        pdf.set_font("DejaVu", "", 10)
    
        # ------------------------------------------
        # Render grouped output
        # ------------------------------------------
        for swimmer_name, entries in favorites_entries.items(): # grouped.items():
    
            # Swimmer header
            pdf.set_font("DejaVu", "B", 11)
            pdf.cell(0, 6, safe_text(swimmer_name), ln=1)
    
            # Table header
            pdf.set_font("DejaVu", "B", 10)
            pdf.cell(20, 6, "", 0, 0)  # indent
            pdf.cell(15, 6, "Event", 1, 0, "C")
            pdf.cell(100, 6, "Event Name", 1, 0, "C")
            pdf.cell(15, 6, "Heat", 1, 0,"C")
            pdf.cell(15, 6, "Lane", 1, 0, "C")
            pdf.cell(20, 6, "Time", 1, 1, "C")
            # Rows under swimmer
            pdf.set_font("DejaVu", "B", 9)
            for entry in entries:
                pdf.cell(20, 6, "", 0, 0)  # indent
                pdf.cell(15, 6, str(entry.event.event_number), 1, 0, "C")
                pdf.cell(100, 6, entry.event.name, 1, 0, "L")
                pdf.cell(15, 6, str(entry.heat_number), 1, 0, "C")
                pdf.cell(15, 6, str(entry.lane_number), 1, 0, "C")
                pdf.cell(20, 6, entry.entry_time, 1, 1, "R")
            pdf.ln(2)

    # --------------------------------------------------
    # HEAT SHEET
    # --------------------------------------------------
    pdf.add_page()

    gutter = 5
    column_width = (
        pdf.w
        - pdf.l_margin
        - pdf.r_margin
        - gutter
    ) / 2

    x_left = pdf.l_margin
    x_right = x_left + column_width + gutter

    # Fixed start below title/header
    column_top = 22

    y_left = column_top
    y_right = column_top

    current_col = "left"

    bottom_limit = pdf.h - pdf.b_margin

    HEADER_SPACING = 2
    HEAT_SPACING = 2

    def estimate_heat_height(heat):
        lane_count = sum(
            1 for lane in heat.lanes
            if lane.entry is not None
        )

        # Heat title + lane rows + spacing
        return 5 + lane_count * 5 + HEAT_SPACING

    for event in meet.events:
        # --------------------------------------------------
        # EVENT HEADER
        # --------------------------------------------------

        if current_col == "left":
            header_y = y_left
            if header_y + 8 > bottom_limit:
                current_col = "right"
                header_y = y_right
        else:
            header_y = y_right
            if header_y + 8 > bottom_limit:
                pdf.add_page()
                y_left = column_top
                y_right = column_top
                current_col = "left"
                header_y = y_left
        if current_col == "left":
            y_left = pdf.print_event_header(
                event,
                x_left,
                header_y,
                column_width
            )
            y_left += HEADER_SPACING
        else:
            y_right = pdf.print_event_header(
                event,
                x_right,
                header_y,
                column_width
            )
            y_right += HEADER_SPACING

        # --------------------------------------------------
        # HEATS
        # --------------------------------------------------

        for heat in event.heats:

            estimated_height = estimate_heat_height(heat)

            # ------------------------------------------
            # LEFT -> RIGHT COLUMN
            # ------------------------------------------

            if (
                current_col == "left"
                and y_left + estimated_height > bottom_limit
            ):
                current_col = "right"

            # ------------------------------------------
            # RIGHT COLUMN -> NEW PAGE
            # ------------------------------------------

            if (
                current_col == "right"
                and y_right + estimated_height > bottom_limit
            ):

                pdf.add_page()

                y_left = column_top
                y_right = column_top

                current_col = "left"

                # Repeat event header only on new page
                y_left = pdf.print_event_header(
                    event,
                    x_left,
                    y_left,
                    column_width
                )

                y_left += HEADER_SPACING

            # ------------------------------------------
            # PRINT HEAT
            # ------------------------------------------

            if current_col == "left":

                y_left = pdf.print_heat(
                    heat,
                    len(event.heats),
                    x_left,
                    y_left
                )

                y_left += HEAT_SPACING

            else:

                # First heat after moving from left to right
                # starts at the top of the right column.
                if y_right < column_top:
                    y_right = column_top

                y_right = pdf.print_heat(
                    heat,
                    len(event.heats),
                    x_right,
                    y_right
                )

                y_right += HEAT_SPACING

    return bytes(pdf.output(dest="S"))

# ------------------------------------------
# Create a filtered meet for fav swimmers
# ------------------------------------------
def build_favorite_meet(meet, favorite_names):

    favorite_names = set(favorite_names)

    filtered_events = [
        event
        for event in meet.events
        if any(
            lane.entry
            and lane.entry.swimmer.name in favorite_names
            for heat in event.heats
            for lane in heat.lanes
        )
    ]

    return Meet(
        name=f"{meet.name} - Favorites",
        settings=meet.settings,
        events=filtered_events
    )

def generate_favorite_pdf(meet, favorites_entries):

    if not favorites_entries:
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 10, "No favorite swimmers selected.", ln=1)
        return bytes(pdf.output(dest="S"))

    favorite_names = set(favorites_entries.keys())

    favorite_meet = build_favorite_meet(meet, favorite_names)

    # reuse your FULL pipeline
    return generate_pdf(favorite_meet, favorites_entries)
