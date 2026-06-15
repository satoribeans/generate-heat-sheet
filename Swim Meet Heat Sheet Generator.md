# Swim Meet Heat Sheet Generator

This guide explains how to use the provided Python script to generate a compact, two-column swim meet heat sheet from a psych sheet PDF.

The generated heat sheet will feature:
*   **Font Size 8** for compactness.
*   **Single Line Spacing**.
*   **Two-Column Layout** to save paper.
*   **Heats will not be split** across columns, ensuring readability.
*   **Format**: `Event {Num}: {Event Name}`, `Heat {number}`, and then for each swimmer: `{Lane} {Name} {Age} {Team Entry Time}`.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

*   **Python 3.x**: You can download it from [python.org](https://www.python.org/downloads/).
*   **pip**: Python's package installer, usually comes with Python.

## Installation

1.  **Save the script**: Save the provided Python script (`generate_heat_sheet.py`) to a location on your computer.

2.  **Install dependencies**: Open your terminal or command prompt, navigate to the directory where you saved the script, and run the following command to install the necessary Python libraries:

    ```bash
    pip install pypdf WeasyPrint
    ```

    *Note: WeasyPrint might require some system dependencies, especially on Linux. If you encounter issues, please refer to the [WeasyPrint installation documentation](https://weasyprint.org/docs/install/).*

## Usage

To generate a heat sheet, you need a psych sheet in PDF format.

1.  **Place your psych sheet**: Put your psych sheet PDF file in the same directory as the `generate_heat_sheet.py` script, or note its full path.

2.  **Run the script**: Open your terminal or command prompt, navigate to the directory where you saved the script, and execute the script with the path to your psych sheet PDF as an argument:

    ```bash
    python generate_heat_sheet.py your_psych_sheet.pdf
    ```

    Replace `your_psych_sheet.pdf` with the actual name or full path of your psych sheet PDF file.

    For example:
    ```bash
    python generate_heat_sheet.py 202606_GYC_SycSheet.pdf
    ```

3.  **Output**: The script will generate a PDF file named `your_psych_sheet_heat_sheet.pdf` (e.g., `202606_GYC_SycSheet_heat_sheet.pdf`) in the same directory. This PDF will contain your formatted heat sheet.

## How it Works

The `generate_heat_sheet.py` script performs the following steps:

1.  **PDF Text Extraction**: It uses `pypdf` to extract all text content from the input psych sheet PDF.
2.  **Data Parsing**: It parses the extracted text to identify events, swimmers, their ages, teams, and seed times.
3.  **Heat Seeding**: It applies standard swim meet seeding rules to organize swimmers into heats, ensuring that Heat 1 is the slowest, the last heat is the fastest, and heats are filled efficiently.
4.  **HTML Generation**: It generates an HTML file with embedded CSS styling to achieve the desired compact layout, font size, and two-column structure, ensuring heats are not split.
5.  **PDF Conversion**: Finally, it uses `WeasyPrint` to convert the styled HTML file into a print-ready PDF document.
