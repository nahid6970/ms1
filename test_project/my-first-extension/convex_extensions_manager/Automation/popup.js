// Convex — fetched directly from popup (avoids MV3 service worker message drop)
const CONVEX_URL = "https://joyous-stingray-672.convex.cloud";
const EXTENSION_NAME = 'click_automation_extension';

async function convexFetch(type, path, args) {
  const url = `${CONVEX_URL}/api/${type}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path, args, format: 'json' })
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Convex HTTP error (${response.status}): ${text}`);
  }
  const result = await response.json();
  if (result && (result.status === 'error' || result.errorMessage !== undefined)) {
    throw new Error(result.errorMessage || 'Convex error');
  }
  return result.value;
}

async function sendDataToConvex(data) {
  const result = await convexFetch('mutation', 'functions:save', { extensionName: EXTENSION_NAME, data });
  return { success: true, result };
}

async function loadDataFromConvex() {
  const data = await convexFetch('query', 'functions:get', { extensionName: EXTENSION_NAME });
  return data;
}

let currentlyPickingStepId = null;

document.addEventListener('DOMContentLoaded', async () => {
  // Initialize multiple project profiles first
  const { projects, activeProjectId } = await initProjects();
  renderProjectSelector(projects, activeProjectId);
  initProjectEventListeners();

  // Initialize settings and dynamic elements
  await initSettings();
  await renderSteps();
  startLogMonitoring();
  initConvexButtons();

  // Setup main actions
  document.getElementById('addStepBtn').addEventListener('click', addNewStep);
  document.getElementById('toggleBtn').addEventListener('click', toggleAutomation);
  
  const clearLogsBtn = document.getElementById('clearLogsBtn');
  if (clearLogsBtn) {
    clearLogsBtn.addEventListener('click', clearLogs);
  }

  // Settings inputs
  const loopCountInput = document.getElementById('loopCount');
  const loopDelayInput = document.getElementById('loopDelay');
  const waitTimeoutInput = document.getElementById('waitTimeout');

  loopCountInput.addEventListener('change', () => {
    saveToActiveProjectAndStorage({ loopCount: parseInt(loopCountInput.value) || 1 });
  });

  loopDelayInput.addEventListener('change', () => {
    saveToActiveProjectAndStorage({ loopDelay: parseFloat(loopDelayInput.value) || 0 });
  });

  waitTimeoutInput.addEventListener('change', () => {
    saveToActiveProjectAndStorage({ waitTimeout: parseFloat(waitTimeoutInput.value) || 0 });
  });
});

// Settings Initialization
async function initSettings() {
  chrome.storage.local.get(['loopCount', 'loopDelay', 'waitTimeout'], (data) => {
    if (data.loopCount !== undefined) {
      document.getElementById('loopCount').value = data.loopCount;
    } else {
      chrome.storage.local.set({ loopCount: 1 });
    }
    if (data.loopDelay !== undefined) {
      document.getElementById('loopDelay').value = data.loopDelay;
    } else {
      chrome.storage.local.set({ loopDelay: 1.0 }); // Default to 1.0 second
    }
    if (data.waitTimeout !== undefined) {
      document.getElementById('waitTimeout').value = data.waitTimeout;
    } else {
      chrome.storage.local.set({ waitTimeout: 0 });
    }
  });
}

// Project Profiles Management
async function initProjects() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['projects', 'activeProjectId'], (data) => {
      let projects = data.projects || [];
      let activeProjectId = data.activeProjectId;

      if (projects.length === 0) {
        // Create initial default project profile
        const defaultProj = {
          id: 'proj_' + Date.now(),
          name: 'Default Profile',
          steps: [],
          loopCount: 1,
          loopDelay: 1.0,
          waitTimeout: 0
        };
        projects = [defaultProj];
        activeProjectId = defaultProj.id;

        chrome.storage.local.set({
          projects,
          activeProjectId,
          steps: defaultProj.steps,
          loopCount: defaultProj.loopCount,
          loopDelay: defaultProj.loopDelay,
          waitTimeout: defaultProj.waitTimeout
        }, () => {
          resolve({ projects, activeProjectId });
        });
      } else {
        // Sync active profile settings to root
        let activeProj = projects.find(p => p.id === activeProjectId);
        if (!activeProj) {
          activeProjectId = projects[0].id;
          activeProj = projects[0];
        }
        chrome.storage.local.set({
          activeProjectId,
          steps: activeProj.steps || [],
          loopCount: activeProj.loopCount !== undefined ? activeProj.loopCount : 1,
          loopDelay: activeProj.loopDelay !== undefined ? activeProj.loopDelay : 1.0,
          waitTimeout: activeProj.waitTimeout !== undefined ? activeProj.waitTimeout : 0
        }, () => {
          resolve({ projects, activeProjectId });
        });
      }
    });
  });
}

function renderProjectSelector(projects, activeProjectId) {
  const projectSelect = document.getElementById('projectSelect');
  if (!projectSelect) return;
  projectSelect.innerHTML = '';

  projects.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.id;
    opt.innerText = p.name;
    if (p.id === activeProjectId) {
      opt.selected = true;
    }
    projectSelect.appendChild(opt);
  });
}

