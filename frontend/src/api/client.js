import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.error || err.response?.data?.detail || err.message;
    console.error("API Error:", msg);
    return Promise.reject(err);
  }
);

export const getLaws = (params) => api.get("/laws", { params });
export const getLaw = (id) => api.get(`/laws/${id}`);
export const createLaw = (body) => api.post("/laws", body);
export const updateLaw = (id, body) => api.patch(`/laws/${id}`, body);
export const replaceLaw = (id, body) => api.put(`/laws/${id}`, body);
export const deleteLaw = (id) => api.delete(`/laws/${id}`);

export const getAllTags = (params) => api.get("/tags", { params });
export const getLawTags = (id) => api.get(`/laws/${id}/tags`);
export const addTag = (id, body) => api.post(`/laws/${id}/tags`, body);
export const removeTag = (id, tag) => api.delete(`/laws/${id}/tags/${tag}`);

export const getArticles = (params) => api.get("/articles", { params });
export const getLawArticles = (lawId, params) => api.get(`/laws/${lawId}/articles`, { params });
export const createArticle = (lawId, body) => api.post(`/laws/${lawId}/articles`, body);
export const getArticle = (id) => api.get(`/articles/${id}`);
export const updateArticle = (id, body) => api.patch(`/articles/${id}`, body);
export const deleteArticle = (id) => api.delete(`/articles/${id}`);
export const getVersions = (id, params) => api.get(`/articles/${id}/versions`, { params });

export const getAllAmendments = (params) => api.get("/amendments", { params });
export const getArticleAmendments = (id, params) => api.get(`/articles/${id}/amendments`, { params });
export const createAmendment = (id, body) => api.post(`/articles/${id}/amendments`, body);
export const getAmendment = (id) => api.get(`/amendments/${id}`);
export const updateAmendment = (id, body) => api.patch(`/amendments/${id}`, body);
export const deleteAmendment = (id) => api.delete(`/amendments/${id}`);

export const getRefsOut = (id) => api.get(`/articles/${id}/references`);
export const getRefsIn = (id) => api.get(`/articles/${id}/references/incoming`);
export const addRef = (id, body) => api.post(`/articles/${id}/references`, body);
export const deleteRef = (id, toId) => api.delete(`/articles/${id}/references/${toId}`);

export const getEnrichedLaw = (id) => api.get(`/enriched/laws/${id}`);
export const getAggregatedStats = () => api.get("/enriched/stats");

export const getAudit = (params) => api.get("/audit", { params });

export const searchWikipedia = (q) => api.get("/wikipedia/search", { params: { q } });
export const searchNews = (q) => api.get("/news/search", { params: { q } });

export default api;