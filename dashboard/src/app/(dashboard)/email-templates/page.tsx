"use client";

import { useState } from "react";
import useSWR from "swr";
import { fetcher, fetchEmailTemplates, createEmailTemplate, renderEmailTemplate as renderTemplate, type EmailTemplate } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Mail, Plus, FileText, Eye, Trash2 } from "lucide-react";

export default function EmailTemplatesPage() {
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [previewTemplate, setPreviewTemplate] = useState<EmailTemplate | null>(null);
  const [newTemplate, setNewTemplate] = useState({ name: "", subject: "", body: "", category: "general" });
  const [previewVars, setPreviewVars] = useState<Record<string, string>>({});

  const { data, mutate } = useSWR("/api/v1/email-templates", fetcher as any, {
    onSuccess: (d: any) => { setTemplates(d.templates); setLoading(false); },
  });

  const handleCreate = async () => {
    if (!newTemplate.name || !newTemplate.subject || !newTemplate.body) return;
    try {
      await createEmailTemplate(newTemplate);
      setNewTemplate({ name: "", subject: "", body: "", category: "general" });
      setCreateOpen(false);
      mutate();
    } catch (err) {
      console.error("Failed to create template:", err);
    }
  };

  const handlePreview = async (template: EmailTemplate) => {
    setPreviewTemplate(template);
    const vars: Record<string, string> = {};
    if (template.variables) {
      template.variables.split(",").forEach((v) => { vars[v.trim()] = ""; });
    }
    setPreviewVars(vars);
  };

  const handleRender = async () => {
    if (!previewTemplate) return;
    try {
      const result = await renderTemplate(previewTemplate.id, previewVars);
      setPreviewTemplate({ ...previewTemplate, subject: result.subject, body: result.body } as EmailTemplate);
    } catch (err) {
      console.error("Failed to render template:", err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this template?")) return;
    try {
      const res = await fetch(`/api/v1/email-templates/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error(`API ${res.status}`);
      mutate();
    } catch (err) {
      console.error("Failed to delete template:", err);
    }
  };

  const categoryColors: Record<string, string> = {
    onboarding: "bg-green-500",
    "follow-up": "bg-blue-500",
    meeting: "bg-purple-500",
    general: "bg-gray-500",
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Mail className="h-6 w-6" />
          Email Templates
        </h1>
        <Button onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4 mr-1" />
          New Template
        </Button>
      </div>

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Email Template</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 mt-4">
            <div>
              <label className="text-sm font-medium">Name</label>
              <Input value={newTemplate.name} onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })} placeholder="Template name" />
            </div>
            <div>
              <label className="text-sm font-medium">Subject</label>
              <Input value={newTemplate.subject} onChange={(e) => setNewTemplate({ ...newTemplate, subject: e.target.value })} placeholder="Email subject. Use {{variable}} for dynamic content" />
            </div>
            <div>
              <label className="text-sm font-medium">Category</label>
              <select className="w-full border rounded p-2" value={newTemplate.category} onChange={(e) => setNewTemplate({ ...newTemplate, category: e.target.value })}>
                <option value="general">General</option>
                <option value="onboarding">Onboarding</option>
                <option value="follow-up">Follow Up</option>
                <option value="meeting">Meeting</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">Body</label>
              <Textarea value={newTemplate.body} onChange={(e) => setNewTemplate({ ...newTemplate, body: e.target.value })} rows={6} placeholder="Email body. Use {{variable}} for dynamic content" />
            </div>
            <Button onClick={handleCreate} className="w-full">Create Template</Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={!!previewTemplate} onOpenChange={() => setPreviewTemplate(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Preview: {previewTemplate?.name}</DialogTitle>
          </DialogHeader>
          {previewTemplate && (
            <div className="space-y-4 mt-4">
              <div className="space-y-2">
                {Object.keys(previewVars).map((key) => (
                  <div key={key} className="flex items-center gap-2">
                    <label className="text-sm w-24">{key}:</label>
                    <Input value={previewVars[key]} onChange={(e) => setPreviewVars({ ...previewVars, [key]: e.target.value })} placeholder={`Enter ${key}`} />
                  </div>
                ))}
              </div>
              <Button onClick={handleRender} size="sm">Render Preview</Button>
              <div className="border rounded p-4 space-y-2">
                <div><strong>Subject:</strong> {previewTemplate.subject}</div>
                <div className="whitespace-pre-wrap"><strong>Body:</strong><br />{previewTemplate.body}</div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {loading ? (
        <div className="text-center py-12 text-muted-foreground">Loading templates...</div>
      ) : templates.length === 0 ? (
        <Card><CardContent className="text-center py-12 text-muted-foreground">No email templates yet. Create your first template.</CardContent></Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((template) => (
            <Card key={template.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    {template.name}
                  </CardTitle>
                  <div className="flex items-center gap-1">
                    <Badge variant="secondary" className={categoryColors[template.category] || "bg-gray-500"}>
                      {template.category}
                    </Badge>
                    {template.is_predefined && <Badge variant="outline">Default</Badge>}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="text-sm font-medium truncate">{template.subject}</div>
                <div className="text-xs text-muted-foreground line-clamp-3">{template.body}</div>
                <div className="flex items-center gap-2 pt-2">
                  <Button size="sm" variant="outline" onClick={() => handlePreview(template)}>
                    <Eye className="h-3 w-3 mr-1" /> Preview
                  </Button>
                  {!template.is_predefined && (
                    <Button size="sm" variant="ghost" onClick={() => handleDelete(template.id)} className="text-destructive">
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}