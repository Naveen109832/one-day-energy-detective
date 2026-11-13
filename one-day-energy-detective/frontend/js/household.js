/**
 * One-Day Energy Detective - Household Settings Manager
 * Configures dwelling type, occupants, tariff rates, and transparent grid carbon baselines.
 */

const Household = {
  availableRegions: {},

  init() {
    this.bindEvents();
  },

  bindEvents() {
    const pill = document.getElementById("header-household-pill");
    const modal = document.getElementById("household-modal");
    const closeBtn = document.getElementById("household-modal-close");
    const form = document.getElementById("household-settings-form");
    const regionSelect = document.getElementById("edit_grid_region");

    if (pill) {
      pill.addEventListener("click", () => this.openSettingsModal());
    }
    if (closeBtn && modal) {
      closeBtn.addEventListener("click", () => modal.classList.remove("active"));
    }
    if (form) {
      form.addEventListener("submit", (e) => this.handleSaveSettings(e));
    }
    if (regionSelect) {
      regionSelect.addEventListener("change", (e) => this.handleRegionChange(e.target.value));
    }
  },

  async openSettingsModal() {
    const modal = document.getElementById("household-modal");
    if (!modal) return;

    try {
      const res = await API.getHousehold();
      const h = res.household;
      this.availableRegions = res.available_regions || {};

      const form = document.getElementById("household-settings-form");
      if (form) {
        form.edit_household_name.value = h.household_name || "";
        form.edit_dwelling_type.value = h.dwelling_type || "apartment";
        form.edit_occupants.value = h.occupants || 3;
        form.edit_tariff_rate.value = h.tariff_rate || 7.5;
        form.edit_currency_symbol.value = h.currency_symbol || "₹";
        form.edit_grid_region.value = h.grid_region || "india_cea";
        
        if (form.edit_custom_emission_factor) {
          form.edit_custom_emission_factor.value = h.custom_emission_factor || "";
        }
      }

      this.updateRegionCitation(h.grid_region);
      modal.classList.add("active");
    } catch (err) {
      App.showToast("Failed to load household settings", "error");
    }
  },

  handleRegionChange(regionKey) {
    this.updateRegionCitation(regionKey);
    const customWrap = document.getElementById("custom-emission-wrap");
    if (customWrap) {
      customWrap.style.display = regionKey === "custom" ? "block" : "none";
    }
  },

  updateRegionCitation(regionKey) {
    const citationElem = document.getElementById("region-citation-note");
    if (!citationElem) return;

    const info = this.availableRegions[regionKey];
    if (info) {
      citationElem.innerHTML = `
        <strong>Verified Factor:</strong> ${info.factor_kg_per_kwh} kg CO<sub>2</sub>e / kWh<br>
        <strong>Citation:</strong> ${info.source}
      `;
    }
  },

  async handleSaveSettings(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    const payload = {
      household_name: form.edit_household_name.value.trim(),
      dwelling_type: form.edit_dwelling_type.value,
      occupants: parseInt(form.edit_occupants.value, 10),
      tariff_rate: parseFloat(form.edit_tariff_rate.value),
      currency_symbol: form.edit_currency_symbol.value.trim() || "₹",
      grid_region: form.edit_grid_region.value,
      custom_emission_factor: form.edit_custom_emission_factor ? form.edit_custom_emission_factor.value : null
    };

    try {
      submitBtn.disabled = true;
      submitBtn.textContent = "Updating...";
      const res = await API.updateHousehold(payload);

      Auth.currentHousehold = res.household;
      Auth.updateHeaderProfile();
      App.showToast("Household parameters saved successfully", "success");

      document.getElementById("household-modal").classList.remove("active");
      await App.loadAppData();
    } catch (err) {
      App.showToast(err.message || "Failed to update settings", "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Save Configuration";
    }
  }
};
