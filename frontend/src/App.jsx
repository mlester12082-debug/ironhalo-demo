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

  const logRef = useRef(null);

  // Auto-scroll forensic log
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = 0;
    }
  }, [forensics]);

  const submitConfig = async () => {
    if (!config.trim()) return;

    setLoading(true);
    setReplay(null);

    try {
      const res = await fetch("https://ironhalo-engine.onrender.com/config-strike", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ config_text: config }),
      });

      const data = await res.json();

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
      setDrift(data.drift_value);
      setIntent(data.intent_strength);
      setPerimeterIndex(data.perimeter_index);

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
    setDrift(e.drift_value);
    setIntent(e.intent_strength);
    setPerimeterIndex(e.perimeter_index);
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
  };

  return (
    <div style={styles.page}>
      <h1 style={styles.title}>IronHalo — Constitutional Governance Demo</h1>

      <div style={styles.card}>
        <h2>Submit Config</h2>
        <textarea
          style={styles.textarea}
          value={config}
          onChange={(e) => setConfig(e.target.value)}
          placeholder="Paste any cloud config..."
        />
        <button style={styles.button} onClick={submitConfig} disabled={loading}>
          {loading ? "Analyzing…" : "Submit to IronHalo"}
        </button>
        <button style={styles.resetButton} onClick={resetDemo}>
          Reset Demo
        </button>
      </div>

      {decision && (
        <div style={styles.row}>
          <div style={styles.card}>
            <h2>Decision</h2>
            <div style={styles.decision(decision)}>{decision}</div>
            <p>{clause}</p>
          </div>

          <div style={styles.card}>
            <h2>Perimeter State</h2>
            <div style={styles.perimeter(perimeterIndex)} />
            <p>Boundary: <b>{boundary}</b></p>
          </div>
        </div>
      )}

      {decision && (
        <div style={styles.row}>
          <div style={styles.card}>
            <h2>Drift</h2>
            <div style={styles.barOuter}>
              <div style={styles.barFill(drift)} />
            </div>
            <p>{Math.round(drift * 100)} / 100</p>
          </div>

          <div style={styles.card}>
            <h2>Intent Strength</h2>
            <div style={styles.barOuter}>
              <div style={styles.barFill(intent)} />
            </div>
            <p>{Math.round(intent * 100)} / 100</p>
          </div>
        </div>
      )}

      {decision && (
        <div style={styles.row}>
          <div style={styles.card}>
            <h2>Patterns</h2>
            <pre style={styles.pre}>{patterns}</pre>
          </div>

          <div style={styles.card}>
            <h2>Constitutional Reasoning</h2>
            <pre style={styles.pre}>{rationale}</pre>
          </div>
        </div>
      )}

      <div style={styles.row}>
        <div style={styles.card} style={{ ...styles.card, maxHeight: 300, overflow: "auto" }} ref={logRef}>
          <h2>Forensic Log</h2>
          {forensics.map((e, i) => (
            <div key={i} style={styles.logItem} onClick={() => replayEvent(e)}>
              <b>{e.decision}</b> — {e.pattern_detected}
              <div style={styles.timestamp}>{e.timestamp}</div>
            </div>
          ))}
        </div>

        <div style={styles.card}>
          <h2>Replay Capsule</h2>
          {!replay && <p>Select an event to replay.</p>}
          {replay && (
            <pre style={styles.pre}>{JSON.stringify(replay, null, 2)}</pre>
          )}
        </div>
      </div>
    </div>
  );
}

const perimeterPulse = {
  animation: "pulse 1.6s infinite ease-in-out",
};

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
  },
  card: {
    background: "#0b0f1f",
    padding: 16,
    borderRadius: 12,
    border: "1px solid #1b2140",
    flex: 1,
    marginBottom: 20,
  },
  row: {
    display: "flex",
    gap: 20,
    flexWrap: "wrap",
  },
  textarea: {
    width: "100%",
    height: 150,
    background: "#050814",
    color: "white",
    borderRadius: 8,
    border: "1px solid #1b2140",
    padding: 10,
    fontFamily: "monospace",
  },
  button: {
    marginTop: 10,
    padding: "10px 20px",
    background: "#4b6bff",
    border: "none",
    borderRadius: 8,
    color: "white",
    cursor: "pointer",
  },
  resetButton: {
    marginTop: 10,
    marginLeft: 10,
    padding: "10px 20px",
    background: "#ff4757",
    border: "none",
    borderRadius: 8,
    color: "white",
    cursor: "pointer",
  },
  decision: (d) => ({
    padding: "8px 12px",
    borderRadius: 8,
    display: "inline-block",
    background:
      d === "ALLOW"
        ? "rgba(46,213,115,0.2)"
        : d === "DENY"
        ? "rgba(255,71,87,0.2)"
        : "rgba(255,195,18,0.2)",
    border:
      d === "ALLOW"
        ? "1px solid #2ed573"
        : d === "DENY"
        ? "1px solid #ff4757"
        : "1px solid #ffc312",
  }),
  perimeter: (index) => ({
    width: 120,
    height: 120,
    borderRadius: "50%",
    margin: "0 auto",
    background:
      index === 0
        ? "rgba(255,71,87,0.4)"
        : index === 1
        ? "rgba(46,213,115,0.4)"
        : "rgba(255,195,18,0.4)",
    transition: "0.4s",
    ...perimeterPulse,
  }),
  barOuter: {
    width: "100%",
    height: 10,
    background: "#050814",
    borderRadius: 6,
    overflow: "hidden",
    border: "1px solid #1b2140",
  },
  barFill: (v) => ({
    width: `${v * 100}%`,
    height: "100%",
    background: "linear-gradient(90deg, #2ed573, #ffc312, #ff4757)",
    transition: "0.3s",
  }),
  pre: {
    background: "#050814",
    padding: 10,
    borderRadius: 8,
    border: "1px solid #1b2140",
    maxHeight: 200,
    overflow: "auto",
  },
  logItem: {
    padding: 8,
    borderBottom: "1px solid #1b2140",
    cursor: "pointer",
  },
  timestamp: {
    fontSize: "0.75rem",
    color: "#9aa0c5",
  },
};

// Add CSS keyframes for perimeter pulse
const styleSheet = document.styleSheets[0];
styleSheet.insertRule(`
@keyframes pulse {
  0% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.08); opacity: 1; }
  100% { transform: scale(1); opacity: 0.8; }
}
`, styleSheet.cssRules.length);