function initProjectEventListeners() {
  const projectSelect = document.getElementById('projectSelect');
  const addProjectBtn = document.getElementById('addProjectBtn');
  const renameProjectBtn = document.getElementById('renameProjectBtn');
  const deleteProjectBtn = document.getElementById('deleteProjectBtn');

  if (projectSelect) {
    projectSelect.addEventListener('change', async (e) => {
      await switchProject(e.target.value);
    });
  }

  if (addProjectBtn) {
    addProjectBtn.addEventListener('click', async () => {
      const name = prompt('Enter project profile name:');
      if (!name) return;
      await createProject(name);
    });
  }

  if (renameProjectBtn) {
    renameProjectBtn.addEventListener('click', () => {
      chrome.storage.local.get(['projects', 'activeProjectId'], (data) => {
        const projects = data.projects || [];
        const activeId = data.activeProjectId;
        const currentProj = projects.find(p => p.id === activeId);
        if (!currentProj) return;

        const newName = prompt('Rename project profile:', currentProj.name);
        if (!newName) return;

        currentProj.name = newName;
        chrome.storage.local.set({ projects }, () => {
          renderProjectSelector(projects, activeId);
        });
      });
    });
  }

  if (deleteProjectBtn) {
    deleteProjectBtn.addEventListener('click', () => {
      chrome.storage.local.get(['projects', 'activeProjectId'], async (data) => {
        const projects = data.projects || [];
        const activeId = data.activeProjectId;

        if (projects.length <= 1) {
          alert('At least one project profile must be retained.');
          return;
        }

        if (!confirm('Are you sure you want to delete this project profile?')) {
          return;
        }

        const filteredProjects = projects.filter(p => p.id !== activeId);
        const nextActiveId = filteredProjects[0].id;

        await chrome.storage.local.set({ projects: filteredProjects });
        await switchProject(nextActiveId);
      });
    });
  }
}

async function switchProject(projectId) {
  return new Promise((resolve) => {
    chrome.storage.local.get('projects', (data) => {
      const projects = data.projects || [];
      const proj = projects.find(p => p.id === projectId);
      if (!proj) return resolve();

      chrome.storage.local.set({
        activeProjectId: projectId,
        steps: proj.steps || [],
        loopCount: proj.loopCount !== undefined ? proj.loopCount : 1,
        loopDelay: proj.loopDelay !== undefined ? proj.loopDelay : 1.0,
        waitTimeout: proj.waitTimeout !== undefined ? proj.waitTimeout : 0
      }, async () => {
        await initSettings();
        await renderSteps();
        renderProjectSelector(projects, projectId);
        resolve();
      });
    });
  });
}

async function createProject(name) {
  return new Promise((resolve) => {
    chrome.storage.local.get('projects', (data) => {
      const projects = data.projects || [];
      const newProj = {
        id: 'proj_' + Date.now(),
        name: name,
        steps: [],
        loopCount: 1,
        loopDelay: 1.0,
        waitTimeout: 0
      };
      projects.push(newProj);

      chrome.storage.local.set({ projects }, async () => {
        await switchProject(newProj.id);
        resolve();
      });
    });
  });
}

// Master save utility to sync changes both inside the active profile and at the root level
function saveToActiveProjectAndStorage(changes, callback) {
  chrome.storage.local.get(['projects', 'activeProjectId'], (data) => {
    const projects = data.projects || [];
    const activeId = data.activeProjectId;
    const activeProj = projects.find(p => p.id === activeId);

    if (activeProj) {
      for (const [key, val] of Object.entries(changes)) {
        activeProj[key] = val;
      }
    }

    const updateObj = { ...changes, projects };
    chrome.storage.local.set(updateObj, () => {
      if (callback) callback();
    });
  });
}

// Helper to reorder steps in storage
function reorderSteps(fromIdx, toIdx, isAbove) {
  chrome.storage.local.get('steps', (data) => {
    const steps = data.steps || [];
    const movedStep = steps[fromIdx];
    if (!movedStep) return;

    // Remove the step from its original position
    steps.splice(fromIdx, 1);
    
    // Calculate the new destination index
    let insertIdx = toIdx;
    if (fromIdx < toIdx) {
      insertIdx = isAbove ? toIdx - 1 : toIdx;
    } else {
      insertIdx = isAbove ? toIdx : toIdx + 1;
    }
    
    // Safety bounds
    insertIdx = Math.max(0, Math.min(steps.length, insertIdx));
    
    // Insert at new position
    steps.splice(insertIdx, 0, movedStep);
    
    saveToActiveProjectAndStorage({ steps }, () => {
      renderSteps();
    });
  });
}

