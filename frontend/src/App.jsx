import { Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import LawsList from "./pages/LawsList";
import LawDetail from "./pages/LawDetail";
import LawForm from "./pages/LawForm";
import AmendmentsList from "./pages/AmendmentsList";
import ArticleDetail from "./pages/ArticleDetail";

export default function App() {
  return (
    <div style={{ fontFamily: "system-ui, sans-serif", minHeight: "100vh", background: "#f8fafc" }}>
      <nav style={{
        background: "#1e40af", color: "#fff", padding: "0 2rem",
        display: "flex", alignItems: "center", gap: "2rem", height: "56px"
      }}>
        <span style={{ fontWeight: 700, fontSize: "1.1rem" }}>⚖️ LawNews ⚖️</span>
        {[
          ["Dashboard", "/"],
          ["Laws", "/laws"],
          ["Amendments", "/amendments"],
        ].map(([label, to]) => (
          <NavLink key={to} to={to}
            style={({ isActive }) => ({
              color: isActive ? "#93c5fd" : "#fff",
              textDecoration: "none", fontWeight: isActive ? 600 : 400
            })}>
            {label}
          </NavLink>
        ))}
      </nav>

      <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem" }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/laws" element={<LawsList />} />
          <Route path="/laws/new" element={<LawForm />} />
          <Route path="/laws/:id" element={<LawDetail />} />
          <Route path="/laws/:id/edit" element={<LawForm />} />
          <Route path="/laws/:lawId/articles/:articleId" element={<ArticleDetail />} />
          <Route path="/amendments" element={<AmendmentsList />} />
        </Routes>
      </main>
    </div>
  );
}