import React, { useState, useRef, useEffect } from "react";

export default function App() {
  const [config, setConfig] = useState("");
  const [loading, setLoading] = useState(false);

  const [decision, setDecision] = useState(null);
  const [boundary, setBoundary] = useState(null);
  const [patterns, setPatterns] = useState("");
  const [rationale, setRationale] = useState("");
  const [clause, setClause] = useState("");
  const [drift, setDrift] = useState(0);
  const [intent, setIntent] = useState(0);
  const [perimeterIndex, setPerimeterIndex] = useState(1);

  const [forensics, setForensics] = useState([]);
  const [replay, setReplay] = useState(null);

  // Optional: unauthorized change narrative + recovery
  const [unauthorizedStory, setUnauthorizedStory] = useState(null);
  const [recovery, setRecovery] = useState(null);

  const logRef = useRef(null);

  // Auto-scroll precedent ledger to top on new event
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = 0;
    }
  }, [forensics]);

  // Inject perimeter pulse keyframes once
  useEffect(() => {
    const styleSheet = document.styleSheets[0];
    if (!styleSheet) return;
    const exists = Array.from(styleSheet.cssRules || []).some(
      (r) => r.name === "perimeterPulse"
    );
    if (!exists) {
      styleSheet.insertRule(
        `
        @keyframes perimeterPulse {
          0% { transform: scale(1); opacity: 0.8; }
          50% { transform: scale(1.06); opacity: 1; }
          100% { transform: scale(1); opacity: 0.8; }
        }
      `,
        styleSheet.cssRules.length
      );
    }
  }, []);

  const submitConfig = async () => {
    if (!config.trim()) return;

    setLoading(true);
    setReplay(null);
    setUnauthorizedStory(null);
    setRecovery(null);

    try {
      const res = await fetch(
        "https://ironhalo-engine.onrender.com/config-strike",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ config_text: config }),
        }
      );

      const data = await res.json();

      // Core fields (current backend)
      setDecision(data.decision);
      setBoundary(data.boundary_state);
      setPatterns(
        typeof data.pattern_detected === "string"
          ? data.pattern_detected
          : JSON.stringify(data.pattern_detected, null, 2)
      );
      setRationale(data.rationale);
      setClause(
        data.clause_id && data.clause_title
          ? `${data.clause_id}: ${data.clause_title}`
          : data.clause_title || data.clause_id || "—"
      );
      setDrift(data.drift_value ?? 0);
      setIntent(data.intent_strength ?? 0);
      setPerimeterIndex(data.perimeter_index ?? 1);

      // Optional: unauthorized change narrative + recovery (future backend)
      if (Array.isArray(data.story)) {
        setUnauthorizedStory(data.story);
      }
      if (data.recovery) {
        setRecovery(data.recovery);
      }

      setForensics((prev) => [
        { ...data, timestamp: data.timestamp || new Date().toISOString() },
        ...prev,
      ]);
    } catch (err) {
      console.error("IronHalo error:", err);
    }

    setLoading(false);
  };

  const replayEvent = (e) => {
    setReplay(e);
    setDecision(e.decision);
    setBoundary(e.boundary_state);
    setPatterns(
      typeof e.pattern_detected === "string"
        ? e.pattern_detected
        : JSON.stringify(e.pattern_detected, null, 2)
    );
    setRationale(e.rationale);
    setClause(
      e.clause_id && e.clause_title
        ? `${e.clause_id}: ${e.clause_title}`
        : e.clause_title || e.clause_id || "—"
    );
    setDrift(e.drift_value ?? 0);
    setIntent(e.intent_strength ?? 0);
    setPerimeterIndex(e.perimeter_index ?? 1);

    // If past events ever include story/recovery, replay them too
    if (Array.isArray(e.story)) {
      setUnauthorizedStory(e.story);
    } else {
      setUnauthorizedStory(null);
    }
    if (e.recovery) {
      setRecovery(e.recovery);
    } else {
      setRecovery(null);
    }
  };

  const resetDemo = () => {
    setConfig("");
    setDecision(null);
    setBoundary(null);
    setPatterns("");
    setRationale("");
    setClause("");
    setDrift(0);
    setIntent(0);
    setPerimeterIndex(1);
    setForensics([]);
    setReplay(null);
    setUnauthorizedStory(null);
    setRecovery(null);
  };

  const rulingTone = decision
    ? decision === "ALLOW"
      ? "#2ed573"
      : decision === "DENY"
      ? "#ff4757"
      : "#ffc312"
    : "#ffffff";

  return (
    <div style={styles.page}>
      <h1 style={styles.title}>IronHalo — Constitutional Intelligence Console</h1>

      {/* Input / Controls */}
      <div style={styles.card}>
        <h2 style={styles.sectionLabel}>Submit Artifact for Constitutional Review</h2>
        <p style={styles.muted}>
          Paste <b>any cloud config</b> (Terraform, YAML, JSON, IAM, NSG, firewall, Kubernetes, policy docs).
          Try to <b>trick the perimeter</b> with misconfigurations or override attempts.
        </p>
        <textarea
          style={styles.textarea}
          value={config}
          onChange={(e) => setConfig(e.target.value)}
          placeholder={`Example: 
- Public S3 bucket
- Azure NSG 0.0.0.0/0
- GCP open firewall
- Kubernetes privilege escalation
- Any YAML/JSON you think can slip past governance...`}
        />
        <div style={styles.buttonRow}>
          <button style={styles.button} onClick={submitConfig} disabled={loading}>
            {loading ? "Analyzing…" : "Submit to IronHalo"}
          </button>
          <button style={styles.resetButton} onClick={resetDemo}>
            Reset Demo
          </button>
        </div>
      </div>

      {/* Main console layout */}
      <div style={styles.mainRow}>
        {/* Precedent Ledger */}
        <div style={{ ...styles.card, ...styles.ledgerCard }} ref={logRef}>
          <h2 style={styles.sectionLabel}>Precedent Ledger</h2>
          {forensics.length === 0 && (
            <p style={styles.muted}>
              No rulings yet. Submit an artifact to establish precedent.
            </p>
          )}
          {forensics.map((e, i) => (
            <div key={i} style={styles.logItem} onClick={() => replayEvent(e)}>
              <span
                style={{
                  color:
                    e.decision === "DENY"
                      ? "#ff6b81"
                      : e.decision === "ALLOW"
                      ? "#2ed573"
                      : "#ffc312",
                }}
              >
                [{e.decision}]
              </span>{" "}
              {e.pattern_detected}
              <div style={styles.timestamp}>{e.timestamp}</div>
            </div>
          ))}
        </div>

        {/* Ruling + Reasoning */}
        <div style={styles.centerColumn}>
          <div style={styles.card}>
            <h2 style={styles.sectionLabel}>Ruling</h2>
            {!decision && <p style={styles.muted}>Awaiting submission.</p>}
            {decision && (
              <>
                <div
                  style={{
                    ...styles.rulingLine,
                    borderColor: rulingTone,
                    color: rulingTone,
                  }}
                >
                  RULING: {decision}
                </div>
                <div style={styles.rulingSub}>
                  Constitutional Basis: {clause}
                </div>
                <div style={styles.rulingSub}>
                  Perimeter Response: <b>{boundary}</b>
                </div>
                <div style={styles.rulingSub}>
                  Pattern Detected: <b>{patterns}</b>
                </div>
              </>
            )}
          </div>

          {decision && (
            <div style={styles.card}>
              <h2 style={styles.sectionLabel}>Constitutional Reasoning</h2>
              <pre style={styles.pre}>{rationale}</pre>
            </div>
          )}

          {/* Optional: Unauthorized Change Narrative */}
          {decision && unauthorizedStory && (
            <div style={styles.card}>
              <h2 style={styles.sectionLabel}>Unauthorized Change Narrative</h2>
              <pre style={styles.pre}>{unauthorizedStory.join("\n")}</pre>
            </div>
          )}

          {/* Drift + Intent */}
          {decision && (
            <div style={styles.row}>
              <div style={styles.card}>
                <h2 style={styles.sectionLabel}>Drift</h2>
                <div style={styles.barOuter}>
                  <div style={styles.barFill(drift)} />
                </div>
                <p style={styles.metricText}>{Math.round(drift * 100)} / 100</p>
              </div>

              <div style={styles.card}>
                <h2 style={styles.sectionLabel}>Intent Strength</h2>
                <div style={styles.barOuter}>
                  <div style={styles.barFill(intent)} />
                </div>
                <p style={styles.metricText}>{Math.round(intent * 100)} / 100</p>
              </div>
            </div>
          )}

          {/* Optional: Recovery Action */}
          {decision && recovery && (
            <div style={styles.card}>
              <h2 style={styles.sectionLabel}>Recovery Action</h2>
              <p style={styles.muted}>
                The system executed the following stabilization step:
              </p>
              <pre style={styles.pre}>
                {typeof recovery === "string"
                  ? recovery
                  : JSON.stringify(recovery, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Perimeter + Replay */}
        <div style={styles.sideColumn}>
          <div style={styles.card}>
            <h2 style={styles.sectionLabel}>Perimeter Pulse</h2>
            <div style={styles.perimeter(perimeterIndex, decision)} />
            {decision && (
              <p style={styles.perimeterLabel}>
                Active Perimeter Index: <b>{perimeterIndex}</b>
              </p>
            )}
          </div>

          <div style={styles.card}>
            <h2 style={styles.sectionLabel}>Replay Capsule</h2>
            {!replay && (
              <p style={styles.muted}>
                Select a precedent to replay its constitutional capsule.
              </p>
            )}
            {replay && (
              <pre style={styles.pre}>{JSON.stringify(replay, null, 2)}</pre>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    padding: 20,
    fontFamily: "system-ui",
    background: "#050711",
    color: "white",
    minHeight: "100vh",
  },
  title: {
    textAlign: "center",
    marginBottom: 20,
    letterSpacing: 1,
  },
  sectionLabel: {
    fontSize: "0.9rem",
    textTransform: "uppercase",
    letterSpacing: 1.5,
    color: "#9aa0c5",
    marginBottom: 8,
  },
  card: {
    background: "#0b0f1f",
    padding: 16,
    borderRadius: 12,
    border: "1px solid #1b2140",
    marginBottom: 20,
  },
  mainRow: {
    display: "flex",
    gap: 20,
    alignItems: "flex-start",
    flexWrap: "wrap",
  },
  centerColumn: {
    flex: 2,
    minWidth: 320,
  },
  sideColumn: {
    flex: 1,
    minWidth: 260,
  },
  ledgerCard: {
    flex: 1,
    minWidth: 260,
    maxHeight: 480,
    overflow: "auto",
  },
  row: {
    display: "flex",
    gap: 20,
    flexWrap: "wrap",
  },
  textarea: {
    width: "100%",
    height: 160,
    background: "#050814",
    color: "white",
    borderRadius: 8,
    border: "1px solid #1b2140",
    padding: 10,
    fontFamily: "monospace",
    fontSize: "0.9rem",
  },
  buttonRow: {
    marginTop: 10,
    display: "flex",
    gap: 10,
  },
  button: {
    padding: "10px 20px",
    background: "#4b6bff",
    border: "none",
    borderRadius: 8,
    color: "white",
    cursor: "pointer",
    fontSize: "0.9rem",
  },
  resetButton: {
    padding: "10px 20px",
    background: "#2f3542",
    border: "none",
    borderRadius: 8,
    color: "white",
    cursor: "pointer",
    fontSize: "0.9rem",
  },
  pre: {
    background: "#050814",
    padding: 10,
    borderRadius: 8,
    border: "1px solid #1b2140",
    maxHeight: 200,
    overflow: "auto",
    fontSize: "0.8rem",
  },
  logItem: {
    padding: 8,
    borderBottom: "1px solid #1b2140",
    cursor: "pointer",
    fontSize: "0.8rem",
  },
  timestamp: {
    fontSize: "0.7rem",
    color: "#9aa0c5",
    marginTop: 2,
  },
  muted: {
    fontSize: "0.85rem",
    color: "#7f85aa",
  },
  rulingLine: {
    padding: "10px 14px",
    borderRadius: 8,
    border: "1px solid",
    display: "inline-block",
    fontWeight: 600,
    marginBottom: 6,
  },
  rulingSub: {
    fontSize: "0.85rem",
    color: "#d0d4ff",
    marginTop: 2,
  },
  metricText: {
    fontSize: "0.85rem",
    marginTop: 6,
  },
  barOuter: {
    width: "100%",
    height: 10,
    background: "#050814",
    borderRadius: 6,
    overflow: "hidden",
    border: "1px solid #1b2140",
  },
  barFill: (v) => ({
    width: `${Math.max(0, Math.min(1, v)) * 100}%`,
    height: "100%",
    background: "linear-gradient(90deg, #2ed573, #ffc312, #ff4757)",
    transition: "0.3s",
  }),
  perimeter: (index, decision) => {
    const baseColor =
      index === 0
        ? "rgba(255,71,87,0.4)"
        : index === 1
        ? "rgba(46,213,115,0.4)"
        : "rgba(255,195,18,0.4)";

    const duration =
      decision === "DENY" ? "1.1s" : decision === "ALLOW" ? "2.0s" : "1.5s";

    return {
      width: 130,
      height: 130,
      borderRadius: "50%",
      margin: "10px auto 4px",
      background: baseColor,
      boxShadow: `0 0 18px ${baseColor}`,
      animation: `perimeterPulse ${duration} infinite ease-in-out`,
    };
  },
  perimeterLabel: {
    fontSize: "0.8rem",
    textAlign: "center",
    color: "#d0d4ff",
  },
};
