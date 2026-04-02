# Cell PDF Export Feature

## Problem Description

Users need to export individual cells or selected cells to PDF format while preserving all visual formatting including:
- Markdown rendering (bold, italic, highlights, colors, headings)
- Right-click formatting (bold, italic, center align, colors, borders)
- Cell styling (background colors, text colors, font sizes)
- Multi-line content with proper line breaks

## Proposed Solution

Add a "📄 Export Cell to PDF (Image)" and "🖨️ Print Cell (Selectable PDF)" options to the right-click context menu.

## Implementation Approach

### Option 1: Visual Capture Method (Image-based)

Use `html2canvas` to capture the exact visual appearance of cells and embed as images in PDF. This is best for preserving pixel-perfect layout but the text is not selectable.

### Option 2: Native Print Method (Selectable PDF)

Use a hidden iframe to render the cell content and trigger the browser's native print dialog. This produces high-quality, searchable, and selectable PDFs with vector text and math.

```javascript
function printCellToPDF() {
    // 1. Create hidden iframe
    // 2. Inject cell content and full application CSS
    // 3. Call window.print() on the iframe
    // 4. Remove iframe after printing
}
```

**Pros:**
- Text is fully selectable and searchable
- Perfectly renders vector fonts and KaTeX math
- High-quality output regardless of zoom level
- Smaller file sizes than image-based PDFs

**Cons:**
- Relies on the browser's print dialog (extra user step)
- CSS must be explicitly handled for the print media

## Recommended Implementation

### Step 1: Add Context Menu Options

**File:** `templates/index.html`
```html
<div class="context-menu-item" onclick="exportCellToPDF()">
    <span>📄</span>
    <span>Export Cell to PDF (Image)</span>
</div>
<div class="context-menu-item" onclick="printCellToPDF()">
    <span>🖨️</span>
    <span>Print Cell (Selectable PDF)</span>
</div>
```

... (keep existing steps) ...

### Step 6: Selectable PDF Generation

