import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { useState } from "react";
import {
  getEnrichedLaw, getLawArticles, createArticle,
  deleteArticle, getLawTags, addTag, removeTag,
} from "../api/client";

export default function LawDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const { data: enriched, isLoading } = useQuery({
    queryKey: ["enriched-law", id],
    queryFn: () => getEnrichedLaw(id).then((r) => r.data),
  });

  const { data: articlesData } = useQuery({
    queryKey: ["law-articles", id],
    queryFn: () => getLawArticles(id, { sort: "article_number", order: "asc" }).then((r) => r.data),
  });

  const { data: tags } = useQuery({
    queryKey: ["law-tags", id],
    queryFn: () => getLawTags(id).then((r) => r.data),
  });

  const [newTag, setNewTag] = useState("");
  const [newArticle, setNewArticle] = useState({ article_number: "", content: "" });
  const [showArticleForm, setShowArticleForm] = useState(false);

  const { mutate: doAddTag } = useMutation({
    mutationFn: (name) => addTag(id, { name }),
    onSuccess: () => { qc.invalidateQueries(["law-tags", id]); setNewTag(""); },
  });

  const { mutate: doRemoveTag } = useMutation({
    mutationFn: (tag) => removeTag(id, tag),
    onSuccess: () => qc.invalidateQueries(["law-tags", id]),
  });

  const { mutate: doCreateArticle, error: articleError } = useMutation({
    mutationFn: (body) => createArticle(id, body),
    onSuccess: () => {
      qc.invalidateQueries(["law-articles", id]);
      setShowArticleForm(false);
      setNewArticle({ article_number: "", content: "" });
    },
  });

  const { mutate: doDeleteArticle } = useMutation({
    mutationFn: deleteArticle,
    onSuccess: () => qc.invalidateQueries(["law-articles", id]),
  });

  if (isLoading) return <p>Loading...</p>;
  if (!enriched?.law) return <p>Law not found.</p>;

  const { law, wikipedia, news } = enriched;
  const STATUS_COLOR = { active: "#059669", draft: "#d97706", repealed: "#dc2626" };

  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.5rem" }}>
        <div>
          <button onClick={() => navigate("/laws")}
            style={{ background: "none", border: "none", color: "#6b7280", cursor: "pointer", marginBottom: 8 }}>
            ← Back to laws
          </button>
          <h1 style={{ margin: 0 }}>{law.title}</h1>
          <span style={{
            background: STATUS_COLOR[law.status] + "20", color: STATUS_COLOR[law.status],
            padding: ".2rem .7rem", borderRadius: 12, fontSize: ".8rem", fontWeight: 600
          }}>
            {law.status}
          </span>
        </div>
        <button onClick={() => navigate(`/laws/${id}/edit`)}
          style={{ background: "#1e40af", color: "#fff", border: "none", padding: ".5rem 1.25rem", borderRadius: 8, cursor: "pointer" }}>
           Edit
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>

        {/* Coloana stânga */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>

          {/* Info lege */}
          <div style={{ background: "#fff", borderRadius: 12, padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,.1)" }}>
            <h2 style={{ marginTop: 0 }}>Details</h2>
            {law.description && <p style={{ color: "#374151" }}>{law.description}</p>}
            {law.promulgation_date && (
              <div style={{ color: "#6b7280", fontSize: ".875rem" }}>
                Promulgated: {new Date(law.promulgation_date).toLocaleDateString("ro-RO")}
              </div>
            )}
          </div>

          {/* Tags */}
          <div style={{ background: "#fff", borderRadius: 12, padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,.1)" }}>
            <h2 style={{ marginTop: 0 }}>Tags</h2>
            <div style={{ display: "flex", flexWrap: "wrap", gap: ".5rem", marginBottom: "1rem" }}>
              {tags?.map((t) => (
                <span key={t.id} style={{
                  background: "#eff6ff", color: "#1e40af",
                  padding: ".25rem .75rem", borderRadius: 20, fontSize: ".875rem",
                  display: "flex", alignItems: "center", gap: ".25rem"
                }}>
                  {t.name}
                  <button onClick={() => doRemoveTag(t.name)}
                    style={{ background: "none", border: "none", cursor: "pointer", color: "#6b7280", padding: 0 }}>×</button>
                </span>
              ))}
            </div>
            <div style={{ display: "flex", gap: ".5rem" }}>
              <input
                value={newTag} onChange={(e) => setNewTag(e.target.value)}
                placeholder="New tag..."
                style={{ flex: 1, padding: ".4rem .7rem", borderRadius: 6, border: "1px solid #d1d5db" }}
              />
              <button onClick={() => newTag.trim() && doAddTag(newTag.trim())}
                style={{ background: "#1e40af", color: "#fff", border: "none", padding: ".4rem .8rem", borderRadius: 6, cursor: "pointer" }}>
                Add
              </button>
            </div>
          </div>

          {/* Articole */}
          <div style={{ background: "#fff", borderRadius: 12, padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,.1)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <h2 style={{ margin: 0 }}>Articles</h2>
              <button onClick={() => setShowArticleForm((v) => !v)}
                style={{ background: "#059669", color: "#fff", border: "none", padding: ".3rem .8rem", borderRadius: 6, cursor: "pointer", fontSize: ".875rem" }}>
                + Article
              </button>
            </div>

            {showArticleForm && (
              <div style={{ background: "#f9fafb", borderRadius: 8, padding: "1rem", marginBottom: "1rem" }}>
                <div style={{ display: "flex", gap: ".5rem", marginBottom: ".5rem" }}>
                  <input
                    type="number" placeholder="Article number"
                    value={newArticle.article_number}
                    onChange={(e) => setNewArticle((a) => ({ ...a, article_number: parseInt(e.target.value) || "" }))}
                    style={{ width: 100, padding: ".4rem", borderRadius: 6, border: "1px solid #d1d5db" }}
                  />
                </div>
                <textarea
                  placeholder="Article content..."
                  value={newArticle.content}
                  onChange={(e) => setNewArticle((a) => ({ ...a, content: e.target.value }))}
                  rows={3}
                  style={{ width: "100%", padding: ".4rem", borderRadius: 6, border: "1px solid #d1d5db", resize: "vertical", boxSizing: "border-box" }}
                />
                {articleError && (
                  <p style={{ color: "#dc2626", fontSize: ".875rem" }}>
                    {articleError.response?.data?.error || "Error creating article"}
                  </p>
                )}
                <button
                  onClick={() => doCreateArticle({ article_number: newArticle.article_number, content: newArticle.content })}
                  style={{ background: "#059669", color: "#fff", border: "none", padding: ".4rem .8rem", borderRadius: 6, cursor: "pointer", marginTop: ".5rem" }}>
                  Save
                </button>
              </div>
            )}

            {articlesData?.results?.map((a) => (
                <div key={a.id} style={{
                    borderLeft: "3px solid #3b82f6", paddingLeft: "1rem",
                    marginBottom: "1rem", display: "flex", justifyContent: "space-between", alignItems: "flex-start"
                }}>
                    <Link
                    to={`/laws/${id}/articles/${a.id}`}
                    style={{ flex: 1, textDecoration: "none", color: "inherit" }}
                    >
                    <div style={{ display: "flex", alignItems: "center", gap: ".5rem" }}>
                        <strong style={{ color: "#1e40af" }}>Art. {a.article_number}</strong>
                        <span style={{ color: "#6b7280", fontSize: ".75rem" }}>v{a.version}</span>
                        <span style={{ color: "#9ca3af", fontSize: ".75rem" }}>→</span>
                    </div>
                    <p style={{ margin: "4px 0 0", color: "#374151", fontSize: ".875rem" }}>
                        {a.content.slice(0, 120)}{a.content.length > 120 ? "..." : ""}
                    </p>
                    </Link>
                    <button
                    onClick={() => { if (window.confirm("Delete article?")) doDeleteArticle(a.id); }}
                    style={{ background: "none", border: "none", cursor: "pointer", color: "#dc2626", alignSelf: "flex-start", marginLeft: ".5rem" }}>
                    🗑️
                    </button>
                </div>
                ))}
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>

          <div style={{ background: "#fff", borderRadius: 12, padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,.1)" }}>
            <h2 style={{ marginTop: 0, display: "flex", alignItems: "center", gap: ".5rem" }}>
              📖 Context Wikipedia
              <span style={{ fontSize: ".75rem", color: "#6b7280", fontWeight: 400 }}>via Wikipedia API</span>
            </h2>
            {wikipedia?.length === 0 && <p style={{ color: "#6b7280" }}>No Wikipedia results.</p>}
            {wikipedia?.map((w, i) => (
              <div key={i} style={{ marginBottom: "1rem", paddingBottom: "1rem", borderBottom: i < wikipedia.length - 1 ? "1px solid #f3f4f6" : "none" }}>
                <a href={w.url} target="_blank" rel="noopener noreferrer"
                  style={{ fontWeight: 600, color: "#1e40af", textDecoration: "none" }}>
                  {w.title} ↗
                </a>
                <p style={{ margin: "4px 0 0", color: "#374151", fontSize: ".875rem", lineHeight: 1.5 }}>
                  {w.snippet}
                </p>
              </div>
            ))}
          </div>

          <div style={{ background: "#fff", borderRadius: 12, padding: "1.5rem", boxShadow: "0 1px 3px rgba(0,0,0,.1)" }}>
            <h2 style={{ marginTop: 0, display: "flex", alignItems: "center", gap: ".5rem" }}>
              📰 Recent News
              <span style={{ fontSize: ".75rem", color: "#6b7280", fontWeight: 400 }}>via NewsAPI</span>
            </h2>
            {news?.error && (
              <p style={{ color: "#d97706", fontSize: ".875rem", background: "#fffbeb", padding: ".5rem .75rem", borderRadius: 6 }}>
                ⚠️ {news.error}
              </p>
            )}
            {news?.articles?.length === 0 && !news?.error && <p style={{ color: "#6b7280" }}>No news articles found.</p>}
            {news?.articles?.map((a, i) => (
              <div key={i} style={{ marginBottom: "1rem", paddingBottom: "1rem", borderBottom: i < news.articles.length - 1 ? "1px solid #f3f4f6" : "none" }}>
                <a href={a.url} target="_blank" rel="noopener noreferrer"
                  style={{ fontWeight: 600, color: "#1e40af", textDecoration: "none", fontSize: ".9rem" }}>
                  {a.title} ↗
                </a>
                <div style={{ display: "flex", gap: ".5rem", marginTop: 4, fontSize: ".75rem", color: "#6b7280" }}>
                  <span>{a.source}</span>
                  <span>·</span>
                  <span>{new Date(a.publishedAt).toLocaleDateString("ro-RO")}</span>
                </div>
                {a.description && (
                  <p style={{ margin: "4px 0 0", color: "#374151", fontSize: ".875rem", lineHeight: 1.5 }}>
                    {a.description.slice(0, 150)}{a.description.length > 150 ? "..." : ""}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}