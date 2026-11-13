# 🌱 One-Day Energy Detective — Household Energy Audit

A simple, user-friendly web application for auditing household electricity consumption, comparing against locality baselines, and evaluating whether your household energy usage is safe for the environment.

---

## 🎨 Environmental Design System
Built strictly using the eco-friendly palette:
- **Deep Green (`#123D2B`)**: Sidebar, brand logo, and header accents.
- **Leaf Green (`#238653`)**: Action buttons, active navigation, and positive highlights.
- **Sage (`#B9DDBD`)**: Soft badge fills, tags, and secondary borders.
- **Mint (`#EAF5E9`)**: Light, welcoming page background.
- **White (`#FFFFFF`)**: Clean cards with subtle elevation and readable form inputs.
- **Text (`#26352D`)**: High-contrast, legible typography.
- **Energy (`#E5B84B`)**: Warm yellow for energy highlights, kWh stats, and warnings.
- **Border (`#DDE8DF`)**: Subtle lines and dividers.
- **Consistent Rounded Corners**: `12px – 16px`.

---

## 🚀 Application Flow & Pages

### 1. Simple Login & Account Creation
- Features the environmental hero image from [Fastweb](https://www.fastweb.com/uploads/article_photo/photo/2036160/Simple_Environment.jpeg).
- New users can click **Create Account** to register with their name, email, password, and household members count.
- Passwords are encrypted and hashed with **PBKDF2-HMAC-SHA256** and stored securely in the SQLite database.
- Data is saved separately for each user email so they can log in anytime to review or edit their audit.

### 2. Household & Appliances Input
- Set the number of household members and local tariff rate (₹/kWh).
- Add appliances used in the home with:
  - Appliance Name
  - Category (Climate, Kitchen, Lighting, Entertainment, Electronics, Laundry, Other)
  - Number of appliances (Quantity)
  - Average power in **Watts (W)**
  - Daily operating **hours (0–24)**
- Quick suggestion chips for common appliances (Fan, AC, Fridge, TV, LED, Tube Light, Geyser, Washing Machine, PC, Laptop) with typical wattage ratings to make data entry effortless.
- Users can add, edit, or delete appliances anytime.
- Halfway progress is preserved in the database automatically.

### 3. Calculated Energy Results & Locality Comparison
- Prominently calculates each appliance using the exact formula:
  $$\text{Daily Energy Consumption (kWh)} = \frac{\text{Power (Watts)} \times \text{Number of Appliances} \times \text{Hours used}}{1000}$$
- Sums all appliances together to provide:
  - **Total Daily Consumption** (kWh/day)
  - **Weekly Energy Report** ($\text{Daily} \times 7$)
  - **Monthly Energy Report** ($\text{Daily} \times 30$)
  - Estimated financial costs based on user's tariff.
- **Locality Energy Usage Comparison**:
  - Compares daily household consumption against the average urban residential locality baseline (**7.50 kWh/household/day**, sourced from *Prayas Energy Group* & *Central Electricity Authority*).
  - Displays a visual comparative meter showing whether the household is higher or lower than the locality average.
- **Environmental Safety Verdict**:
  - Evaluated logically by considering household members and appliance load:
    $$\text{Per-Capita Daily Energy} = \frac{\text{Total Daily kWh}}{\text{Household Members}}$$
  - **Safe for the Environment** ($\le 3.0\text{ kWh/person/day}$): Green badge — Highly efficient, sustainable per-capita residential footprint.
  - **Moderate Environmental Impact** ($3.0 - 5.0\text{ kWh/person/day}$): Yellow badge — Acceptable urban living standard.
  - **High Environmental Impact** ($> 5.0\text{ kWh/person/day}$): Red badge — Exceeds sustainable thresholds; heavy thermal or continuous loads generating high Scope 2 carbon emissions.

### 4. Practical Energy-Saving Recommendations
Actionable advice tailored to actual household appliances observed:
1. **Switch off unused lights**: Turn off lighting in vacant rooms to save 15–20 kWh/month.
2. **Avoid unnecessary standby operation**: Turn off wall switches to eliminate phantom vampire loads.
3. **Use LED lighting**: Replace traditional bulbs with 9W LEDs for 80% energy reduction.
4. **Reduce unnecessary operating hours**: Trim idle AC, fan, or geyser runtime with timers.
5. **Maintain appliances properly**: Clean AC filters and refrigerator condenser coils to preserve compressor efficiency.

---

## 🏃 How to Run the Application

### Option A: Double Click
1. Open [`C:\Users\DELL\.gemini\antigravity\scratch\one-day-energy-detective`](file:///C:/Users/DELL/.gemini/antigravity/scratch/one-day-energy-detective)
2. Double-click **`start.bat`** (or right-click **`start.ps1`** and select *Run with PowerShell*).

### Option B: Terminal Command
```powershell
cd "C:\Users\DELL\.gemini\antigravity\scratch\one-day-energy-detective"
& "C:\Users\DELL\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\python.exe" run_server.py
```

Open your browser to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

### Run Automated Tests
```powershell
& "C:\Users\DELL\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\python.exe" run_tests.py
```
All 15 test suites verify calculations, auth security, multi-tenant isolation, and validation rules.
