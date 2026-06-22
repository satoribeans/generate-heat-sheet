# 🏊 Swim Meet Heat Sheet Generator (Streamlit)

Quick start — How to use

1. Run the app:
   ```bash
   streamlit run generate_heat_sheet_streamlit.py
   ```
2. Upload a psych-sheet PDF (text-based PDFs work best).
3. Adjust sidebar settings (lanes per heat, circle-seed top N heats, long-distance order).
4. Select favorite swimmers (optional) and click "Generate Heat Sheet".
5. Download the generated PDF or HTML preview using the buttons shown; the HTML preview is also rendered inline.

Installation

- Python 3.7+ and pip
- Install dependencies:
  ```bash
  pip install streamlit pypdf fpdf2
  ```
- Ensure DejaVu Sans fonts are available at `fonts/DejaVuSans.ttf` and `fonts/DejaVuSans-Bold.ttf` for PDF generation, or install DejaVu on your system.

What the app produces

- PDF (print-ready): Favorites index page followed by two-column heat sheets (events → heats → lanes).
- HTML preview: Downloadable and rendered inline for quick inspection.

Notes & limitations

- There is no JSON export in this implementation — the non-PDF preview is HTML.
- Works best with text-based PDFs. Scanned/image PDFs may not extract correctly.
- Parser handles common psych-sheet layouts but may require tweaks for unusual formats.

Troubleshooting

- Missing/garbled text: confirm your PDF contains selectable text (not scanned images).
- PDF font errors: add DejaVu TTF files to `fonts/` or install the fonts system-wide.
- Heat/seeding issues: check parsed seed times in the preview; adjust "Lanes per Heat" and seeding options.

Contributing

Report issues or submit PRs. If reporting parsing problems, include a (redacted) sample psych sheet that reproduces the issue.

License

MIT
