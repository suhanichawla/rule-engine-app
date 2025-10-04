// Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

let allRules = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadRules();
});

// Tab management
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Deactivate all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');

    // Load rules for checkboxes when switching to evaluate tab
    if (tabName === 'evaluate') {
        loadRuleCheckboxes();
    }
}

// Load all rules
async function loadRules() {
    try {
        const response = await fetch(`${API_BASE_URL}/rules`);
        if (!response.ok) throw new Error('Failed to fetch rules');

        allRules = await response.json();
        displayRules(allRules);
    } catch (error) {
        console.error('Error loading rules:', error);
        document.getElementById('rules-list').innerHTML = `
            <div class="error">Failed to load rules: ${error.message}</div>
        `;
    }
}

// Display rules
function displayRules(rules) {
    const rulesList = document.getElementById('rules-list');

    if (rules.length === 0) {
        rulesList.innerHTML = '<div class="loading">No rules found. Create your first rule!</div>';
        return;
    }

    rulesList.innerHTML = rules.map(rule => `
        <div class="rule-card">
            <div class="rule-header">
                <div class="rule-title">
                    <h3>${escapeHtml(rule.name)}</h3>
                    <div class="rule-id">${rule.id}</div>
                </div>
                <div class="rule-actions">
                    <button class="btn btn-secondary btn-small" onclick="editRule('${rule.id}')">Edit</button>
                    <button class="btn btn-danger btn-small" onclick="deleteRule('${rule.id}')">Delete</button>
                </div>
            </div>

            <div class="rule-description">${escapeHtml(rule.description)}</div>

            ${rule.predicates ? `
                <div class="rule-predicates">
                    <strong>Predicates ${rule.logical_operator ? '(' + rule.logical_operator + ')' : ''}:</strong>
                    ${rule.predicates.map(p => `
                        <div class="predicate">• ${escapeHtml(p.field)} ${escapeHtml(p.operator)} ${JSON.stringify(p.value)}</div>
                    `).join('')}
                </div>
            ` : ''}

            ${rule.expression ? `
                <div class="rule-predicates">
                    <strong>Expression:</strong>
                    <div class="predicate" style="font-family: monospace; color: #4f46e5;">${escapeHtml(rule.expression)}</div>
                </div>
            ` : ''}

        </div>
    `).join('');
}

// Toggle between predicates and expression
function toggleRuleType() {
    const ruleType = document.querySelector('input[name="rule-type"]:checked').value;
    const predicatesSection = document.getElementById('predicates-section');
    const expressionSection = document.getElementById('expression-section');

    if (ruleType === 'predicates') {
        predicatesSection.style.display = 'block';
        expressionSection.style.display = 'none';
    } else {
        predicatesSection.style.display = 'none';
        expressionSection.style.display = 'block';
    }
}

// Show create rule modal
function showCreateRuleModal() {
    document.getElementById('modal-title').textContent = 'Create Rule';
    document.getElementById('edit-rule-id').value = '';
    document.getElementById('rule-name').value = '';
    document.getElementById('rule-description').value = '';
    document.getElementById('rule-expression').value = '';
    document.getElementById('logical-operator').value = 'AND';
    document.getElementById('predicates-container').innerHTML = '';

    // Reset to predicates mode
    document.querySelector('input[name="rule-type"][value="predicates"]').checked = true;
    toggleRuleType();

    // Add one empty predicate
    addPredicate();

    document.getElementById('rule-modal').classList.add('active');
}

// Close rule modal
function closeRuleModal() {
    document.getElementById('rule-modal').classList.remove('active');
}

