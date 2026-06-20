from fpdf import FPDF
import streamlit as st


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, self.title, ln=1, align="C")
        self.ln(2)

    def print_event_header(self, event, x, y, width):
        self.set_xy(x, y)

        self.set_font("Helvetica", "B", 9)

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
        self.set_font("Helvetica", "B", 9)
        self.cell(
            0,
            5,
            f"Heat {heat.heat_number} of {event_total_heats}",
            ln=1
        )

        # 1 John Doe 15 NCAC 1:23.45
        self.set_font("Helvetica", "", 9)
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

def generate_pdf(meet_title, events, favorites):

    pdf = PDF(
        orientation="P",
        unit="mm",
        format="Letter"
    )

    pdf.title = meet_title
    # pdf.set_auto_page_break(False)

    # --------------------------------------------------
    # FAVORITES PAGE
    # --------------------------------------------------
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Favorite Swimmers", ln=1)

    pdf.set_font("Helvetica", "", 10)

    for event in events:
        for heat in event.heats:
            for lane in heat.lanes:

                entry = lane.entry
                if not entry:
                    continue

                if entry.swimmer.name in favorites:
                    pdf.cell(
                        0,
                        5,
                        f"Event {event.event_number} "
                        f"Heat {heat.heat_number} "
                        f"Lane {lane.lane_number} - "
                        f"{entry.swimmer.name} "
                        f"({entry.entry_time})",
                        ln=1
                    )

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

    for event in events:
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