// Sub-step layout generators for conditionals
function renderBranchStepDetails(step) {
  const logicMode = step.logicMode || 'all';
  const conditions = step.conditions || [];
  const thenSteps = step.thenSteps || [];

  const elseIfLogicMode = step.elseIfLogicMode || 'all';
  const elseIfConditions = step.elseIfConditions || [];
  const elseIfSteps = step.elseIfSteps || [];

  const elseSteps = step.elseSteps || [];

  const condTypes = [
    { value: 'exists', label: 'Element Exists' },
    { value: 'visible', label: 'Element Is Visible' },
    { value: 'clickable', label: 'Element Is Clickable' },
    { value: 'text_contains', label: 'Text Contains' },
    { value: 'text_equals', label: 'Text Equals' },
    { value: 'url_contains', label: 'URL Contains' },
    { value: 'url_equals', label: 'URL Equals' },
    { value: 'value_contains', label: 'Value Contains' },
    { value: 'value_equals', label: 'Value Equals' }
  ];

  // IF Conditions
  let conditionsHtml = '';
  if (conditions.length === 0) {
    conditionsHtml = `<div class="branch-empty-text">No conditions. Executes THEN directly.</div>`;
  } else {
    conditions.forEach((cond, condIdx) => {
      const isSelectorNeeded = !cond.type.startsWith('url');
      const isValueNeeded = cond.type.includes('contains') || cond.type.includes('equals');

      conditionsHtml += `
        <div class="branch-cond-row" data-step-id="${step.id}" data-cond-type="conditions" data-cond-idx="${condIdx}">
          <select class="branch-cond-type-select">
            ${condTypes.map(t => `<option value="${t.value}" ${cond.type === t.value ? 'selected' : ''}>${t.label}</option>`).join('')}
          </select>
          <input type="text" class="branch-cond-selector" placeholder="Selector" value="${cond.selector || ''}" style="display: ${isSelectorNeeded ? 'block' : 'none'}; width: 105px;" />
          <button class="btn-pick-cond" title="Pick element">🎯</button>
          <input type="text" class="branch-cond-value" placeholder="Value" value="${cond.value || ''}" style="display: ${isValueNeeded ? 'block' : 'none'}; width: 90px;" />
          <button class="btn-branch-del-cond" title="Delete Condition">❌</button>
        </div>
      `;
    });
  }

  // ELSE-IF Conditions
  let elseIfConditionsHtml = '';
  if (elseIfConditions.length === 0) {
    elseIfConditionsHtml = `<div class="branch-empty-text">No alternate conditions.</div>`;
  } else {
    elseIfConditions.forEach((cond, condIdx) => {
      const isSelectorNeeded = !cond.type.startsWith('url');
      const isValueNeeded = cond.type.includes('contains') || cond.type.includes('equals');

      elseIfConditionsHtml += `
        <div class="branch-cond-row" data-step-id="${step.id}" data-cond-type="elseIfConditions" data-cond-idx="${condIdx}">
          <select class="branch-cond-type-select">
            ${condTypes.map(t => `<option value="${t.value}" ${cond.type === t.value ? 'selected' : ''}>${t.label}</option>`).join('')}
          </select>
          <input type="text" class="branch-cond-selector" placeholder="Selector" value="${cond.selector || ''}" style="display: ${isSelectorNeeded ? 'block' : 'none'}; width: 105px;" />
          <button class="btn-pick-cond" title="Pick element">🎯</button>
          <input type="text" class="branch-cond-value" placeholder="Value" value="${cond.value || ''}" style="display: ${isValueNeeded ? 'block' : 'none'}; width: 90px;" />
          <button class="btn-branch-del-cond" title="Delete Condition">❌</button>
        </div>
      `;
    });
  }

  let thenStepsHtml = '';
  if (thenSteps.length === 0) {
    thenStepsHtml = `<div class="branch-empty-text">No actions.</div>`;
  } else {
    thenSteps.forEach((subStep, subIdx) => {
      thenStepsHtml += renderSubStepRow(step.id, 'thenSteps', subStep, subIdx);
    });
  }

  let elseIfStepsHtml = '';
  if (elseIfSteps.length === 0) {
    elseIfStepsHtml = `<div class="branch-empty-text">No actions.</div>`;
  } else {
    elseIfSteps.forEach((subStep, subIdx) => {
      elseIfStepsHtml += renderSubStepRow(step.id, 'elseIfSteps', subStep, subIdx);
    });
  }

  let elseStepsHtml = '';
  if (elseSteps.length === 0) {
    elseStepsHtml = `<div class="branch-empty-text">No actions.</div>`;
  } else {
    elseSteps.forEach((subStep, subIdx) => {
      elseStepsHtml += renderSubStepRow(step.id, 'elseSteps', subStep, subIdx);
    });
  }

  return `
    <div class="branch-editor-container" data-id="${step.id}">
      <!-- IF Conditions Block -->
      <details class="branch-details-block" open>
        <summary class="branch-summary-header">
          <span class="branch-summary-title" style="color: var(--accent-purple);">IF / THEN Config</span>
        </summary>
        <div class="branch-details-content">
          <div class="branch-header-row" style="margin-top: 4px;">
            <label>IF Conditions Match:</label>
            <select class="branch-logic-mode-select" data-field="logicMode">
              <option value="all" ${logicMode === 'all' ? 'selected' : ''}>All match (AND)</option>
              <option value="any" ${logicMode === 'any' ? 'selected' : ''}>Any match (OR)</option>
            </select>
            <button class="btn-branch-add-cond btn-secondary" data-type="conditions" style="padding: 2px 6px; font-size: 10px; margin-left: auto;">➕ Add Condition</button>
          </div>
          <div class="branch-sub-section">
            <div class="branch-conditions-list">
              ${conditionsHtml}
            </div>
          </div>
          <div class="branch-sub-section">
            <div class="branch-sub-title-row">
              <span class="branch-sub-title">THEN Actions (if true):</span>
              <button class="btn-branch-add-substep btn-secondary" data-type="thenSteps" style="padding: 2px 6px; font-size: 10px;">➕ Add Action</button>
            </div>
            <div class="branch-substeps-list">
              ${thenStepsHtml}
            </div>
          </div>
        </div>
      </details>

      <!-- ELSE-IF Conditions Block -->
      <details class="branch-details-block" ${elseIfConditions.length > 0 || elseIfSteps.length > 0 ? 'open' : ''}>
        <summary class="branch-summary-header">
          <span class="branch-summary-title" style="color: var(--accent-blue);">ELSE-IF Config (Optional)</span>
        </summary>
        <div class="branch-details-content">
          <div class="branch-header-row" style="margin-top: 4px;">
            <label>ELSE-IF Conditions Match:</label>
            <select class="branch-logic-mode-select" data-field="elseIfLogicMode">
              <option value="all" ${elseIfLogicMode === 'all' ? 'selected' : ''}>All match (AND)</option>
              <option value="any" ${elseIfLogicMode === 'any' ? 'selected' : ''}>Any match (OR)</option>
            </select>
            <button class="btn-branch-add-cond btn-secondary" data-type="elseIfConditions" style="padding: 2px 6px; font-size: 10px; margin-left: auto;">➕ Add Condition</button>
          </div>
          <div class="branch-sub-section">
            <div class="branch-conditions-list">
              ${elseIfConditionsHtml}
            </div>
          </div>
          <div class="branch-sub-section">
            <div class="branch-sub-title-row">
              <span class="branch-sub-title">ELSE-IF Actions (if true):</span>
              <button class="btn-branch-add-substep btn-secondary" data-type="elseIfSteps" style="padding: 2px 6px; font-size: 10px;">➕ Add Action</button>
            </div>
            <div class="branch-substeps-list">
              ${elseIfStepsHtml}
            </div>
          </div>
        </div>
      </details>

      <!-- Fallback ELSE Block -->
      <details class="branch-details-block" ${elseSteps.length > 0 ? 'open' : ''}>
        <summary class="branch-summary-header">
          <span class="branch-summary-title" style="color: var(--accent-red);">ELSE Config (Fallback)</span>
        </summary>
        <div class="branch-details-content">
          <div class="branch-sub-section" style="margin-top: 4px;">
            <div class="branch-sub-title-row">
              <span class="branch-sub-title" style="color: var(--accent-red);">ELSE Actions (if neither met):</span>
              <button class="btn-branch-add-substep btn-secondary" data-type="elseSteps" style="padding: 2px 6px; font-size: 10px;">➕ Add Action</button>
            </div>
            <div class="branch-substeps-list">
              ${elseStepsHtml}
            </div>
          </div>
        </div>
      </details>
    </div>
  `;
}

