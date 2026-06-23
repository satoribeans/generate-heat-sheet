from html import escape


def favorite_swimmers_html(favorites):
    html = []

    for swimmer_name, entries in favorites.items():
        html.append(f"<h3>{swimmer_name}</h3>")
        html.append("""
        <table class="fav-swimmer-table">
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
                <td>{escape(entry.event.name)}</td>
                <td>{entry.heat_number}</td>
                <td>{entry.lane_number}</td>
                <td>{entry.entry_time}</td>
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
    # Expand/Collapse Button
    # ==================
    rows.append("""
    <button onclick="toggleEvents()" style="
        margin: 10px 0;
        padding: 6px 10px;
        cursor: pointer;
    ">
        Expand / Collapse All Events
    </button>
    """)

    # ==================
    # Favorite Swimmers
    # ==================
    if favorite_entries:
        rows.append("<h2>⭐ Favorite Swimmers</h2>")
        rows.append(favorite_swimmers_html(favorite_entries))

    # ==================
    # Events
    # ==================
    for event in meet.events:

        # detect if event contains favorite swimmer
        event_has_favorite = False

        for heat in event.heats:
            for lane in heat.lanes:
                entry = lane.entry
                if entry and entry.swimmer.name in favorite_entries:
                    event_has_favorite = True
                    break

        rows.append(f"""
        <details class="event-block" {'open' if event_has_favorite else ''}>
        """.strip())

        rows.append(
            f"<summary><strong>"
            f"Event {event.event_number}: {escape(event.name)}"
            f"</strong></summary>"
        )

        for heat in event.heats:

            rows.append(f"""
            <h3>Heat {heat.heat_number}</h3>

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
                if not entry:
                    continue

                swimmer = entry.swimmer
                is_favorite = swimmer.name in favorite_entries

                name = escape(swimmer.name)
                team = escape(swimmer.team)

                rows.append(f"""
                <tr class="{'favorite' if is_favorite else ''}">
                    <td>{lane.lane_number}</td>
                    <td>{'★ ' if is_favorite else ''}{name}</td>
                    <td>{swimmer.age}</td>
                    <td>{team}</td>
                    <td>{entry.entry_time}</td>
                </tr>
                """)

            rows.append("""
                </tbody>
            </table>
            """)

        rows.append("</details>")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>

            body {{
                font-family: Arial, Helvetica, sans-serif;
                margin: 20px;
            }}

            .heat-table,
            .fav-swimmer-table {{
                border-collapse: collapse;
                table-layout: fixed;
                width: 700px;
            }}

            .heat-table th,
            .heat-table td,
            .fav-swimmer-table th,
            .fav-swimmer-table td {{
                border: 1px solid #ccc;
                padding: 4px 6px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}

            .heat-table th,
            .fav-swimmer-table th {{
                background: #f2f2f2;
            }}

            .favorite {{
                font-weight: bold;
                background: #fff8dc;
            }}

            details.event-block {{
                margin-bottom: 12px;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 6px 10px;
                background: #fafafa;
            }}

            summary {{
                cursor: pointer;
                font-size: 1.1rem;
                padding: 4px 0;
            }}

            summary:hover {{
                color: #2a5bd7;
            }}

            h3 {{
                margin-top: 15px;
                margin-bottom: 5px;
            }}

        </style>

        <script>
            function toggleEvents() {{
                const events = document.querySelectorAll("details.event-block");
                const anyClosed = Array.from(events).some(e => !e.open);

                events.forEach(e => {{
                    e.open = anyClosed;
                }});
            }}
        </script>

    </head>

    <body>
        {''.join(rows)}
    </body>
    </html>
    """

    return html
