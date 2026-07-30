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
    const slot = getToolbarSlot(turnEl);
    const threeDotBtn = slot?.threeDotBtn || getThreeDotButton(turnEl);

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
    console.log(`[AI Studio Quick Delete] Deleting ${turnsToDelete.length} turns starting from index ${targetIndex}`);

    for (let i = turnsToDelete.length - 1; i >= 0; i--) {
      const turn = turnsToDelete[i];
      await deleteTurnElement(turn);
      await new Promise(r => setTimeout(r, 200));
    }
  }

  // Attach quick delete buttons beside 3-dot menu triggers inside the main toolbar row
  function attachQuickDeleteButtons() {
    injectStyles();

    const turns = document.querySelectorAll('[id^="turn-"], ms-turn, div.turn');

    turns.forEach((turnEl) => {
      if (turnEl.querySelector('.ai-quick-actions-wrapper')) return;

      const slot = getToolbarSlot(turnEl);
      if (!slot || !slot.toolbar || !slot.anchor) return;

      const { toolbar, anchor } = slot;

      // Ensure toolbar container displays items in a single horizontal flex row
      if (window.getComputedStyle(toolbar).display !== 'flex') {
        toolbar.style.display = 'inline-flex';
        toolbar.style.alignItems = 'center';
      }
      toolbar.style.flexWrap = 'nowrap';

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

      toolbar.insertBefore(wrapper, anchor);
    });
  }

  setInterval(attachQuickDeleteButtons, 1000);
  attachQuickDeleteButtons();
})();