// Add predicate input
function addPredicate(field = '', operator = '==', value = '') {
    const container = document.getElementById('predicates-container');
    const predicateId = Date.now();

    const predicateHtml = `
        <div class="predicate-item" id="predicate-${predicateId}">
            <input type="text" placeholder="Field name (e.g., age)" value="${escapeHtml(field)}" data-field="field">
            <select data-field="operator">
                <option value="==" ${operator === '==' ? 'selected' : ''}>==(equals)</option>
                <option value="!=" ${operator === '!=' ? 'selected' : ''}>!=(not equals)</option>
                <option value=">" ${operator === '>' ? 'selected' : ''}>&gt;(greater)</option>
                <option value=">=" ${operator === '>=' ? 'selected' : ''}>≥(greater/equal)</option>
                <option value="<" ${operator === '<' ? 'selected' : ''}>&lt;(less)</option>
                <option value="<=" ${operator === '<=' ? 'selected' : ''}>≤(less/equal)</option>
                <option value="contains" ${operator === 'contains' ? 'selected' : ''}>contains</option>
                <option value="not_contains" ${operator === 'not_contains' ? 'selected' : ''}>not contains</option>
                <option value="in" ${operator === 'in' ? 'selected' : ''}>in (array)</option>
                <option value="not_in" ${operator === 'not_in' ? 'selected' : ''}>not in (array)</option>
            </select>
            <input type="text" placeholder='Value: 18 or "USA" or ["USA","Canada"]' value="${escapeHtml(String(value))}" data-field="value" title='For arrays use: ["value1", "value2"]. For strings use: "text". For numbers: 18'>
            <button class="btn btn-danger btn-small" onclick="removePredicate(${predicateId})" title="Remove this predicate">×</button>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', predicateHtml);
}

// Remove predicate
function removePredicate(predicateId) {
    const element = document.getElementById(`predicate-${predicateId}`);
    if (element) element.remove();
}

// Get predicates from form
function getPredicatesFromForm() {
    const predicates = [];
    const predicateItems = document.querySelectorAll('.predicate-item');

    predicateItems.forEach(item => {
        const field = item.querySelector('[data-field="field"]').value.trim();
        const operator = item.querySelector('[data-field="operator"]').value;
        let value = item.querySelector('[data-field="value"]').value.trim();

        // Try to parse value as JSON (for arrays and numbers)
        try {
            value = JSON.parse(value);
        } catch {
            // Keep as string if not valid JSON
        }

        if (field) {
            predicates.push({ field, operator, value });
        }
    });

    return predicates;
}

// Save rule
async function saveRule() {
    const ruleId = document.getElementById('edit-rule-id').value;
    const name = document.getElementById('rule-name').value.trim();
    const description = document.getElementById('rule-description').value.trim();
    const ruleType = document.querySelector('input[name="rule-type"]:checked').value;

    if (!name || !description) {
        alert('Please fill in name and description');
        return;
    }

    let ruleData = { name, description };

    if (ruleType === 'predicates') {
        const predicates = getPredicatesFromForm();
        const logicalOperator = document.getElementById('logical-operator').value;

        if (predicates.length === 0) {
            alert('Please add at least one predicate');
            return;
        }

        ruleData.predicates = predicates;
        ruleData.logical_operator = logicalOperator;
    } else {
        const expression = document.getElementById('rule-expression').value.trim();

        if (!expression) {
            alert('Please enter an expression');
            return;
        }

        ruleData.expression = expression;
    }

    try {
        let response;
        if (ruleId) {
            // Update existing rule
            response = await fetch(`${API_BASE_URL}/rules/${ruleId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(ruleData)
            });
        } else {
            // Create new rule
            response = await fetch(`${API_BASE_URL}/rules`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(ruleData)
            });
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save rule');
        }

        closeRuleModal();
        await loadRules();
    } catch (error) {
        console.error('Error saving rule:', error);
        alert(`Failed to save rule: ${error.message}`);
    }
}

// Edit rule
async function editRule(ruleId) {
    const rule = allRules.find(r => r.id === ruleId);
    if (!rule) return;

    document.getElementById('modal-title').textContent = 'Edit Rule';
    document.getElementById('edit-rule-id').value = rule.id;
    document.getElementById('rule-name').value = rule.name;
    document.getElementById('rule-description').value = rule.description;

    // Check if it's an expression-based rule
    if (rule.expression) {
        // Switch to expression mode
        document.querySelector('input[name="rule-type"][value="expression"]').checked = true;
        document.getElementById('rule-expression').value = rule.expression;
        toggleRuleType();
    } else {
        // Switch to predicates mode
        document.querySelector('input[name="rule-type"][value="predicates"]').checked = true;
        toggleRuleType();

        // Set logical operator
        if (rule.logical_operator) {
            document.getElementById('logical-operator').value = rule.logical_operator;
        }

        // Clear and populate predicates
        document.getElementById('predicates-container').innerHTML = '';
        if (rule.predicates && rule.predicates.length > 0) {
            rule.predicates.forEach(p => {
                addPredicate(p.field, p.operator, typeof p.value === 'object' ? JSON.stringify(p.value) : p.value);
            });
        } else {
            // Add one empty predicate if none exist
            addPredicate();
        }
    }

    document.getElementById('rule-modal').classList.add('active');
}