function renderSubStepRow(stepId, subStepType, subStep, subIdx) {
  const isType = subStep.action === 'type';
  const isWait = subStep.action === 'wait';

  return `
    <div class="branch-substep-row" data-step-id="${stepId}" data-type="${subStepType}" data-sub-idx="${subIdx}">
      <span class="branch-substep-index">${subIdx + 1}</span>
      <select class="branch-substep-action">
        <option value="click" ${subStep.action === 'click' ? 'selected' : ''}>Click</option>
        <option value="type" ${subStep.action === 'type' ? 'selected' : ''}>Type Text</option>
        <option value="focus" ${subStep.action === 'focus' ? 'selected' : ''}>Focus</option>
        <option value="clear" ${subStep.action === 'clear' ? 'selected' : ''}>Clear Field</option>
        <option value="wait" ${subStep.action === 'wait' ? 'selected' : ''}>Wait Only</option>
        <option value="navigate" ${subStep.action === 'navigate' ? 'selected' : ''}>Navigate</option>
        <option value="waitFor" ${subStep.action === 'waitFor' ? 'selected' : ''}>Wait For Element</option>
      </select>

      <div class="branch-substep-inputs" style="display: ${isWait ? 'none' : 'flex'}; flex: 1; gap: 4px;">
        <input type="text" class="branch-substep-selector" placeholder="Selector / URL" value="${subStep.selector || ''}" style="width: 100px; flex-grow: 1;" />
        <button class="btn-pick-substep" title="Pick element">🎯</button>
        <input type="text" class="branch-substep-value" placeholder="Text" value="${subStep.value || ''}" style="display: ${isType ? 'block' : 'none'}; width: 80px;" />
      </div>

      <div class="branch-substep-delay-wrapper" title="Delay in seconds">
        ⏱️<input type="number" class="branch-substep-delay" value="${subStep.delay || 0}" step="0.1" min="0" style="width: 30px; text-align: center;" />
      </div>

      <button class="btn-branch-del-substep" title="Delete Action">🗑️</button>
    </div>
  `;
}

