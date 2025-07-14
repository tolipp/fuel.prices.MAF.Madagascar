# ⛽ Fuel Prices – Madagascar (MAF)

This project extracts and processes monthly fuel price data for Madagascar from PDF documents published by [MAF](https://mafmada.com). It converts these documents into structured JSON files for easy use in a static HTML page.

---

## 📌 Overview

1. **Fuel prices are uploaded monthly** as PDF files into the `fuel_price/` directory.
2. Run the Python script to extract and convert the PDF contents.
3. A new `.json` file is generated with the structured data.
4. Copy and paste the generated JSON content into the HTML file (ctr+f 'UPDATE') to update the visualization.

---

## 📁 Directory Structure

fuel.prices.MAF.Madagascar/
├── fuel_price/ # Directory containing monthly PDFs
├── fuel_parser.py # Main script to process PDF and create JSON
├── output.json # Auto-generated JSON file with fuel price data
├── index.html # HTML file displaying data (manually updated)
├── requirements.txt # Python dependencies
└── README.md # This file

yaml
Copy code

---

## ⚙️ Setup

1. **Clone the repo**:

```bash
git clone https://github.com/tolipp/fuel.prices.MAF.Madagascar.git
cd fuel.prices.MAF.Madagascar
Install dependencies:

bash
pip install -r requirements.txt

Dependencies include:

PyMuPDF (fitz)

json

os

🚀 Usage
Add the latest PDF to the fuel_price/ folder.

Run the parser:

bash
Copy code
python fuel_parser.py
Check the generated output in output.json.

Open index.html, and copy-paste the contents of output.json into the designated section inside the HTML file.

📝 Notes
The script assumes that the PDF layout and structure remain consistent from month to month.

If the format changes, the parsing logic may need to be updated.

The HTML file is not automatically updated — this is a manual step for flexibility.

✅ Contributing
Pull requests, issue reports, and suggestions are welcome. Please make sure your code is clean and well-documented.

🪪 License
MIT License © tolipp

📬 Contact
For questions or suggestions, please open an issue or reach out via GitHub
