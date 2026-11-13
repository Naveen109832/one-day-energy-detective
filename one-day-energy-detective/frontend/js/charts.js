/**
 * One-Day Energy Detective - High-Performance Reactive SVG Charts
 * Pure zero-dependency SVG vector renderers with responsive tooltips.
 */

const Charts = {
  CATEGORY_COLORS: {
    climate: "#06b6d4",
    kitchen: "#f59e0b",
    lighting: "#eab308",
    electronics: "#6366f1",
    laundry: "#0ea5e9",
    entertainment: "#a855f7",
    other: "#64748b"
  },

  renderDonutChart(containerId, categories, currencySymbol = "₹") {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!categories || categories.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding: 2rem 1rem; color: var(--text-dim); font-size: 0.8125rem;">
          No appliance consumption data available to plot category distribution.
        </div>
      `;
      return;
    }

    const size = 220;
    const strokeWidth = 28;
    const radius = (size - strokeWidth) / 2;
    const center = size / 2;
    const circumference = 2 * Math.PI * radius;

    let cumulativePct = 0;
    let svgPaths = "";

    categories.forEach((cat) => {
      const pct = cat.share_pct;
      if (pct <= 0) return;

      const strokeDash = (pct / 100) * circumference;
      const strokeGap = circumference - strokeDash;
      const rotation = (cumulativePct / 100) * 360 - 90;
      const color = this.CATEGORY_COLORS[cat.category] || "#64748b";

      svgPaths += `
        <circle
          cx="${center}"
          cy="${center}"
          r="${radius}"
          fill="transparent"
          stroke="${color}"
          stroke-width="${strokeWidth}"
          stroke-dasharray="${strokeDash} ${strokeGap}"
          transform="rotate(${rotation} ${center} ${center})"
          style="transition: stroke-width 0.2s;"
        >
          <title>${cat.category.toUpperCase()}: ${pct}% (${cat.monthly_kwh} kWh/mo, ${currencySymbol}${cat.monthly_cost})</title>
        </circle>
      `;
      cumulativePct += pct;
    });

    // Build legend
    let legendHtml = '<div style="display: flex; flex-direction: column; gap: 0.4rem; font-size: 0.75rem; margin-left: 1rem;">';
    categories.forEach((cat) => {
      const color = this.CATEGORY_COLORS[cat.category] || "#64748b";
      legendHtml += `
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.75rem;">
          <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span style="width: 10px; height: 10px; border-radius: 2px; background: ${color};"></span>
            <span style="text-transform: capitalize; color: var(--text-main); font-weight: 500;">${cat.category}</span>
          </div>
          <span style="color: var(--text-muted); font-weight: 600;">${cat.share_pct}%</span>
        </div>
      `;
    });
    legendHtml += '</div>';

    container.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: center; width: 100%; flex-wrap: wrap; gap: 1rem;">
        <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
          <circle cx="${center}" cy="${center}" r="${radius}" fill="transparent" stroke="var(--border-subtle)" stroke-width="${strokeWidth}" />
          ${svgPaths}
          <text x="${center}" y="${center - 5}" text-anchor="middle" fill="var(--text-main)" font-size="16" font-weight="700">Categories</text>
          <text x="${center}" y="${center + 14}" text-anchor="middle" fill="var(--text-dim)" font-size="11">Breakdown</text>
        </svg>
        ${legendHtml}
      </div>
    `;
  },

  renderCulpritBarChart(containerId, culprits, currencySymbol = "₹") {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!culprits || culprits.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding: 2rem 1rem; color: var(--text-dim); font-size: 0.8125rem;">
          No appliance records to rank energy consumption.
        </div>
      `;
      return;
    }

    const maxKwh = Math.max(...culprits.map((c) => c.daily_kwh), 0.01);

    let html = '<div style="display: flex; flex-direction: column; gap: 0.85rem; width: 100%;">';
    culprits.slice(0, 5).forEach((c, idx) => {
      const pctWidth = Math.min(100, Math.max(5, (c.daily_kwh / maxKwh) * 100));
      const color = c.is_dominant ? "var(--rose-main)" : idx === 0 ? "var(--amber-main)" : "var(--cyan-main)";

      html += `
        <div style="display: flex; flex-direction: column; gap: 0.25rem;">
          <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.8125rem;">
            <span style="font-weight: 600; color: var(--text-main);">${idx + 1}. ${c.name}</span>
            <span style="color: var(--text-muted); font-size: 0.75rem;">
              <strong>${c.daily_kwh.toFixed(2)} kWh/day</strong> (${currencySymbol}${c.monthly_cost}/mo)
            </span>
          </div>
          <div style="width: 100%; height: 8px; background: var(--bg-input); border-radius: 4px; overflow: hidden; border: 1px solid var(--border-subtle);">
            <div style="width: ${pctWidth}%; height: 100%; background: ${color}; border-radius: 4px; transition: width 0.4s ease;"></div>
          </div>
        </div>
      `;
    });
    html += '</div>';

    container.innerHTML = html;
  },

  renderHourlyCurve(containerId, hourlyData) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!hourlyData || hourlyData.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding: 2rem 1rem; color: var(--text-dim); font-size: 0.8125rem;">
          Load profile will generate automatically after adding appliances.
        </div>
      `;
      return;
    }

    const width = 560;
    const height = 180;
    const padding = { top: 20, right: 25, bottom: 30, left: 45 };

    const maxKw = Math.max(...hourlyData.map((d) => d.load_kw), 0.1) * 1.15;
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    const points = hourlyData.map((d, i) => {
      const x = padding.left + (i / 23) * chartWidth;
      const y = padding.top + chartHeight - (d.load_kw / maxKw) * chartHeight;
      return { x, y, ...d };
    });

    const pathData = points.reduce((acc, p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `${acc} L ${p.x} ${p.y}`), "");
    const areaData = `${pathData} L ${points[points.length - 1].x} ${padding.top + chartHeight} L ${points[0].x} ${padding.top + chartHeight} Z`;

    // Horizontal gridlines
    let gridLines = "";
    [0, 0.33, 0.66, 1].forEach((fraction) => {
      const val = (maxKw * fraction).toFixed(2);
      const y = padding.top + chartHeight - fraction * chartHeight;
      gridLines += `
        <line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="var(--border-subtle)" stroke-dasharray="3 3" />
        <text x="${padding.left - 8}" y="${y + 4}" font-size="10" fill="var(--text-dim)" text-anchor="end">${val}kW</text>
      `;
    });

    // X-Axis labels
    let xLabels = "";
    [0, 6, 12, 18, 23].forEach((hour) => {
      const p = points[hour];
      xLabels += `
        <text x="${p.x}" y="${height - 10}" font-size="10" fill="var(--text-dim)" text-anchor="middle">${p.label}</text>
      `;
    });

    // Interactive data dots
    let dots = "";
    points.forEach((p) => {
      dots += `
        <circle cx="${p.x}" cy="${p.y}" r="3" fill="var(--cyan-main)" opacity="0.8">
          <title>${p.label}: ${p.load_kw} kW active load</title>
        </circle>
      `;
    });

    container.innerHTML = `
      <svg width="100%" height="100%" viewBox="0 0 ${width} ${height}" style="overflow: visible;">
        <defs>
          <linearGradient id="curveGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.25" />
            <stop offset="100%" stop-color="#06b6d4" stop-opacity="0.0" />
          </linearGradient>
        </defs>
        ${gridLines}
        <path d="${areaData}" fill="url(#curveGradient)" />
        <path d="${pathData}" fill="none" stroke="var(--cyan-main)" stroke-width="2.5" stroke-linecap="round" />
        ${dots}
        ${xLabels}
      </svg>
    `;
  }
};