// Delete rule
async function deleteRule(ruleId) {
    if (!confirm('Are you sure you want to delete this rule?')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/rules/${ruleId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete rule');
        }

        await loadRules();
    } catch (error) {
        console.error('Error deleting rule:', error);
        alert(`Failed to delete rule: ${error.message}`);
    }
}

// Load rule checkboxes for evaluation
function loadRuleCheckboxes() {
    const container = document.getElementById('rule-checkboxes');

    if (allRules.length === 0) {
        container.innerHTML = '<div style="padding: 1rem; color: var(--text-secondary);">No rules available</div>';
        return;
    }

    container.innerHTML = allRules.map(rule => `
        <div class="checkbox-item">
            <input type="checkbox" id="rule-check-${rule.id}" value="${rule.id}">
            <label for="rule-check-${rule.id}">${escapeHtml(rule.name)}</label>
        </div>
    `).join('');
}

// Evaluate payload
async function evaluatePayload() {
    const payloadText = document.getElementById('payload-input').value.trim();
    const ruleIdsText = document.getElementById('rule-ids-input').value.trim();

    // Get rule IDs from checkboxes
    const checkedRuleIds = Array.from(document.querySelectorAll('#rule-checkboxes input[type="checkbox"]:checked'))
        .map(cb => cb.value);

    // Parse rule IDs from text input
    let ruleIds = [];
    if (ruleIdsText) {
        ruleIds = ruleIdsText.split(',').map(id => id.trim()).filter(id => id);
    } else if (checkedRuleIds.length > 0) {
        ruleIds = checkedRuleIds;
    }

    if (!payloadText || ruleIds.length === 0) {
        alert('Please provide both a payload and at least one rule ID');
        return;
    }

    let payload;
    try {
        payload = JSON.parse(payloadText);
    } catch (error) {
        alert('Invalid JSON payload');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ payload, rule_ids: ruleIds })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Evaluation failed');
        }

        const result = await response.json();
        displayEvaluationResult(result);
    } catch (error) {
        console.error('Error evaluating payload:', error);
        alert(`Evaluation failed: ${error.message}`);
    }
}

// Display evaluation result
function displayEvaluationResult(result) {
    const resultContainer = document.getElementById('evaluation-result');
    const resultContent = document.getElementById('result-content');

    resultContent.innerHTML = `
        <div class="result-badge ${result.result}">${result.result}</div>

        <h4>Summary</h4>
        <ul>
            ${result.reasons.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
        </ul>

        <h4>Detailed Results</h4>
        ${result.details.map(detail => `
            <div class="result-detail">
                <h4>${escapeHtml(detail.rule_name)} <span class="result-badge ${detail.result}">${detail.result}</span></h4>
                <p><em>${escapeHtml(detail.reason)}</em></p>

                <div style="margin-top: 0.5rem;">
                    <strong>Predicates:</strong>
                    ${detail.predicate_results.map(pr => {
                        const passed = pr.passed;
                        const icon = passed ? '✓' : '✗';
                        const className = passed ? 'passed' : 'failed';
                        return `
                            <div class="predicate-result ${className}">
                                ${icon} ${escapeHtml(pr.field)} ${escapeHtml(pr.operator)} ${JSON.stringify(pr.expected)}
                                (actual: ${JSON.stringify(pr.actual)})
                                ${pr.error ? `<br>&nbsp;&nbsp;&nbsp;Error: ${escapeHtml(pr.error)}` : ''}
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `).join('')}
    `;

    resultContainer.style.display = 'block';
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

