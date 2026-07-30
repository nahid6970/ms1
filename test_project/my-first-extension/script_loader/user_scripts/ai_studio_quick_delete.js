(function () {
  'use strict';

  if (!window.location.hostname.includes('aistudio.google.com')) return;
  if (window.__aiStudioQuickDeleteLoaded) return;
  window.__aiStudioQuickDeleteLoaded = true;

  console.log('[AI Studio Quick Delete] Script loaded');

  // Inject CSS styles for native-feeling Google AI Studio action icons
  function injectStyles() {
    if (document.getElementById('ai-studio-quick-delete-css')) return;
    const style = document.createElement('style');
    style.id = 'ai-studio-quick-delete-css';
    style.textContent = `
      .ai-quick-actions-wrapper {
        display: inline-flex;
        align-items: center;
        gap: 2px;
        vertical-align: middle;
        flex-shrink: 0;
      }

      .ai-quick-del-btn {
        background: transparent;
        border: none;
        color: #c4c7c5;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        padding: 0;
        cursor: pointer;
        transition: background-color 0.15s ease, color 0.15s ease, transform 0.15s ease;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        user-select: none;
        outline: none;
        flex-shrink: 0;
      }

      .ai-quick-del-btn svg {
        width: 16px;
        height: 16px;
        stroke: currentColor;
        pointer-events: none;
      }

      .ai-quick-del-btn:hover {
        background: rgba(244, 67, 54, 0.18);
        color: #f2b8b5;
      }

      .ai-quick-del-btn-subsequent:hover {
        background: rgba(255, 183, 77, 0.22);
        color: #ffcc80;
      }

      .ai-quick-del-btn:active {
        transform: scale(0.92);
      }

      .ai-quick-del-btn.deleting {
        opacity: 0.6;
        pointer-events: none;
      }

      @keyframes ai-del-spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }

      .ai-del-spinner {
        animation: ai-del-spin 0.8s linear infinite;
      }
    `;
    document.head.appendChild(style);
  }

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

  // Poll for the open Angular Material menu and find the "Delete" item
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
    const threeDotBtn = getThreeDotButton(turnEl);
    if (!threeDotBtn) {
      console.warn('[AI Studio Quick Delete] Could not locate 3-dot menu trigger for turn');
      return false;
    }

    threeDotBtn.click();
    const deleteMenuItem = await waitForMenuItem();
    
    if (deleteMenuItem) {
      deleteMenuItem.click();
      await handleConfirmationDialog();
      return true;
    } else {
      console.warn('[AI Studio Quick Delete] Delete menu item not found');
      document.body.click(); // Close opened menu
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
    console.log(`[AI Studio Quick Delete] Deleting ${turnsToDelete.length} turns starting from index ${targetIndex}`);

    for (let i = turnsToDelete.length - 1; i >= 0; i--) {
      const turn = turnsToDelete[i];
      await deleteTurnElement(turn);
      await new Promise(r => setTimeout(r, 200));
    }
  }

  // Attach quick delete buttons beside 3-dot menu triggers
  function attachQuickDeleteButtons() {
    injectStyles();

    const turns = document.querySelectorAll('[id^="turn-"], ms-turn, div.turn');

    turns.forEach((turnEl) => {
      if (turnEl.querySelector('.ai-quick-actions-wrapper')) return;

      const threeDotBtn = getThreeDotButton(turnEl);
      if (!threeDotBtn) return;

      const wrapper = document.createElement('div');
      wrapper.className = 'ai-quick-actions-wrapper';

      // 1. Single Turn Delete button
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

      // 2. Turn + All Subsequent Turns Delete button
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

      wrapper.appendChild(singleDelBtn);
      wrapper.appendChild(subsequentDelBtn);

      if (threeDotBtn.parentNode) {
        threeDotBtn.parentNode.insertBefore(wrapper, threeDotBtn);
      }
    });
  }

  setInterval(attachQuickDeleteButtons, 1000);
  attachQuickDeleteButtons();
})();
