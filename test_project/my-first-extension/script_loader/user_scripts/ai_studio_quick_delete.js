(function () {
  'use strict';

  if (!window.location.hostname.includes('aistudio.google.com')) return;
  if (window.__aiStudioQuickDeleteLoaded) return;
  window.__aiStudioQuickDeleteLoaded = true;

  console.log('[AI Studio Quick Delete] Script loaded');

  // Inject CSS styles for the quick delete action buttons
  function injectStyles() {
    if (document.getElementById('ai-studio-quick-delete-css')) return;
    const style = document.createElement('style');
    style.id = 'ai-studio-quick-delete-css';
    style.textContent = `
      .ai-quick-actions-wrapper {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-right: 6px;
        vertical-align: middle;
        z-index: 100;
      }

      .ai-quick-del-btn {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #e3e3e3;
        border-radius: 6px;
        padding: 3px 7px;
        font-size: 12px;
        line-height: 1;
        cursor: pointer;
        transition: all 0.15s ease;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-family: inherit;
        user-select: none;
      }

      .ai-quick-del-btn:hover {
        background: rgba(244, 67, 54, 0.25);
        border-color: #f44336;
        color: #ff8a80;
        transform: translateY(-1px);
      }

      .ai-quick-del-btn:active {
        transform: translateY(0);
      }

      .ai-quick-del-btn.deleting {
        opacity: 0.5;
        pointer-events: none;
      }

      .ai-quick-del-btn-subsequent {
        background: rgba(255, 152, 0, 0.12);
        border: 1px solid rgba(255, 152, 0, 0.35);
        color: #ffe0b2;
      }

      .ai-quick-del-btn-subsequent:hover {
        background: rgba(255, 152, 0, 0.3);
        border-color: #ff9800;
        color: #ffb74d;
      }
    `;
    document.head.appendChild(style);
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

    // Fallback: look for button inside the actions toolbar area
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
          // If a menu is open, the first item is typically Delete in AI Studio
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

    // Delete from bottom to top to preserve DOM order during deletion
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
      singleDelBtn.innerHTML = '🗑️';
      singleDelBtn.title = 'Delete this item';

      singleDelBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();

        singleDelBtn.classList.add('deleting');
        singleDelBtn.innerText = '⏳';

        await deleteTurnElement(turnEl);
      });

      // 2. Turn + All Subsequent Turns Delete button
      const subsequentDelBtn = document.createElement('button');
      subsequentDelBtn.className = 'ai-quick-del-btn ai-quick-del-btn-subsequent';
      subsequentDelBtn.innerHTML = '🗑️👇';
      subsequentDelBtn.title = 'Delete this item AND all subsequent turns below it';

      subsequentDelBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation();

        if (confirm('Delete this item and ALL turns below it?')) {
          subsequentDelBtn.classList.add('deleting');
          subsequentDelBtn.innerText = '⏳';
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
