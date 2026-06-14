import axios from "axios";
const api = axios.create({
  baseURL: "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// log every request
api.interceptors.request.use((config) => {
  console.log(`→ ${config.method.toUpperCase()} ${config.url}`);
  return config;
});

//log every response
api.interceptors.response.use(
  (response) => {
    console.log(`← ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`✗ ${error.response?.status} ${error.config?.url}`, error.response?.data);
    return Promise.reject(error);
  }
);

export const reviewPR = (repo, prNumber) =>
  api.post("/review/pr", { repo, pr_number: prNumber });
export const reviewCommit = (repo, sha) =>
  api.post("/review/commit", { repo, sha });
export const reviewIssue = (repo, issueNumber) =>
  api.post("/review/issue", { repo, issue_number: issueNumber });
export const healthCheck = () => api.get("/health");

export const getHistory = (repo = null, type = null) => {
  const params = new URLSearchParams();
  if (repo) params.append("repo", repo);
  if (type) params.append("type", type);
  return api.get(`/history?${params.toString()}`);
};

export const getReviewDetail = (id) => api.get(`/history/${id}`);

export const getStats = (repo = null) => {
  const params = repo ? `?repo=${repo}` : "";
  return api.get(`/stats${params}`);
};