```javascript
function printCellToPDF() {
    if (!contextMenuCell) return;

    const { rowIndex, colIndex, tdElement } = contextMenuCell;
    const sheet = tableData.sheets[currentSheet];
    const columnName = sheet.columns[colIndex]?.name || getExcelColumnName(colIndex);
    const sheetName = sheet.name || 'Sheet';

    // Prompt for width (optional for printing, but useful to constrain layout)
    const widthInput = prompt('Enter layout width in pixels (or leave for default):', '800');
    if (widthInput === null) return; 
    const customWidth = widthInput.trim() === '' ? '100%' : (parseInt(widthInput) || 800) + 'px';

    // Create a hidden iframe for printing
    const iframe = document.createElement('iframe');
    iframe.style.position = 'fixed';
    iframe.style.width = '0';
    iframe.style.height = '0';
    iframe.style.border = 'none';
    document.body.appendChild(iframe);

    const doc = iframe.contentWindow.document;

    // Extract content
    const contentContainer = extractCellContent(tdElement, rowIndex, colIndex);
    
    // Construct the full HTML with styles
    const html = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>${sheetName}_${columnName}_Row${rowIndex + 1}</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
                
                body {
                    font-family: 'JetBrains Mono', 'Vrinda', Tahoma, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    padding: 40px;
                }
                
                .print-container { width: ${customWidth}; margin: 0 auto; }

                /* Grid Table Styles for PDF */
                .md-grid {
                    display: grid !important;
                    grid-template-columns: repeat(var(--cols), auto) !important;
                    gap: 0 !important;
                    border: 1px solid #eee;
                    width: fit-content;
                }

                .md-cell {
                    padding: 2px 12px !important;
                    border-right: 3px solid #000000 !important;
                    min-width: 80px;
                }

                .md-cell:nth-child(var(--cols)n) { border-right: none !important; }

                .md-header {
                    font-weight: 600 !important;
                    border-bottom: 2px solid #000000 !important;
                }
                
                /* Markdown and KaTeX */
                .markdown-preview { word-wrap: break-word; white-space: pre-wrap; }
                .katex-display { margin: 1em 0; overflow-x: auto; }
            </style>
        </head>
        <body>
            <div class="print-container">
                ${contentContainer.innerHTML}
            </div>
            <script>
                window.onload = function() {
                    window.print();
                    window.onfocus = function() {
                        setTimeout(() => {
                            window.frameElement.parentNode.removeChild(window.frameElement);
                        }, 500);
                    };
                };
            </script>
        </body>
        </html>
    `;

    doc.open();
    doc.write(html);
    doc.close();
}
```

### Step 2: Add Required Libraries

**File:** `templates/index.html`
```html
<!-- jsPDF for PDF generation -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<!-- html2canvas for visual capture -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
```

### Step 3: Core Export Function

**File:** `static/script.js`
```javascript
function exportCellToPDF() {
    if (!contextMenuCell) return;
    
    const { rowIndex, colIndex, inputElement, tdElement } = contextMenuCell;
    
    // Get metadata
    const sheet = tableData.sheets[currentSheet];
    const columnName = sheet.columns[colIndex]?.name || `Column ${colIndex + 1}`;
    const sheetName = sheet.name || 'Sheet';
    
    // Prompt for width first
    const widthInput = prompt('Enter PDF width (px):', '800');
    if (widthInput === null) return; // User cancelled
    const customWidth = parseInt(widthInput) || 800;

    // Prompt for filename
    const defaultFilename = `${sheetName}_${columnName}_Row${rowIndex + 1}.pdf`;
    const filename = prompt('Enter filename for PDF:', defaultFilename);
    if (!filename) return;
    
    // Create temporary container for rendering
    const tempContainer = createTempContainer(customWidth);
    
    // Add header
    addPDFHeader(tempContainer, sheetName, columnName, rowIndex, colIndex);
    
    // Extract and style content
    const contentContainer = extractCellContent(tdElement, rowIndex, colIndex);
    tempContainer.appendChild(contentContainer);
    
    // Add footer
    addPDFFooter(tempContainer);
    
    // Capture and generate PDF
    captureAndGeneratePDF(tempContainer, filename);
}
```

### Step 4: Content Extraction

```javascript
function createTempContainer(width = 800) {
    const container = document.createElement('div');
    container.id = 'pdf-export-container';
    container.style.position = 'fixed';
    container.style.left = '-9999px';
    container.style.top = '0';
    container.style.width = width + 'px';
    // ... rest of styling ...
    return container;
}
```

### Step 5: Visual Capture and PDF Generation

```javascript
function captureAndGeneratePDF(tempContainer, filename) {
    html2canvas(tempContainer, {
        backgroundColor: 'white',
        scale: 1, // Optimize for file size
        useCORS: true,
        allowTaint: true,
        logging: false,
        width: Math.min(tempContainer.scrollWidth, 800),
        height: Math.min(tempContainer.scrollHeight, 1200)
    }).then(canvas => {
        // Create PDF
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        // Calculate dimensions
        const maxWidth = 190;
        const maxHeight = 250;
        let imgWidth = maxWidth;
        let imgHeight = (canvas.height * imgWidth) / canvas.width;
        
        if (imgHeight > maxHeight) {
            imgHeight = maxHeight;
            imgWidth = (canvas.width * imgHeight) / canvas.height;
        }
        
        // Add image with compression
        const imgData = canvas.toDataURL('image/jpeg', 0.8);
        doc.addImage(imgData, 'JPEG', 10, 10, imgWidth, imgHeight);
        
        // Save PDF
        doc.save(filename.endsWith('.pdf') ? filename : filename + '.pdf');
        
        // Cleanup
        document.body.removeChild(tempContainer);
        showToast(`PDF exported: ${filename}`, 'success');
    });
}
```

## Multi-Cell Export Support

```javascript
function exportMultipleCellsToPDF() {
    // Sort selected cells logically
    const sortedCells = [...selectedCells].sort((a, b) => {
        if (a.row !== b.row) return a.row - b.row;
        return a.col - b.col;
    });
    
    // Create container with all cells
    const tempContainer = createTempContainer();
    addPDFHeader(tempContainer, sheetName, `${selectedCells.length} Selected Cells`);
    
    // Add each cell with header
    sortedCells.forEach((cellInfo, index) => {
        const cellSection = createCellSection(cellInfo, index);
        tempContainer.appendChild(cellSection);
    });
    
    addPDFFooter(tempContainer);
    captureAndGeneratePDF(tempContainer, filename);
}
```

## Key Challenges & Solutions

### Challenge 1: Large File Sizes (71MB+ for simple cells)

**Problem:** html2canvas with high scale creates enormous images
**Solutions:**
- Reduce scale to 1 (from 2)
- Limit canvas dimensions (800x1200 max)
- Use JPEG compression (80% quality) instead of PNG
- Add content size warnings for large cells

```javascript
// Optimized capture settings
html2canvas(container, {
    scale: 1, // Not 2
    width: Math.min(container.scrollWidth, 800),
    height: Math.min(container.scrollHeight, 1200)
});

