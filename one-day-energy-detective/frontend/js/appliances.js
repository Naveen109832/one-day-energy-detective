/**
 * One-Day Energy Detective - Appliance Inventory Manager
 * Handles appliance input, editing, deletion, and household occupancy updates.
 */

const Appliances = {
  items: [],

  init() {
    this.bindEvents();
  },

  bindEvents() {
    // Add Appliance Form
    const addForm = document.getElementById("add-appliance-form");
    if (addForm) {
      addForm.addEventListener("submit", (e) => this.handleAddAppliance(e));
    }

    // Edit Appliance Form
    const editForm = document.getElementById("edit-appliance-form");
    if (editForm) {
      editForm.addEventListener("submit", (e) => this.handleSaveEdit(e));
    }

    // Urban / Rural selector updates results immediately
    const localitySel = document.getElementById("input-locality-type");
    if (localitySel) {
      localitySel.addEventListener("change", (e) => this.handleUpdateHousehold(e));
    }

    // Household Members Form
    const membersForm = document.getElementById("members-form");
    if (membersForm) {
      membersForm.addEventListener("submit", (e) => this.handleUpdateHousehold(e));
    }
  },

  fillPreset(name, category, watts, hours) {
    const nameInput = document.getElementById("add-app-name");
    const catInput = document.getElementById("add-app-category");
    const powerInput = document.getElementById("add-app-power");
    const hoursInput = document.getElementById("add-app-hours");

    if (nameInput) nameInput.value = name;
    if (catInput) catInput.value = category;
    if (powerInput) powerInput.value = watts;
    if (hoursInput) hoursInput.value = hours;

    App.showToast(`Selected ${name} (${watts}W, ~${hours}h/day)`, "info");
    if (nameInput) nameInput.focus();
  },

  async handleAddAppliance(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    const name = document.getElementById("add-app-name").value.trim();
    const category = document.getElementById("add-app-category").value;
    const quantity = parseInt(document.getElementById("add-app-quantity").value, 10) || 1;
    const power_watts = parseFloat(document.getElementById("add-app-power").value);
    const daily_hours = parseFloat(document.getElementById("add-app-hours").value);
    const standby_watts = parseFloat(document.getElementById("add-app-standby").value) || 0.0;

    if (!name) {
      App.showToast("Please enter an appliance name", "error");
      return;
    }
    if (isNaN(power_watts) || power_watts <= 0) {
      App.showToast("Power in Watts must be greater than 0", "error");
      return;
    }
    if (isNaN(daily_hours) || daily_hours < 0 || daily_hours > 24) {
      App.showToast("Daily hours must be between 0 and 24 hours", "error");
      return;
    }

    try {
      submitBtn.disabled = true;
      submitBtn.textContent = "Adding...";

      await API.createAppliance({
        name,
        category,
        quantity,
        power_watts,
        daily_hours,
        standby_watts,
        room_location: "Home",
        energy_star_rating: 3,
        allow_duplicate: true
      });

      App.showToast(`Added ${name} to your household!`, "success");
      form.reset();
      document.getElementById("add-app-quantity").value = 1;
      document.getElementById("add-app-standby").value = 0;

      await App.loadUserData();
    } catch (err) {
      App.showToast(err.message || "Failed to add appliance", "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "+ Add Appliance to Inventory";
    }
  },

  async handleUpdateHousehold(e) {
    e.preventDefault();
    const members = parseInt(document.getElementById("input-household-members").value, 10) || 3;
    const tariff = parseFloat(document.getElementById("input-tariff-rate").value) || 7.5;
    const localitySelect = document.getElementById("input-locality-type");
    const locality_type = localitySelect ? localitySelect.value : "urban";

    try {
      const currentH = Auth.currentHousehold || {};
      const res = await API.updateHousehold({
        household_name: currentH.household_name || "My Home",
        dwelling_type: currentH.dwelling_type || "apartment",
        occupants: members,
        tariff_rate: tariff,
        locality_type,
        currency_symbol: "₹",
        grid_region: currentH.grid_region || "india_cea"
      });

      Auth.currentHousehold = res.household;
      App.showToast("Household details updated successfully!", "success");
      await App.loadUserData();
    } catch (err) {
      App.showToast(err.message || "Failed to update household", "error");
    }
  },

  openEditModal(id) {
    const app = this.items.find((a) => a.id === id);
    if (!app) return;

    document.getElementById("edit-app-id").value = app.id;
    document.getElementById("edit-app-name").value = app.name;
    document.getElementById("edit-app-category").value = app.category;
    document.getElementById("edit-app-quantity").value = app.quantity || 1;
    document.getElementById("edit-app-power").value = app.power_watts;
    document.getElementById("edit-app-hours").value = app.daily_hours;
    document.getElementById("edit-app-standby").value = app.standby_watts || 0;

    document.getElementById("edit-modal").classList.add("active");
  },

  async handleSaveEdit(e) {
    e.preventDefault();
    const id = parseInt(document.getElementById("edit-app-id").value, 10);
    const name = document.getElementById("edit-app-name").value.trim();
    const category = document.getElementById("edit-app-category").value;
    const quantity = parseInt(document.getElementById("edit-app-quantity").value, 10) || 1;
    const power_watts = parseFloat(document.getElementById("edit-app-power").value);
    const daily_hours = parseFloat(document.getElementById("edit-app-hours").value);
    const standby_watts = parseFloat(document.getElementById("edit-app-standby").value) || 0.0;

    try {
      await API.updateAppliance(id, {
        name,
        category,
        quantity,
        power_watts,
        daily_hours,
        standby_watts,
        room_location: "Home",
        energy_star_rating: 3,
        allow_duplicate: true
      });

      App.showToast(`Updated ${name} successfully!`, "success");
      document.getElementById("edit-modal").classList.remove("active");
      await App.loadUserData();
    } catch (err) {
      App.showToast(err.message || "Failed to update appliance", "error");
    }
  },

  async confirmDelete(id, name) {
    if (!confirm(`Are you sure you want to remove "${name}" from your household?`)) {
      return;
    }

    try {
      await API.deleteAppliance(id);
      App.showToast(`Removed "${name}" from your appliances.`, "success");
      await App.loadUserData();
    } catch (err) {
      App.showToast(err.message || "Failed to remove appliance", "error");
    }
  },

  renderAppliancesTable() {
    const tbody = document.getElementById("appliances-table-body");
    const countText = document.getElementById("appliances-count-text");

    if (countText) {
      countText.textContent = this.items.length;
    }

    if (!tbody) return;

    if (this.items.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align: center; color: var(--color-text-muted); padding: 2rem;">
            No appliances entered yet. Use the quick chips or form above to add appliances used in your home.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = this.items
      .map((app) => {
        const formulaDailyKwh = ((app.power_watts * app.quantity * app.daily_hours) / 1000).toFixed(3);

        return `
          <tr>
            <td><strong>${app.name}</strong></td>
            <td style="text-transform: capitalize; color: var(--color-text-muted);">${app.category}</td>
            <td>${app.quantity}</td>
            <td>${app.power_watts} W</td>
            <td>${app.daily_hours} hrs/day</td>
            <td class="kwh-val">${formulaDailyKwh} kWh</td>
            <td>
              <div style="display: flex; gap: 0.4rem;">
                <button type="button" class="btn btn-secondary btn-sm" onclick="Appliances.openEditModal(${app.id})">
                  Edit
                </button>
                <button type="button" class="btn btn-danger btn-sm" onclick="Appliances.confirmDelete(${app.id}, '${app.name.replace(/'/g, "\\'")}')">
                  Delete
                </button>
              </div>
            </td>
          </tr>
        `;
      })
      .join("");
  }
};
