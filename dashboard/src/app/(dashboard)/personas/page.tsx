"use client";

import { useState } from "react";
import useSWR from "swr";
import { fetcher, postJSON, patchJSON, deleteJSON } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, Users, Plus, Pencil, Trash2 } from "lucide-react";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";

const SCOPE_COLORS: Record<string, string> = {
  cs: "bg-blue-600 text-white",
  outreach: "bg-purple-600 text-white",
  universal: "bg-green-600 text-white",
};

const SCOPE_LABELS: Record<string, string> = {
  cs: "CS",
  outreach: "Outreach",
  universal: "Universal",
};

const TONE_LABELS: Record<string, string> = {
  casual: "Casual",
  formal: "Formal",
  playful: "Playful",
  professional: "Professional",
};

const LANG_LABELS: Record<string, string> = {
  id: "ID",
  en: "EN",
  ms: "MS",
};

function slugify(text: string) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

interface Persona {
  id: string;
  name: string;
  scope: string;
  system_prompt: string;
  tone: string;
  language: string;
  example_replies: string[];
  is_builtin: number;
}

const EMPTY_FORM = {
  id: "",
  name: "",
  scope: "universal",
  system_prompt: "",
  tone: "casual",
  language: "id",
  example_replies: "",
};

export default function PersonasPage() {
  const { data, isLoading, mutate } = useSWR<{ personas: Persona[] }>("/api/v1/personas", fetcher);
  const personas = data?.personas || [];

  const [saving, setSaving] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);

  function openCreate() {
    setForm(EMPTY_FORM);
    setEditingId(null);
    setEditOpen(true);
  }

  function openEdit(p: Persona) {
    setForm({
      id: p.id,
      name: p.name,
      scope: p.scope,
      system_prompt: p.system_prompt,
      tone: p.tone,
      language: p.language,
      example_replies: Array.isArray(p.example_replies) ? p.example_replies.join("\n") : "",
    });
    setEditingId(p.id);
    setEditOpen(true);
  }

  async function handleSave() {
    setSaving(true);
    try {
      const payload = {
        ...form,
        example_replies: form.example_replies.split("\n").filter((l) => l.trim()),
      };
      if (editingId) {
        await patchJSON(`/api/v1/personas/${editingId}`, payload);
      } else {
        payload.id = form.id || slugify(form.name);
        await postJSON("/api/v1/personas", payload);
      }
      mutate();
      setEditOpen(false);
    } catch (e) {
      console.error("Save failed:", e);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this persona?")) return;
    try {
      await deleteJSON(`/api/v1/personas/${id}`);
      mutate();
    } catch (e) {
      console.error("Delete failed:", e);
    }
  }

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center h-[50vh]">
        <Loader2 className="h-8 w-8 animate-spin text-orange-500" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Users className="h-6 w-6 text-orange-500" />
          Personas
        </h1>
        <Button onClick={openCreate} className="bg-orange-600 hover:bg-orange-700 h-8 gap-1 text-sm">
          <Plus className="h-3 w-3 mr-1" /> Create Persona
        </Button>
      </div>

      {personas.length === 0 ? (
        <p className="text-center text-neutral-500 py-12">No personas yet.</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {personas.map((p) => (
            <Card key={p.id} className="bg-neutral-900 border-neutral-800 hover:border-neutral-700 transition-colors">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <CardTitle className="text-base">{p.name}</CardTitle>
                  <div className="flex gap-1.5">
                    <Badge className={SCOPE_COLORS[p.scope] || "bg-neutral-600 text-white"}>
                      {SCOPE_LABELS[p.scope] || p.scope}
                    </Badge>
                    {p.is_builtin ? (
                      <Badge className="bg-neutral-700 text-neutral-300">Built-in</Badge>
                    ) : null}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex gap-1.5">
                  <Badge variant="secondary" className="text-xs">{TONE_LABELS[p.tone] || p.tone}</Badge>
                  <Badge variant="secondary" className="text-xs">{LANG_LABELS[p.language] || p.language}</Badge>
                </div>
                <p className="text-sm text-neutral-400 line-clamp-2">{p.system_prompt}</p>
                <div className="flex gap-2 pt-1">
                  <Button variant="outline" size="sm" onClick={() => openEdit(p)} className="h-7 text-xs gap-1">
                    <Pencil className="h-3 w-3" /> Edit
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(p.id)}
                    disabled={!!p.is_builtin}
                    className="h-7 text-xs gap-1 text-red-400 hover:text-red-300 disabled:opacity-30"
                  >
                    <Trash2 className="h-3 w-3" /> Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="bg-neutral-900 border-neutral-800 text-neutral-100 max-w-lg">
          <DialogTitle className="text-lg font-bold">{editingId ? "Edit Persona" : "Create Persona"}</DialogTitle>
          <DialogDescription className="text-sm text-neutral-400">
            {editingId ? "Update persona settings and system prompt." : "Define a new AI persona for your channels."}
          </DialogDescription>
          <div className="space-y-3 mt-4">
            <div>
              <label className="text-xs text-neutral-400 mb-1 block">Name</label>
              <Input
                value={form.name}
                onChange={(e) => {
                  setForm({ ...form, name: e.target.value });
                  if (!editingId) setForm((f) => ({ ...f, name: e.target.value, id: slugify(e.target.value) }));
                }}
                className="bg-neutral-800 border-neutral-700"
                placeholder="e.g. Friendly CS Agent"
              />
            </div>
            {!editingId && (
              <div>
                <label className="text-xs text-neutral-400 mb-1 block">ID</label>
                <Input
                  value={form.id}
                  onChange={(e) => setForm({ ...form, id: e.target.value })}
                  className="bg-neutral-800 border-neutral-700"
                  placeholder="auto-generated from name"
                />
              </div>
            )}
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="text-xs text-neutral-400 mb-1 block">Scope</label>
                <select
                  value={form.scope}
                  onChange={(e) => setForm({ ...form, scope: e.target.value })}
                  className="w-full h-9 rounded-md bg-neutral-800 border border-neutral-700 text-sm px-2"
                >
                  <option value="cs">CS</option>
                  <option value="outreach">Outreach</option>
                  <option value="universal">Universal</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-neutral-400 mb-1 block">Tone</label>
                <select
                  value={form.tone}
                  onChange={(e) => setForm({ ...form, tone: e.target.value })}
                  className="w-full h-9 rounded-md bg-neutral-800 border border-neutral-700 text-sm px-2"
                >
                  <option value="casual">Casual</option>
                  <option value="formal">Formal</option>
                  <option value="playful">Playful</option>
                  <option value="professional">Professional</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-neutral-400 mb-1 block">Language</label>
                <select
                  value={form.language}
                  onChange={(e) => setForm({ ...form, language: e.target.value })}
                  className="w-full h-9 rounded-md bg-neutral-800 border border-neutral-700 text-sm px-2"
                >
                  <option value="id">Indonesian</option>
                  <option value="en">English</option>
                  <option value="ms">Malay</option>
                </select>
              </div>
            </div>
            <div>
              <label className="text-xs text-neutral-400 mb-1 block">System Prompt</label>
              <textarea
                value={form.system_prompt}
                onChange={(e) => setForm({ ...form, system_prompt: e.target.value })}
                rows={5}
                className="w-full rounded-md bg-neutral-800 border border-neutral-700 text-sm p-2 resize-y"
                placeholder="Define the persona's behavior and personality..."
              />
            </div>
            <div>
              <label className="text-xs text-neutral-400 mb-1 block">Example Replies (one per line)</label>
              <textarea
                value={form.example_replies}
                onChange={(e) => setForm({ ...form, example_replies: e.target.value })}
                rows={3}
                className="w-full rounded-md bg-neutral-800 border border-neutral-700 text-sm p-2 resize-y"
                placeholder="Oke Kak, ditunggu ya!"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={() => setEditOpen(false)} className="h-8">Cancel</Button>
              <Button onClick={handleSave} disabled={saving || !form.name || !form.system_prompt} className="bg-orange-600 hover:bg-orange-700 h-8">
                {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : editingId ? "Update" : "Create"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
