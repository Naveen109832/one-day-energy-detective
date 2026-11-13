"""Script to patch index.html: add locality selector in register form, update locality comparison section."""

path = r'C:\Users\DELL\.gemini\antigravity\scratch\one-day-energy-detective\frontend\index.html'

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# ── Patch 1: Add Urban/Rural radio to registration form ─────────────────────
OLD_REG = '''          </div>
          <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 0.5rem;">
            Create Account & Begin
          </button>
        </form>'''

NEW_REG = '''          </div>
          <div class="form-group">
            <label class="form-label">Where do you live?</label>
            <div style="display: flex; gap: 1rem; margin-top: 0.4rem;">
              <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;font-size:0.9rem;color:#26352D;">
                <input type="radio" id="reg-urban" name="locality_type" value="urban" checked style="accent-color:#238653;"> Urban / City
              </label>
              <label style="display:flex;align-items:center;gap:0.5rem;cursor:pointer;font-size:0.9rem;color:#26352D;">
                <input type="radio" id="reg-rural" name="locality_type" value="rural" style="accent-color:#238653;"> Rural / Village
              </label>
            </div>
            <div class="form-hint">Urban: ~5-10 kWh/day &nbsp;|&nbsp; Rural: ~1.3-4 kWh/day</div>
          </div>
          <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 0.5rem;">
            Create Account & Begin
          </button>
        </form>'''

if OLD_REG in html:
    html = html.replace(OLD_REG, NEW_REG, 1)
    print('OK: registration locality selector added')
else:
    print('WARN: registration block not found — check whitespace')
    # Debug: show surrounding context
    idx = html.find('Create Account & Begin')
    if idx >= 0:
        print(repr(html[idx-200:idx+100]))

# ── Patch 2: Add Urban/Rural toggle in Household Details section ─────────────
OLD_HH = '''          <form id="members-form" style="display: flex; align-items: flex-end; gap: 1.25rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px;">
              <label class="form-label" for="input-household-members">Number of Household Members (Persons)</label>
              <input type="number" id="input-household-members" class="form-input" min="1" max="50" value="3" required>
            </div>
            <div style="flex: 1; min-width: 200px;">
              <label class="form-label" for="input-tariff-rate">Electricity Tariff Rate (&#8377; per kWh / unit)</label>
              <input type="number" id="input-tariff-rate" class="form-input" step="0.1" min="0.1" value="7.5" required>
            </div>
            <button type="submit" class="btn btn-secondary">Update Household</button>
          </form>'''

NEW_HH = '''          <form id="members-form" style="display: flex; align-items: flex-end; gap: 1.25rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px;">
              <label class="form-label" for="input-household-members">Number of Household Members (Persons)</label>
              <input type="number" id="input-household-members" class="form-input" min="1" max="50" value="3" required>
            </div>
            <div style="flex: 1; min-width: 200px;">
              <label class="form-label" for="input-tariff-rate">Electricity Tariff Rate (&#8377; per kWh / unit)</label>
              <input type="number" id="input-tariff-rate" class="form-input" step="0.1" min="0.1" value="7.5" required>
            </div>
            <div style="flex: 1; min-width: 200px;">
              <label class="form-label">Locality Type</label>
              <select id="input-locality-type" class="form-select">
                <option value="urban">Urban / City (5-10 kWh/day)</option>
                <option value="rural">Rural / Village (1.3-4 kWh/day)</option>
              </select>
            </div>
            <button type="submit" class="btn btn-secondary">Update Household</button>
          </form>'''

if OLD_HH in html:
    html = html.replace(OLD_HH, NEW_HH, 1)
    print('OK: household locality selector added')
else:
    # Try with tariff label that may have the rupee symbol differently
    OLD_HH2 = '''          <form id="members-form" style="display: flex; align-items: flex-end; gap: 1.25rem; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px;">
              <label class="form-label" for="input-household-members">Number of Household Members (Persons)</label>
              <input type="number" id="input-household-members" class="form-input" min="1" max="50" value="3" required>
            </div>
            <div style="flex: 1; min-width: 200px;">
              <label class="form-label" for="input-tariff-rate">Electricity Tariff Rate (&#x20B9; per kWh / unit)</label>
              <input type="number" id="input-tariff-rate" class="form-input" step="0.1" min="0.1" value="7.5" required>
            </div>
            <button type="submit" class="btn btn-secondary">Update Household</button>
          </form>'''
    
    NEW_HH2 = NEW_HH  # same replacement

    if OLD_HH2 in html:
        html = html.replace(OLD_HH2, NEW_HH2, 1)
        print('OK: household locality selector added (variant 2)')
    else:
        print('WARN: household members form block not found')
        idx = html.find('members-form')
        if idx >= 0:
            print(repr(html[idx:idx+600]))

# ── Patch 3: Update locality comparison text in results view ─────────────────
OLD_LOC_TEXT = 'Comparing your daily consumption against the average urban residential locality baseline (7.5 kWh/household/day).'
NEW_LOC_TEXT = 'Comparing your daily consumption against your selected locality benchmark. Urban: 5-10 kWh/day | Rural: 1.3-4 kWh/day.'

if OLD_LOC_TEXT in html:
    html = html.replace(OLD_LOC_TEXT, NEW_LOC_TEXT, 1)
    print('OK: locality comparison text updated')
else:
    print('WARN: locality comparison text not found')

OLD_LOC_STAT = 'A typical electrified urban household in India uses between <strong>6.5 to 8.0 kWh per day</strong> (approx. 200\u2013240 units/month).'
NEW_LOC_STAT = 'The average is <strong id="locality-range-text">5 to 10 kWh per day</strong> for urban or <strong>1.3 to 4 kWh per day</strong> for rural Indian households.'

if OLD_LOC_STAT in html:
    html = html.replace(OLD_LOC_STAT, NEW_LOC_STAT, 1)
    print('OK: locality static text updated')
else:
    # Try with HTML entities
    idx = html.find('A typical electrified urban household')
    if idx >= 0:
        print('WARN: locality static text needs manual fix')
        print(repr(html[idx:idx+200]))
    else:
        print('WARN: locality static text not found')

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print('\nHTML patching complete.')
