# 🏊 Swim Meet Heat Sheet Generator (Streamlit)

A user-friendly web app to convert swim meet psych sheets into organized, searchable heat sheets. Perfect for swimmers, parents, and coaches preparing for upcoming meets.

> **Note:** This is an unofficial preparation tool. Always verify the official heat sheet from your meet organizers before the event.

## Features

- 📤 Easy Upload: Upload a psych sheet PDF (text-based PDFs work best).
- 🔍 Smart Parsing: Extracts events, swimmer info, ages, teams, and seed times from common psych-sheet layouts.
- ⭐ Favorites Tracking: Mark favorite swimmers to quickly find their events, heats, and lanes.
- 📄 Exports: Download a formatted PDF and an HTML preview. (JSON export is not implemented in this version.)
- 🎯 Seeding: Applies circle-seeding rules so faster swimmers are placed in later heats and lane assignments follow standard meet ordering.
- ⚙️ Configurable Settings: Choose lanes per heat (8 or 10), how many top heats are treated specially for circle seeding, and the ordering for long-distance events.
- 📊 Clean Layout: Two-column heat sheet layout optimized for readability in the generated PDF.

## What You'll Get

When you process a psych sheet, the app generates:

1. Favorite Swimmers Index — a dedicated page (PDF) showing the selected swimmers and where they swim.
2. Embedded HTML preview — a full preview of the heat sheets in your browser (streamlit component).
3. Heat Sheets (PDF) — full event details organized by heat, including event number, event name, heat number, lane assignments, swimmer names, ages, teams, and seed times.

## Getting Started

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/satoribeans/generate-heat-sheet.git
   cd generate-heat-sheet
   ```

2. Install dependencies:
   ```bash
   pip install streamlit pypdf fpdf2
   ```

3. Fonts: The PDF generator uses DejaVu Sans to support a wide range of characters. Ensure the `fonts/DejaVuSans.ttf` and `fonts/DejaVuSans-Bold.ttf` files are present in the repository's `fonts/` directory. If they are missing, install DejaVu fonts on your system or place those TTF files in `fonts/`.

### Running the App

```bash
streamlit run generate_heat_sheet_streamlit.py
```

The app will open in your default browser at `http://localhost:8501`.

## How to Use

1. Upload your psych sheet PDF using the upload control.
2. Adjust meet settings in the sidebar:
   - Lanes per Heat (8 or 10)
   - Circle Seed Top N Heats (integer)
   - Long Distance Event Heat Order (Fast to Slow / Slow to Fast)
3. Select favorite swimmers from the multi-select dropdown.
4. Click "Generate Heat Sheet". The app will:
   - Parse the psych sheet text
   - Build heats using the seeding logic
   - Produce an HTML preview and a PDF (the PDF includes a favorites page first, then the heat sheets in a two-column layout)
5. Download the generated HTML or PDF using the provided buttons. The HTML is also rendered inline for quick inspection.

## How It Works

The app processes your psych sheet in four steps:

1. Text extraction — reads text from the PDF using `pypdf`.
2. Data parsing — identifies events, swimmers, ages, teams, and seed times from the raw text (`parser.py`).
3. Seeding logic — organizes swimmers into heats following circle-seeding rules implemented in `seeding.py`:
   - Heat 1 contains the slowest swimmers
   - Final heats contain the fastest swimmers
   - Lanes within each heat follow a typical pool lane order ([4,5,3,6,2,7,1,8] for 8 lanes, and a corresponding order for 10 lanes)
   - Long-distance events can be seeded in either fast-to-slow or slow-to-fast order based on the sidebar setting
4. Document generation — creates a formatted PDF using `fpdf2` and an HTML preview using `export_html.py`.

## Supported Psych Sheet Formats

The parser supports several common layouts exported by meet management tools. It handles common formatting variations and some non-ASCII characters via a small replacement map.

## Output Files

### PDF
- Favorites index page (first page)
- Multi-page heat sheets with a two-column layout
- Uses DejaVu Sans fonts to support extended characters

### HTML
- Embeddable preview that shows the meet header, favorites section (if any), and the per-event heat tables

Note: There is no JSON download implemented in the current codebase. The README previously mentioned JSON export — that is not available in this implementation.

## Tips for Success

- Use text-based PDFs (not scanned images) for best results.
- Verify parsed seed times and names before relying on printed heat sheets.
- If PDF generation fails because fonts are missing, ensure the required TTF files are in `fonts/` or install DejaVu on your system.

## Limitations

- Scanned images or heavily formatted PDFs may not parse correctly.
- Specialized or regional psych sheet formats may require parser adjustments.
- The app assumes the psych sheet contains extractable text via `pypdf`.

## Troubleshooting

- "Swimmers not extracting correctly?" — Check that the PDF is text-based and not an image scan.
- "Heat assignments look wrong?" — Verify seed times were parsed correctly and check the 'Lanes per Heat' setting.
- "PDF missing or rendering issues?" — Confirm the `fonts/` directory contains DejaVu Sans TTFs and that `fpdf2` is installed.

## Contributing

Have improvements or found a bug? Open an issue or submit a pull request. Please include a sample psych sheet (with any private data redacted) if you're reporting a parsing bug.

## License

MIT License – feel free to use and modify for your needs.

---

Happy swimming! 🏊‍♀️🏊‍♂️
