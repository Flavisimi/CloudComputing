import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getAllAmendments, updateAmendment, deleteAmendment } from "../api/client";

export default function AmendmentsList() {
  const qc = useQueryClient();
  const [page, setPage] = useState(1);
  const [approved, setApproved] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["amendments", page, approved],
    queryFn: () => getAllAmendments({ page, approved: approved || undefined, sort: "amendment_date", order: "desc" }).then((r) => r.data),
    keepPreviousData: true,
  });

  const { mutate: doApprove } = useMutation({
    mutationFn: ({ id, val }) => updateAmendment(id, { approved: val }),
    onSuccess: () => qc.invalidateQueries(["amendments"]),
  });

  const { mutate: doDelete } = useMutation({
    mutationFn: deleteAmendment,
    onSuccess: () => qc.invalidateQueries(["amendments"]),
  });

  return (
    <div>
      <h1>Amendments</h1>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem" }}>
        <select value={approved} onChange={(e) => { setApproved(e.target.value); setPage(1); }}
          style={{ padding: ".5rem .75rem", borderRadius: 8, border: "1px solid #d1d5db" }}>
          <option value="">All</option>
          <option value="true">Approved</option>
          <option value="false">Not Approved</option>
        </select>
      </div>

      {isLoading ? <p>Loading...</p> : (
        <div style={{ display: "grid", gap: "1rem" }}>
          {data?.results?.map((a) => (
            <div key={a.id} style={{
              background: "#fff", borderRadius: 12, padding: "1.25rem",
              boxShadow: "0 1px 3px rgba(0,0,0,.1)",
              borderLeft: `4px solid ${a.approved ? "#059669" : "#d97706"}`
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div style={{ flex: 1 }}>
                  <p style={{ margin: 0, color: "#374151" }}>{a.amendment_text}</p>
                  <div style={{ color: "#6b7280", fontSize: ".8rem", marginTop: 6 }}>
                    Date: {new Date(a.amendment_date).toLocaleDateString("ro-RO")} ·
                    Art. {a.article_number} · {a.law_title}
                  </div>
                </div>
                <div style={{ display: "flex", gap: ".5rem", marginLeft: "1rem" }}>
                  <button
                    onClick={() => doApprove({ id: a.id, val: !a.approved })}
                    style={{
                      background: a.approved ? "#fef3c7" : "#d1fae5",
                      color: a.approved ? "#d97706" : "#059669",
                      border: "none", padding: ".3rem .7rem", borderRadius: 6, cursor: "pointer", fontSize: ".8rem"
                    }}>
                    {a.approved ? "Disapprove" : "Approve"}
                  </button>
                  {!a.approved && (
                    <button onClick={() => { if (window.confirm("Delete amendment?")) doDelete(a.id); }}
                      style={{ background: "#fef2f2", color: "#dc2626", border: "none", padding: ".3rem .7rem", borderRadius: 6, cursor: "pointer", fontSize: ".8rem" }}>
                      Delete
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

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
    </div>
  );
}