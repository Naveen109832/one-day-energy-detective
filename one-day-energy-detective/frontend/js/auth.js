/**
 * One-Day Energy Detective - Authentication Manager
 * Handles login, registration, session persistence, and sidebar profile updates.
 */

const Auth = {
  currentUser: null,
  currentHousehold: null,

  init() {
    this.bindEvents();
  },

  bindEvents() {
    const tabLogin = document.getElementById("tab-login");
    const tabRegister = document.getElementById("tab-register");
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const logoutBtn = document.getElementById("logout-btn");

    if (tabLogin && tabRegister) {
      tabLogin.addEventListener("click", () => {
        tabLogin.classList.add("active");
        tabRegister.classList.remove("active");
        loginForm.style.display = "block";
        registerForm.style.display = "none";
      });

      tabRegister.addEventListener("click", () => {
        tabRegister.classList.add("active");
        tabLogin.classList.remove("active");
        loginForm.style.display = "none";
        registerForm.style.display = "block";
      });
    }

    if (loginForm) {
      loginForm.addEventListener("submit", (e) => this.handleLogin(e));
    }

    if (registerForm) {
      registerForm.addEventListener("submit", (e) => this.handleRegister(e));
    }

    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => this.handleLogout());
    }

    window.addEventListener("auth:expired", () => {
      this.currentUser = null;
      this.currentHousehold = null;
      App.showAuthScreen();
      App.showToast("Your session has expired. Please sign in again.", "warning");
    });
  },

  async checkExistingSession() {
    const token = API.getToken();
    if (!token) {
      App.showAuthScreen();
      return false;
    }

    try {
      const data = await API.getMe();
      this.currentUser = data.user;
      this.currentHousehold = data.household;
      this.updateSidebarProfile();
      return true;
    } catch (err) {
      API.clearToken();
      App.showAuthScreen();
      return false;
    }
  },

  async handleLogin(e) {
    e.preventDefault();
    const form = e.target;
    const email = form.email.value.trim();
    const password = form.password.value;
    const submitBtn = form.querySelector('button[type="submit"]');

    if (!email || !password) {
      App.showToast("Please enter your email and password", "error");
      return;
    }

    try {
      submitBtn.disabled = true;
      submitBtn.textContent = "Signing In...";
      const res = await API.login(email, password);

      API.setToken(res.token);
      this.currentUser = res.user;
      this.currentHousehold = res.household;
      this.updateSidebarProfile();

      App.showToast(`Welcome back, ${res.user.full_name}!`, "success");
      await App.loadUserData();
      App.showAppShell();
      App.showView("appliances");
    } catch (err) {
      App.showToast(err.message || "Invalid email or password", "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Sign In";
    }
  },

  async handleRegister(e) {
    e.preventDefault();
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');

    const name = form.name.value.trim();
    const email = form.email.value.trim();
    const password = form.password.value;
    const members = parseInt(form.members.value, 10) || 3;
    const tariff = parseFloat(form.tariff.value) || 7.5;
    const localityInput = form.querySelector('input[name="locality_type"]:checked');
    const locality_type = localityInput ? localityInput.value : "urban";

    if (!name || !email || !password) {
      App.showToast("Please fill in all required fields", "error");
      return;
    }

    if (password.length < 6) {
      App.showToast("Password must be at least 6 characters long", "error");
      return;
    }

    try {
      submitBtn.disabled = true;
      submitBtn.textContent = "Creating Account...";
      const res = await API.register({
        full_name: name,
        email: email,
        password: password,
        household_name: `${name}'s Home`,
        occupants: members,
        tariff_rate: tariff,
        locality_type,
        currency_symbol: "₹",
        grid_region: "india_cea"
      });

      API.setToken(res.token);
      this.currentUser = res.user;
      this.currentHousehold = res.household;
      this.updateSidebarProfile();

      App.showToast("Account created successfully! Welcome to Energy Detective.", "success");
      await App.loadUserData();
      App.showAppShell();
      App.showView("appliances");
    } catch (err) {
      App.showToast(err.message || "Failed to create account", "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Create Account & Begin";
    }
  },

  async handleLogout() {
    try {
      await API.logout();
    } catch (err) {
      console.warn("Logout error:", err);
    }
    this.currentUser = null;
    this.currentHousehold = null;
    App.showAuthScreen();
    App.showToast("You have been signed out.", "success");
  },

  updateSidebarProfile() {
    const nameElem = document.getElementById("sidebar-user-name");
    const emailElem = document.getElementById("sidebar-user-email");
    const initialElem = document.getElementById("user-avatar-initial");

    if (this.currentUser) {
      if (nameElem) nameElem.textContent = this.currentUser.full_name || "User";
      if (emailElem) emailElem.textContent = this.currentUser.email || "";
      if (initialElem && this.currentUser.full_name) {
        initialElem.textContent = this.currentUser.full_name.charAt(0).toUpperCase();
      }
    }
  }
};
