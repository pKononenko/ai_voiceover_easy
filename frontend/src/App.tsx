import { useEffect, useMemo, useState } from "react";
import { SubmitHandler, useForm } from "react-hook-form";
import apiClient, { API_BASE_URL } from "./lib/api";
import { useAuth } from "./hooks/useAuth";
import "./styles/App.css";

interface AuthFormValues {
  email: string;
  password: string;
}

interface Voice {
  id: number;
  name: string;
  language: string;
  accent?: string | null;
  gender?: string | null;
  style?: string | null;
}

type ProjectStatus = "pending" | "processing" | "completed" | "failed";

interface ProjectSummary {
  id: number;
  title: string;
  status: ProjectStatus;
  language?: string | null;
  style?: string | null;
  voice_id?: number | null;
  audio_url?: string | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

interface ProjectDetail extends ProjectSummary {
  source_text: string;
  source_filename?: string | null;
}

interface ProjectFormValues {
  title: string;
  voice_id?: string;
  language?: string;
  style?: string;
  text?: string;
  file?: FileList;
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

function formatDate(value: string) {
  const date = new Date(value);
  return date.toLocaleString();
}

const App = () => {
  const { token, email, setAuth, clearAuth, isAuthenticated } = useAuth();
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");
  const [voices, setVoices] = useState<Voice[]>([]);
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [selectedProject, setSelectedProject] = useState<ProjectDetail | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const authForm = useForm<AuthFormValues>({
    defaultValues: { email: "", password: "" },
  });

  const projectForm = useForm<ProjectFormValues>({
    defaultValues: { title: "", text: "" },
  });

  const authHeaders = useMemo(() => ({
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  }), [token]);

  const loadVoices = async () => {
    try {
      const response = await apiClient.get<Voice[]>("/voices", authHeaders);
      setVoices(response.data);
    } catch (error) {
      console.error("Failed to load voices", error);
    }
  };

  const loadProjects = async () => {
    if (!token) return;
    try {
      const response = await apiClient.get<ProjectSummary[]>("/projects", authHeaders);
      setProjects(response.data);
    } catch (error) {
      console.error("Failed to load projects", error);
    }
  };

  useEffect(() => {
    if (token) {
      loadVoices();
      loadProjects();
    }
  }, [token]);

  const handleAuthSubmit: SubmitHandler<AuthFormValues> = async (values) => {
    try {
      const endpoint = authMode === "login" ? "/auth/login" : "/auth/signup";
      if (authMode === "signup") {
        await apiClient.post(endpoint, values);
        setStatusMessage("Account created! Please log in.");
        setAuthMode("login");
        return;
      }

      const response = await apiClient.post<{ access_token: string }>(endpoint, values);
      setAuth(response.data.access_token, values.email);
      setStatusMessage("Logged in successfully.");
      authForm.reset();
    } catch (error: any) {
      setStatusMessage(error.response?.data?.detail ?? "Authentication failed");
    }
  };

  const pollProject = async (projectId: number) => {
    if (!token) return;
    for (let attempt = 0; attempt < 20; attempt += 1) {
      try {
        const response = await apiClient.get<ProjectDetail>(`/projects/${projectId}`, authHeaders);
        const detail = response.data;
        if (detail.status !== "pending" && detail.status !== "processing") {
          setSelectedProject(detail);
          if (detail.status === "completed") {
            setStatusMessage("Narration ready! Download or preview below.");
          } else if (detail.error_message) {
            setStatusMessage(`Generation failed: ${detail.error_message}`);
          }
          return;
        }
      } catch (error) {
        console.error("Polling failed", error);
        break;
      }
      await sleep(1000);
    }
    setStatusMessage("Still working... refresh the page to update status.");
  };

  const onProjectSubmit: SubmitHandler<ProjectFormValues> = async (values) => {
    if (!token) return;
    const formData = new FormData();
    formData.append("title", values.title);
    if (values.voice_id) formData.append("voice_id", values.voice_id);
    if (values.language) formData.append("language", values.language);
    if (values.style) formData.append("style", values.style);
    if (values.text) formData.append("text", values.text);
    if (values.file && values.file.length > 0) {
      formData.append("file", values.file[0]);
    }

    setIsSubmitting(true);
    setStatusMessage("Uploading project...");

    try {
      const response = await apiClient.post<ProjectDetail>("/projects", formData, {
        headers: {
          ...authHeaders.headers,
          "Content-Type": "multipart/form-data",
        },
      });
      setSelectedProject(response.data);
      setStatusMessage("Narration requested. Generating audio...");
      projectForm.reset();
      await pollProject(response.data.id);
      await loadProjects();
    } catch (error: any) {
      setStatusMessage(error.response?.data?.detail ?? "Failed to create project");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSelectProject = async (projectId: number) => {
    if (!token) return;
    try {
      const response = await apiClient.get<ProjectDetail>(`/projects/${projectId}`, authHeaders);
      setSelectedProject(response.data);
    } catch (error) {
      console.error("Failed to load project", error);
    }
  };

  const downloadAudio = async (project: ProjectSummary) => {
    if (!token || !project.audio_url) return;
    try {
      const response = await apiClient.get<ArrayBuffer>(project.audio_url, {
        ...authHeaders,
        responseType: "arraybuffer",
      });
      const blob = new Blob([response.data], { type: "audio/wav" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${project.title}.wav`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Download failed", error);
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>AI Voiceover Easy</h1>
          <p>Create quick audiobooks and narration from your documents.</p>
        </div>
        {isAuthenticated ? (
          <div className="user-badge">
            <span>{email}</span>
            <button type="button" onClick={clearAuth} className="secondary">
              Log out
            </button>
          </div>
        ) : null}
      </header>

      {!isAuthenticated ? (
        <section className="auth-view">
          <div className="auth-hero">
            <div className="badge">New</div>
            <h2>Turn manuscripts into beautiful audio with a single click.</h2>
            <p>
              Upload a document or paste your script, pick a voice that matches your brand, and
              generate polished narration ready for download in minutes.
            </p>
            <ul>
              <li>🎙️ Premium multilingual voice library</li>
              <li>⚡ Fast generation with progress tracking</li>
              <li>📚 Save and revisit every audiobook project</li>
            </ul>
          </div>

          <div className="auth-card">
            <div className="card-header">
              <h2>{authMode === "login" ? "Welcome back" : "Create your account"}</h2>
              <button
                type="button"
                className="link"
                onClick={() => setAuthMode(authMode === "login" ? "signup" : "login")}
              >
                {authMode === "login" ? "Need an account?" : "Already registered?"}
              </button>
            </div>

            <form className="form" onSubmit={authForm.handleSubmit(handleAuthSubmit)}>
              <label>
                Email address
                <input
                  type="email"
                  required
                  autoComplete="email"
                  placeholder="you@example.com"
                  {...authForm.register("email")}
                />
              </label>
              <label>
                Password
                <input
                  type="password"
                  required
                  minLength={6}
                  autoComplete={authMode === "login" ? "current-password" : "new-password"}
                  placeholder="••••••••"
                  {...authForm.register("password")}
                />
              </label>
              <button type="submit" className="primary">
                {authMode === "login" ? "Log in" : "Create account"}
              </button>
            </form>
            <p className="fine-print">By continuing you agree to our terms of service.</p>
          </div>
        </section>
      ) : (
        <section className="dashboard">
          <div className="card">
            <div className="card-header">
              <h2>New narration</h2>
            </div>
            <form className="form" onSubmit={projectForm.handleSubmit(onProjectSubmit)}>
              <label>
                Title
                <input type="text" placeholder="My audiobook" required {...projectForm.register("title")} />
              </label>
              <label>
                Voice
                <select {...projectForm.register("voice_id")}> 
                  <option value="">Automatic</option>
                  {voices.map((voice) => (
                    <option key={voice.id} value={voice.id}>
                      {voice.name} ({voice.language}
                      {voice.accent ? ` · ${voice.accent}` : ""})
                    </option>
                  ))}
                </select>
              </label>
              <div className="grid">
                <label>
                  Language
                  <input type="text" placeholder="en" {...projectForm.register("language")} />
                </label>
                <label>
                  Speaking style
                  <input type="text" placeholder="narration" {...projectForm.register("style")} />
                </label>
              </div>
              <label>
                Paste text
                <textarea rows={6} placeholder="Paste or upload your manuscript" {...projectForm.register("text")} />
              </label>
              <label className="file-picker">
                Upload document (.txt, .pdf, .docx)
                <input type="file" accept=".txt,.pdf,.docx" {...projectForm.register("file")} />
              </label>
              <button type="submit" className="primary" disabled={isSubmitting}>
                {isSubmitting ? "Generating..." : "Generate narration"}
              </button>
            </form>
          </div>

          <div className="card">
            <div className="card-header">
              <h2>History</h2>
              <button type="button" className="link" onClick={loadProjects}>
                Refresh
              </button>
            </div>
            <ul className="project-list">
              {projects.map((project) => (
                <li key={project.id} className={`project ${project.status}`}>
                  <div>
                    <strong>{project.title}</strong>
                    <div className="meta">
                      <span>{project.status}</span>
                      <span>Updated {formatDate(project.updated_at)}</span>
                    </div>
                  </div>
                  <div className="actions">
                    <button type="button" className="secondary" onClick={() => handleSelectProject(project.id)}>
                      Details
                    </button>
                    <button
                      type="button"
                      className="secondary"
                      disabled={!project.audio_url || project.status !== "completed"}
                      onClick={() => downloadAudio(project)}
                    >
                      Download
                    </button>
                  </div>
                </li>
              ))}
              {projects.length === 0 ? <li className="empty">No narrations yet. Upload your first project!</li> : null}
            </ul>
          </div>

          <div className="card">
            <div className="card-header">
              <h2>Project details</h2>
              {selectedProject ? <span className={`status ${selectedProject.status}`}>{selectedProject.status}</span> : null}
            </div>
            {selectedProject ? (
              <div className="project-detail">
                <p className="meta">
                  Created {formatDate(selectedProject.created_at)} · Updated {formatDate(selectedProject.updated_at)}
                </p>
                {selectedProject.source_filename ? <p>Source file: {selectedProject.source_filename}</p> : null}
                <p>Voice ID: {selectedProject.voice_id ?? "auto"}</p>
                {selectedProject.audio_url ? (
                  <audio
                    controls
                    src={`${API_BASE_URL}${selectedProject.audio_url}?t=${selectedProject.updated_at}`}
                  >
                    Your browser does not support the audio element.
                  </audio>
                ) : (
                  <p>Audio not ready yet.</p>
                )}
                <details>
                  <summary>Show transcript</summary>
                  <pre>{selectedProject.source_text}</pre>
                </details>
                {selectedProject.error_message ? (
                  <p className="error">Error: {selectedProject.error_message}</p>
                ) : null}
              </div>
            ) : (
              <p className="empty">Select a project to see its details.</p>
            )}
          </div>
        </section>
      )}

      {statusMessage ? <div className="toast">{statusMessage}</div> : null}
    </div>
  );
};

export default App;
