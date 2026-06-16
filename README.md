# 🏊 Swim Meet Heat Sheet Generator (Streamlit)

A user-friendly web app to convert swim meet psych sheets into organized, searchable heat sheets. Perfect for swimmers, parents, and coaches preparing for upcoming meets.

> **Note:** This is an unofficial preparation tool. Always verify the official heat sheet from your meet organizers before the event.

## Features

- **📤 Easy Upload**: Simply upload a psych sheet PDF
- **🔍 Smart Parsing**: Automatically extracts events, swimmer info, and seed times
- **⭐ Favorites Tracking**: Mark favorite swimmers to quickly find their heats, events, and lanes
- **📄 Multiple Exports**: Download as JSON for data analysis or PDF for printing
- **🎯 Optimal Seeding**: Applies standard swim meet seeding rules (fastest swimmers in later heats)
- **📊 Clean Layout**: Two-column heat sheet format optimized for readability

## What You'll Get

When you process a psych sheet, the app generates:

1. **Favorite Swimmers Index** – A dedicated page showing where each marked swimmer competes
2. **Meet Summary** – Total event count and your favorite swimmers list
3. **Heat Sheets** – Full event details organized by heat, including:
   - Event number and name
   - Heat number
   - Lane assignments
   - Swimmer names, ages, teams, and seed times

## Getting Started

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/satoribeans/generate-heat-sheet.git
   cd generate-heat-sheet
   ```

2. **Install dependencies**:
   ```bash
   pip install streamlit pypdf fpdf2
   ```

### Running the App

```bash
streamlit run generate_heat_sheet_streamlit.py
```

The app will open in your default browser at `http://localhost:8501`.

## How to Use

1. **Upload your psych sheet**: Click "Upload Psych Sheet PDF" and select your PDF file
2. **Select favorite swimmers**: Use the multiselect dropdown to mark swimmers you want to track
3. **Download your heat sheet**: 
   - Download as **PDF** for printing or viewing
   - Download as **JSON** for detailed data analysis

## How It Works

The app processes your psych sheet in four steps:

1. **Text Extraction** – Reads all text from the PDF using `pypdf`
2. **Data Parsing** – Identifies events, swimmers, ages, teams, and seed times from the raw text
3. **Seeding Logic** – Organizes swimmers into heats following standard swim meet rules:
   - Heat 1 contains the slowest swimmers
   - Final heats contain the fastest swimmers
   - Lanes within each heat are ordered by seed time
4. **Document Generation** – Creates a formatted PDF using `fpdf2`

## Supported Psych Sheet Formats

The parser recognizes multiple psych sheet layouts and handles common formatting variations:
- Different delimiter patterns between swimmer data fields
- Non-ASCII characters (smart character replacement)
- Various age group and team designations

## Output Files

### PDF Output
- Meet title header
- Favorites index page
- Meet summary page
- Multi-page heat sheets with two-column layout
- Optimized for printing

### JSON Output
Structured data including:
- Event numbers and names
- Heat assignments
- Swimmer information (name, age, team, seed time)
- Lane assignments

## Tips for Success

- **Quality PDFs work best**: Clear, text-based PDFs extract more accurately than scanned images
- **Double-check information**: Always compare against the official meet heat sheet
- **Use for preparation**: Great for pre-meet planning, travel logistics, and warm-up scheduling
- **Multiple copies**: Generate and print multiple copies for family members

## Limitations

- Works best with standard psych sheet formats
- Scanned images or heavily formatted PDFs may require manual cleanup
- Specialized or regional psych sheet formats may need custom parsing

## Troubleshooting

**"Swimmers not extracting correctly?"**
- Check that your PDF is text-based (not scanned/image)
- Try a different psych sheet format if available

**"Heat assignments look wrong?"**
- Verify the seed times were parsed correctly in the JSON output
- Confirm your pool's lane count (default is 8)

**"PDF not downloading?"**
- Check your browser's download settings
- Try a different browser

## Contributing

Have improvements or found a bug? Feel free to open an issue or submit a pull request!

## Disclaimer

This tool is designed to help swimmers and families prepare for upcoming meets. It is **not** an official document. Always verify all information with the official meet heat sheet provided by meet organizers.

## License

MIT License – feel free to use and modify for your needs.

---

Happy swimming! 🏊‍♀️🏊‍♂️
