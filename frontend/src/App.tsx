import { useState } from "react";
import ClaimForm, { ClaimPayload } from "./components/ClaimForm";
import Scene3D from "./components/Scene3D";

type LogTone = "info" | "success" | "error";

type LogEntry = {
  id: number;
  message: string;
  tone: LogTone;
};

type AgentEvidence = {
  source?: string;
  snippet?: string;
  page?: number;
};

type AgentFinding = {
  agent: string;
  status: string;
  summary: string;
  confidence?: number;
  evidence?: AgentEvidence[];
};

type AssessmentResult = {
  recommendation?: string;
  confidence?: number;
  answer?: string;
  human_review_required?: boolean;
  review_reasons?: string[];
  agent_findings?: AgentFinding[];
};

const publicHighlights = [
  {
    title: "Fast filing",
    text: "Submit farmer details and loss information in minutes from any phone or desktop.",
  },
  {
    title: "Trusted review",
    text: "The system checks policy rules, weather evidence, and historical patterns before giving a recommendation.",
  },
  {
    title: "Secure documents",
    text: "Attach images and PDFs so the claim can be assessed with supporting evidence.",
  },
];

const developerItems = [
  { label: "Policies", id: "developer-policies", text: "Policy lookup and coverage rules" },
  { label: "Weather", id: "developer-weather", text: "Weather anomaly and risk review" },
  { label: "Historical", id: "developer-historical", text: "Past claim comparisons" },
  { label: "Evidence", id: "developer-evidence", text: "Documents and citation review" },
  { label: "Reasoning", id: "developer-reasoning", text: "Decision path and recommendation" },
  { label: "Compliance", id: "developer-compliance", text: "Review checkpoints and audit trail" },
];

const initialLogs: LogEntry[] = [
  { id: 1, message: "System ready for public claim intake.", tone: "info" },
];

