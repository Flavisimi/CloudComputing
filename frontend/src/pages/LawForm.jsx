import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { getLaw, createLaw, replaceLaw } from "../api/client";

export default function LawForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);

  const [form, setForm] = useState({ title: "", description: "", status: "draft" });
  const [error, setError] = useState("");

  const { data: existing } = useQuery({
    queryKey: ["law", id],
    queryFn: () => getLaw(id).then((r) => r.data),
    enabled: isEdit,
  });

  useEffect(() => {
    if (existing) setForm({ title: existing.title, description: existing.description || "", status: existing.status });
  }, [existing]);

  const { mutate, isPending } = useMutation({
    mutationFn: (body) => isEdit ? replaceLaw(id, body) : createLaw(body),
    onSuccess: (res) => {
      const newId = res.data?.law_id || id;
      navigate(`/laws/${newId}`);
    },
    onError: (err) => setError(err.response?.data?.error || "Error saving the law"),
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");
    mutate(form);
  };

  return (
    <div style={{ maxWidth: 600 }}>
      <button onClick={() => navigate(-1)} style={{ background: "none", border: "none", color: "#6b7280", cursor: "pointer", marginBottom: 16 }}>
        ← Back
      </button>
      <h1>{isEdit ? "Edit Law" : "New Law"}</h1>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem", background: "#fff", padding: "1.5rem", borderRadius: 12, boxShadow: "0 1px 3px rgba(0,0,0,.1)" }}>
        <label>
          <div style={{ marginBottom: 4, fontWeight: 500 }}>Title *</div>
          <input
            value={form.title} required
            onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            style={{ width: "100%", padding: ".5rem .75rem", borderRadius: 8, border: "1px solid #d1d5db", boxSizing: "border-box" }}
          />
        </label>
        <label>
          <div style={{ marginBottom: 4, fontWeight: 500 }}>Description</div>
          <textarea
            value={form.description} rows={4}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
            style={{ width: "100%", padding: ".5rem .75rem", borderRadius: 8, border: "1px solid #d1d5db", resize: "vertical", boxSizing: "border-box" }}
          />
        </label>
        <label>
          <div style={{ marginBottom: 4, fontWeight: 500 }}>Status</div>
          <select value={form.status} onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
            style={{ padding: ".5rem .75rem", borderRadius: 8, border: "1px solid #d1d5db" }}>
            <option value="draft">Draft</option>
            <option value="active">Active</option>
            <option value="repealed">Repealed</option>
          </select>
        </label>

        {error && <p style={{ color: "#dc2626", background: "#fef2f2", padding: ".5rem .75rem", borderRadius: 6, margin: 0 }}>{error}</p>}

        <div style={{ display: "flex", gap: ".75rem" }}>
          <button type="submit" disabled={isPending}
            style={{ background: "#1e40af", color: "#fff", border: "none", padding: ".5rem 1.5rem", borderRadius: 8, cursor: "pointer", fontWeight: 500 }}>
            {isPending ? "Saving..." : isEdit ? "Update" : "Create"}
          </button>
          <button type="button" onClick={() => navigate(-1)}
            style={{ background: "#f3f4f6", border: "none", padding: ".5rem 1.5rem", borderRadius: 8, cursor: "pointer" }}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}