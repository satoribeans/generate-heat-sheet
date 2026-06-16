def generate_html_preview(meet_title, heat_sheet, favorites):

    rows = []

    for event in heat_sheet:

        rows.append(f"""
        <div class="event-header">
            Event {event['number']}: {event['name']}
            <span class="heat-count">
                ({len(event['heats'])} heats)
            </span>
        </div>
        """)

        for heat in event["heats"]:

            rows.append(
                f"<div class='heat-header'>Heat {heat['heat_number']}</div>"
            )

            rows.append("""
            <table>
                <tr>
                    <th>Lane</th>
                    <th>Name</th>
                    <th>Age</th>
                    <th>Team</th>
                    <th>Seed</th>
                </tr>
            """)

            for lane in range(1, 9):

                swimmer = heat["lanes"].get(str(lane))

                if not swimmer:
                    continue

                name = swimmer.get("name", "")
                is_favorite = name in favorites

                display_name = (
                    f"★ {name}" if is_favorite else name
                )

                favorite_class = (
                    "favorite" if is_favorite else ""
                )

                rows.append(f"""
                <tr class="{favorite_class}">
                    <td class="center">{lane}</td>
                    <td>{display_name}</td>
                    <td class="center">{swimmer.get('age','')}</td>
                    <td class="center">{swimmer.get('team','')}</td>
                    <td class="right">{swimmer.get('seed_time','')}</td>
                </tr>
                """)

            rows.append("</table>")

    body = "\n".join(rows)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<style>

body {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: 9pt;
    column-count: 2;
    column-gap: 12mm;
}}

h1 {{
    column-span: all;
    text-align: center;
}}

.event-header {{
    font-weight: bold;
    font-size: 10pt;
    margin-top: 10pt;
    border-bottom: 2px solid #000;
    break-after: avoid;
}}

.heat-count {{
    font-size: 8pt;
    color: #666;
}}

.heat-header {{
    font-weight: bold;
    margin-top: 6pt;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 2pt;
}}

th {{
    background: #eee;
    border: 1px solid #aaa;
    padding: 2px;
    font-size: 8pt;
}}

td {{
    border: 1px solid #ccc;
    padding: 2px;
    font-size: 8pt;
}}

.center {{
    text-align: center;
}}

.right {{
    text-align: right;
}}

.favorite {{
    font-weight: bold;
    background: #fffbcc;
}}

</style>
</head>

<body>

<h1>{meet_title}</h1>

{body}

</body>
</html>
"""
