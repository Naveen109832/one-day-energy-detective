/**
 * One-Day Energy Detective - Official Case Report & Audit Certificate Generator
 * Formats official forensic audit reports with transparent carbon citations and print styling.
 */

const Report = {
  init() {
    const printBtn = document.getElementById("print-report-btn");
    if (printBtn) {
      printBtn.addEventListener("click", () => window.print());
    }
  },

  renderReport(auditData, detectiveCase) {
    const container = document.getElementById("report-content-target");
    if (!container) return;

    if (!auditData || !auditData.summary || auditData.summary.appliance_count === 0) {
      container.innerHTML = `
        <div class="zero-state">
          <div class="zero-state-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
          </div>
          <h3>Audit Certificate Pending</h3>
          <p>Please log your household appliances in the inventory to generate your official One-Day Energy Detective Case File & Audit Certificate.</p>
        </div>
      `;
      return;
    }

    const h = auditData.household;
    const s = auditData.summary;
    const curr = h.currency_symbol || "₹";
    const dateStr = new Date().toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric"
    });

    // Appliance breakdown rows
    const applianceRows = auditData.appliances
      .map(
        (a, i) => `
        <tr>
          <td>${i + 1}</td>
          <td><strong>${a.name}</strong></td>
          <td style="text-transform: capitalize;">${a.category}</td>
          <td>${a.power_watts} W</td>
          <td>${a.quantity}</td>
          <td>${a.daily_hours} h</td>
          <td>${a.standby_watts > 0 ? a.standby_watts + " W" : "—"}</td>
          <td><strong>${a.total_daily_kwh}</strong></td>
          <td>${a.monthly_kwh} kWh</td>
          <td>${curr}${a.monthly_cost.toFixed(2)}</td>
        </tr>
      `
      )
      .join("");

    // Top suspects
    const culpritsList = (detectiveCase.top_culprits || [])
      .map(
        (c, idx) => `
        <li style="margin-bottom: 0.4rem;">
          <strong>Suspect #${idx + 1}: ${c.name}</strong> — Consumes <strong>${c.daily_kwh.toFixed(2)} kWh/day</strong> 
          (${c.share_of_household_pct}% of total household energy). Est. monthly bill impact: ${curr}${c.monthly_cost.toFixed(2)}.
        </li>
      `
      )
      .join("");

    // Action plan items
    const recsList = (detectiveCase.recommendations || [])
      .slice(0, 5)
      .map(
        (r, idx) => `
        <li style="margin-bottom: 0.65rem;">
          <strong>${idx + 1}. ${r.action_title}</strong> (${r.impact_tier})<br>
          <span style="font-size: 0.8125rem; color: var(--text-muted);">${r.description}</span><br>
          <span style="font-size: 0.75rem; color: var(--emerald-main); font-weight: 600;">
            Estimated savings: ${curr}${r.estimated_monthly_cost_savings.toFixed(2)}/mo (${r.estimated_monthly_kwh_savings} kWh/mo)
          </span>
        </li>
      `
      )
      .join("");

    container.innerHTML = `
      <div class="report-paper">
        <div class="report-header-banner">
          <div>
            <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--cyan-main); font-weight: 700; letter-spacing: 0.08em; margin-bottom: 0.25rem;">
              OFFICIAL ONE-DAY ENERGY AUDIT CERTIFICATE
            </div>
            <h2 style="font-size: 1.5rem; margin-bottom: 0.25rem;">${h.household_name}</h2>
            <div style="font-size: 0.8125rem; color: var(--text-muted);">
              Audit Timestamp: ${dateStr} • Dwelling: ${h.dwelling_type} • Occupants: ${h.occupants} persons
            </div>
          </div>
          <div style="text-align: right;">
            <div style="font-size: 0.75rem; color: var(--text-dim); text-transform: uppercase;">Audit Rating</div>
            <div style="font-size: 1.125rem; font-weight: 700; color: var(--cyan-main);">${detectiveCase.efficiency_grade}</div>
          </div>
        </div>

        <div style="background: var(--bg-input); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 1.25rem; margin-bottom: 1.5rem;">
          <h4 style="font-size: 0.875rem; text-transform: uppercase; color: var(--text-dim); margin-bottom: 0.5rem; letter-spacing: 0.05em;">
            Executive Detective Verdict
          </h4>
          <p style="font-size: 0.9375rem; line-height: 1.5; color: var(--text-main); margin-bottom: 0.75rem;">
            ${detectiveCase.detective_verdict}
          </p>
          <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; border-top: 1px solid var(--border-subtle); padding-top: 0.75rem;">
            <div>
              <div style="font-size: 0.7rem; color: var(--text-dim);">Daily Consumption</div>
              <div style="font-size: 1.125rem; font-weight: 700;">${s.total_daily_kwh} <span style="font-size: 0.75rem;">kWh/day</span></div>
            </div>
            <div>
              <div style="font-size: 0.7rem; color: var(--text-dim);">Per-Capita Metric</div>
              <div style="font-size: 1.125rem; font-weight: 700;">${s.daily_kwh_per_capita.toFixed(2)} <span style="font-size: 0.75rem;">kWh/capita</span></div>
            </div>
            <div>
              <div style="font-size: 0.7rem; color: var(--text-dim);">Est. Monthly Bill</div>
              <div style="font-size: 1.125rem; font-weight: 700;">${curr}${s.total_monthly_cost.toFixed(2)}</div>
            </div>
            <div>
              <div style="font-size: 0.7rem; color: var(--text-dim);">Scope 2 Carbon</div>
              <div style="font-size: 1.125rem; font-weight: 700;">${s.total_monthly_carbon_kg.toFixed(1)} <span style="font-size: 0.75rem;">kg CO2e/mo</span></div>
            </div>
          </div>
        </div>

        <h3 style="font-size: 1.125rem; margin-bottom: 0.5rem;">Audited Appliance Inventory</h3>
        <table class="report-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Appliance Name</th>
              <th>Category</th>
              <th>Rated Power</th>
              <th>Qty</th>
              <th>Daily Hours</th>
              <th>Standby</th>
              <th>Daily kWh</th>
              <th>Monthly kWh</th>
              <th>Monthly Bill</th>
            </tr>
          </thead>
          <tbody>
            ${applianceRows}
          </tbody>
        </table>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin: 1.5rem 0;">
          <div style="background: var(--bg-input); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 1.25rem;">
            <h4 style="font-size: 0.9375rem; margin-bottom: 0.75rem; color: var(--rose-main);">
              Primary Energy Suspects (Highest Daily Consumption)
            </h4>
            <ol style="padding-left: 1.25rem; font-size: 0.8125rem; line-height: 1.45;">
              ${culpritsList || "<li>No major energy culprits identified.</li>"}
            </ol>
          </div>

          <div style="background: var(--bg-input); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 1.25rem;">
            <h4 style="font-size: 0.9375rem; margin-bottom: 0.75rem; color: var(--emerald-main);">
              Detective Action Plan (Targeted Interventions)
            </h4>
            <ul style="padding-left: 1.25rem; font-size: 0.8125rem; line-height: 1.45; list-style-type: none;">
              ${recsList || "<li>All inspected appliances are operating within high efficiency parameters.</li>"}
            </ul>
          </div>
        </div>

        <div style="border-top: 1px solid var(--border-subtle); padding-top: 1rem; margin-top: 1.5rem; font-size: 0.75rem; color: var(--text-dim); line-height: 1.5;">
          <strong>Methodology & Citations:</strong><br>
          • Electricity Consumption Formula: <em>Daily kWh = (Power_Watts × Quantity × Hours) / 1000 + (Standby_Watts × Quantity × Idle_Hours) / 1000</em>.<br>
          • Monthly projections model a standard 30-day billing cycle: <em>Monthly kWh = Daily kWh × 30</em>.<br>
          • Grid Emission Factor: <strong>${h.emission_factor_kg_per_kwh} kg CO<sub>2</sub>e/kWh</strong> (${h.grid_region_name}). 
          Source: ${h.citation_source}. Scope 2 emissions reflect grid average; actual instantaneous emissions vary with renewable grid dispatch.<br>
          • Residential Benchmarks: Referenced from Bureau of Energy Efficiency (BEE) & Central Electricity Authority (CEA) Urban Electrified Dwelling Indices.
        </div>
      </div>
    `;
  }
};
