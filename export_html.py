def generate_html_preview(meet_title, heat_sheet, favorites):

    rows = []

    for event in heat_sheet:
        rows.append(f"<h3>Event {event['number']}: {event['name']}</h3>")

        for heat in event["heats"]:
            rows.append(f"<b>Heat {heat['heat_number']}</b>")

            # Sort lanes by number
            sorted_lanes = sorted(heat["lanes"].items(), key=lambda x: int(x[0]))
            for lane, s in sorted_lanes:

                fav = "★ " if s["name"] in favorites else ""

                rows.append(
                    f"<div>{fav}Lane {lane} "
                    f"{s['name']} {s['seed_time']} {s['age']}</div>"
                )

    return f"""
    <html>
    <body>
    <h1>{meet_title}</h1>
    {''.join(rows)}
    </body>
    </html>
    """
