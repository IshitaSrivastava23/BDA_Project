import { useEffect, useMemo, useState } from "react";
import { Activity, BarChart3, BookOpen, Database, Factory, Gauge, Info, Menu, RefreshCw, X } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getJson } from "./api";

type Page = "overview" | "explorer" | "analytics" | "processing" | "insights" | "methodology" | "about";
type MetricValue = number | null;
type Summary = { data_available: boolean; message?: string; metrics: Record<string, MetricValue>; insights: Insight[] };
type Insight = { title: string; metric: number; value: string; explanation: string };
type Analytics = {
  data_available: boolean;
  options?: { age_groups?: string[]; admission_types?: string[]; severities?: string[] };
  length_of_stay?: { average: number | null; median: number | null; distribution: { bucket: string; count: number }[] };
  age: Record<string, unknown>[];
  admission: Record<string, unknown>[];
  severity: Record<string, unknown>[];
  hospitals: Record<string, unknown>[];
};
type Metadata = { data_available: boolean; source: string; message?: string; rows?: number; column_count?: number; columns: { name: string; dtype: string; missing: number; unique_values: number }[] };
type Sample = { data_available: boolean; total: number; rows: Record<string, unknown>[] };

const nav = [
  ["overview", "Overview", Gauge], ["explorer", "Dataset Explorer", Database], ["analytics", "Healthcare Analytics", BarChart3],
  ["processing", "Big Data Processing", Factory], ["insights", "Insights & Findings", Activity], ["methodology", "Methodology", BookOpen], ["about", "About", Info],
] as const;

function formatMetric(value: MetricValue | undefined, suffix = ""): string {
  return value === null || value === undefined ? "Unavailable" : `${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}${suffix}`;
}

function State({ message }: { message: string }) {
  return <div className="state"><Database size={25} /><strong>Dataset not configured</strong><span>{message}</span><small>Place the SPARCS CSV in HospitalAnalytics/data/raw or set DATASET_PATH for the API.</small></div>;
}

function ChartCard({ title, children, note }: { title: string; children: React.ReactNode; note?: string }) {
  return <section className="card chart-card"><div className="card-heading"><h3>{title}</h3>{note && <span className="muted">{note}</span>}</div><div className="chart">{children}</div></section>;
}

function App() {
  const [page, setPage] = useState<Page>("overview");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [metadata, setMetadata] = useState<Metadata | null>(null);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({ age_group: "", admission_type: "", severity: "" });

  const load = async () => {
    setError("");
    try {
      const [nextSummary, nextMetadata] = await Promise.all([
        getJson<Summary>("/api/dashboard/summary"),
        getJson<Metadata>("/api/dataset/metadata"),
      ]);
      setSummary(nextSummary); setMetadata(nextMetadata);
      if (nextSummary.data_available) setAnalytics(await getJson<Analytics>(`/api/analytics/overview?${new URLSearchParams(filters)}`));
    } catch (reason) { setError(reason instanceof Error ? reason.message : "The API could not be reached."); }
  };
  useEffect(() => { void load(); }, []);
  useEffect(() => { if (summary?.data_available) void getJson<Analytics>(`/api/analytics/overview?${new URLSearchParams(filters)}`).then(setAnalytics).catch(() => setError("Could not refresh filtered analytics.")); }, [filters, summary?.data_available]);
  const go = (next: Page) => { setPage(next); setMobileOpen(false); };
  const current = nav.find(([key]) => key === page);

  return <div className="app-shell">
    <aside className={`sidebar ${mobileOpen ? "open" : ""}`}>
      <div className="brand"><div className="brand-mark"><Activity size={20} /></div><div><strong>Health<span>lytics</span></strong><small>BIG DATA PLATFORM</small></div><button className="icon-btn mobile-close" onClick={() => setMobileOpen(false)}><X size={18} /></button></div>
      <nav>{nav.map(([key, label, Icon]) => <button key={key} className={page === key ? "active" : ""} onClick={() => go(key)}><Icon size={18} />{label}</button>)}</nav>
      <div className="sidebar-foot"><span className="status-dot" />SPARCS 2016 • Research workspace</div>
    </aside>
    <main className="main"><header className="topbar"><button className="icon-btn menu-btn" onClick={() => setMobileOpen(true)}><Menu size={21} /></button><div><span className="eyebrow">HEALTHCARE ANALYTICS / {current?.[1].toUpperCase()}</span><h1>{current?.[1]}</h1></div><button className="refresh" onClick={() => void load()}><RefreshCw size={16} /> Refresh data</button></header>
      {error && <div className="error">{error}</div>}
      {page === "overview" && <Overview summary={summary} onExplore={() => go("analytics")} />}
      {page === "explorer" && <Explorer metadata={metadata} />}
      {page === "analytics" && <AnalyticsPage data={analytics} filters={filters} setFilters={setFilters} />}
      {page === "processing" && <Processing />}
      {page === "insights" && <Insights summary={summary} />}
      {page === "methodology" && <Methodology />}
      {page === "about" && <About />}
    </main>
  </div>;
}

