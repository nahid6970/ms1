(function () {
  'use strict';

  if (!window.location.hostname.includes('aistudio.google.com')) return;
  if (window.__aiStudioQuickDeleteLoaded) return;
  window.__aiStudioQuickDeleteLoaded = true;

  console.log('[AI Studio Quick Tools] Script loaded');

  // Inject CSS styles for action buttons, floating pinned panel, and toasts
  function injectStyles() {
    if (document.getElementById('ai-studio-quick-delete-css')) return;
    const style = document.createElement('style');
    style.id = 'ai-studio-quick-delete-css';
    style.textContent = `
      .ai-quick-actions-wrapper {
        display: inline-flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 2px !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
        height: auto !important;
        width: auto !important;
        flex-shrink: 0 !important;
        white-space: nowrap !important;
      }

      .ai-quick-del-btn {
        background: transparent !important;
        border: none !important;
        color: #c4c7c5 !important;
        border-radius: 50% !important;
        width: 28px !important;
        height: 28px !important;
        min-width: 28px !important;
        min-height: 28px !important;
        padding: 0 !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: background-color 0.15s ease, color 0.15s ease, transform 0.15s ease !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        user-select: none !important;
        outline: none !important;
        flex-shrink: 0 !important;
        box-sizing: border-box !important;
      }

      .ai-quick-del-btn svg {
        width: 16px !important;
        height: 16px !important;
        stroke: currentColor !important;
        pointer-events: none !important;
      }

      /* Hover effects for each action type */
      .ai-quick-del-btn-code:hover {
        background: rgba(76, 175, 80, 0.18) !important;
        color: #81c784 !important;
      }

      .ai-quick-del-btn-pin:hover {
        background: rgba(255, 215, 0, 0.18) !important;
        color: #ffe066 !important;
      }

      .ai-quick-del-btn-pin.pinned {
        color: #ffd700 !important;
      }

      .ai-quick-del-btn:hover {
        background: rgba(244, 67, 54, 0.18) !important;
        color: #f2b8b5 !important;
      }

      .ai-quick-del-btn-subsequent:hover {
        background: rgba(255, 183, 77, 0.22) !important;
        color: #ffcc80 !important;
      }

      .ai-quick-del-btn:active {
        transform: scale(0.92) !important;
      }

      .ai-quick-del-btn.deleting {
        opacity: 0.6 !important;
        pointer-events: none !important;
      }

      /* Pinned turn highlight */
      .ai-turn-pinned {
        border-left: 3px solid #ffd700 !important;
        box-shadow: inset 3px 0 10px -2px rgba(255, 215, 0, 0.25) !important;
      }

      /* Floating Pinned Turns Panel */
      #ai-studio-pinned-panel {
        position: fixed;
        top: 70px;
        right: 20px;
        z-index: 10000;
        width: 250px;
        max-height: 380px;
        background: rgba(22, 22, 26, 0.94);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 215, 0, 0.3);
        border-radius: 10px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
        font-family: 'JetBrains Mono', -apple-system, monospace;
        font-size: 11px;
        color: #e3e3e3;
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }

      .ai-pinned-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        background: rgba(255, 215, 0, 0.08);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        font-weight: bold;
        color: #ffd700;
      }

      .ai-pinned-list {
        overflow-y: auto;
        max-height: 320px;
        padding: 6px;
        display: flex;
        flex-direction: column;
        gap: 4px;
      }

      .ai-pinned-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 8px;
        background: rgba(255, 255, 255, 0.04);
        border-radius: 6px;
        cursor: pointer;
        transition: background 0.15s ease;
      }

      .ai-pinned-item:hover {
        background: rgba(255, 215, 0, 0.15);
      }

      .ai-pinned-text {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 180px;
        color: #d4d4d4;
      }

      .ai-pinned-unpin {
        background: transparent;
        border: none;
        color: #888;
        cursor: pointer;
        padding: 2px 4px;
        font-size: 12px;
        line-height: 1;
      }

      .ai-pinned-unpin:hover {
        color: #ff5252;
      }

      /* Notification Toast */
      #ai-studio-tools-toast {
        position: fixed;
        bottom: 24px;
        left: 50%;
        transform: translateX(-50%) translateY(20px);
        background: #1e1e24;
        color: #4ec9b0;
        border: 1px solid #3c3c42;
        padding: 8px 16px;
        border-radius: 20px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        z-index: 100000;
        opacity: 0;
        pointer-events: none;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(0,0,0,0.5);
      }

      #ai-studio-tools-toast.ai-toast-visible {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
      }

      #ai-studio-tools-toast.warn {
        color: #ffb74d;
      }

      @keyframes ai-del-spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }

      .ai-del-spinner {
        animation: ai-del-spin 0.8s linear infinite !important;
      }
    `;
    document.head.appendChild(style);
  }

  // SVG Icons
  const CODE_SVG = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="16 18 22 12 16 6"></polyline>
      <polyline points="8 6 2 12 8 18"></polyline>
    </svg>
  `;

  const CHECKMARK_SVG = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4caf50" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="20 6 9 17 4 12"></polyline>
    </svg>
  `;

  const PIN_SVG = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 17v5"></path>
      <path d="M9 2v3l-2 5v3h10v-3l-2-5V2H9z"></path>
    </svg>
  `;

  const TRASH_SVG = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M3 6h18"></path>
      <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
      <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
      <line x1="10" y1="11" x2="10" y2="17"></line>
      <line x1="14" y1="11" x2="14" y2="17"></line>
    </svg>
  `;

  const TRASH_SUBSEQUENT_SVG = `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M3 6h18"></path>
      <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
      <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
      <path d="M12 10v7"></path>
      <path d="M9.5 14.5L12 17l2.5-2.5"></path>
    </svg>
  `;

  const SPINNER_SVG = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="ai-del-spinner">
      <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
      <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"></path>
    </svg>
  `;

  // Toast notification helper
  function showToast(msg, type = 'info') {
    let toast = document.getElementById('ai-studio-tools-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'ai-studio-tools-toast';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.className = `ai-toast-visible ${type}`;

    clearTimeout(window.__aiToastTimer);
    window.__aiToastTimer = setTimeout(() => {
      toast.className = '';
    }, 2200);
  }

  // Copy only code blocks from a turn
  function copyCodeFromTurn(turnEl, copyBtn) {
    const preElements = Array.from(turnEl.querySelectorAll('pre, .code-block, ms-code-block'));
    let codeTexts = [];

    if (preElements.length > 0) {
      codeTexts = preElements.map(el => {
        const codeEl = el.querySelector('code') || el;
        return codeEl.innerText.trim();
      }).filter(text => text.length > 0);
    } else {
      const codeElements = Array.from(turnEl.querySelectorAll('code'));
      codeTexts = codeElements.map(el => el.innerText.trim()).filter(text => text.length > 0);
    }

    if (codeTexts.length === 0) {
      showToast('No code blocks found in this turn', 'warn');
      return;
    }

    const fullCode = codeTexts.join('\n\n// --- Next Code Block ---\n\n');
    navigator.clipboard.writeText(fullCode).then(() => {
      copyBtn.innerHTML = CHECKMARK_SVG;
      showToast(`Copied ${codeTexts.length} code block${codeTexts.length > 1 ? 's' : ''}!`);
      setTimeout(() => {
        copyBtn.innerHTML = CODE_SVG;
      }, 1800);
    }).catch(err => {
      console.error('Copy failed:', err);
      showToast('Copy failed', 'warn');
    });
  }

  // Floating Pinned Turns Panel
  function updatePinnedPanel() {
    let panel = document.getElementById('ai-studio-pinned-panel');
    const pinnedTurns = Array.from(document.querySelectorAll('.ai-turn-pinned'));

    if (pinnedTurns.length === 0) {
      if (panel) panel.remove();
      return;
    }

    if (!panel) {
      panel = document.createElement('div');
      panel.id = 'ai-studio-pinned-panel';
      document.body.appendChild(panel);
    }

    let itemsHtml = '';
    pinnedTurns.forEach((turn, idx) => {
      const textEl = turn.querySelector('p, span, div') || turn;
      const rawText = (textEl.innerText || '').trim().replace(/\s+/g, ' ');
      const snippet = rawText ? rawText.substring(0, 28) + (rawText.length > 28 ? '...' : '') : `Turn #${idx + 1}`;

      itemsHtml += `
        <div class="ai-pinned-item" data-turn-idx="${idx}">
          <span class="ai-pinned-text" title="${rawText}">${snippet}</span>
          <button class="ai-pinned-unpin" data-turn-idx="${idx}" title="Unpin">✕</button>
        </div>
      `;
    });

    panel.innerHTML = `
      <div class="ai-pinned-header">
        <span>📌 Pinned Turns (${pinnedTurns.length})</span>
      </div>
      <div class="ai-pinned-list">
        ${itemsHtml}
      </div>
    `;

    // Click to scroll to pinned turn
    panel.querySelectorAll('.ai-pinned-item').forEach(item => {
      item.addEventListener('click', (e) => {
        if (e.target.classList.contains('ai-pinned-unpin')) return;
        const idx = parseInt(item.dataset.turnIdx, 10);
        const targetTurn = pinnedTurns[idx];
        if (targetTurn) {
          targetTurn.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
    });

    // Unpin click
    panel.querySelectorAll('.ai-pinned-unpin').forEach(unpinBtn => {
      unpinBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = parseInt(unpinBtn.dataset.turnIdx, 10);
        const targetTurn = pinnedTurns[idx];
        if (targetTurn) {
          targetTurn.classList.remove('ai-turn-pinned');
          const pinBtn = targetTurn.querySelector('.ai-quick-del-btn-pin');
          if (pinBtn) pinBtn.classList.remove('pinned');
          updatePinnedPanel();
        }
      });
    });
  }

  // Toggle Pin / Bookmark on turn
  function togglePinTurn(turnEl, pinBtn) {
    const isPinned = turnEl.classList.toggle('ai-turn-pinned');
    pinBtn.classList.toggle('pinned', isPinned);
    showToast(isPinned ? 'Turn pinned to side panel 📌' : 'Turn unpinned');
    updatePinnedPanel();
  }

  // Locate the 3-dot menu trigger button inside or near a turn item
  function getThreeDotButton(turnEl) {
    if (!turnEl) return null;

    const buttons = Array.from(turnEl.querySelectorAll('button, [role="button"], div[aria-haspopup]'));
    
    for (const btn of buttons) {
      if (btn.classList.contains('ai-quick-del-btn')) continue;

      const hasMenuAttr = btn.getAttribute('aria-haspopup') === 'true' || 
                          btn.getAttribute('aria-haspopup') === 'menu' ||
                          btn.hasAttribute('matmenutriggerfor') ||
                          btn.getAttribute('mat-menu-trigger-for') !== null ||
                          btn.className.includes('mat-mdc-menu-trigger');

      const text = (btn.textContent || '').trim().toLowerCase();
      const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
      const hasMoreIcon = text.includes('more_vert') || 
                          text.includes('more_horiz') || 
                          ariaLabel.includes('more') || 
                          ariaLabel.includes('option') ||
                          ariaLabel.includes('action');

      if (hasMenuAttr || hasMoreIcon) {
        return btn;
      }
    }

    const fallbackBtn = turnEl.querySelector('button');
    return fallbackBtn || null;
  }

  // Find the parent toolbar pill that holds all action buttons
  function getToolbarSlot(turnEl) {
    const threeDotBtn = getThreeDotButton(turnEl);
    if (!threeDotBtn) return null;

    let curr = threeDotBtn;
    while (curr && curr !== turnEl && curr !== document.body) {
      const parent = curr.parentElement;
      if (!parent) break;

      const buttons = parent.querySelectorAll('button, [role="button"]');
      if (buttons.length > 1) {
        return {
          toolbar: parent,
          anchor: curr,
          threeDotBtn: threeDotBtn
        };
      }
      curr = parent;
    }

    return {
      toolbar: threeDotBtn.parentNode,
      anchor: threeDotBtn,
      threeDotBtn: threeDotBtn
    };
  }

  // Poll for open Angular Material menu and find "Delete" item
  function waitForMenuItem(maxWaitMs = 500) {
    return new Promise((resolve) => {
      const startTime = Date.now();

      const check = () => {
        const overlays = document.querySelectorAll('.cdk-overlay-container, mat-menu, [role="menu"], .mat-mdc-menu-panel, [class*="mat-menu-panel"]');
        for (const overlay of overlays) {
          const menuButtons = Array.from(overlay.querySelectorAll('button[role="menuitem"], button.mat-mdc-menu-item, button'));
          for (const btn of menuButtons) {
            const txt = btn.textContent.toLowerCase();
            const iconTxt = btn.querySelector('mat-icon')?.textContent?.toLowerCase() || '';
            if (txt.includes('delete') || iconTxt.includes('delete') || txt.includes('remove')) {
              return resolve(btn);
            }
          }
          if (menuButtons.length > 0) {
            return resolve(menuButtons[0]);
          }
        }

        if (Date.now() - startTime < maxWaitMs) {
          setTimeout(check, 30);
        } else {
          resolve(null);
        }
      };

      check();
    });
  }

  // Auto-confirm if a confirmation dialog appears after clicking Delete
  async function handleConfirmationDialog() {
    await new Promise(r => setTimeout(r, 120));
    const confirmBtn = document.querySelector('mat-dialog-container button.mat-primary, mat-dialog-container button[color="warn"], mat-dialog-actions button:last-child');
    if (confirmBtn && confirmBtn.textContent.toLowerCase().includes('delete')) {
      confirmBtn.click();
    }
  }

  // Triggers 3-dot menu and clicks Delete for a single turn
  async function deleteTurnElement(turnEl) {
    const slot = getToolbarSlot(turnEl);
    const threeDotBtn = slot?.threeDotBtn || getThreeDotButton(turnEl);

    if (!threeDotBtn) {
      console.warn('[AI Studio Quick Tools] Could not locate 3-dot menu trigger for turn');
      return false;
    }

    threeDotBtn.click();
    const deleteMenuItem = await waitForMenuItem();
    
    if (deleteMenuItem) {
      deleteMenuItem.click();
      await handleConfirmationDialog();
      updatePinnedPanel();
      return true;
    } else {
      console.warn('[AI Studio Quick Tools] Delete menu item not found');
      document.body.click();
      return false;
    }
  }

  // Sequentially deletes target turn and all turns following it (from bottom to top)
  async function deleteTurnAndSubsequent(targetTurnEl) {
    const allTurns = Array.from(document.querySelectorAll('[id^="turn-"], ms-turn, div.turn'));
    const targetIndex = allTurns.indexOf(targetTurnEl);

    if (targetIndex === -1) {
      return await deleteTurnElement(targetTurnEl);
    }

    const turnsToDelete = allTurns.slice(targetIndex);
    console.log(`[AI Studio Quick Tools] Deleting ${turnsToDelete.length} turns starting from index ${targetIndex}`);

    for (let i = turnsToDelete.length - 1; i >= 0; i--) {
      const turn = turnsToDelete[i];
      await deleteTurnElement(turn);
      await new Promise(r => setTimeout(r, 200));
    }
  }

  // Attach quick action buttons inside the main toolbar row
  function attachQuickDeleteButtons() {
    injectStyles();

    const turns = document.querySelectorAll('[id^="turn-"], ms-turn, div.turn');

    turns.forEach((turnEl) => {
      if (turnEl.querySelector('.ai-quick-actions-wrapper')) return;

      const slot = getToolbarSlot(turnEl);
      if (!slot || !slot.toolbar || !slot.anchor) return;

      const { toolbar, anchor } = slot;

      if (window.getComputedStyle(toolbar).display !== 'flex') {
        toolbar.style.display = 'inline-flex';
        toolbar.style.alignItems = 'center';
      }
      toolbar.style.flexWrap = 'nowrap';

      const wrapper = document.createElement('div');
      wrapper.className = 'ai-quick-actions-wrapper';

      // 1. Copy Code Blocks button
      const copyCodeBtn = document.createElement('button');
      copyCodeBtn.className = 'ai-quick-del-btn ai-quick-del-btn-code';
      copyCodeBtn.innerHTML = CODE_SVG;
      copyCodeBtn.title = 'Copy only code blocks from this response';

      copyCodeBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        copyCodeFromTurn(turnEl, copyCodeBtn);
      });

      // 2. Pin / Bookmark Turn button
      const pinBtn = document.createElement('button');
      pinBtn.className = 'ai-quick-del-btn ai-quick-del-btn-pin';
      pinBtn.innerHTML = PIN_SVG;
      pinBtn.title = 'Bookmark / Pin this turn';

      pinBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        togglePinTurn(turnEl, pinBtn);
      });

      // 3. Single Turn Delete button
      const singleDelBtn = document.createElement('button');
      singleDelBtn.className = 'ai-quick-del-btn';
      singleDelBtn.innerHTML = TRASH_SVG;
      singleDelBtn.title = 'Delete this item';

      singleDelBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();

        singleDelBtn.classList.add('deleting');
        singleDelBtn.innerHTML = SPINNER_SVG;

        await deleteTurnElement(turnEl);
      });

      // 4. Turn + All Subsequent Turns Delete button
      const subsequentDelBtn = document.createElement('button');
      subsequentDelBtn.className = 'ai-quick-del-btn ai-quick-del-btn-subsequent';
      subsequentDelBtn.innerHTML = TRASH_SUBSEQUENT_SVG;
      subsequentDelBtn.title = 'Delete this item AND all subsequent turns below it';

      subsequentDelBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();

        if (confirm('Delete this item and ALL turns below it?')) {
          subsequentDelBtn.classList.add('deleting');
          subsequentDelBtn.innerHTML = SPINNER_SVG;
          await deleteTurnAndSubsequent(turnEl);
        }
      });

      wrapper.appendChild(copyCodeBtn);
      wrapper.appendChild(pinBtn);
      wrapper.appendChild(singleDelBtn);
      wrapper.appendChild(subsequentDelBtn);

      toolbar.insertBefore(wrapper, anchor);
    });
  }

  setInterval(attachQuickDeleteButtons, 1000);
  attachQuickDeleteButtons();
})();
