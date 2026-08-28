
import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [allLogs, setAllLogs] = useState([]);
  const [selected, setSelected] = useState(null);

  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");

  // =========================================================
  // ACTIVE PAGE (Overview / Transactions / Recovery Agent / Audit Logs)
  // =========================================================

  const [view, setView] = useState("overview");

  const navItems = [
    { id: "overview", icon: "◈", label: "Overview" },
    { id: "transactions", icon: "◉", label: "Transactions" },
    { id: "agent", icon: "⚡", label: "Recovery Agent" },
    { id: "logs", icon: "▣", label: "Audit Logs" },
  ];

  const pageTitles = {
    overview: {
      heading: "Revenue Recovery Overview",
      subtext: "Autonomous payment investigation, decision and recovery",
    },
    transactions: {
      heading: "Transactions",
      subtext: "Every transaction RecoverAI has processed",
    },
    agent: {
      heading: "Recovery Agent",
      subtext: "Run the autonomous recovery agent on a transaction",
    },
    logs: {
      heading: "Audit Logs",
      subtext: "Full decision history — every attempt, not just the latest",
    },
  };

  // =========================================================
  // FORMAT CURRENCY
  // =========================================================

  const formatCurrency = (value) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(Number(value) || 0);
  };

  // =========================================================
  // STATUS CLASS
  // =========================================================

  const statusClass = (status) => {
    if (!status) {
      return "";
    }

    return String(status)
      .toLowerCase()
      .replaceAll("_", "-");
  };

  // =========================================================
  // LOAD DASHBOARD
  // =========================================================

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const [metricsResponse, logsResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/metrics`),
        fetch(`${API_BASE_URL}/recovery-logs`),
      ]);

      if (!metricsResponse.ok) {
        throw new Error("Failed to load metrics");
      }

      if (!logsResponse.ok) {
        throw new Error("Failed to load recovery logs");
      }

      const metricsData = await metricsResponse.json();
      const logsData = await logsResponse.json();

      // Metrics API is the single source of truth
      setDashboard(metricsData);

      const logs = Array.isArray(logsData)
        ? logsData
        : logsData?.logs ||
          logsData?.recovery_logs ||
          [];

      // Full, un-deduped history for the Audit Logs page —
      // every attempt on every transaction, not just the latest.
      setAllLogs(logs);

      /*
       * Show only the latest recovery record for each transaction.
       *
       * The backend keeps ALL recovery attempts for audit purposes.
       * The dashboard only displays the latest attempt.
       *
       * /recovery-logs is already ordered newest -> oldest,
       * so the first record we encounter for a transaction
       * is the latest one.
       */

      const latestTransactions = [];
      const seenTransactions = new Set();

      for (const log of logs) {
        if (!log.transaction_id) {
          continue;
        }

        if (seenTransactions.has(log.transaction_id)) {
          continue;
        }

        seenTransactions.add(log.transaction_id);
        latestTransactions.push(log);
      }

      setTransactions(latestTransactions);

    } catch (err) {
      console.error("Dashboard loading error:", err);

      setError(
        "Unable to connect to RecoverAI backend. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================================================
  // ANALYZE TRANSACTION
  // =========================================================

  const analyzeTransaction = async (transactionId) => {
    try {
      setAnalyzing(true);
      setError("");

      const response = await fetch(
        `${API_BASE_URL}/analyze/${transactionId}`
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        throw new Error(
          errorData.detail ||
            `Analysis failed with status ${response.status}`
        );
      }

      const data = await response.json();

      setSelected(data);

      /*
       * Refresh metrics/logs after recovery so the dashboard
       * immediately reflects the latest result.
       */
      await loadDashboard();

    } catch (err) {
      console.error("Analysis error:", err);

      setError(
        err.message ||
          "Unable to analyze transaction."
      );
    } finally {
      setAnalyzing(false);
    }
  };

  // =========================================================
  // INITIAL LOAD
  // =========================================================

  useEffect(() => {
    loadDashboard();
  }, []);

  // =========================================================
  // LOADING SCREEN
  // =========================================================

  if (loading && !dashboard) {
    return (
      <div className="loading-screen">
        Loading RecoverAI...
      </div>
    );
  }

  // =========================================================
  // MAIN UI
  // =========================================================

  return (
    <div className="app">

      {/* ================================================= */}
      {/* SIDEBAR */}
      {/* ================================================= */}

      <aside className="sidebar">

        {/* LOGO */}

        <div className="logo">

          <div className="logo-icon">
            R
          </div>

          <div>
            <h1>
              RecoverAI
            </h1>

            <span>
              Revenue Recovery Agent
            </span>
          </div>

        </div>


        {/* NAVIGATION */}

        <nav>

          {navItems.map((item) => (
            <div
              key={item.id}
              className={
                `nav-item ${view === item.id ? "active" : ""}`
              }
              onClick={() => setView(item.id)}
              style={{ cursor: "pointer" }}
            >
              <span>{item.icon}</span>
              {item.label}
            </div>
          ))}

        </nav>


        {/* AGENT STATUS */}

        <div className="sidebar-bottom">

          <div className="agent-status">

            <span className="status-dot"></span>

            <div>

              <strong>
                Agent Online
              </strong>

              <small>
                Autonomous recovery active
              </small>

            </div>

          </div>

        </div>

      </aside>


      {/* ================================================= */}
      {/* MAIN */}
      {/* ================================================= */}

      <main className="main">

        {/* ================================================= */}
        {/* HEADER */}
        {/* ================================================= */}

        <header className="header">

          <div>

            <h2>
              {pageTitles[view].heading}
            </h2>

            <p>
              {pageTitles[view].subtext}
            </p>

          </div>


          <button
            className="refresh-btn"
            onClick={loadDashboard}
            disabled={loading}
          >
            {loading ? "Refreshing..." : "↻ Refresh"}
          </button>

        </header>


        {/* ================================================= */}
        {/* ERROR */}
        {/* ================================================= */}

        {error && (

          <div
            style={{
              marginBottom: "20px",
              padding: "14px 16px",
              borderRadius: "9px",
              background: "#fef2f2",
              border: "1px solid #fecaca",
              color: "#b91c1c",
              fontSize: "12px",
              fontWeight: "700",
            }}
          >
            {error}
          </div>

        )}


        {/* ================================================= */}
        {/* KPI CARDS (Overview only) */}
        {/* ================================================= */}

        {view === "overview" && (
        <section className="kpi-grid">

          {/* REVENUE AT RISK */}

          <div className="kpi-card">

            <div className="kpi-label">
              Revenue at Risk
            </div>

            <div className="kpi-value">

              {formatCurrency(
                dashboard?.total_revenue_at_risk
              )}

            </div>

            <div className="kpi-description">
              Failed payment exposure
            </div>

          </div>


          {/* ERV */}

          <div className="kpi-card">

            <div className="kpi-label">
              Expected Recovery Value
            </div>

            <div className="kpi-value purple">

              {formatCurrency(
                dashboard?.expected_recovery_value
              )}

            </div>

            <div className="kpi-description">
              AI-estimated recoverable revenue
            </div>

          </div>


          {/* RECOVERED */}

          <div className="kpi-card">

            <div className="kpi-label">
              Amount Recovered
            </div>

            <div className="kpi-value green">

              {formatCurrency(
                dashboard?.total_amount_recovered
              )}

            </div>

            <div className="kpi-description">
              Successfully recovered
            </div>

          </div>


          {/* RECOVERY RATE */}

          <div className="kpi-card">

            <div className="kpi-label">
              Recovery Rate
            </div>

            <div className="kpi-value">

              {dashboard?.recovery_rate || 0}%

            </div>

            <div className="kpi-description">
              Transaction recovery rate
            </div>

          </div>

        </section>
        )}


        {/* ================================================= */}
        {/* SECONDARY METRICS (Overview only) */}
        {/* ================================================= */}

        {view === "overview" && (
        <section className="secondary-grid">

          {/* PENDING */}

          <div className="metric-card">

            <span className="metric-icon pending">
              ◷
            </span>

            <div>

              <small>
                Pending
              </small>

              <strong>

                {formatCurrency(
                  dashboard?.pending_amount
                )}

              </strong>

            </div>

          </div>


          {/* ESCALATED */}

          <div className="metric-card">

            <span className="metric-icon danger">
              !
            </span>

            <div>

              <small>
                Escalated
              </small>

              <strong>

                {formatCurrency(
                  dashboard?.escalated_amount
                )}

              </strong>

            </div>

          </div>


          {/* TOTAL */}

          <div className="metric-card">

            <span className="metric-icon">
              #
            </span>

            <div>

              <small>
                Total Transactions
              </small>

              <strong>

                {dashboard?.total_transactions || 0}

              </strong>

            </div>

          </div>


          {/* FAILED */}

          <div className="metric-card">

            <span className="metric-icon">
              ₹
            </span>

            <div>

              <small>
                Failed Amount
              </small>

              <strong>

                {formatCurrency(
                  dashboard?.failed_amount
                )}

              </strong>

            </div>

          </div>

        </section>
        )}


        {/* ================================================= */}
        {/* TRANSACTIONS TABLE */}
        {/* Shown on Overview, Transactions, and Recovery Agent  */}
        {/* pages — same underlying data, different framing.     */}
        {/* ================================================= */}

        {(view === "overview" || view === "transactions" || view === "agent") && (
        <section className="panel">

          {/* PANEL HEADER */}

          <div className="panel-header">

            <div>

              <h3>
                {view === "agent"
                  ? "Run Recovery Agent"
                  : "Recovery Activity"}
              </h3>

              <p>
                {view === "agent"
                  ? "Click Analyze to run the agent on a transaction — detect, decide, execute, and log the result."
                  : "Transactions processed by RecoverAI"}
              </p>

            </div>


            <span className="transaction-count">

              {transactions.length}
              {" "}
              transactions

            </span>

          </div>


          {/* TABLE */}

          <div className="table-container">

            <table>

              <thead>

                <tr>

                  <th>
                    Transaction
                  </th>

                  <th>
                    Amount
                  </th>

                  <th>
                    Action
                  </th>

                  <th>
                    Recovery Probability
                  </th>

                  <th>
                    Expected Recovery
                  </th>

                  <th>
                    Status
                  </th>

                  <th>
                  </th>

                </tr>

              </thead>


              <tbody>

                {transactions.length === 0 ? (

                  <tr>

                    <td
                      colSpan="7"
                      style={{
                        textAlign: "center",
                        padding: "35px",
                        color: "#9ca3af",
                      }}
                    >
                      No recovery activity found.
                    </td>

                  </tr>

                ) : (

                  transactions.map(
                    (
                      transaction,
                      index
                    ) => {

                      const transactionId =
                        transaction.transaction_id ||
                        transaction.id ||
                        `RECOVERY-${index + 1}`;

                      const probability =
                        Number(
                          transaction.recovery_probability
                        ) || 0;

                      const amount =
                        Number(
                          transaction.amount ||
                          transaction.payment_amount ||
                          transaction.amount_recovered ||
                          0
                        );

                      const expectedRecovery =
                        Number(
                          transaction.expected_recovery_value
                        ) || 0;

                      const action =
                        transaction.action ||
                        transaction.intervention?.action ||
                        "—";

                      const status =
                        transaction.final_status ||
                        transaction.verification_status ||
                        transaction.status ||
                        "UNKNOWN";

                      return (

                        <tr
                          key={
                            `${transactionId}-${index}`
                          }
                        >

                          {/* TRANSACTION */}

                          <td>

                            <strong>
                              {transactionId}
                            </strong>

                          </td>


                          {/* AMOUNT */}

                          <td>

                            <strong>
                              {formatCurrency(amount)}
                            </strong>

                          </td>


                          {/* ACTION */}

                          <td>

                            <span className="action">
                              {action}
                            </span>

                          </td>


                          {/* PROBABILITY */}

                          <td>

                            <div className="probability">

                              <div className="probability-bar">

                                <div
                                  className="probability-fill"
                                  style={{
                                    width:
                                      `${Math.min(
                                        Math.max(
                                          probability,
                                          0
                                        ),
                                        100
                                      )}%`,
                                  }}
                                />

                              </div>

                              <span>
                                {probability}%
                              </span>

                            </div>

                          </td>


                          {/* ERV */}

                          <td>

                            <strong>
                              {formatCurrency(
                                expectedRecovery
                              )}
                            </strong>

                          </td>


                          {/* STATUS */}

                          <td>

                            <span
                              className={
                                `status ${
                                  statusClass(status)
                                }`
                              }
                            >
                              {status}
                            </span>

                          </td>


                          {/* ANALYZE */}

                          <td>

                            <button
                              className="recover-btn"
                              onClick={() =>
                                analyzeTransaction(
                                  transactionId
                                )
                              }
                              disabled={analyzing}
                            >
                              {analyzing
                                ? "..."
                                : "Analyze"}
                            </button>

                          </td>

                        </tr>

                      );

                    }
                  )

                )}

              </tbody>

            </table>

          </div>

        </section>
        )}


        {/* ================================================= */}
        {/* AUDIT LOGS — full, non-deduped decision history */}
        {/* ================================================= */}

        {view === "logs" && (
        <section className="panel">

          <div className="panel-header">

            <div>
              <h3>Audit Trail</h3>
              <p>Every recovery decision ever logged, oldest actions included</p>
            </div>

            <span className="transaction-count">
              {allLogs.length} log entries
            </span>

          </div>

          <div className="table-container">

            <table>

              <thead>
                <tr>
                  <th>Transaction</th>
                  <th>Action</th>
                  <th>Recovery Probability</th>
                  <th>Policy Decision</th>
                  <th>Final Status</th>
                  <th>Amount Recovered</th>
                  <th>Timestamp</th>
                </tr>
              </thead>

              <tbody>

                {allLogs.length === 0 ? (
                  <tr>
                    <td
                      colSpan="7"
                      style={{
                        textAlign: "center",
                        padding: "35px",
                        color: "#9ca3af",
                      }}
                    >
                      No audit log entries found.
                    </td>
                  </tr>
                ) : (
                  allLogs.map((log, index) => (
                    <tr key={`${log.transaction_id}-${index}`}>

                      <td><strong>{log.transaction_id}</strong></td>

                      <td>
                        <span className="action">
                          {log.action || "—"}
                        </span>
                      </td>

                      <td>
                        {log.recovery_probability ?? 0}%
                      </td>

                      <td>
                        {log.policy_decision || "—"}
                      </td>

                      <td>
                        <span
                          className={
                            `status ${statusClass(log.final_status)}`
                          }
                        >
                          {log.final_status || "UNKNOWN"}
                        </span>
                      </td>

                      <td>
                        {formatCurrency(log.amount_recovered)}
                      </td>

                      <td>
                        {log.timestamp
                          ? new Date(log.timestamp).toLocaleString()
                          : "—"}
                      </td>

                    </tr>
                  ))
                )}

              </tbody>

            </table>

          </div>

        </section>
        )}


        {/* ================================================= */}
        {/* SELECTED TRANSACTION */}
        {/* ================================================= */}

        {selected && (

          <section className="panel details-panel">

            {/* HEADER */}

            <div className="panel-header">

              <div>

                <h3>
                  Recovery Decision
                </h3>

                <p>
                  {selected.transaction_id}
                </p>

              </div>


              <button
                className="close-btn"
                onClick={() =>
                  setSelected(null)
                }
              >
                ×
              </button>

            </div>


            {/* ================================================= */}
            {/* DECISION CARDS */}
            {/* ================================================= */}

            <div className="decision-grid">

              {/* PROBABILITY */}

              <div className="decision-card">

                <small>
                  Recovery Probability
                </small>

                <strong>

                  {
                    selected.recovery_probability ??
                    0
                  }%

                </strong>

              </div>


              {/* ERV */}

              <div className="decision-card">

                <small>
                  Expected Recovery Value
                </small>

                <strong>

                  {formatCurrency(
                    selected.expected_recovery_value
                  )}

                </strong>

              </div>


              {/* ACTION */}

              <div className="decision-card">

                <small>
                  AI Intervention
                </small>

                <strong>

                  {
                    selected.intervention?.action ||
                    selected.action ||
                    "—"
                  }

                </strong>

              </div>


              {/* POLICY */}

              <div className="decision-card">

                <small>
                  Policy Decision
                </small>

                <strong>

                  {
                    selected.policy?.decision ||
                    selected.policy_decision ||
                    "—"
                  }

                </strong>

              </div>

            </div>


            {/* ================================================= */}
            {/* TIMELINE */}
            {/* ================================================= */}

            <div className="timeline-section">

              <h4>
                Agent Decision Timeline
              </h4>


              <div className="timeline">

                {(
                  selected.state_history || []
                ).map(
                  (
                    state,
                    index
                  ) => (

                    <div
                      className="timeline-item"
                      key={index}
                    >

                      <div className="timeline-dot">
                        {index + 1}
                      </div>

                      <div>

                        <strong>
                          {state}
                        </strong>

                        {index <
                          (
                            selected.state_history?.length ||
                            0
                          ) - 1 && (

                          <span>
                            Decision completed
                          </span>

                        )}

                      </div>

                    </div>

                  )
                )}

              </div>

            </div>


            {/* ================================================= */}
            {/* AI REASONING */}
            {/* ================================================= */}

            <div className="reasoning-box">

              <div className="reasoning-title">
                AI Reasoning
              </div>

              <p>

                {
                  selected.ai_reasoning?.reasoning ||
                  selected.investigation?.investigation?.reason ||
                  selected.intervention?.reason ||
                  selected.policy?.reason ||
                  selected.message ||
                  "No reasoning available."
                }

              </p>

            </div>


            {/* ================================================= */}
            {/* EXECUTION */}
            {/* ================================================= */}

            {selected.execution && (

              <div className="reasoning-box">

                <div className="reasoning-title">
                  Execution Result
                </div>

                <p>

                  {
                    selected.execution.message ||
                    (
                      selected.execution.payment_recovered
                        ? "Payment successfully recovered."
                        : "Recovery action executed."
                    )
                  }

                </p>

              </div>

            )}


            {/* ================================================= */}
            {/* VERIFICATION */}
            {/* ================================================= */}

            {selected.verification && (

              <div className="reasoning-box">

                <div className="reasoning-title">
                  Verification
                </div>

                <p>

                  {
                    selected.verification.message ||
                    "Recovery result verified."
                  }

                </p>

              </div>

            )}


            {/* ================================================= */}
            {/* FINAL RESULT */}
            {/* ================================================= */}

            <div className="final-result">

              <span>
                Final Status
              </span>

              <strong
                className={
                  statusClass(
                    selected.final_status
                  )
                }
              >

                {
                  selected.final_status ||
                  "UNKNOWN"
                }

              </strong>

            </div>

          </section>

        )}

      </main>

    </div>
  );
}

export default App;