function Overview({ summary, onExplore }: { summary: Summary | null; onExplore: () => void }) {
  if (!summary) return <div className="loading">Loading dashboard…</div>;
  const m = summary.metrics;
  return <div className="page-content"><section className="hero"><div><span className="pill">NYS SPARCS • 2016</span><h2>Healthcare Big Data<br /><em>Analytics</em></h2><p>Explore inpatient discharge patterns, Length of Stay, and scalable Spark processing from a de-identified public health dataset.</p><button className="primary" onClick={onExplore}>Explore analytics <span>→</span></button></div><div className="hero-orbit"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><Activity size={62} /></div></section>
    {!summary.data_available && <State message={summary.message ?? "No local dataset was found."} />}
    <div className="kpi-grid">{[["Total records", m.total_records, ""], ["Facilities", m.facilities, ""], ["Diagnosis categories", m.categories, ""], ["Average Length of Stay", m.average_los, " days"], ["Numeric LoS records", m.numeric_los_records, ""], ["Data completeness", m.data_completeness, "%"]].map(([label, value, suffix]) => <div className="kpi card" key={label as string}><span>{label}</span><strong>{formatMetric(value as MetricValue, suffix as string)}</strong><small>Actual API metric</small></div>)}</div>
    <section className="section-title"><div><span className="eyebrow">PROJECT CONTEXT</span><h2>From raw data to useful evidence</h2></div><p>Descriptive analysis only: findings describe historical records and are not clinical recommendations.</p></section>
    <div className="feature-grid"><div className="card feature"><Factory size={22} /><h3>Distributed processing</h3><p>PySpark reads, cleans, aggregates, and models the large SPARCS dataset with a leakage-aware workflow.</p></div><div className="card feature"><BarChart3 size={22} /><h3>Transparent analytics</h3><p>Interactive views expose the actual filters, counts, Length of Stay summaries, and data-quality context.</p></div><div className="card feature"><Database size={22} /><h3>Data fidelity first</h3><p>No sample KPIs or fabricated charts are shown when the source dataset is unavailable.</p></div></div>
  </div>;
}

function Explorer({ metadata }: { metadata: Metadata | null }) {
  const [query, setQuery] = useState("");
  const [rows, setRows] = useState<Sample | null>(null);
  useEffect(() => { if (metadata?.data_available) void getJson<Sample>(`/api/dataset/sample?search=${encodeURIComponent(query)}`).then(setRows); }, [metadata?.data_available, query]);
  if (!metadata) return <div className="loading">Loading dataset metadata…</div>;
  if (!metadata.data_available) return <div className="page-content"><State message={metadata.message ?? "No local dataset was found."} /></div>;
  return <div className="page-content"><div className="section-title"><div><span className="eyebrow">SOURCE INSPECTION</span><h2>{metadata.source}</h2></div><p>Only safe analytical fields are included in the sample table.</p></div><div className="kpi-grid compact"><div className="kpi card"><span>Rows</span><strong>{formatMetric(metadata.rows ?? null)}</strong></div><div className="kpi card"><span>Columns</span><strong>{formatMetric(metadata.column_count ?? null)}</strong></div><div className="kpi card"><span>Fields shown</span><strong>9</strong></div></div><section className="card table-card"><div className="card-heading"><h3>Dataset sample</h3><input className="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search safe fields…" /></div><div className="table-wrap">{rows?.rows.length ? <table><thead><tr>{Object.keys(rows.rows[0]).map((key) => <th key={key}>{key.replaceAll("_", " ")}</th>)}</tr></thead><tbody>{rows.rows.map((row, index) => <tr key={index}>{Object.values(row).map((value, cell) => <td key={cell}>{String(value)}</td>)}</tr>)}</tbody></table> : <p className="muted table-empty">No rows match the current search.</p>}</div></section><section className="card table-card"><div className="card-heading"><h3>Columns and data quality</h3></div><div className="table-wrap"><table><thead><tr><th>Column</th><th>Type</th><th>Missing</th><th>Unique values</th></tr></thead><tbody>{metadata.columns.map((column) => <tr key={column.name}><td>{column.name}</td><td>{column.dtype}</td><td>{column.missing.toLocaleString()}</td><td>{column.unique_values.toLocaleString()}</td></tr>)}</tbody></table></div></section></div>;
}

