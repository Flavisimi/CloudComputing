import { useQuery } from "@tanstack/react-query";
import { getAggregatedStats } from "../api/client";

const StatCard = ({ title, value, color }) => (
  <div style={{
    background: "#fff", borderRadius: 12, padding: "1.5rem",
    borderLeft: `4px solid ${color}`, boxShadow: "0 1px 3px rgba(0,0,0,.1)"
  }}>
    <div style={{ color: "#6b7280", fontSize: ".875rem" }}>{title}</div>
    <div style={{ fontSize: "2rem", fontWeight: 700, color }}>{value}</div>
  </div>
);

export default function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["stats"],
    queryFn: () => getAggregatedStats().then((r) => r.data),
  });

  if (isLoading) return <p>Loading stats...</p>;
  if (error) return <p style={{ color: "red" }}>Error: {error.message}</p>;

  const totalArticles = data.articles_count?.total ?? 0;
  const totalLaws = data.laws_per_category?.reduce((s, c) => s + c.total, 0) ?? 0;
  const topLaw = data.most_amended_laws?.[0];

  return (
    <div>
      <h1 style={{ marginBottom: "1.5rem" }}>Dashboard</h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
        <StatCard title="Total Laws" value={totalLaws} color="#1e40af" />
        <StatCard title="Total Articles" value={totalArticles} color="#059669" />
        <StatCard title="Law with Most Amendments" value={topLaw?.title?.slice(0, 20) + "..." ?? "—"} color="#d97706" />
      </div>

      <div style={{ background: "#fff", borderRadius: 12, padding: "1.5rem", marginBottom: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,.1)" }}>
        <h2 style={{ marginBottom: "1rem" }}>Laws by Category</h2>
        <div style={{ display: "flex", flexWrap: "wrap", gap: ".5rem" }}>
          {data.laws_per_category?.map((c) => (
            <span key={c.name} style={{
              background: "#eff6ff", color: "#1e40af",
              padding: ".25rem .75rem", borderRadius: 20, fontSize: ".875rem"
            }}>
              {c.name}: <strong>{c.total}</strong>
            </span>
          ))}
        </div>
      </div>

      <div style={{ background: "#fff", borderRadius: 12, padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,.1)" }}>
        <h2 style={{ marginBottom: "1rem" }}>Amendments by Year</h2>
        <div style={{ display: "flex", gap: "1rem", alignItems: "flex-end" }}>
          {data.amendments_per_year?.map((y) => (
            <div key={y.year} style={{ textAlign: "center" }}>
              <div style={{
                width: 40, background: "#3b82f6", borderRadius: 4,
                height: `${Math.min(y.total * 8, 120)}px`,
                display: "flex", alignItems: "flex-end", justifyContent: "center",
                color: "#fff", fontSize: ".75rem", paddingBottom: 4
              }}>
                {y.total}
              </div>
              <div style={{ fontSize: ".75rem", color: "#6b7280", marginTop: 4 }}>{y.year}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}