// Compressed output
canvas.toDataURL('image/jpeg', 0.8); // Not PNG
```

### Challenge 2: Content Cropping

**Problem:** Cell constraints limit content display
**Solutions:**
- Extract content without cell size limitations
- Remove positioning constraints from cloned elements
- Set proper overflow and width properties
- Use scrollWidth/scrollHeight for full content

```javascript
// Remove constraints
previewClone.style.position = 'static';
previewClone.style.width = '100%';
previewClone.style.height = 'auto';
previewClone.style.maxHeight = 'none';
previewClone.style.overflow = 'visible';
```

### Challenge 3: Empty PDFs

**Problem:** Content extraction fails silently
**Solutions:**
- Multiple fallback approaches for content
- Debug logging to identify issues
- Fallback debug display in PDF
- Clear error messages

```javascript
// Fallback chain
if (previewElement && previewElement.innerHTML.trim()) {
    // Use markdown preview
} else if (inputElement && inputElement.value.trim()) {
    // Use raw text
} else {
    // Show empty cell message
}
```

### Challenge 4: Formatting Loss

**Problem:** Cell styling not preserved
**Solutions:**
- Extract both input styling and cell styling
- Apply right-click formatting (bold, italic, colors)
- Preserve background colors and borders
- Maintain font sizes and text alignment

```javascript
// Apply all styling sources
if (cellStyle.bold) contentDiv.style.fontWeight = 'bold';
if (cellStyle.bgColor) container.style.backgroundColor = cellStyle.bgColor;
if (inputElement.style.color) contentDiv.style.color = inputElement.style.color;
```

## Performance Optimizations

1. **Size Limits:**
   - Canvas: 800x1200 max
   - Content warning for >10,000 characters
   - JPEG compression at 80% quality

2. **Memory Management:**
   - Remove temporary containers after use
   - Use removeContainer: false in html2canvas
   - Clear canvas references

3. **User Experience:**
   - Progress indicators during generation
   - File size estimates
   - Confirmation for large content

## File Structure

```
templates/index.html          - Context menu option
static/script.js             - Main export functions
static/style.css             - PDF-specific styling (optional)
```

## Dependencies

- **jsPDF 2.5.1+**: PDF generation
- **html2canvas 1.4.1+**: Visual capture
- **Existing functions**: getCellStyle(), getExcelColumnName(), showToast()

## Testing Checklist

- [ ] Single cell export with plain text
- [ ] Single cell export with markdown formatting
- [ ] Single cell export with right-click formatting
- [ ] Multi-cell export (2-10 cells)
- [ ] Empty cell export
- [ ] Large content export (>1000 characters)
- [ ] Cells with background colors and borders
- [ ] File size verification (<5MB for normal cells)
- [ ] Cross-browser compatibility
- [ ] Mobile device testing

## Future Enhancements

1. **Export Options:**
   - Multiple format support (PNG, HTML)
   - Page size selection (A4, Letter, Custom)
   - Quality settings (High, Medium, Low)

2. **Batch Export:**
   - Export entire sheet to PDF
   - Export selected range to PDF
   - Export with table structure

3. **Advanced Features:**
   - Password protection
   - Watermarks
   - Custom headers/footers
   - Print-ready formatting

## Error Handling

```javascript
try {
    // PDF generation code
} catch (error) {
    console.error('PDF Export Error:', error);
    showToast('PDF export failed. Please try again.', 'error');
    // Cleanup temporary elements
}
```

## Browser Compatibility

- **Chrome/Edge**: Full support
- **Firefox**: Full support
- **Safari**: Requires CORS configuration
- **Mobile**: Limited by device memory

## Security Considerations

- Validate filename input
- Sanitize HTML content before capture
- Limit file size generation
- Rate limiting for bulk exports