function AnalyticsPage({ data, filters, setFilters }: { data: Analytics | null; filters: typeof defaultFilters; setFilters: (value: typeof defaultFilters) => void }) {
  const defaultFilters = { age_group: "", admission_type: "", severity: "" };
  if (!data) return <div className="loading">Loading analytics…</div>;
  if (!data.data_available) return <div className="page-content"><State message="Analytics require the configured SPARCS dataset." /></div>;
  const chart = (items: Record<string, unknown>[], key: string, value: string) => items.map((item) => ({ name: String(item[key] ?? "Unknown"), value: Number(item[value] ?? 0) }));
  const age = chart(data.age, "age_group", "average_los"), admission = chart(data.admission, "type_of_admission", "average_los"), severity = chart(data.severity, "apr_severity_of_illness_description", "average_los");
  return <div className="page-content"><div className="section-title"><div><span className="eyebrow">FILTERED ANALYSIS</span><h2>Patterns in inpatient stays</h2></div><p>Every chart is calculated by the API from the selected records.</p></div><div className="filters card"><label>Age group<select value={filters.age_group} onChange={(e) => setFilters({ ...filters, age_group: e.target.value })}><option value="">All age groups</option>{data.options?.age_groups?.map((option) => <option key={option}>{option}</option>)}</select></label><label>Admission type<select value={filters.admission_type} onChange={(e) => setFilters({ ...filters, admission_type: e.target.value })}><option value="">All admission types</option>{data.options?.admission_types?.map((option) => <option key={option}>{option}</option>)}</select></label><label>Severity<select value={filters.severity} onChange={(e) => setFilters({ ...filters, severity: e.target.value })}><option value="">All severity levels</option>{data.options?.severities?.map((option) => <option key={option}>{option}</option>)}</select></label><button className="secondary" onClick={() => setFilters(defaultFilters)}>Reset</button></div><div className="kpi-grid compact"><div className="kpi card"><span>Average LoS</span><strong>{formatMetric(data.length_of_stay?.average, " days")}</strong></div><div className="kpi card"><span>Median LoS</span><strong>{formatMetric(data.length_of_stay?.median, " days")}</strong></div></div><div className="chart-grid"><ChartCard title="Average LoS by age group"><SimpleBar data={age} color="#087f8c" /></ChartCard><ChartCard title="Average LoS by admission type"><SimpleBar data={admission} color="#1f4e79" /></ChartCard><ChartCard title="Average LoS by severity"><SimpleBar data={severity} color="#d4882e" /></ChartCard><ChartCard title="Numeric LoS distribution" note="Top-coded 120+ values are excluded from numeric days"><SimpleLine data={(data.length_of_stay?.distribution ?? []).map((item) => ({ name: item.bucket, value: item.count }))} /></ChartCard></div></div>;
}

