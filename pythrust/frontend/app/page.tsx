"use client";

import { useMemo, useState } from "react";

type GeneratedFile = {
  path: string;
  kind: "ts" | "html" | "css" | "json" | "md";
  content: string;
};

type ValidationIssue = {
  level: "error" | "warning";
  code: string;
  message: string;
  file_path?: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [files, setFiles] = useState<GeneratedFile[]>([]);
  const [selectedPath, setSelectedPath] = useState<string>("");
  const [issues, setIssues] = useState<ValidationIssue[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const selectedFile = useMemo(
    () => files.find((file) => file.path === selectedPath) || files[0],
    [files, selectedPath],
  );

  const previewHtml = useMemo(
    () => files.find((file) => file.path.endsWith(".component.html"))?.content || "",
    [files],
  );

  const previewCss = useMemo(
    () => files.find((file) => file.path.endsWith(".component.css"))?.content || "",
    [files],
  );

  const stats = useMemo(() => {
    const byKind = files.reduce<Record<string, number>>((acc, f) => {
      acc[f.kind] = (acc[f.kind] || 0) + 1;
      return acc;
    }, {});
    return {
      totalFiles: files.length,
      ts: byKind.ts || 0,
      html: byKind.html || 0,
      css: byKind.css || 0,
      json: byKind.json || 0,
    };
  }, [files]);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setError("");
    setIssues([]);
    setFiles([]);
    setSelectedPath("");

    try {
      const response = await fetch(`${API_URL}/v1/generate/page`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data?.detail || "Generation failed. Please try again.");
        return;
      }

      const generated: GeneratedFile[] = data?.manifest?.files || [];
      const validationIssues: ValidationIssue[] = data?.validation?.issues || [];

      setFiles(generated);
      setIssues(validationIssues);
      setSelectedPath(generated[0]?.path || "");

      if (!generated.length) {
        setError("No files were generated. Try refining your prompt.");
      }
    } catch (e) {
      console.error(e);
      setError("Unable to reach backend. Ensure backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-slate-100 p-6 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <header className="rounded-2xl border border-slate-800 bg-slate-900/80 backdrop-blur p-6 shadow-xl">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Guided Component Architect</h1>
              <p className="text-slate-400 mt-1 text-sm md:text-base">
                Generate full-page Angular scaffolds with governance checks and file-level validation.
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs">
              <span className="px-2 py-1 rounded-full bg-indigo-500/20 text-indigo-200 border border-indigo-400/40">API: {API_URL}</span>
              <span className="px-2 py-1 rounded-full bg-emerald-500/20 text-emerald-200 border border-emerald-400/40">
                {loading ? "Generating" : "Ready"}
              </span>
            </div>
          </div>

          <div className="mt-5 grid gap-3">
            <textarea
              className="w-full bg-slate-950/70 border border-slate-700 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-500/30 outline-none p-4 rounded-xl min-h-28"
              placeholder="Example: Build a SaaS landing page with hero, features, testimonials, pricing, and footer"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
            <div className="flex gap-3">
              <button
                onClick={handleGenerate}
                disabled={loading || !prompt.trim()}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {loading ? "Generating full page..." : "Generate Full Page"}
              </button>
            </div>
          </div>

          {error && (
            <div className="mt-4 rounded-xl border border-rose-400/40 bg-rose-500/10 text-rose-200 px-4 py-3 text-sm">
              {error}
            </div>
          )}
        </header>

        <section className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="md:col-span-3 grid grid-cols-2 md:grid-cols-5 gap-3">
            <Stat label="Files" value={String(stats.totalFiles)} />
            <Stat label="TS" value={String(stats.ts)} />
            <Stat label="HTML" value={String(stats.html)} />
            <Stat label="CSS" value={String(stats.css)} />
            <Stat label="JSON" value={String(stats.json)} />
          </div>
          <div className="md:col-span-2 rounded-xl border border-slate-800 bg-slate-900 p-3">
            <p className="text-sm font-semibold mb-2">Validation</p>
            {issues.length === 0 ? (
              <p className="text-emerald-300 text-sm">No validation issues reported.</p>
            ) : (
              <ul className="space-y-2 max-h-32 overflow-auto text-sm">
                {issues.map((issue, index) => (
                  <li
                    key={`${issue.code}-${index}`}
                    className={`rounded-md px-2 py-1 border ${issue.level === "error" ? "border-rose-500/40 bg-rose-500/10 text-rose-200" : "border-amber-500/40 bg-amber-500/10 text-amber-200"}`}
                  >
                    <span className="font-medium">{issue.code}</span>: {issue.message}
                    {issue.file_path ? <span className="text-slate-300"> ({issue.file_path})</span> : null}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <aside className="lg:col-span-4 rounded-2xl border border-slate-800 bg-slate-900 p-4 max-h-[70vh] overflow-auto">
            <h2 className="text-sm font-semibold text-slate-200 mb-3">Generated Files</h2>
            {files.length === 0 ? (
              <p className="text-sm text-slate-400">No files yet. Generate from the prompt above.</p>
            ) : (
              <div className="space-y-2">
                {files.map((file) => (
                  <button
                    key={file.path}
                    onClick={() => setSelectedPath(file.path)}
                    className={`w-full text-left px-3 py-2 rounded-lg border transition ${selectedFile?.path === file.path ? "border-indigo-400 bg-indigo-500/20" : "border-slate-700 bg-slate-800/70 hover:bg-slate-800"}`}
                  >
                    <div className="text-sm font-medium truncate">{file.path}</div>
                    <div className="text-xs text-slate-400 uppercase">{file.kind}</div>
                  </button>
                ))}
              </div>
            )}
          </aside>

          <section className="lg:col-span-8 space-y-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4">
              <h2 className="text-sm font-semibold mb-2">Code Viewer</h2>
              <pre className="bg-slate-950/80 border border-slate-800 rounded-lg p-3 overflow-auto max-h-[34vh] text-xs md:text-sm text-slate-100">
                {selectedFile?.content || "Select a generated file to inspect its code."}
              </pre>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-4">
              <h2 className="text-sm font-semibold mb-2">Live Preview</h2>
              {previewHtml || previewCss ? (
                <div className="bg-white rounded-xl p-4 text-black min-h-36">
                  <style>{previewCss}</style>
                  <div dangerouslySetInnerHTML={{ __html: previewHtml }} />
                </div>
              ) : (
                <div className="rounded-lg border border-slate-700 bg-slate-950/60 p-6 text-sm text-slate-400">
                  Preview will appear after generation.
                </div>
              )}
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-3">
      <p className="text-xs text-slate-400 uppercase">{label}</p>
      <p className="text-lg font-semibold mt-1">{value}</p>
    </div>
  );
}
