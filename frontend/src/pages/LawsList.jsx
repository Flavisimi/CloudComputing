import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { getLaws, deleteLaw } from "../api/client";

const STATUS_COLOR = { active: "#059669", draft: "#d97706", repealed: "#dc2626" };

export default function LawsList() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");
  const [title, setTitle] = useState("");
  const [sort, setSort] = useState("created_at");
  const [order, setOrder] = useState("desc");

  const { data, isLoading } = useQuery({
    queryKey: ["laws", page, status, title, sort, order],
    queryFn: () => getLaws({ page, status: status || undefined, title: title || undefined, sort, order }).then((r) => r.data),
    keepPreviousData: true,
  });

  const { mutate: doDelete } = useMutation({
    mutationFn: deleteLaw,
    onSuccess: () => qc.invalidateQueries(["laws"]),
  });

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h1>Laws</h1>
        <button
          onClick={() => navigate("/laws/new")}
          style={{ background: "#1e40af", color: "#fff", border: "none", padding: ".5rem 1.25rem", borderRadius: 8, cursor: "pointer" }}
        >
          + New Law
        </button>
      </div>

      {/* Filtre */}
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
        <input
          placeholder="Searching for title..."
          value={title}
          onChange={(e) => { setTitle(e.target.value); setPage(1); }}
          style={{ padding: ".5rem .75rem", borderRadius: 8, border: "1px solid #d1d5db", width: 220 }}
        />
        <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }}
          style={{ padding: ".5rem .75rem", borderRadius: 8, border: "1px solid #d1d5db" }}>
          <option value="">All status</option>
          <option value="draft">Draft</option>
          <option value="active">Active</option>
          <option value="repealed">Repealed</option>
        </select>
        <select value={sort} onChange={(e) => setSort(e.target.value)}
          style={{ padding: ".5rem .75rem", borderRadius: 8, border: "1px solid #d1d5db" }}>
          <option value="created_at">Creation Date</option>
          <option value="title">Title</option>
          <option value="promulgation_date">Promulgation Date</option>
          <option value="status">Status</option>
        </select>
        <select value={order} onChange={(e) => setOrder(e.target.value)}
          style={{ padding: ".5rem .75rem", borderRadius: 8, border: "1px solid #d1d5db" }}>
          <option value="desc">Descending</option>
          <option value="asc">Ascending</option>
        </select>
      </div>

      {isLoading ? <p>Loading...</p> : (
        <>
          <div style={{ display: "grid", gap: "1rem" }}>
            {data?.results?.map((law) => (
              <div key={law.id} style={{
                background: "#fff", borderRadius: 12, padding: "1.25rem",
                boxShadow: "0 1px 3px rgba(0,0,0,.1)",
                display: "flex", justifyContent: "space-between", alignItems: "center"
              }}>
                <div>
                  <Link to={`/laws/${law.id}`} style={{ fontWeight: 600, color: "#1e40af", fontSize: "1rem", textDecoration: "none" }}>
                    {law.title}
                  </Link>
                  <div style={{ color: "#6b7280", fontSize: ".875rem", marginTop: 4 }}>
                    {law.description?.slice(0, 100)}{law.description?.length > 100 ? "..." : ""}
                  </div>
                  <div style={{ display: "flex", gap: ".5rem", marginTop: 8 }}>
                    <span style={{
                      background: STATUS_COLOR[law.status] + "20",
                      color: STATUS_COLOR[law.status],
                      padding: ".15rem .6rem", borderRadius: 12, fontSize: ".75rem", fontWeight: 600
                    }}>
                      {law.status}
                    </span>
                    <span style={{ color: "#6b7280", fontSize: ".75rem" }}>
                      {law.article_count} article{law.article_count !== 1 ? "s" : ""}
                    </span>
                  </div>
                </div>
                <div style={{ display: "flex", gap: ".5rem" }}>
                  <button onClick={() => navigate(`/laws/${law.id}/edit`)}
                    style={{ background: "#f3f4f6", border: "none", padding: ".4rem .8rem", borderRadius: 6, cursor: "pointer" }}>
                    ✏️
                  </button>
                  <button
                    onClick={() => { if (window.confirm(`Ștergi "${law.title}"?`)) doDelete(law.id); }}
                    style={{ background: "#fef2f2", color: "#dc2626", border: "none", padding: ".4rem .8rem", borderRadius: 6, cursor: "pointer" }}>
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Paginare */}
          <div style={{ display: "flex", gap: ".5rem", marginTop: "1.5rem", justifyContent: "center" }}>
            <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}
              style={{ padding: ".4rem .8rem", borderRadius: 6, border: "1px solid #d1d5db", cursor: "pointer", background: "#fff" }}>
              ← Previous
            </button>
            <span style={{ padding: ".4rem .8rem", color: "#6b7280" }}>Page {page}</span>
            <button onClick={() => setPage((p) => p + 1)} disabled={!data?.results?.length || data.results.length < 5}
              style={{ padding: ".4rem .8rem", borderRadius: 6, border: "1px solid #d1d5db", cursor: "pointer", background: "#fff" }}>
              Next →
            </button>
          </div>
        </>
      )}
    </div>
  );
}