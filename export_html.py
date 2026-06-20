from html import escape

def favorite_swimmers_html(favorites):
    html = []

    for swimmer_name, entries in favorites.items():
        html.append(f"<h3>{swimmer_name}</h3>")
        html.append("""
        <table class="heat-table">
        <tr>
            <th>Event</th>
            <th>Event Name</th>
            <th>Heat</th>
            <th>Lane</th>
            <th>Time</th>
        </tr>
        """)

        for entry in entries:
            html.append(f"""
            <tr>
                <td>{entry.event.event_number}</td>
                <td>{entry.event.name}</td>
                <td>{entry.heat_number}</td>
                <td class="fav">{entry.lane_number}</td>
                <td class="fav-time">{entry.entry_time}</td>
            </tr>
            """)
        html.append("</table>")
    return "".join(html)

def generate_html_preview(meet, favorites):
    favorite_entries = meet.favorite_entries(favorites)

    rows = []

    total_events = len(meet.events)
    total_heats = sum(len(event.heats) for event in meet.events)

    rows.append(f"<h1>{escape(meet.name)}</h1>")
    rows.append(
        f"<p><strong>{total_events}</strong> events, "
        f"<strong>{total_heats}</strong> heats</p>"
    )

    # ==================
    # Favorite Swimmers
    # ==================
    if favorite_entries:
        rows.append("<h2>⭐ Favorite Swimmers</h2>")
        rows.append(
            favorite_swimmers_html(favorite_entries)
        )

    for event in meet.events:

        rows.append(
            f"<h2>Event {event.event_number}: "
            f"{escape(event.name)}</h2>"
        )

        for heat in event.heats:

            rows.append(
                f"<h3>Heat {heat.heat_number}</h3>"
            )

            rows.append("""
            <table class="heat-table">
                <thead>
                    <tr>
                        <th>Lane</th>
                        <th>Name</th>
                        <th>Age</th>
                        <th>Team</th>
                        <th>Seed Time</th>
                    </tr>
                </thead>
                <tbody>
            """)

            sorted_lanes = sorted(
                heat.lanes,
                key=lambda l: l.lane_number
            )

            for lane in sorted_lanes:
                entry = lane.entry
                swimmer = entry.swimmer

                is_favorite = swimmer.name in favorite_entries

                name = escape(swimmer.name)
                team = escape(swimmer.team)

                rows.append(
                    f"""
                    <tr class="{'favorite' if is_favorite else ''}">
                        <td>{lane.lane_number}</td>
                        <td>{'★ ' if is_favorite else ''}{name}</td>
                        <td>{swimmer.age}</td>
                        <td>{team}</td>
                        <td>{entry.entry_time}</td>
                    </tr>
                    """
                )

            rows.append("""
                </tbody>
            </table>
            """)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">

        <style>

            body {{
                font-family: Arial, Helvetica, sans-serif;
                margin: 20px;
            }}

            h1 {{
                margin-bottom: 10px;
            }}

            h2 {{
                margin-top: 30px;
                margin-bottom: 10px;
                border-bottom: 2px solid #ddd;
                padding-bottom: 4px;
            }}

            h3 {{
                margin-top: 15px;
                margin-bottom: 5px;
            }}

            .heat-table {{
                border-collapse: collapse;
                table-layout: fixed;
                width: 700px;
                margin-bottom: 20px;
            }}

            .heat-table th,
            .heat-table td {{
                border: 1px solid #cccccc;
                padding: 4px 6px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}

            .heat-table th {{
                background: #f2f2f2;
            }}

            .favorite {{
                font-weight: bold;
                background: #fff8dc;
            }}

            /* fixed widths */

            .heat-table th:nth-child(1),
            .heat-table td:nth-child(1) {{
                width: 50px;
                text-align: center;
            }}

            .heat-table th:nth-child(2),
            .heat-table td:nth-child(2) {{
                width: 280px;
            }}

            .heat-table th:nth-child(3),
            .heat-table td:nth-child(3) {{
                width: 60px;
                text-align: center;
            }}

            .heat-table th:nth-child(4),
            .heat-table td:nth-child(4) {{
                width: 120px;
            }}

            .heat-table th:nth-child(5),
            .heat-table td:nth-child(5) {{
                width: 100px;
                text-align: center;
            }}

            .heat-table .fav {{
                text-align: center;
            }}

            .heat-table .fav-time {{
                text-align: right;
            }}

        </style>
    </head>

    <body>
        {''.join(rows)}
    </body>
    </html>
    """

    return html