const defaultFilters = { age_group: "", admission_type: "", severity: "" };
function SimpleBar({ data, color }: { data: { name: string; value: number }[]; color: string }) { return data.length ? <ResponsiveContainer width="100%" height="100%"><BarChart data={data} margin={{ top: 8, right: 12, left: -18, bottom: 30 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="name" angle={-25} textAnchor="end" height={55} tick={{ fontSize: 11 }} /><YAxis tick={{ fontSize: 11 }} /><Tooltip /><Bar dataKey="value" fill={color} radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer> : <p className="muted centered">No data for this view.</p>; }
function SimpleLine({ data }: { data: { name: string; value: number }[] }) { return data.length ? <ResponsiveContainer width="100%" height="100%"><LineChart data={data} margin={{ top: 8, right: 12, left: -18, bottom: 20 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="name" tick={{ fontSize: 11 }} /><YAxis tick={{ fontSize: 11 }} /><Tooltip /><Line type="monotone" dataKey="value" stroke="#087f8c" strokeWidth={3} dot={false} /></LineChart></ResponsiveContainer> : <p className="muted centered">No data for this view.</p>; }

function Processing() { const steps = [{ name: "Ingestion", text: "Read and validate the source CSV or cleaned Parquet dataset." }, { name: "Cleaning", text: "Deduplicate rows, normalize categorical missing values, and classify numeric versus top-coded Length of Stay." }, { name: "Aggregation", text: "Build overall, age, admission, severity, diagnosis, and hospital summaries." }, { name: "Prediction", text: "Train a Spark MLlib Random Forest baseline using predictors selected to avoid post-discharge leakage." }, { name: "Visualization", text: "Write bounded reports and charts for the dashboard and research report." }]; return <div className="page-content"><div className="section-title"><div><span className="eyebrow">PIPELINE</span><h2>Raw data → evidence</h2></div><p>Implementation follows the existing HospitalAnalytics Python modules.</p></div><div className="pipeline">{steps.map((step, index) => <div className="pipeline-step card" key={step.name}><div className="step-number">0{index + 1}</div><div><h3>{step.name}</h3><p>{step.text}</p></div>{index < steps.length - 1 && <span className="connector">→</span>}</div>)}</div><section className="card prose"><h3>Why PySpark?</h3><p>The source dataset contains approximately 2.34 million historical, de-identified inpatient discharge records. Spark provides distributed CSV ingestion, transformations, SQL-style aggregations, and a Spark MLlib baseline while keeping the workflow reproducible on a local machine.</p><div className="code-note">Source of truth: HospitalAnalytics/src/ingestion, preprocessing, analysis, ml, and visualization</div></section></div>; }
function Insights({ summary }: { summary: Summary | null }) { if (!summary) return <div className="loading">Loading insights…</div>; return <div className="page-content"><div className="section-title"><div><span className="eyebrow">EVIDENCE</span><h2>Insights & findings</h2></div><p>Descriptive findings are generated from the configured dataset; no causal claims are made.</p></div>{summary.data_available && summary.insights.length ? <div className="insight-grid">{summary.insights.map((item) => <article className="card insight" key={item.title}><span className="insight-icon"><Activity size={18} /></span><h3>{item.title}</h3><strong>{item.value}</strong><span>{item.metric.toLocaleString()} records</span><p>{item.explanation}</p></article>)}</div> : <State message="Insights will appear after the SPARCS dataset is configured." />}</div>; }
function Methodology() { return <div className="page-content"><div className="section-title"><div><span className="eyebrow">TECHNICAL METHOD</span><h2>Methodology & architecture</h2></div><p>A faithful web layer around the existing research implementation.</p></div><div className="architecture"><div className="arch-node"><Database />SPARCS 2016<br /><small>CSV / Parquet</small></div><span>→</span><div className="arch-node"><Factory />PySpark<br /><small>Clean + aggregate</small></div><span>→</span><div className="arch-node"><BarChart3 />FastAPI<br /><small>REST APIs</small></div><span>→</span><div className="arch-node"><Activity />React UI<br /><small>Interactive views</small></div></div><div className="two-col"><section className="card prose"><h3>Research methodology</h3><p>The workflow ingests the NYS SPARCS 2016 inpatient discharge dataset, normalizes headers, removes exact duplicates, audits missing values, preserves the top-coded “120+” stay category, and computes grouped descriptive statistics. A Random Forest regression baseline uses age group, admission type, severity, and risk of mortality while excluding post-discharge leakage fields.</p></section><section className="card prose"><h3>Technologies</h3><ul><li>Python, Pandas, NumPy</li><li>Apache Spark, PySpark SQL, Spark MLlib</li><li>FastAPI REST service</li><li>React, TypeScript, Vite, Recharts</li></ul></section></div></div>; }
function About() { return <div className="page-content"><div className="section-title"><div><span className="eyebrow">PROJECT NOTES</span><h2>About the project</h2></div><p>Academic healthcare analytics for historical operational understanding.</p></div><div className="two-col"><section className="card prose"><h3>Problem statement</h3><p>Hospitals need to understand how inpatient stay duration varies across demographics, admission patterns, diagnoses, and severity. This project demonstrates how big-data methods can support historical analysis and resource planning.</p><h3>Objectives</h3><ul><li>Prepare and quality-check a large discharge dataset.</li><li>Compare Length of Stay across relevant groups.</li><li>Demonstrate scalable PySpark processing.</li><li>Evaluate a reproducible Random Forest baseline.</li></ul></section><section className="card prose"><h3>Scope and limitations</h3><p>The dataset is historical, static, de-identified, and not a live occupancy feed. Top-coded values are not treated as exactly 120 days. Results are descriptive and the model is an academic baseline, not clinical advice or a validated decision system.</p><h3>Future enhancements</h3><p>Possible extensions include scheduled data refreshes, richer model interpretation, role-based access, and deployment monitoring without changing the research objective.</p></section></div></div>; }

export default App;
