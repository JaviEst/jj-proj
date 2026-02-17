import { mkdir, writeFile } from "node:fs/promises";

await mkdir("dist", { recursive: true });

const html = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Asset LTV Dashboard</title>
    <style>
      :root {
        --bg: #f5f7fa;
        --panel: #ffffff;
        --text: #132235;
        --muted: #5f7386;
        --line: #dce6ed;
        --primary: #0077b8;
        --primary-2: #0596d7;
        --ok: #0a8f62;
        --warn: #b87509;
        --danger: #bf2020;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        color: var(--text);
        font-family: "Avenir Next", "Segoe UI", sans-serif;
        background: radial-gradient(circle at 0% 0%, #e6f5fb, var(--bg) 40%);
      }
      .shell {
        max-width: 1240px;
        margin: 0 auto;
        padding: 1.2rem 1rem 2rem;
        display: grid;
        gap: 1rem;
      }
      .hero {
        background: linear-gradient(115deg, #04233a, #0b4468 60%, #0d5b8f);
        color: #fff;
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
      }
      .hero h1 { margin: 0 0 0.35rem; font-size: 1.55rem; }
      .hero p { margin: 0; opacity: 0.93; }
      .layout {
        display: grid;
        gap: 1rem;
        grid-template-columns: minmax(320px, 430px) minmax(0, 1fr);
      }
      .panel {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 14px;
        box-shadow: 0 8px 24px rgba(12, 35, 56, 0.06);
      }
      .panel header {
        padding: 0.9rem 1rem;
        border-bottom: 1px solid var(--line);
      }
      .panel header h2 {
        margin: 0;
        font-size: 1rem;
      }
      .panel header p {
        margin: 0.25rem 0 0;
        color: var(--muted);
        font-size: 0.88rem;
      }
      .panel .body { padding: 0.9rem 1rem 1rem; }
      .section {
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 0.75rem;
        margin-bottom: 0.8rem;
      }
      .section h3 {
        margin: 0 0 0.5rem;
        font-size: 0.93rem;
      }
      .help { color: var(--muted); font-size: 0.82rem; margin: 0.3rem 0 0; }
      .grid { display: grid; gap: 0.65rem; }
      .grid.cols-2 { grid-template-columns: 1fr 1fr; }
      label { font-size: 0.81rem; color: var(--muted); display: grid; gap: 0.25rem; }
      input, select, button {
        width: 100%;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.55rem 0.6rem;
        font-size: 0.95rem;
        background: #fff;
      }
      .btn {
        border: none;
        color: #fff;
        cursor: pointer;
        background: linear-gradient(90deg, var(--primary), var(--primary-2));
        font-weight: 600;
      }
      .btn.secondary { background: #31485c; }
      .btn.ghost {
        background: #eef5fb;
        color: #19415e;
        border: 1px solid #cce3f0;
      }
      .row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
      .row > * { flex: 1; min-width: 120px; }
      .preset {
        background: #f8fbfe;
        border: 1px dashed #c8dcea;
        color: #2e5572;
      }
      .status {
        margin-top: 0.55rem;
        font-size: 0.88rem;
        color: var(--muted);
        padding: 0.35rem 0.45rem;
        border-radius: 7px;
        background: #f7fafc;
        border: 1px solid #e3ebf0;
      }
      .status.ok { color: #0a6c4d; background: #e7f6f0; border-color: #c7ebdc; }
      .status.warn { color: #7a4e08; background: #fff6e8; border-color: #f2ddb3; }
      .status.err { color: #8c1616; background: #ffeded; border-color: #f4c7c7; }
      .metrics {
        display: grid;
        gap: 0.7rem;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      }
      .metric {
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 0.65rem;
        background: #fff;
      }
      .metric small { display: block; color: var(--muted); margin-bottom: 0.22rem; }
      .metric strong { font-size: 1.05rem; }
      .risk-card {
        margin-top: 0.8rem;
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 0.75rem;
      }
      .risk-row { margin-bottom: 0.5rem; }
      .risk-row:last-child { margin-bottom: 0; }
      .risk-row .top {
        display: flex;
        justify-content: space-between;
        font-size: 0.84rem;
        margin-bottom: 0.22rem;
        color: var(--muted);
      }
      .bar {
        position: relative;
        height: 10px;
        border-radius: 999px;
        background: #e8eff4;
        overflow: hidden;
      }
      .fill { height: 100%; }
      .fill.stressed { background: linear-gradient(90deg, #0077b8, #26b6ff); }
      .fill.margin { background: #d08a19; }
      .fill.liq { background: #c22b2b; }
      .badge {
        display: inline-block;
        padding: 0.22rem 0.5rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
      }
      .badge.safe { color: #0a6c4d; background: #e7f6f0; }
      .badge.warn { color: #7a4e08; background: #fff6e8; }
      .badge.danger { color: #8c1616; background: #ffeded; }
      .charts {
        margin-top: 0.9rem;
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
      }
      .charts .top {
        display: grid;
        grid-template-columns: 1fr 1fr auto;
        gap: 0.5rem;
        padding: 0.65rem;
        border-bottom: 1px solid var(--line);
        background: #fbfdff;
      }
      .charts .frame { height: 620px; }
      .charts iframe { width: 100%; height: 100%; border: none; }
      .links {
        font-size: 0.88rem;
        color: var(--muted);
      }
      .links a { color: var(--primary); text-decoration: none; }
      @media (max-width: 980px) {
        .layout { grid-template-columns: 1fr; }
        .charts .top { grid-template-columns: 1fr; }
        .charts .frame { height: 520px; }
      }
    </style>
  </head>
  <body>
    <main class="shell">
      <section class="hero">
        <h1>Asset LTV Risk Monitor</h1>
        <p>Step 1: pick a ticker. Step 2: choose a risk profile. Step 3: run once or live mode.</p>
      </section>

      <section class="layout">
        <aside class="panel">
          <header>
            <h2>Control Center</h2>
            <p>Designed for non-technical users with guided defaults.</p>
          </header>
          <div class="body">
            <div class="section">
              <h3>1) Find Instrument</h3>
              <div class="grid cols-2">
                <label>Ticker
                  <input id="ticker" placeholder="AAPL, TSLA, BTC" />
                </label>
                <label>Market
                  <select id="market">
                    <option value="us">US Equities</option>
                    <option value="crypto">Crypto</option>
                    <option value="raw">Raw Symbol</option>
                  </select>
                </label>
              </div>
              <div class="row" style="margin-top: 0.5rem;">
                <button class="btn ghost" id="applyTicker" type="button">Apply Ticker</button>
              </div>
              <div class="row" style="margin-top: 0.5rem;">
                <button class="preset" data-quick="AAPL,us" type="button">AAPL</button>
                <button class="preset" data-quick="TSLA,us" type="button">TSLA</button>
                <button class="preset" data-quick="BTC,crypto" type="button">BTC</button>
              </div>
            </div>

            <div class="section">
              <h3>2) Set Risk Rules</h3>
              <div class="grid cols-2">
                <label>Risk Profile
                  <select id="profile">
                    <option value="balanced">Balanced</option>
                    <option value="conservative">Conservative</option>
                    <option value="aggressive">Aggressive</option>
                    <option value="custom">Custom</option>
                  </select>
                </label>
                <label>Asset Label
                  <input id="asset" value="AAPL" />
                </label>
                <label>Source Symbol
                  <input id="symbol" value="aapl.us" />
                </label>
                <label>Data Source
                  <select id="source"><option value="stooq">stooq</option></select>
                </label>
                <label>Entry LTV
                  <input id="entry_ltv" type="number" min="0.01" max="1" step="0.01" value="0.50" />
                </label>
                <label>Margin Call LTV
                  <input id="margin_call_ltv" type="number" min="0.01" max="1" step="0.01" value="0.70" />
                </label>
                <label>Liquidation LTV
                  <input id="liquidation_ltv" type="number" min="0.01" max="1" step="0.01" value="0.80" />
                </label>
                <label>Safety Buffer
                  <input id="safety_buffer" type="number" min="0" max="1" step="0.01" value="0.05" />
                </label>
              </div>
              <p class="help">Profile presets update these values automatically. Select custom to fine tune manually.</p>
            </div>

            <div class="section">
              <h3>3) Choose Update Mode</h3>
              <div class="grid cols-2">
                <label>Mode
                  <select id="mode">
                    <option value="once">One-time Snapshot</option>
                    <option value="pull">Live Pull (polling)</option>
                    <option value="push">Live Push (server stream)</option>
                  </select>
                </label>
                <label>Interval (seconds)
                  <input id="interval_seconds" type="number" min="1" max="60" step="1" value="5" />
                </label>
              </div>
              <div class="row" style="margin-top: 0.5rem;">
                <button class="btn" id="start" type="button">Run Analysis</button>
                <button class="btn secondary" id="stop" type="button">Stop Live</button>
              </div>
              <div class="status" id="status">Ready</div>
            </div>
          </div>
        </aside>

        <section class="panel">
          <header>
            <h2>Live Results</h2>
            <p>Clear metrics and risk indicators, optimized for user-facing clients.</p>
          </header>
          <div class="body">
            <div class="metrics" id="metrics"></div>

            <div class="risk-card">
              <div class="risk-row">
                <div class="top"><span>Stressed LTV</span><span id="vStressed">-</span></div>
                <div class="bar"><div class="fill stressed" id="barStressed" style="width:0%"></div></div>
              </div>
              <div class="risk-row">
                <div class="top"><span>Margin Call Threshold</span><span id="vMargin">-</span></div>
                <div class="bar"><div class="fill margin" id="barMargin" style="width:0%"></div></div>
              </div>
              <div class="risk-row">
                <div class="top"><span>Liquidation Threshold</span><span id="vLiq">-</span></div>
                <div class="bar"><div class="fill liq" id="barLiq" style="width:0%"></div></div>
              </div>
              <div style="margin-top:0.55rem;">Risk Status: <span class="badge safe" id="riskBadge">Waiting</span></div>
            </div>

            <div class="charts">
              <div class="top">
                <label>API Base URL
                  <input id="apiBase" />
                </label>
                <label>Grafana URL
                  <input id="grafanaBase" value="http://localhost:3000" />
                </label>
                <button class="btn ghost" id="refreshGraph" type="button">Refresh Graphs</button>
              </div>
              <div class="frame"><iframe id="grafanaFrame" title="Grafana Charts"></iframe></div>
            </div>

            <p class="links" style="margin-top:0.65rem;">
              Hover on chart lines in Grafana to inspect exact values and timestamps.
              <a id="apiDocsLink" href="/docs" target="_blank" rel="noreferrer">API Docs</a>
            </p>
          </div>
        </section>
      </section>
    </main>

    <script>
      const metricsEl = document.getElementById("metrics");
      const statusEl = document.getElementById("status");
      const riskBadge = document.getElementById("riskBadge");

      const controls = {
        ticker: document.getElementById("ticker"),
        market: document.getElementById("market"),
        profile: document.getElementById("profile"),
        asset: document.getElementById("asset"),
        source: document.getElementById("source"),
        symbol: document.getElementById("symbol"),
        entry: document.getElementById("entry_ltv"),
        margin: document.getElementById("margin_call_ltv"),
        liq: document.getElementById("liquidation_ltv"),
        buffer: document.getElementById("safety_buffer"),
        mode: document.getElementById("mode"),
        interval: document.getElementById("interval_seconds"),
        apiBase: document.getElementById("apiBase"),
        grafanaBase: document.getElementById("grafanaBase"),
      };

      const bars = {
        stressed: document.getElementById("barStressed"),
        margin: document.getElementById("barMargin"),
        liq: document.getElementById("barLiq"),
        vStressed: document.getElementById("vStressed"),
        vMargin: document.getElementById("vMargin"),
        vLiq: document.getElementById("vLiq"),
      };

      const grafanaFrame = document.getElementById("grafanaFrame");
      const apiDocsLink = document.getElementById("apiDocsLink");

      let pollTimer = null;
      let eventSource = null;

      const defaultApiBase = window.location.port === "4200" ? "http://localhost:8000" : window.location.origin;
      controls.apiBase.value = defaultApiBase;

      function pct(value) { return (value * 100).toFixed(2) + "%"; }

      function setStatus(message, tone) {
        statusEl.textContent = message;
        statusEl.className = "status";
        if (tone) {
          statusEl.classList.add(tone);
        }
      }

      function getApiBase() {
        return (controls.apiBase.value.trim() || defaultApiBase).replace(/\/$/, "");
      }

      function updateApiDocsLink() {
        apiDocsLink.href = getApiBase() + "/docs";
      }

      function normalizeSymbol(rawTicker, market) {
        const ticker = rawTicker.trim().toLowerCase();
        if (!ticker) return "";
        if (market === "raw") return ticker;
        if (market === "crypto") return ticker.endsWith("usd") ? ticker : ticker + "usd";
        if (ticker.includes(".")) return ticker;
        return ticker + ".us";
      }

      function stopLive() {
        if (pollTimer) {
          clearInterval(pollTimer);
          pollTimer = null;
        }
        if (eventSource) {
          eventSource.close();
          eventSource = null;
        }
      }

      function applyProfile() {
        const profile = controls.profile.value;
        if (profile === "custom") return;

        if (profile === "conservative") {
          controls.entry.value = "0.35";
          controls.margin.value = "0.65";
          controls.liq.value = "0.80";
          controls.buffer.value = "0.08";
          return;
        }
        if (profile === "aggressive") {
          controls.entry.value = "0.60";
          controls.margin.value = "0.72";
          controls.liq.value = "0.82";
          controls.buffer.value = "0.03";
          return;
        }

        controls.entry.value = "0.50";
        controls.margin.value = "0.70";
        controls.liq.value = "0.80";
        controls.buffer.value = "0.05";
      }

      function applyTicker(rawTicker, market) {
        const ticker = (rawTicker || controls.ticker.value || "").trim();
        const mk = market || controls.market.value;
        if (!ticker) {
          setStatus("Enter a ticker first", "warn");
          return;
        }
        const symbol = normalizeSymbol(ticker, mk);
        controls.asset.value = ticker.toUpperCase();
        controls.symbol.value = symbol;
        updateGrafana(symbol);
        setStatus("Mapped ticker to symbol: " + symbol, "ok");
      }

      function payloadFromForm() {
        return {
          asset: controls.asset.value.trim(),
          source: controls.source.value,
          symbol: controls.symbol.value.trim().toLowerCase(),
          entry_ltv: Number(controls.entry.value),
          liquidation_ltv: Number(controls.liq.value),
          margin_call_ltv: Number(controls.margin.value),
          safety_buffer: Number(controls.buffer.value),
        };
      }

      function renderMetrics(data) {
        const cards = [
          ["Asset", data.asset],
          ["Symbol", data.symbol],
          ["Price Date", data.latest_price_date],
          ["Current Price", data.current_price.toFixed(4)],
          ["4Y MA Baseline", data.baseline_4y_ma.toFixed(4)],
          ["Planned Entry LTV", pct(data.planned_entry_ltv)],
          ["Stressed LTV", pct(data.stressed_ltv_at_baseline)],
          ["Max for Margin Call", pct(data.max_entry_ltv_for_margin_call)],
          ["Max for Liquidation", pct(data.max_entry_ltv_for_liquidation)],
          ["Recommended Max", pct(data.recommended_max_entry_ltv)],
        ];

        metricsEl.innerHTML = cards
          .map(function (row) {
            return '<article class="metric"><small>' + row[0] + '</small><strong>' + row[1] + '</strong></article>';
          })
          .join("");

        bars.vStressed.textContent = pct(data.stressed_ltv_at_baseline);
        bars.vMargin.textContent = pct(data.max_entry_ltv_for_margin_call);
        bars.vLiq.textContent = pct(data.max_entry_ltv_for_liquidation);

        bars.stressed.style.width = Math.min(100, data.stressed_ltv_at_baseline * 100) + "%";
        bars.margin.style.width = Math.min(100, data.max_entry_ltv_for_margin_call * 100) + "%";
        bars.liq.style.width = Math.min(100, data.max_entry_ltv_for_liquidation * 100) + "%";

        let label = "Safe";
        let badge = "safe";
        if (data.stressed_ltv_at_baseline >= data.max_entry_ltv_for_liquidation) {
          label = "Critical";
          badge = "danger";
        } else if (data.stressed_ltv_at_baseline >= data.max_entry_ltv_for_margin_call) {
          label = "Caution";
          badge = "warn";
        }
        riskBadge.textContent = label;
        riskBadge.className = "badge " + badge;
      }

      async function fetchAnalyze(payload) {
        const response = await fetch(getApiBase() + "/v1/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const error = await response.json().catch(function () { return { detail: "Request failed" }; });
          throw new Error(error.detail || "Request failed");
        }

        const body = await response.json();
        renderMetrics(body.data);
      }

      function updateGrafana(symbol) {
        const base = (controls.grafanaBase.value.trim() || "http://localhost:3000").replace(/\/$/, "");
        const query = "orgId=1&kiosk&theme=light&refresh=5s&var-symbol=" + encodeURIComponent(symbol || "");
        grafanaFrame.src = base + "/d/asset-ltv-live/asset-ltv-live?" + query;
      }

      function startPush(payload, interval) {
        const params = new URLSearchParams({
          asset: payload.asset,
          source: payload.source,
          symbol: payload.symbol,
          entry_ltv: String(payload.entry_ltv),
          liquidation_ltv: String(payload.liquidation_ltv),
          margin_call_ltv: String(payload.margin_call_ltv),
          safety_buffer: String(payload.safety_buffer),
          interval_seconds: String(interval),
        });

        eventSource = new EventSource(getApiBase() + "/v1/stream/analyze?" + params.toString());
        eventSource.addEventListener("analysis", function (event) {
          const body = JSON.parse(event.data);
          renderMetrics(body.data);
          setStatus("Live push updates active", "ok");
        });
        eventSource.addEventListener("error", function (event) {
          if (event.data) {
            try {
              const payload = JSON.parse(event.data);
              setStatus("Push error: " + payload.detail, "err");
              return;
            } catch (_err) {
              // noop
            }
          }
          setStatus("Push stream disconnected", "warn");
        });
      }

      document.getElementById("applyTicker").addEventListener("click", function () {
        applyTicker();
      });

      document.querySelectorAll("[data-quick]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          const parts = (btn.getAttribute("data-quick") || "").split(",");
          if (parts.length !== 2) return;
          controls.ticker.value = parts[0];
          controls.market.value = parts[1];
          applyTicker(parts[0], parts[1]);
        });
      });

      controls.profile.addEventListener("change", applyProfile);

      document.getElementById("refreshGraph").addEventListener("click", function () {
        updateGrafana(controls.symbol.value.trim().toLowerCase());
      });

      controls.apiBase.addEventListener("input", updateApiDocsLink);

      document.getElementById("stop").addEventListener("click", function () {
        stopLive();
        setStatus("Live updates stopped", "warn");
      });

      document.getElementById("start").addEventListener("click", async function () {
        stopLive();
        const payload = payloadFromForm();

        if (!payload.asset || !payload.symbol) {
          setStatus("Asset and symbol are required", "err");
          return;
        }

        updateGrafana(payload.symbol);

        try {
          const mode = controls.mode.value;
          const interval = Number(controls.interval.value);

          if (mode === "once") {
            setStatus("Running analysis...", "ok");
            await fetchAnalyze(payload);
            setStatus("Snapshot updated", "ok");
            return;
          }

          if (mode === "pull") {
            setStatus("Pull mode every " + interval + "s", "ok");
            await fetchAnalyze(payload);
            pollTimer = setInterval(function () {
              fetchAnalyze(payload).catch(function (err) {
                setStatus("Pull error: " + err.message, "err");
              });
            }, interval * 1000);
            return;
          }

          setStatus("Connecting push stream...", "ok");
          startPush(payload, interval);
        } catch (err) {
          setStatus("Error: " + err.message, "err");
        }
      });

      applyProfile();
      updateApiDocsLink();
      updateGrafana(controls.symbol.value.trim().toLowerCase());
      setStatus("Ready: choose a ticker and click Run Analysis");
    </script>
  </body>
</html>`;

await writeFile("dist/index.html", html, "utf8");
