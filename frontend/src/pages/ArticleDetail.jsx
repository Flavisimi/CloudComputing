import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import {
  getArticle, updateArticle, deleteArticle,
  getVersions, getArticleAmendments, createAmendment,
  updateAmendment, deleteAmendment,
  getRefsOut, getRefsIn,
} from "../api/client";

export default function ArticleDetail() {
  const { lawId, articleId } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const [editMode, setEditMode] = useState(false);
  const [editContent, setEditContent] = useState("");
  const [editError, setEditError] = useState("");

  const [newAmendment, setNewAmendment] = useState({ text: "", date: "" });
  const [amendError, setAmendError] = useState("");
  const [showAmendForm, setShowAmendForm] = useState(false);

  const [activeTab, setActiveTab] = useState("versions");

  const { data: article, isLoading } = useQuery({
    queryKey: ["article", articleId],
    queryFn: () => getArticle(articleId).then((r) => r.data),
  });

  const { data: versionsData } = useQuery({
    queryKey: ["versions", articleId],
    queryFn: () => getVersions(articleId, { page: 1 }).then((r) => r.data),
    enabled: activeTab === "versions",
  });

  const { data: amendmentsData } = useQuery({
    queryKey: ["article-amendments", articleId],
    queryFn: () => getArticleAmendments(articleId, { page: 1 }).then((r) => r.data),
    enabled: activeTab === "amendments",
  });

  const { mutate: doUpdate } = useMutation({
    mutationFn: (content) => updateArticle(articleId, { content }),
    onSuccess: () => {
      qc.invalidateQueries(["article", articleId]);
      qc.invalidateQueries(["versions", articleId]);
      setEditMode(false);
      setEditError("");
    },
    onError: (err) => setEditError(err.response?.data?.error || "Eroare la salvare"),
  });

  const { mutate: doDelete } = useMutation({
    mutationFn: () => deleteArticle(articleId),
    onSuccess: () => navigate(`/laws/${lawId}`),
  });

  const { mutate: doAddAmendment } = useMutation({
    mutationFn: () => createAmendment(articleId, { text: newAmendment.text, date: newAmendment.date }),
    onSuccess: () => {
      qc.invalidateQueries(["article-amendments", articleId]);
      setNewAmendment({ text: "", date: "" });
      setShowAmendForm(false);
      setAmendError("");
    },
    onError: (err) => setAmendError(err.response?.data?.error || "Eroare"),
  });

  const { mutate: doApprove } = useMutation({
    mutationFn: ({ id, val }) => updateAmendment(id, { approved: val }),
    onSuccess: () => qc.invalidateQueries(["article-amendments", articleId]),
  });

  const { mutate: doDeleteAmendment } = useMutation({
    mutationFn: (id) => deleteAmendment(id),
    onSuccess: () => qc.invalidateQueries(["article-amendments", articleId]),
  });

  if (isLoading) return <p>Loading...</p>;
  if (!article) return <p>Article not found.</p>;

  const tabStyle = (name) => ({
    padding: ".5rem 1.25rem",
    border: "none",
    borderBottom: activeTab === name ? "2px solid #1e40af" : "2px solid transparent",
    background: "none",
    cursor: "pointer",
    fontWeight: activeTab === name ? 600 : 400,
    color: activeTab === name ? "#1e40af" : "#6b7280",
  });

  return (
    <div>
      <button onClick={() => navigate(`/laws/${lawId}`)}
        style={{ background: "none", border: "none", color: "#6b7280", cursor: "pointer", marginBottom: 16 }}>
        ← Back to law
      </button>

      <div style={{ background: "#fff", borderRadius: 12, padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,.1)", marginBottom: "1.5rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <h1 style={{ margin: 0 }}>Articolul {article.article_number}</h1>
            <span style={{ color: "#6b7280", fontSize: ".875rem" }}>
              Version {article.version} · Modified: {new Date(article.changed_at).toLocaleDateString("ro-RO")}
            </span>
          </div>
          <div style={{ display: "flex", gap: ".5rem" }}>
            {!editMode && (
              <button
                onClick={() => { setEditContent(article.content); setEditMode(true); }}
                style={{ background: "#eff6ff", color: "#1e40af", border: "none", padding: ".4rem .9rem", borderRadius: 8, cursor: "pointer" }}>
                Edit
              </button>
            )}
            <button
              onClick={() => { if (window.confirm("Delete article?")) doDelete(); }}
              style={{ background: "#fef2f2", color: "#dc2626", border: "none", padding: ".4rem .9rem", borderRadius: 8, cursor: "pointer" }}>
              Delete
            </button>
          </div>
        </div>

        <div style={{ marginTop: "1.25rem" }}>
          {editMode ? (
            <>
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                rows={8}
                style={{ width: "100%", padding: ".75rem", borderRadius: 8, border: "1px solid #d1d5db", fontSize: ".95rem", lineHeight: 1.6, resize: "vertical", boxSizing: "border-box" }}
              />
              {editError && <p style={{ color: "#dc2626", fontSize: ".875rem" }}>{editError}</p>}
              <div style={{ display: "flex", gap: ".5rem", marginTop: ".75rem" }}>
                <button onClick={() => doUpdate(editContent)}
                  style={{ background: "#1e40af", color: "#fff", border: "none", padding: ".4rem 1rem", borderRadius: 8, cursor: "pointer" }}>
                  Save New Version
                </button>
                <button onClick={() => setEditMode(false)}
                  style={{ background: "#f3f4f6", border: "none", padding: ".4rem 1rem", borderRadius: 8, cursor: "pointer" }}>
                  Cancel
                </button>
              </div>
            </>
          ) : (
            <p style={{ color: "#374151", lineHeight: 1.7, fontSize: ".95rem", margin: 0 }}>
              {article.content}
            </p>
          )}
        </div>
      </div>

      <div style={{ background: "#fff", borderRadius: 12, boxShadow: "0 1px 3px rgba(0,0,0,.1)", overflow: "hidden" }}>
        <div style={{ display: "flex", borderBottom: "1px solid #f3f4f6", padding: "0 1rem" }}>
          {[["versions", "Versions"], ["amendments", "Amendments"]].map(([key, label]) => (
            <button key={key} onClick={() => setActiveTab(key)} style={tabStyle(key)}>{label}</button>
          ))}
        </div>

        <div style={{ padding: "1.5rem" }}>

          {activeTab === "versions" && (
            <div>
              <h3 style={{ marginTop: 0 }}>Version History</h3>
              {versionsData?.results?.length === 0 && <p style={{ color: "#6b7280" }}>No versions available.</p>}
              {versionsData?.results?.map((v) => (
                <div key={v.version} style={{
                  borderLeft: `3px solid ${v.version === article.version ? "#1e40af" : "#e5e7eb"}`,
                  paddingLeft: "1rem", marginBottom: "1.25rem"
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: ".5rem", marginBottom: 4 }}>
                    <strong>v{v.version}</strong>
                    {v.version === article.version && (
                      <span style={{ background: "#eff6ff", color: "#1e40af", fontSize: ".75rem", padding: ".1rem .5rem", borderRadius: 10 }}>curentă</span>
                    )}
                    <span style={{ color: "#9ca3af", fontSize: ".8rem" }}>
                      {new Date(v.changed_at).toLocaleDateString("ro-RO")}
                    </span>
                  </div>
                  <p style={{ color: "#374151", fontSize: ".875rem", lineHeight: 1.6, margin: 0 }}>
                    {v.content.slice(0, 200)}{v.content.length > 200 ? "..." : ""}
                  </p>
                </div>
              ))}
            </div>
          )}

          {activeTab === "amendments" && (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                <h3 style={{ margin: 0 }}>Amendments</h3>
                <button onClick={() => setShowAmendForm((v) => !v)}
                  style={{ background: "#059669", color: "#fff", border: "none", padding: ".35rem .9rem", borderRadius: 8, cursor: "pointer", fontSize: ".875rem" }}>
                  + Add Amendment
                </button>
              </div>

              {showAmendForm && (
                <div style={{ background: "#f9fafb", borderRadius: 8, padding: "1rem", marginBottom: "1rem" }}>
                  <textarea
                    placeholder="Amendment text..."
                    value={newAmendment.text}
                    onChange={(e) => setNewAmendment((a) => ({ ...a, text: e.target.value }))}
                    rows={3}
                    style={{ width: "100%", padding: ".5rem", borderRadius: 6, border: "1px solid #d1d5db", resize: "vertical", boxSizing: "border-box", marginBottom: ".5rem" }}
                  />
                  <input
                    type="date"
                    value={newAmendment.date}
                    onChange={(e) => setNewAmendment((a) => ({ ...a, date: e.target.value }))}
                    style={{ padding: ".4rem .7rem", borderRadius: 6, border: "1px solid #d1d5db", marginBottom: ".5rem" }}
                  />
                  {amendError && <p style={{ color: "#dc2626", fontSize: ".875rem" }}>{amendError}</p>}
                  <div style={{ display: "flex", gap: ".5rem" }}>
                    <button onClick={() => doAddAmendment()}
                      style={{ background: "#059669", color: "#fff", border: "none", padding: ".4rem .9rem", borderRadius: 6, cursor: "pointer" }}>
                      Save Amendment
                    </button>
                    <button onClick={() => setShowAmendForm(false)}
                      style={{ background: "#f3f4f6", border: "none", padding: ".4rem .9rem", borderRadius: 6, cursor: "pointer" }}>
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {amendmentsData?.results?.length === 0 && <p style={{ color: "#6b7280" }}>No amendments available.</p>}
              {amendmentsData?.results?.map((am) => (
                <div key={am.id} style={{
                  borderLeft: `3px solid ${am.approved ? "#059669" : "#d97706"}`,
                  paddingLeft: "1rem", marginBottom: "1rem",
                  display: "flex", justifyContent: "space-between", alignItems: "flex-start"
                }}>
                  <div style={{ flex: 1 }}>
                    <p style={{ margin: 0, color: "#374151", fontSize: ".9rem", lineHeight: 1.6 }}>{am.amendment_text}</p>
                    <div style={{ display: "flex", gap: ".75rem", marginTop: 6, fontSize: ".8rem", color: "#6b7280" }}>
                      <span>📅 {new Date(am.amendment_date).toLocaleDateString("ro-RO")}</span>
                      <span style={{ color: am.approved ? "#059669" : "#d97706", fontWeight: 600 }}>
                        {am.approved ? "✓ Approved" : "Pending"}
                      </span>
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: ".4rem", marginLeft: "1rem" }}>
                    <button
                      onClick={() => doApprove({ id: am.id, val: !am.approved })}
                      style={{ background: am.approved ? "#fef3c7" : "#d1fae5", color: am.approved ? "#d97706" : "#059669", border: "none", padding: ".3rem .6rem", borderRadius: 6, cursor: "pointer", fontSize: ".8rem" }}>
                      {am.approved ? "Disapprove" : "Approve"}
                    </button>
                    {!am.approved && (
                      <button onClick={() => { if (window.confirm("Delete amendment?")) doDeleteAmendment(am.id); }}
                        style={{ background: "#fef2f2", color: "#dc2626", border: "none", padding: ".3rem .6rem", borderRadius: 6, cursor: "pointer", fontSize: ".8rem" }}>
                        🗑️
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

        </div>
      </div>
    </div>
  );
}