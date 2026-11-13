/**
 * One-Day Energy Detective - Master Application Coordinator
 * Coordinates views, formula calculation displays, locality benchmarking, and eco recommendations.
 */

const App = {
  currentView: "appliances",
  auditData: null,
  detectiveCase: null,

  async init() {
    Auth.init();
    Appliances.init();
    this.bindNavigation();

    const hasSession = await Auth.checkExistingSession();
    if (hasSession) {
      await this.loadUserData();
      this.showAppShell();
      this.showView("appliances");
    } else {
      this.showAuthScreen();
    }
  },

  bindNavigation() {
    const navBtns = document.querySelectorAll(".nav-link-btn");
    navBtns.forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const view = e.currentTarget.dataset.view;
        if (view) {
          this.showView(view);
        }
      });
    });
  },

  showAuthScreen() {
    const authScreen = document.getElementById("auth-screen");
    const appShell = document.getElementById("app-shell");
    if (authScreen) authScreen.style.display = "flex";
    if (appShell) appShell.style.display = "none";
  },

  showAppShell() {
    const authScreen = document.getElementById("auth-screen");
    const appShell = document.getElementById("app-shell");
    if (authScreen) authScreen.style.display = "none";
    if (appShell) appShell.style.display = "flex";
  },

  showView(viewName) {
    this.currentView = viewName;

    // Toggle navigation buttons
    const navBtns = document.querySelectorAll(".nav-link-btn");
    navBtns.forEach((btn) => {
      if (btn.dataset.view === viewName) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    // Toggle view sections
    const views = ["appliances-view", "results-view", "recommendations-view"];
    views.forEach((vId) => {
      const elem = document.getElementById(vId);
      if (elem) {
        elem.style.display = vId === `${viewName}-view` ? "block" : "none";
      }
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  },

  async loadUserData() {
    try {
      const summaryRes = await API.getAuditSummary();
      this.auditData = summaryRes.audit;
      Appliances.items = this.auditData.appliances || [];

      // Update household members form fields
      if (this.auditData.household) {
        const membersInput = document.getElementById("input-household-members");
        const tariffInput = document.getElementById("input-tariff-rate");
        if (membersInput) membersInput.value = this.auditData.household.occupants || 3;
        if (tariffInput) tariffInput.value = this.auditData.household.tariff_rate || 7.5;
        const localityInput = document.getElementById("input-locality-type");
        if (localityInput) localityInput.value = this.auditData.household.locality_type || "urban";
      }

      // Render Appliances Table
      Appliances.renderAppliancesTable();

      // Render Results Page & Locality Comparison
      this.renderResults();

      // Render Recommendations
      const caseRes = await API.getDetectiveCase();
      this.detectiveCase = caseRes.detective_case;
      this.renderRecommendations();
    } catch (err) {
      console.error("Failed to load user data:", err);
      this.showToast("Failed to load your household energy data", "error");
    }
  },

  renderResults() {
    if (!this.auditData || !this.auditData.summary) return;

    const s = this.auditData.summary;
    const h = this.auditData.household;
    const loc = this.auditData.locality_comparison || {};
    const env = this.auditData.environmental_safety || {};
    const curr = h.currency_symbol || "₹";

    // 1. Primary Highlight Metrics
    const dailyKwh = s.total_daily_kwh;
    const weeklyKwh = s.total_weekly_kwh || (dailyKwh * 7.0);
    const monthlyKwh = s.total_monthly_kwh || (dailyKwh * 30.0);

    const dailyCost = s.total_daily_cost || (dailyKwh * h.tariff_rate);
    const weeklyCost = s.total_weekly_cost || (weeklyKwh * h.tariff_rate);
    const monthlyCost = s.total_monthly_cost || (monthlyKwh * h.tariff_rate);

    const resDailyKwh = document.getElementById("res-daily-kwh");
    const resDailyCost = document.getElementById("res-daily-cost");
    const resWeeklyKwh = document.getElementById("res-weekly-kwh");
    const resWeeklyCost = document.getElementById("res-weekly-cost");
    const resMonthlyKwh = document.getElementById("res-monthly-kwh");
    const resMonthlyCost = document.getElementById("res-monthly-cost");

    if (resDailyKwh) resDailyKwh.textContent = dailyKwh.toFixed(2);
    if (resDailyCost) resDailyCost.textContent = `${curr}${dailyCost.toFixed(2)} per day estimated`;
    if (resWeeklyKwh) resWeeklyKwh.textContent = weeklyKwh.toFixed(2);
    if (resWeeklyCost) resWeeklyCost.textContent = `${curr}${weeklyCost.toFixed(2)} per week estimated`;
    if (resMonthlyKwh) resMonthlyKwh.textContent = monthlyKwh.toFixed(2);
    if (resMonthlyCost) resMonthlyCost.textContent = `${curr}${monthlyCost.toFixed(2)} per month estimated`;

    // 2. Locality Comparison (Urban vs Rural India)
    const isRural = (h.locality_type || loc.locality_type) === "rural";
    const localityAvg = loc.locality_daily_avg_kwh || (isRural ? 2.65 : 7.5);
    const localityMin = loc.locality_daily_min_kwh || (isRural ? 1.3 : 5.0);
    const localityMax = loc.locality_daily_max_kwh || (isRural ? 4.0 : 10.0);
    const areaWord = isRural ? "rural" : "urban";
    const monthlyRange = loc.locality_monthly_range || (isRural ? "40 – 120 kWh/month" : "150 – 300 kWh/month");

    const labelUser = document.getElementById("label-user-kwh");
    const barUser = document.getElementById("bar-user-kwh");
    const barLocality = document.getElementById("bar-locality-kwh");
    const badgeDiff = document.getElementById("locality-diff-badge");
    const textSummary = document.getElementById("locality-text-summary");

    const setText = (id, value) => {
      const el = document.getElementById(id);
      if (el) el.textContent = value;
    };
    setText("locality-intro", `Comparing your daily consumption with the typical Indian ${areaWord} household (${localityMin} – ${localityMax} kWh/day).`);
    setText("label-locality-name", `Typical ${isRural ? "Rural" : "Urban"} Home`);
    setText("label-locality-kwh", `${localityAvg.toFixed(2)} kWh/day`);
    setText("locality-reference", isRural
      ? "Reference: CEA / Ministry of Power rural household electricity data."
      : "Reference: Prayas Energy Group & Central Electricity Authority (CEA) urban residential data.");
    if (labelUser) labelUser.textContent = `${dailyKwh.toFixed(2)} kWh/day`;

    const maxScale = Math.max(isRural ? 6 : 15, Math.max(dailyKwh, localityMax) * 1.25);
    const userPct = Math.min(100, Math.max(4, (dailyKwh / maxScale) * 100));
    if (barLocality) barLocality.style.width = `${Math.min(100, (localityAvg / maxScale) * 100)}%`;

    if (barUser) {
      barUser.style.width = `${userPct}%`;
      barUser.style.background = dailyKwh > localityMax ? "var(--color-energy)" : "var(--color-leaf-green)";
    }

    if (badgeDiff) {
      if (dailyKwh === 0) {
        badgeDiff.textContent = "Awaiting Appliance Entry";
        badgeDiff.style.background = "var(--color-mint)";
        badgeDiff.style.color = "var(--color-text-muted)";
      } else if (dailyKwh > localityMax) {
        badgeDiff.textContent = `▲ Above typical ${areaWord} range`;
        badgeDiff.style.background = "var(--color-energy-soft)";
        badgeDiff.style.color = "#9A6F15";
      } else if (dailyKwh < localityMin) {
        badgeDiff.textContent = `▼ Below typical ${areaWord} range`;
        badgeDiff.style.background = "var(--color-success-soft)";
        badgeDiff.style.color = "var(--color-success)";
      } else {
        badgeDiff.textContent = `✔ Within typical ${areaWord} range`;
        badgeDiff.style.background = "var(--color-success-soft)";
        badgeDiff.style.color = "var(--color-success)";
      }
    }

    if (textSummary) {
      const rangeNote = `Typical ${areaWord} homes in India use about <strong>${localityMin} to ${localityMax} kWh/day</strong> (${monthlyRange}).`;
      if (dailyKwh === 0) {
        textSummary.innerHTML = `${rangeNote} Add appliances in Step 1 to see how you compare.`;
      } else if (dailyKwh > localityMax) {
        textSummary.innerHTML = `Your usage of <strong>${dailyKwh.toFixed(2)} kWh/day</strong> is above the typical range. ${rangeNote}`;
      } else if (dailyKwh < localityMin) {
        textSummary.innerHTML = `Your usage of <strong>${dailyKwh.toFixed(2)} kWh/day</strong> is below the typical range. ${rangeNote}`;
      } else {
        textSummary.innerHTML = `Your usage of <strong>${dailyKwh.toFixed(2)} kWh/day</strong> is within the typical range. ${rangeNote}`;
      }
    }

    // 3. Environmental Safety Assessment
    const safetyBadge = document.getElementById("safety-badge-icon");
    const safetyTitle = document.getElementById("safety-status-title");
    const safetyText = document.getElementById("safety-explanation-text");
    const membersCount = document.getElementById("safety-members-count");
    const perCapitaText = document.getElementById("safety-per-capita");

    if (membersCount) membersCount.textContent = `${h.occupants} persons`;
    if (perCapitaText) perCapitaText.textContent = `${s.daily_kwh_per_capita.toFixed(2)} kWh/person/day`;

    if (safetyBadge && safetyTitle && safetyText) {
      safetyBadge.className = `safety-badge-icon ${env.badge || "safe"}`;
      safetyTitle.textContent = env.status || "Safe for the Environment";
      safetyText.textContent = env.explanation || "Your household is within sustainable environmental limits.";

      if (env.badge === "danger") {
        safetyBadge.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"></polygon><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>';
      } else if (env.badge === "moderate") {
        safetyBadge.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>';
      } else {
        safetyBadge.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>';
      }
    }

    // 4. Per-Appliance Detailed Breakdown Table
    const resultsTbody = document.getElementById("results-table-body");
    if (resultsTbody) {
      if (this.auditData.appliances.length === 0) {
        resultsTbody.innerHTML = `
          <tr>
            <td colspan="6" style="text-align: center; color: var(--color-text-muted); padding: 2rem;">
              No appliances logged. Go to Step 1 to enter your household appliances.
            </td>
          </tr>
        `;
      } else {
        resultsTbody.innerHTML = this.auditData.appliances
          .map((app) => {
            const formulaStr = `(${app.power_watts}W × ${app.quantity} × ${app.daily_hours}h) / 1000`;
            const appDailyKwh = app.total_daily_kwh;
            const appWeeklyKwh = (appDailyKwh * 7.0).toFixed(2);
            const appMonthlyKwh = (appDailyKwh * 30.0).toFixed(2);
            const appMonthlyCost = (appDailyKwh * 30.0 * h.tariff_rate).toFixed(2);

            return `
              <tr>
                <td><strong>${app.name}</strong> (${app.quantity > 1 ? app.quantity + " units" : "1 unit"})</td>
                <td style="color: var(--color-text-muted); font-family: monospace; font-size: 0.82rem;">${formulaStr}</td>
                <td class="kwh-val">${appDailyKwh.toFixed(3)} kWh/day</td>
                <td>${appWeeklyKwh} kWh</td>
                <td>${appMonthlyKwh} kWh</td>
                <td style="font-weight: 600; color: var(--color-deep-green);">${curr}${appMonthlyCost}</td>
              </tr>
            `;
          })
          .join("");
      }
    }
  },

  renderRecommendations() {
    const container = document.getElementById("recommendations-container");
    if (!container) return;

    const curr = (this.auditData && this.auditData.household && this.auditData.household.currency_symbol) || "₹";
    const recs = (this.detectiveCase && this.detectiveCase.recommendations) || [];

    if (recs.length === 0) {
      container.innerHTML = `
        <div class="rec-card">
          <div>
            <h3 class="rec-card-title">${Appliances.items.length ? "No major savings found" : "No appliances added yet"}</h3>
            <p class="rec-card-desc">${Appliances.items.length
              ? "Your current appliance usage is already efficient."
              : "Add your appliances in Step 1 to get recommendations."}</p>
          </div>
        </div>`;
      return;
    }

    container.innerHTML = recs.map((r) => `
      <div class="rec-card">
        <div>
          <span class="rec-badge">${r.category}</span>
          <h3 class="rec-card-title">${r.action_title}</h3>
          <p class="rec-card-desc">${r.description}</p>
        </div>
        <div class="rec-savings-pill">
          <span>Estimated Savings:</span>
          <span class="rec-savings-val">${curr}${r.estimated_monthly_cost_savings.toFixed(0)}/mo (${Math.round(r.estimated_monthly_kwh_savings)} kWh)</span>
        </div>
      </div>
    `).join("");
  },

  showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let iconSvg = "";
    if (type === "success") {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-leaf-green)" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>';
    } else if (type === "error") {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-danger)" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>';
    } else if (type === "warning") {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-energy)" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>';
    } else {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--color-leaf-green)" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';
    }

    toast.innerHTML = `
      <div style="flex-shrink: 0; margin-top: 1px;">${iconSvg}</div>
      <div style="flex: 1; font-weight: 500;">${message}</div>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.transition = "opacity 0.3s ease, transform 0.3s ease";
      toast.style.opacity = "0";
      toast.style.transform = "translateY(8px)";
      setTimeout(() => toast.remove(), 300);
    }, 3800);
  }
};

document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
