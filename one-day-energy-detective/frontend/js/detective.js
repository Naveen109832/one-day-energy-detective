/**
 * One-Day Energy Detective - Detective Diagnostic & Simulation Manager
 * Evaluates audit findings, quantifies vampire loads, and powers the What-If simulation engine.
 */

const Detective = {
  detectiveCase: null,
  simulatedMods: {},

  init() {
    this.bindEvents();
  },

  bindEvents() {
    const resetSimBtn = document.getElementById("reset-sim-btn");
    if (resetSimBtn) {
      resetSimBtn.addEventListener("click", () => this.resetSimulation());
    }
  },

  updateDetectiveBanner(detectiveCase, auditSummary, household) {
    this.detectiveCase = detectiveCase;

    const banner = document.getElementById("detective-briefing-banner");
    const badgeIcon = document.getElementById("detective-badge-icon");
    const verdictTitle = document.getElementById("detective-verdict-title");
    const verdictDesc = document.getElementById("detective-verdict-desc");
    const perCapitaVal = document.getElementById("bench-per-capita-val");
    const vampireLossVal = document.getElementById("bench-vampire-loss-val");

    if (!banner || !detectiveCase) return;

    if (auditSummary.appliance_count === 0) {
      banner.style.display = "none";
      return;
    }
    banner.style.display = "flex";

    const ratingColor = detectiveCase.rating_color || "gray";
    if (badgeIcon) {
      badgeIcon.className = `detective-badge-icon ${ratingColor}`;
    }

    if (verdictTitle) {
      verdictTitle.textContent = detectiveCase.efficiency_grade;
    }

    if (verdictDesc) {
      verdictDesc.textContent = detectiveCase.detective_verdict;
    }

    if (perCapitaVal) {
      perCapitaVal.textContent = `${auditSummary.daily_kwh_per_capita.toFixed(2)} kWh/person/day`;
    }

    if (vampireLossVal) {
      vampireLossVal.textContent = `${auditSummary.vampire_share_pct.toFixed(1)}% of total energy`;
      if (auditSummary.vampire_share_pct > 10) {
        vampireLossVal.style.color = "var(--amber-main)";
      } else {
        vampireLossVal.style.color = "var(--emerald-main)";
      }
    }
  },

  renderRecommendations(recommendations, currencySymbol = "₹") {
    const container = document.getElementById("recommendations-container");
    const countBadge = document.getElementById("recs-count-badge");
    const zeroState = document.getElementById("recs-zero-state");

    if (!container) return;

    if (!recommendations || recommendations.length === 0) {
      container.style.display = "none";
      if (zeroState) zeroState.style.display = "block";
      if (countBadge) countBadge.textContent = "0 items";
      return;
    }

    if (zeroState) zeroState.style.display = "none";
    container.style.display = "grid";
    if (countBadge) countBadge.textContent = `${recommendations.length} actionable items`;

    container.innerHTML = recommendations
      .map((rec) => {
        return `
          <div class="rec-card">
            <div>
              <div class="rec-header">
                <span class="rec-tier-pill">${rec.impact_tier}</span>
                <span style="font-size: 0.75rem; color: var(--text-dim);">${rec.difficulty}</span>
              </div>
              <h4 class="rec-title">${rec.action_title}</h4>
              <p class="rec-desc">${rec.description}</p>
            </div>

            <div>
              <div class="rec-savings-block">
                <div class="savings-label">
                  Estimated Monthly Savings:
                  <div style="font-size: 0.7rem; color: var(--text-dim);">${rec.estimated_monthly_kwh_savings} kWh/month</div>
                </div>
                <div class="savings-amount">${currencySymbol}${rec.estimated_monthly_cost_savings.toFixed(2)}</div>
              </div>
              <p class="rec-disclaimer">${rec.disclaimer}</p>
            </div>
          </div>
        `;
      })
      .join("");
  },

  renderVampireAlert(vampireDrains, currencySymbol = "₹") {
    const alertBox = document.getElementById("vampire-alert-banner");
    if (!alertBox) return;

    if (!vampireDrains || vampireDrains.length === 0) {
      alertBox.style.display = "none";
      return;
    }

    alertBox.style.display = "flex";
    const totalVampireAnnualCost = vampireDrains.reduce((acc, v) => acc + v.annual_standby_cost, 0);
    const topVampire = vampireDrains[0];

    const titleElem = document.getElementById("vampire-banner-title");
    const descElem = document.getElementById("vampire-banner-desc");

    if (titleElem) {
      titleElem.textContent = `Vampire Drain Alert: ${vampireDrains.length} Phantom Loads Detected`;
    }
    if (descElem) {
      descElem.innerHTML = `
        Identified standby drains totaling <strong>${currencySymbol}${totalVampireAnnualCost.toFixed(0)}/year</strong> in wasted phantom power.
        Top vampire: <strong>${topVampire.name}</strong> (${topVampire.standby_watts}W during ${topVampire.idle_hours}h idle).
      `;
    }
  },

  setupSimulator(appliances) {
    const container = document.getElementById("sim-controls-container");
    if (!container) return;

    if (!appliances || appliances.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 2.5rem 1rem; color: var(--text-muted);">
          Log appliances first to activate the What-If energy simulation sandbox.
        </div>
      `;
      return;
    }

    this.simulatedMods = {};
    let html = "";

    appliances.forEach((app) => {
      this.simulatedMods[app.id] = {
        id: app.id,
        daily_hours: app.daily_hours,
        standby_watts: app.standby_watts,
        power_watts: app.power_watts
      };

      html += `
        <div class="sim-item" data-id="${app.id}">
          <div class="sim-item-header">
            <span class="sim-item-title">${app.name} (${app.power_watts}W)</span>
            <span style="font-size: 0.75rem; color: var(--text-dim);">${app.category}</span>
          </div>

          <div style="margin-bottom: 0.75rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">
              <span>Daily Operating Hours</span>
              <span id="sim-hours-label-${app.id}">${app.daily_hours} hrs</span>
            </div>
            <div class="sim-slider-row">
              <input
                type="range"
                class="sim-slider"
                id="sim-hours-slider-${app.id}"
                min="0"
                max="24"
                step="0.5"
                value="${app.daily_hours}"
                oninput="Detective.handleSimHourChange(${app.id}, this.value)"
              >
            </div>
          </div>

          ${
            app.standby_watts > 0
              ? `
              <div>
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.25rem;">
                  <span>Standby Vampire Draw</span>
                  <span id="sim-standby-label-${app.id}">${app.standby_watts} W</span>
                </div>
                <div class="sim-slider-row">
                  <input
                    type="range"
                    class="sim-slider"
                    id="sim-standby-slider-${app.id}"
                    min="0"
                    max="${Math.max(20, app.standby_watts * 2)}"
                    step="1"
                    value="${app.standby_watts}"
                    oninput="Detective.handleSimStandbyChange(${app.id}, this.value)"
                  >
                </div>
              </div>
              `
              : ""
          }
        </div>
      `;
    });

    container.innerHTML = html;
    this.runSimulation();
  },

  handleSimHourChange(id, val) {
    val = parseFloat(val);
    const label = document.getElementById(`sim-hours-label-${id}`);
    if (label) label.textContent = `${val} hrs`;

    if (this.simulatedMods[id]) {
      this.simulatedMods[id].daily_hours = val;
    }
    this.debounceRunSimulation();
  },

  handleSimStandbyChange(id, val) {
    val = parseFloat(val);
    const label = document.getElementById(`sim-standby-label-${id}`);
    if (label) label.textContent = `${val} W`;

    if (this.simulatedMods[id]) {
      this.simulatedMods[id].standby_watts = val;
    }
    this.debounceRunSimulation();
  },

  debounceTimer: null,
  debounceRunSimulation() {
    clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => this.runSimulation(), 120);
  },

  async runSimulation() {
    const modList = Object.values(this.simulatedMods);
    try {
      const res = await API.simulateScenario(modList);
      this.renderSimulationResults(res.simulation);
    } catch (err) {
      console.warn("Simulation calculation failed:", err);
    }
  },

  renderSimulationResults(sim) {
    if (!sim) return;

    const pctElem = document.getElementById("sim-savings-pct");
    const costElem = document.getElementById("sim-savings-monthly-cost");
    const kwhElem = document.getElementById("sim-savings-monthly-kwh");
    const carbonElem = document.getElementById("sim-savings-monthly-carbon");
    const curr = (Auth.currentHousehold && Auth.currentHousehold.currency_symbol) || "₹";

    const savings = sim.estimated_savings;
    const base = sim.baseline;
    const simu = sim.simulated;

    if (pctElem) {
      pctElem.textContent = `${savings.reduction_percentage.toFixed(1)}%`;
      if (savings.reduction_percentage > 0) {
        pctElem.style.color = "var(--emerald-main)";
      } else if (savings.reduction_percentage < 0) {
        pctElem.style.color = "var(--rose-main)";
      } else {
        pctElem.style.color = "var(--text-dim)";
      }
    }

    if (costElem) {
      costElem.textContent = `${curr}${savings.saved_monthly_cost.toFixed(2)}`;
    }
    if (kwhElem) {
      kwhElem.textContent = `${savings.saved_monthly_kwh.toFixed(1)} kWh`;
    }
    if (carbonElem) {
      carbonElem.textContent = `${savings.saved_monthly_carbon_kg.toFixed(1)} kg CO2e`;
    }

    // Comparison Table
    const tableBody = document.getElementById("sim-table-body");
    if (tableBody) {
      tableBody.innerHTML = `
        <tr>
          <td>Monthly Consumption</td>
          <td>${base.total_monthly_kwh.toFixed(1)} kWh</td>
          <td>${simu.total_monthly_kwh.toFixed(1)} kWh</td>
          <td class="diff">-${savings.saved_monthly_kwh.toFixed(1)} kWh</td>
        </tr>
        <tr>
          <td>Estimated Monthly Bill</td>
          <td>${curr}${base.total_monthly_cost.toFixed(2)}</td>
          <td>${curr}${simu.total_monthly_cost.toFixed(2)}</td>
          <td class="diff">-${curr}${savings.saved_monthly_cost.toFixed(2)}</td>
        </tr>
        <tr>
          <td>Estimated Scope 2 Carbon</td>
          <td>${base.total_monthly_carbon_kg.toFixed(1)} kg</td>
          <td>${simu.total_monthly_carbon_kg.toFixed(1)} kg</td>
          <td class="diff">-${savings.saved_monthly_carbon_kg.toFixed(1)} kg</td>
        </tr>
      `;
    }
  },

  resetSimulation() {
    this.setupSimulator(Appliances.items);
    App.showToast("Simulator parameters reset to audited baseline", "info");
  }
};