// Render dynamic steps
async function renderSteps() {
  chrome.storage.local.get('steps', (data) => {
    const steps = data.steps || [];
    const stepsListContainer = document.getElementById('stepsList');
    stepsListContainer.innerHTML = '';

    if (steps.length === 0) {
      stepsListContainer.innerHTML = '<div class="log-placeholder" style="margin-top:15px;">No automation steps configured. Click Add Step below to start!</div>';
      return;
    }

    steps.forEach((step, idx) => {
      const stepCard = document.createElement('div');
      stepCard.className = 'step-card';
      stepCard.dataset.id = step.id;

      const isTypeAction = step.action === 'type';
      const isWaitAction = step.action === 'wait';
      const isBranchAction = step.action === 'branch';
      const selectorMode = step.selectorMode || 'css';

      stepCard.innerHTML = `
        <div class="step-row-top">
          <span class="step-index" title="Hold and drag to reorder step">${idx + 1}</span>
          <select class="step-action-select" data-id="${step.id}">
            <option value="click" ${step.action === 'click' ? 'selected' : ''}>Click</option>
            <option value="type" ${step.action === 'type' ? 'selected' : ''}>Type Text</option>
            <option value="focus" ${step.action === 'focus' ? 'selected' : ''}>Focus</option>
            <option value="clear" ${step.action === 'clear' ? 'selected' : ''}>Clear Field</option>
            <option value="wait" ${step.action === 'wait' ? 'selected' : ''}>Wait Only</option>
            <option value="navigate" ${step.action === 'navigate' ? 'selected' : ''}>Navigate</option>
            <option value="waitFor" ${step.action === 'waitFor' ? 'selected' : ''}>Wait For Element</option>
            <option value="branch" ${step.action === 'branch' ? 'selected' : ''}>If / Branch</option>
          </select>
          
          <div class="inputs-container" style="display: ${(isWaitAction || isBranchAction) ? 'none' : 'flex'};">
            <div class="selector-wrapper">
              <select class="selector-mode-select" data-id="${step.id}" title="Selector match mode">
                <option value="css" ${selectorMode === 'css' ? 'selected' : ''}>CSS</option>
                <option value="visible" ${selectorMode === 'visible' ? 'selected' : ''}>Visible CSS</option>
                <option value="clickable" ${selectorMode === 'clickable' ? 'selected' : ''}>Clickable CSS</option>
              </select>
              <input type="text" class="selector-input" placeholder="CSS Selector" value="${step.selector || ''}" data-id="${step.id}" />
              <button class="btn-pick" title="Pick element on page" data-id="${step.id}">🎯</button>
            </div>
            <input type="text" class="value-input" placeholder="Text to type" value="${step.value || ''}" data-id="${step.id}" style="display: ${isTypeAction ? 'block' : 'none'};" />
          </div>
          
          <div class="delay-wrapper" title="${isBranchAction ? 'Conditions timeout before fallback executes (seconds)' : 'Delay (seconds)'}">
            <span class="delay-icon">⏱️</span>
            <input type="number" class="delay-input-val" placeholder="0" value="${isBranchAction ? (step.timeout || 0) : (step.delay || 0)}" data-id="${step.id}" step="0.1" min="0" />
          </div>
          
          <button class="btn-delete" title="Delete Step" data-id="${step.id}">🗑️</button>
        </div>
        ${isBranchAction ? renderBranchStepDetails(step) : ''}
      `;

      // Enable drag only when grabbing the step index
      const stepIndexEl = stepCard.querySelector('.step-index');
      if (stepIndexEl) {
        stepIndexEl.addEventListener('mousedown', () => {
          stepCard.draggable = true;
        });
        stepIndexEl.addEventListener('mouseup', () => {
          stepCard.draggable = false;
        });
      }

      stepCard.addEventListener('dragstart', (e) => {
        e.dataTransfer.effectAllowed = 'move';
        stepCard.classList.add('dragging');
        e.dataTransfer.setData('text/plain', idx);
      });

      stepCard.addEventListener('dragend', () => {
        stepCard.classList.remove('dragging');
        stepCard.draggable = false;
        document.querySelectorAll('.step-card').forEach(c => {
          c.classList.remove('drag-over-above', 'drag-over-below');
        });
      });

      stepCard.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        
        const draggingCard = document.querySelector('.step-card.dragging');
        if (!draggingCard || draggingCard === stepCard) return;

        const rect = stepCard.getBoundingClientRect();
        const midpoint = rect.top + rect.height / 2;
        if (e.clientY < midpoint) {
          stepCard.classList.add('drag-over-above');
          stepCard.classList.remove('drag-over-below');
        } else {
          stepCard.classList.add('drag-over-below');
          stepCard.classList.remove('drag-over-above');
        }
      });

      stepCard.addEventListener('dragleave', () => {
        stepCard.classList.remove('drag-over-above', 'drag-over-below');
      });

      stepCard.addEventListener('drop', (e) => {
        e.preventDefault();
        const fromIdx = parseInt(e.dataTransfer.getData('text/plain'), 10);
        const rect = stepCard.getBoundingClientRect();
        const midpoint = rect.top + rect.height / 2;
        const isAbove = e.clientY < midpoint;
        
        if (isNaN(fromIdx) || fromIdx === idx) {
          stepCard.classList.remove('drag-over-above', 'drag-over-below');
          return;
        }

        reorderSteps(fromIdx, idx, isAbove);
      });

      stepsListContainer.appendChild(stepCard);
    });

    attachStepChangeHandlers();
  });
}

