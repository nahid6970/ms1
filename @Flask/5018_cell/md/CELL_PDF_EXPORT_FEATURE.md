# Cell PDF Export Feature

## Problem Description

Users need to export individual cells or selected cells to PDF format while preserving all visual formatting including:
- Markdown rendering (bold, italic, highlights, colors, headings)
- Right-click formatting (bold, italic, center align, colors, borders)
- Cell styling (background colors, text colors, font sizes)
- Multi-line content with proper line breaks

## Proposed Solution

Add a "📄 Export Cell to PDF" option to the right-click context menu that captures the visual appearance of cells and generates a professional PDF document.

## Implementation Approach

### Option 1: Visual Capture Method (Recommended)

Use `html2canvas` to capture the exact visual appearance of cells and embed as images in PDF:

```javascript
function exportCellToPDF() {
    // 1. Create temporary container with cell content
    // 2. Extract and style content without size constraints
    // 3. Capture visual appearance with html2canvas
    // 4. Embed high-quality image in PDF
    // 5. Add professional headers and metadata
}
```

**Pros:**
- Preserves ALL visual formatting perfectly
- Works with complex markdown and styling
- Professional PDF layout
- Handles multi-line content correctly

**Cons:**
- Larger file sizes (image-based)
- Requires external libraries
- More complex implementation

### Option 2: Text-Based PDF Generation

Convert cell content to styled text in PDF using jsPDF text functions:

```javascript
function exportCellToPDF() {
    // 1. Extract plain text content
    // 2. Apply basic formatting (bold, italic)
    // 3. Generate text-based PDF
}
```

**Pros:**
- Smaller file sizes
- Faster generation
- Simpler implementation

**Cons:**
- Limited formatting support
- No markdown rendering
- Complex styling lost

## Recommended Implementation: Option 1

### Step 1: Add Context Menu Option

**File:** `templates/index.html`
```html
<div class="context-menu-item" onclick="exportCellToPDF()">
    <span>📄</span>
    <span>Export Cell to PDF</span>
</div>
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
    
    // Prompt for filename
    const defaultFilename = `${sheetName}_${columnName}_Row${rowIndex + 1}.pdf`;
    const filename = prompt('Enter filename for PDF:', defaultFilename);
    if (!filename) return;
    
    // Create temporary container for rendering
    const tempContainer = createTempContainer();
    
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
function extractCellContent(tdElement, rowIndex, colIndex) {
    const contentContainer = document.createElement('div');
    
    // Style container
    contentContainer.style.padding = '20px';
    contentContainer.style.border = '1px solid #ddd';
    contentContainer.style.borderRadius = '4px';
    contentContainer.style.backgroundColor = 'white';
    
    // Get content sources
    const inputElement = tdElement.querySelector('input, textarea');
    const previewElement = tdElement.querySelector('.markdown-preview');
    const cellStyle = getCellStyle(rowIndex, colIndex);
    
    // Create content div
    const contentDiv = document.createElement('div');
    contentDiv.style.wordWrap = 'break-word';
    contentDiv.style.whiteSpace = 'pre-wrap';
    
    // Extract content
    if (previewElement && previewElement.innerHTML.trim()) {
        // Use markdown preview (clone and clean)
        const previewClone = previewElement.cloneNode(true);
        cleanPreviewElement(previewClone);
        contentDiv.appendChild(previewClone);
    } else if (inputElement && inputElement.value.trim()) {
        // Use raw text with styling
        contentDiv.innerHTML = inputElement.value.replace(/\n/g, '<br>');
        applyCellStyling(contentDiv, inputElement, cellStyle);
    } else {
        // Empty cell
        contentDiv.innerHTML = '<em style="color: #999;">Empty cell</em>';
    }
    
    // Apply container styling
    applyContainerStyling(contentContainer, cellStyle);
    
    contentContainer.appendChild(contentDiv);
    return contentContainer;
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