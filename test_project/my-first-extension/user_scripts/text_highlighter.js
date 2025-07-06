document.addEventListener('mouseup', () => {
  const selection = window.getSelection();
  if (selection.toString().length > 0) {
    const range = selection.getRangeAt(0);
    const span = document.createElement('span');
    span.style.backgroundColor = 'yellow';
    span.style.fontWeight = 'bold';
    span.style.color = 'black';
    range.surroundContents(span);
    selection.removeAllRanges(); // Clear the selection after highlighting
  }
});
console.log('Text highlighter script injected.');