export default function App() {
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [submittedClaim, setSubmittedClaim] = useState<ClaimPayload | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>(initialLogs);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  const appendLog = (message: string, tone: LogTone = "info") => {
    setLogs((current) => [{ id: Date.now(), message, tone }, ...current].slice(0, 8));
  };

  const handleResult = (data: unknown, claim: ClaimPayload) => {
    const assessment = data as AssessmentResult | null;
    setResult(assessment);
    setSubmittedClaim(claim);
    setExpandedAgent(null);
    if (assessment) {
      const recommendation = assessment.recommendation ?? "Review pending";
      appendLog(`Assessment complete: ${recommendation}`, "success");
    } else {
      appendLog("The claim could not be submitted right now.", "error");
    }
  };

  const toggleAgent = (agentName: string) => {
    setExpandedAgent((current) => (current === agentName ? null : agentName));
  };

  return (
    <div className="app-shell">
      <Scene3D result={result} />
      <div className="noise-layer" />

      <nav className="top-nav" aria-label="Primary">
        <a className="brand" href="#home" aria-label="Agri ClaimGuard AI home">
          <span className="brand-mark">AG</span>
          <span>Agri ClaimGuard AI</span>
        </a>
        <div className="nav-links" aria-label="Sections">
          <a href="#home">Home</a>
          <a href="#claims">File claim</a>
          <a href="#how-it-works">How it works</a>
          <a href="#support">Support</a>
          <div className="developer-menu">
            <button className="developer-toggle" type="button">Developer</button>
            <div className="developer-dropdown">
              {developerItems.map((item) => (
                <a href={`#${item.id}`} key={item.id}>
                  <strong>{item.label}</strong>
                  <span>{item.text}</span>
                </a>
              ))}
            </div>
          </div>
        </div>
        <a className="launch-button" href="#claims">Start claim</a>
      </nav>

      <main className="dashboard-grid" id="home">
        <section className="workspace">
          <section className="hero-panel glass-panel">
            <div className="hero-copy">
              <span className="eyebrow">Public claim intake</span>
              <h1>File a crop insurance claim with confidence.</h1>
              <p>
                Farmers can submit claim details, evidence, and supporting documents in one place.
                The system reviews policy coverage, weather conditions, and historical patterns to produce a clear recommendation.
              </p>
            </div>
            <div className="hero-stats">
              <span>Assessment</span>
              <strong>{result ? "Ready" : "Fast"}</strong>
              <div className="confidence-ring" aria-hidden="true" />
            </div>
          </section>

          <section className="info-strip glass-panel" id="how-it-works">
            <div className="section-heading compact">
              <div>
                <span className="eyebrow">How it works</span>
                <h2>Simple steps for a smoother claim experience</h2>
              </div>
            </div>
            <div className="highlight-grid">
              {publicHighlights.map((item) => (
                <article className="highlight-card" key={item.title}>
                  <h3>{item.title}</h3>
                  <p>{item.text}</p>
                </article>
              ))}
            </div>
          </section>

          <section className="content-grid">
            <ClaimForm onResult={handleResult} onLog={appendLog} />

            <article className="public-info glass-panel" id="support">
              <div className="section-heading compact">
                <h2>Submission activity</h2>
                <span className="status-pill info">Live</span>
              </div>
              <div className="activity-card">
                <p><strong>Claim:</strong> {submittedClaim?.query ?? "No claim submitted yet."}</p>

                {result ? (
                  <div className="result-shell">
                    <div className={`result-badge ${String(result.recommendation ?? "review-pending").toLowerCase().replace(/\s+/g, "-")}`}>
                      {result.recommendation ?? "Review pending"}
                    </div>
                    <p className="result-answer">{result.answer ?? "The claim assessment response is being prepared."}</p>
                    <div className="result-meta">
                      <span>Confidence: {Math.round((result.confidence ?? 0) * 100)}%</span>
                      <span>{result.human_review_required ? "Human review required" : "Auto review complete"}</span>
                    </div>
                    {result.review_reasons?.length ? (
                      <ul className="reason-list">
                        {result.review_reasons.map((reason) => (
                          <li key={reason}>{reason}</li>
                        ))}
                      </ul>
                    ) : null}
                    <div className="agent-finding-list">
                      {result.agent_findings?.map((finding, index) => (
                        <div className="agent-finding" key={`${finding.agent}-${index}`}>
                          <div className="agent-finding-header">
                            <strong>{finding.agent}</strong>
                            <div className="agent-finding-actions">
                              <span className={`agent-status ${finding.status}`}>{finding.status.replace(/_/g, " ")}</span>
                              {finding.status === "complete" ? (
                                <button className="view-agent-button" onClick={() => toggleAgent(finding.agent)} type="button">
                                  {expandedAgent === finding.agent ? "Hide" : "View"}
                                </button>
                              ) : null}
                            </div>
                          </div>
                          <p>{finding.summary}</p>
                          {expandedAgent === finding.agent ? (
                            <div className="agent-detail-panel">
                              <div className="agent-detail-meta">
                                <span>Confidence: {Math.round((finding.confidence ?? 0) * 100)}%</span>
                                <span>Status: {finding.status.replace(/_/g, " ")}</span>
                              </div>
                              {finding.evidence?.length ? (
                                <div className="agent-detail-body">
                                  <strong>Supporting evidence</strong>
                                  <ul>
                                    {finding.evidence.map((item, evidenceIndex) => (
                                      <li key={`${finding.agent}-evidence-${evidenceIndex}`}>
                                        <span>{item.source ?? "Evidence"}</span>
                                        {item.snippet ? <p>{item.snippet}</p> : null}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              ) : (
                                <p className="agent-detail-body">No additional evidence was attached for this agent response.</p>
                              )}
                            </div>
                          ) : null}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="result-placeholder">Once a claim is submitted, the multi-agent assessment will appear here with eligibility and policy findings.</p>
                )}

                <div className="log-list" aria-live="polite">
                  {logs.map((entry) => (
                    <div className={`log-item ${entry.tone}`} key={entry.id}>
                      <span className={`status-dot ${entry.tone}`} />
                      <span>{entry.message}</span>
                    </div>
                  ))}
                </div>
              </div>
            </article>
          </section>

          <section className="developer-panel glass-panel" id="developer">
            <div className="section-heading compact">
              <div>
                <span className="eyebrow">Developer workspace</span>
                <h2>Internal review tools</h2>
              </div>
            </div>
            <div className="developer-grid">
              {developerItems.map((item) => (
                <a className="developer-card" href={`#${item.id}`} key={item.id}>
                  <strong>{item.label}</strong>
                  <span>{item.text}</span>
                </a>
              ))}
            </div>
          </section>
        </section>
      </main>

      <div className="toast glass-panel" role="status">
        <span className="status-dot completed" />
        Claim portal ready for public use
      </div>
    </div>
  );
}
