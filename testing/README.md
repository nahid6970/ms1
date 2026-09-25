# Qt HTML Window Demo

A simple Qt application that demonstrates how to display HTML content in a window without browser bars, similar to YASB Reborn.

## Features

- Main window with a button
- Clicking the button opens an HTML window without browser chrome
- Frameless window with custom HTML content
- Uses Qt WebEngine for HTML rendering

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

Click the "Show HTML Window" button to open the HTML display window.

## How it works

- Uses `QWebEngineView` to render HTML content
- `Qt.FramelessWindowHint` removes window decorations
- Custom HTML with CSS styling for a modern look
- No browser bars or navigation elements