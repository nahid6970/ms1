# Excel-like Flask Data Table

A Flask web application with an Excel-like interface for managing data with customizable fields.

## Features

- Add/delete columns with custom names, types, widths, and colors
- Add/delete rows dynamically
- Input data like Excel cells
- Different field types: text, number, date, email
- Customize column appearance (width, background color)
- Auto-save data to JSON file
- Responsive table interface

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open browser to: http://localhost:5018

## Usage

- Click "Add Column" to create new columns with custom settings
- Click "Add Row" to add new data rows
- Type directly in cells to input data
- Click "Save Data" to persist changes
- Click "Refresh" to reload data from server
- Use "×" or "Delete" buttons to remove columns/rows

Data is automatically saved to `data.json` file.
