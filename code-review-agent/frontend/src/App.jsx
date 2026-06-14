import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Home from "./pages/Home";
import PRReview from "./pages/PRReview";
import CommitReview from "./pages/CommitReview";
import IssueReview from "./pages/IssueReview";
import Dashboard from "./pages/Dashboard";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <nav className="navbar">
          <div className="nav-brand">
            <span className="nav-logo"></span>
            <span className="nav-title">CodeReview AI</span>
          </div>
          <div className="nav-links">
            <NavLink to="/" end className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              Home
            </NavLink>
            <NavLink to="/review/pr" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              PR Review
            </NavLink>
            <NavLink to="/review/commit" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              Commit
            </NavLink>
            <NavLink to="/review/issue" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              Issues
            </NavLink>
            <NavLink to="/dashboard" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              Dashboard
            </NavLink>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/review/pr" element={<PRReview />} />
            <Route path="/review/commit" element={<CommitReview />} />
            <Route path="/review/issue" element={<IssueReview />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}