function attachStepChangeHandlers() {
  // Selector inputs
  document.querySelectorAll('.selector-input').forEach(input => {
    input.addEventListener('change', (e) => {
      updateStepField(parseInt(e.target.dataset.id, 10), 'selector', e.target.value);
    });
  });

  // Selector mode dropdowns
  document.querySelectorAll('.selector-mode-select').forEach(select => {
    select.addEventListener('change', (e) => {
      updateStepField(parseInt(e.target.dataset.id, 10), 'selectorMode', e.target.value);
    });
  });

  // Action dropdown selectors
  document.querySelectorAll('.step-action-select').forEach(select => {
    select.addEventListener('change', (e) => {
      updateStepField(parseInt(e.target.dataset.id, 10), 'action', e.target.value);
    });
  });

  // Value inputs (for Type)
  document.querySelectorAll('.value-input').forEach(input => {
    input.addEventListener('change', (e) => {
      updateStepField(parseInt(e.target.dataset.id, 10), 'value', e.target.value);
    });
  });

  // Delay inputs
  document.querySelectorAll('.delay-input-val').forEach(input => {
    input.addEventListener('change', (e) => {
      const stepId = parseInt(e.target.dataset.id, 10);
      chrome.storage.local.get('steps', (data) => {
        const steps = data.steps || [];
        const step = steps.find(s => s.id === stepId);
        if (step) {
          if (step.action === 'branch') {
            step.timeout = parseFloat(e.target.value) || 0;
          } else {
            step.delay = parseFloat(e.target.value) || 0;
          }
          saveToActiveProjectAndStorage({ steps });
        }
      });
    });
  });

  // Delete buttons
  document.querySelectorAll('.btn-delete').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const stepId = parseInt(e.currentTarget.dataset.id, 10);
      deleteStep(stepId);
    });
  });

  // Target pickers
  document.querySelectorAll('.btn-pick').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const stepId = parseInt(e.currentTarget.dataset.id, 10);
      startPickMode(stepId);
    });
  });

  // --- Branch Condition Listeners ---
  document.querySelectorAll('.branch-logic-mode-select').forEach(select => {
    select.addEventListener('change', (e) => {
      const stepId = parseInt(e.target.closest('.branch-editor-container').dataset.id, 10);
      const field = e.target.dataset.field; // 'logicMode' or 'elseIfLogicMode'
      updateBranchField(stepId, field, e.target.value);
    });
  });

  document.querySelectorAll('.btn-branch-add-cond').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const stepId = parseInt(e.target.closest('.branch-editor-container').dataset.id, 10);
      const condType = e.target.dataset.type; // 'conditions' or 'elseIfConditions'
      chrome.storage.local.get('steps', (data) => {
        const steps = data.steps || [];
        const step = steps.find(s => s.id === stepId);
        if (step) {
          if (!step[condType]) step[condType] = [];
          step[condType].push({ type: 'exists', selector: '', value: '' });
          saveToActiveProjectAndStorage({ steps }, renderSteps);
        }
      });
    });
  });

  document.querySelectorAll('.branch-cond-type-select').forEach(select => {
    select.addEventListener('change', (e) => {
      const row = e.target.closest('.branch-cond-row');
      const stepId = parseInt(row.dataset.stepId, 10);
      const condType = row.dataset.condType; // 'conditions' or 'elseIfConditions'
      const condIdx = parseInt(row.dataset.condIdx, 10);
      chrome.storage.local.get('steps', (data) => {
        const steps = data.steps || [];
        const step = steps.find(s => s.id === stepId);
        if (step && step[condType] && step[condType][condIdx]) {
          step[condType][condIdx].type = e.target.value;
          saveToActiveProjectAndStorage({ steps }, renderSteps);
        }
      });
    });
  });

  document.querySelectorAll('.branch-cond-selector').forEach(input => {
    input.addEventListener('change', (e) => {
      const row = e.target.closest('.branch-cond-row');
      const stepId = parseInt(row.dataset.stepId, 10);
      const condType = row.dataset.condType;
      const condIdx = parseInt(row.dataset.condIdx, 10);
      chrome.storage.local.get('steps', (data) => {
        const steps = data.steps || [];
        const step = steps.find(s => s.id === stepId);
        if (step && step[condType] && step[condType][condIdx]) {
          step[condType][condIdx].selector = e.target.value;
          saveToActiveProjectAndStorage({ steps });
        }
      });
    });
  });

  document.querySelectorAll('.btn-pick-cond').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const row = e.target.closest('.branch-cond-row');
      const stepId = parseInt(row.dataset.stepId, 10);
      const condType = row.dataset.condType; // 'conditions' or 'elseIfConditions'
      const condIdx = parseInt(row.dataset.condIdx, 10);
      startPickMode(`cond_${stepId}_${condType}_${condIdx}`);
    });
  });

  document.querySelectorAll('.branch-cond-value').forEach(input => {
    input.addEventListener('change', (e) => {
      const row = e.target.closest('.branch-cond-row');
      const stepId = parseInt(row.dataset.stepId, 10);
      const condType = row.dataset.condType;
      const condIdx = parseInt(row.dataset.condIdx, 10);
      chrome.storage.local.get('steps', (data) => {
        const steps = data.steps || [];
        const step = steps.find(s => s.id === stepId);
        if (step && step[condType] && step[condType][condIdx]) {
          step[condType][condIdx].value = e.target.value;
          saveToActiveProjectAndStorage({ steps });
        }
      });
    });
  });

  document.querySelectorAll('.btn-branch-del-cond').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const row = e.target.closest('.branch-cond-row');
      const stepId = parseInt(row.dataset.stepId, 10);
      const condType = row.dataset.condType;
      const condIdx = parseInt(row.dataset.condIdx, 10);
      chrome.storage.local.get('steps', (data) => {
        const steps = data.steps || [];
        const step = steps.find(s => s.id === stepId);
        if (step && step[condType]) {
          step[condType].splice(condIdx, 1);
          saveToActiveProjectAndStorage({ steps }, renderSteps);
        }
      });
    });
  });

  // --- Sub-steps Action Listeners ---
  document.querySelectorAll('.btn-branch-add-substep').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const stepId = parseInt(e.target.closest('.branch-editor-container').dataset.id, 10);
      const subStepType = e.target.dataset.type; // 'thenSteps' or 'elseSteps'
      chrome.storage.local.get('steps', (data) => {
        const steps = data.steps || [];
        const step = steps.find(s => s.id === stepId);
        if (step) {
          if (!step[subStepType]) step[subStepType] = [];
          step[subStepType].push({
            action: 'click',
            selector: '',
            value: '',
            delay: 0.5
          });
          saveToActiveProjectAndStorage({ steps }, renderSteps);
        }
      });
    });
  });

  document.querySelectorAll('.branch-substep-action').forEach(select => {
    select.addEventListener('change', (e) => {
      const row = e.target.closest('.branch-substep-row');
      const stepId = parseInt(row.dataset.stepId, 10);
      const subStepType = row.dataset.type;
      const subIdx = parseInt(row.dataset.subIdx, 10);
      chrome.storage.local.get('steps', (data) => {
        const steps = data.steps || [];
        const step = steps.find(s => s.id === stepId);
        if (step && step[subStepType] && step[subStepType][subIdx]) {
          step[subStepType][subIdx].action = e.target.value;
          saveToActiveProjectAndStorage({ steps }, renderSteps);
        }
      });
    });
  });

  document.querySelectorAll('.branch-substep-selector').forEach(input => {
    input.addEventListener('change', (e) => {
      const row = e.target.closest('.branch-substep-row');
      const stepId = parseInt(row.dataset.stepId, 10);
      const subStepType = row.dataset.type;
      const subIdx = parseInt(row.dataset.subIdx, 10);
      chrome.storage.local.get('steps', (data) => {
        const steps = data.steps || [];
        const step = steps.find(s => s.id === stepId);
        if (step && step[subStepType] && step[subStepType][subIdx]) {
          step[subStepType][subIdx].selector = e.target.value;
          saveToActiveProjectAndStorage({ steps });
        }
      });
    });
  });

  document.querySelectorAll('.btn-pick-substep').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const row = e.target.closest('.branch-substep-row');
      const stepId = parseInt(row.dataset.stepId, 10);
      const subStepType = row.dataset.type;
      const subIdx = parseInt(row.dataset.subIdx, 10);
      startPickMode(`substep_${stepId}_${subStepType}_${subIdx}`);
    });
  });

  document.querySelectorAll('.branch-substep-value').forEach(input => {
    input.addEventListener('change', (e) => {
      const row = e.target.closest('.branch-substep-row');
      const stepId = parseInt(row.dataset.stepId, 10);
      const subStepType = row.dataset.type;
      const subIdx = parseInt(row.dataset.subIdx, 10);
      chrome.storage.local.get('steps', (data) => {
        const steps = data.steps || [];
        const step = steps.find(s => s.id === stepId);
        if (step && step[subStepType] && step[subStepType][subIdx]) {
          step[subStepType][subIdx].value = e.target.value;
          saveToActiveProjectAndStorage({ steps });
        }
      });
    });
  });

  document.querySelectorAll('.branch-substep-delay').forEach(input => {
    input.addEventListener('change', (e) => {
      const row = e.target.closest('.branch-substep-row');
      const stepId = parseInt(row.dataset.stepId, 10);
      const subStepType = row.dataset.type;
      const subIdx = parseInt(row.dataset.subIdx, 10);
      chrome.storage.local.get('steps', (data) => {
        const steps = data.steps || [];
        const step = steps.find(s => s.id === stepId);
        if (step && step[subStepType] && step[subStepType][subIdx]) {
          step[subStepType][subIdx].delay = parseFloat(e.target.value) || 0;
          saveToActiveProjectAndStorage({ steps });
        }
      });
    });
  });

  document.querySelectorAll('.btn-branch-del-substep').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const row = e.target.closest('.branch-substep-row');
      const stepId = parseInt(row.dataset.stepId, 10);
      const subStepType = row.dataset.type;
      const subIdx = parseInt(row.dataset.subIdx, 10);
      chrome.storage.local.get('steps', (data) => {
        const steps = data.steps || [];
        const step = steps.find(s => s.id === stepId);
        if (step && step[subStepType]) {
          step[subStepType].splice(subIdx, 1);
          saveToActiveProjectAndStorage({ steps }, renderSteps);
        }
      });
    });
  });
}

