(function() {
  // CSS styles for the copy button
  const style = document.createElement('style');
  style.id = 'copy-table-markdown-style';
  style.textContent = `
    .markdown-copy-btn-wrapper {
      position: relative;
    }
    .copy-table-md-btn {
      position: absolute;
      top: 8px;
      right: 8px;
      background: #007acc;
      color: #ffffff;
      border: none;
      border-radius: 4px;
      padding: 6px 10px;
      font-family: 'JetBrains Mono', monospace, sans-serif;
      font-size: 11px;
      font-weight: bold;
      cursor: pointer;
      z-index: 10000;
      opacity: 0;
      transition: opacity 0.2s ease, background-color 0.2s ease;
      box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    table:hover .copy-table-md-btn,
    .copy-table-md-btn:hover {
      opacity: 1;
    }
    .copy-table-md-btn:hover {
      background: #005999;
    }
    .copy-table-md-btn.copied {
      background: #16825d;
    }
  `;
  document.head.appendChild(style);

  // Helper to convert a table element to markdown string
  function tableToMarkdown(table) {
    let markdown = '';
    const rows = Array.from(table.rows);
    if (rows.length === 0) return '';

    // Find max columns
    let maxCols = 0;
    rows.forEach(row => {
      maxCols = Math.max(maxCols, row.cells.length);
    });

    rows.forEach((row, rowIndex) => {
      let rowText = '|';
      for (let i = 0; i < maxCols; i++) {
        const cell = row.cells[i];
        const cellText = cell ? cell.innerText.replace(/\r?\n/g, ' ').trim() : '';
        rowText += ` ${cellText} |`;
      }
      markdown += rowText + '\n';

      // Insert separator after the first row (assuming it's the header)
      if (rowIndex === 0) {
        let separator = '|';
        for (let i = 0; i < maxCols; i++) {
          separator += ' --- |';
        }
        markdown += separator + '\n';
      }
    });

    return markdown;
  }

  // Monitor tables to attach copy button
  function setupTableCopyButtons() {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
      // Avoid duplicate wrappers or buttons
      if (table.querySelector('.copy-table-md-btn')) return;

      // Make sure the table itself can host the absolute positioned button or wrap if necessary
      const tableStyle = window.getComputedStyle(table);
      if (tableStyle.position === 'static') {
        table.style.position = 'relative';
      }

      const btn = document.createElement('button');
      btn.className = 'copy-table-md-btn';
      btn.innerText = 'Copy MD';
      btn.setAttribute('title', 'Copy this table as Markdown');
      
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();

        const markdown = tableToMarkdown(table);
        if (markdown) {
          navigator.clipboard.writeText(markdown).then(() => {
            btn.innerText = 'Copied!';
            btn.classList.add('copied');
            setTimeout(() => {
              btn.innerText = 'Copy MD';
              btn.classList.remove('copied');
            }, 2000);
          }).catch(err => {
            console.error('Failed to copy table: ', err);
            btn.innerText = 'Error';
          });
        }
      });

      table.appendChild(btn);
    });
  }

  // Run on load and poll periodically for dynamic tables
  setupTableCopyButtons();
  setInterval(setupTableCopyButtons, 2000);
  
  console.log('Copy Table as Markdown loaded.');
})();