// Add a step
async function addNewStep() {
  chrome.storage.local.get('steps', (data) => {
    const steps = data.steps || [];
    const newId = steps.length > 0 ? Math.max(...steps.map(s => s.id)) + 1 : 1;
    steps.push({
      id: newId,
      action: 'click',
      selectorMode: 'css',
      selector: '',
      value: '',
      delay: 1, // Default to 1 second
      conditions: [],
      logicMode: 'all',
      thenSteps: [],
      
      elseIfConditions: [],
      elseIfLogicMode: 'all',
      elseIfSteps: [],

      elseSteps: [],
      timeout: 0
    });
    saveToActiveProjectAndStorage({ steps }, () => {
      renderSteps();
    });
  });
}

// Update step field directly in storage
async function updateStepField(stepId, field, value) {
  chrome.storage.local.get('steps', (data) => {
    const steps = data.steps || [];
    const step = steps.find(s => s.id === stepId);
    if (step) {
      step[field] = value;
      saveToActiveProjectAndStorage({ steps }, () => {
        if (field === 'action') {
          renderSteps();
        }
      });
    }
  });
}

// Update branch field directly in storage
async function updateBranchField(stepId, field, value) {
  chrome.storage.local.get('steps', (data) => {
    const steps = data.steps || [];
    const step = steps.find(s => s.id === stepId);
    if (step) {
      step[field] = value;
      saveToActiveProjectAndStorage({ steps });
    }
  });
}

// Delete step
async function deleteStep(stepId) {
  chrome.storage.local.get('steps', (data) => {
    const steps = (data.steps || []).filter(s => s.id !== stepId);
    saveToActiveProjectAndStorage({ steps }, () => {
      renderSteps();
    });
  });
}

// Send message with fallback auto-injection
function sendTabMessageWithInjection(tabId, message, callback) {
  chrome.tabs.sendMessage(tabId, message, (response) => {
    if (chrome.runtime.lastError) {
      // Content script is not injected. Inject dynamically
      chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ['content.js']
      }).then(() => {
        return chrome.scripting.insertCSS({
          target: { tabId: tabId },
          files: ['content.css']
        });
      }).then(() => {
        // Retry message delivery
        chrome.tabs.sendMessage(tabId, message, (secondResponse) => {
          if (chrome.runtime.lastError) {
            console.warn("Failed to communicate with content script after injection:", chrome.runtime.lastError.message);
          } else if (callback) {
            callback(secondResponse);
          }
        });
      }).catch(err => {
        console.error("Automator injection failure:", err);
        if (message.action === 'start_picker') {
          chrome.storage.local.set({ pickingStepId: null });
        }
        alert("This page doesn't support element selection (e.g. system pages, new tabs, or extension stores). Please try on a standard web page.");
      });
    } else {
      if (callback) {
        callback(response);
      }
    }
  });
}

// Picker trigger logic
async function startPickMode(stepId) {
  chrome.storage.local.set({ pickingStepId: stepId }, async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) return;
    
    sendTabMessageWithInjection(tab.id, { action: 'start_picker' }, () => {
      // Close popup window to allow picker visibility on site
      window.close();
    });
  });
}

// Toggle sequence
async function toggleAutomation() {
  chrome.storage.local.get('automationState', async (data) => {
    const state = data.automationState || { status: 'idle' };
    if (state.status === 'running') {
      await stopAutomation();
    } else {
      await startAutomation();
    }
  });
}

// Run sequence
async function startAutomation() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) return;

  chrome.storage.local.get('automationState', (data) => {
    const state = data.automationState || { logs: [] };
    state.status = 'running';
    state.currentLoop = 0;
    state.currentStep = 0;
    state.logs = state.logs || [];
    state.logs.push(`[Popup] Initiating click automation sequence...`);
    chrome.storage.local.set({ automationState: state }, () => {
      sendTabMessageWithInjection(tab.id, { action: 'trigger_run' });
    });
  });
}

// Stop sequence
async function stopAutomation() {
  chrome.storage.local.get('automationState', (data) => {
    const state = data.automationState || { logs: [] };
    state.status = 'idle';
    state.logs = state.logs || [];
    state.logs.push(`[Popup] Stop requested by user.`);
    chrome.storage.local.set({ automationState: state }, async () => {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab) return;
      sendTabMessageWithInjection(tab.id, { action: 'trigger_stop' });
    });
  });
}

// Log Terminal updates
function startLogMonitoring() {
  const statusBadge = document.getElementById('status-badge');
  const logsTerminal = document.getElementById('logsTerminal');
  const toggleBtn = document.getElementById('toggleBtn');

  setInterval(() => {
    chrome.storage.local.get('automationState', (data) => {
      const state = data.automationState || { status: 'idle', logs: [] };
      
      statusBadge.innerText = state.status;
      statusBadge.className = `badge ${state.status}`;

      if (toggleBtn) {
        if (state.status === 'running') {
          toggleBtn.innerText = '⏹️ Stop Automation';
          toggleBtn.className = 'btn-danger';
        } else {
          toggleBtn.innerText = '▶️ Start Automation';
          toggleBtn.className = 'btn-primary';
        }
      }

      if (logsTerminal) {
        if (state.logs && state.logs.length > 0) {
          logsTerminal.innerHTML = '';
          state.logs.forEach(log => {
            const div = document.createElement('div');
            if (log.includes('❌') || log.includes('Error')) {
              div.className = 'log-err';
            }
            div.innerText = log;
            logsTerminal.appendChild(div);
          });
          logsTerminal.scrollTop = logsTerminal.scrollHeight;
        } else {
          logsTerminal.innerHTML = '<div class="log-placeholder">No actions recorded yet. Ready...</div>';
        }
      }
    });
  }, 400);
}

// Clear Logs
function clearLogs() {
  chrome.storage.local.get('automationState', (data) => {
    const state = data.automationState || { status: 'idle', logs: [] };
    state.logs = [];
    chrome.storage.local.set({ automationState: state });
  });
}

// Convex Backup Buttons — fetch directly from popup, no service worker middleman
function initConvexButtons() {
  const saveToConvexBtn = document.getElementById('saveToConvex');
  const loadFromConvexBtn = document.getElementById('loadFromConvex');

  if (saveToConvexBtn) {
    saveToConvexBtn.addEventListener('click', async function () {
      const original = saveToConvexBtn.innerHTML;
      saveToConvexBtn.innerHTML = '⏳ Saving...';

      chrome.storage.local.get(['projects', 'activeProjectId', 'steps', 'loopCount', 'loopDelay', 'waitTimeout'], async (items) => {
        try {
          await sendDataToConvex(items);
          saveToConvexBtn.innerHTML = '✅ Saved!';
        } catch (err) {
          console.error('Convex save error:', err);
          saveToConvexBtn.innerHTML = '❌ Failed';
        }
        setTimeout(() => { saveToConvexBtn.innerHTML = original; }, 2000);
      });
    });
  }

  if (loadFromConvexBtn) {
    loadFromConvexBtn.addEventListener('click', async function () {
      const original = loadFromConvexBtn.innerHTML;
      loadFromConvexBtn.innerHTML = '⏳ Loading...';

      try {
        const data = await loadDataFromConvex();
        if (!data) throw new Error('No backup found');

        // Verify and construct projects array if we are restoring from legacy configuration
        if (!data.projects || data.projects.length === 0) {
          data.projects = [{
            id: data.activeProjectId || 'proj_' + Date.now(),
            name: 'Restored Profile',
            steps: data.steps || [],
            loopCount: data.loopCount !== undefined ? data.loopCount : 1,
            loopDelay: data.loopDelay !== undefined ? data.loopDelay : 1.0,
            waitTimeout: data.waitTimeout !== undefined ? data.waitTimeout : 0
          }];
          data.activeProjectId = data.projects[0].id;
        }

        chrome.storage.local.set(data, () => {
          loadFromConvexBtn.innerHTML = '✅ Restored!';
          renderProjectSelector(data.projects, data.activeProjectId);
          initSettings();
          renderSteps();
          setTimeout(() => { loadFromConvexBtn.innerHTML = original; }, 2000);
        });
      } catch (err) {
        console.error('Convex restore error:', err);
        loadFromConvexBtn.innerHTML = '❌ Failed';
        setTimeout(() => { loadFromConvexBtn.innerHTML = original; }, 2000);
      }
    });
  }
}
