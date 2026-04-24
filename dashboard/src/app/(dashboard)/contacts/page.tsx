"use client";

import { useState } from "react";
import useSWR from "swr";
import { fetcher, postJSON, patchJSON, deleteJSON, type Contact } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Users, Search, Plus, Download, Upload, Loader2, Edit, Trash2, Phone, Mail, Building, FileText, Tag } from "lucide-react";

export default function ContactsPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [selectedContact, setSelectedContact] = useState<Contact | null>(null);
  const [editOpen, setEditOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);

  const query = new URLSearchParams({
    search: search,
    limit: "50",
    offset: String(page * 50),
  }).toString();

  const { data, mutate, isLoading } = useSWR<{ contacts: Contact[]; total: number }>(
    `/api/v1/contacts?${query}`,
    fetcher
  );

  const contacts = data?.contacts ?? [];
  const total = data?.total ?? 0;

  const handleExport = () => {
    window.open("/api/v1/contacts/export-csv", "_blank");
  };

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Users className="h-6 w-6" />
          Contacts
        </h1>
        <div className="flex gap-2">
          <Button onClick={() => setImportOpen(true)} variant="outline" className="border-neutral-700">
            <Upload className="h-4 w-4 mr-1" /> Import CSV
          </Button>
          <Button onClick={handleExport} variant="outline" className="border-neutral-700">
            <Download className="h-4 w-4 mr-1" /> Export
          </Button>
          <Button onClick={() => { setSelectedContact(null); setEditOpen(true); }} className="bg-green-700 hover:bg-green-600">
            <Plus className="h-4 w-4 mr-1" /> Add Contact
          </Button>
        </div>
      </div>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-500" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search contacts..."
            className="pl-10 bg-neutral-900 border-neutral-800"
          />
        </div>
      </div>

      <div className="flex items-center justify-between text-sm text-neutral-500">
        <span>{total} contacts</span>
        <div className="flex gap-1">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 0}
            onClick={() => setPage(p => p - 1)}
          >
            Prev
          </Button>
          <span className="px-3 py-1">Page {page + 1}</span>
          <Button
            variant="outline"
            size="sm"
            disabled={(page + 1) * 50 >= total}
            onClick={() => setPage(p => p + 1)}
          >
            Next
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-orange-500" />
        </div>
      ) : (
        <Card className="bg-neutral-900 border-neutral-800">
          <CardContent className="p-0">
            <ScrollArea className="h-[calc(100vh-320px)]">
              <table className="w-full">
                <thead className="sticky top-0 bg-neutral-900 border-b border-neutral-800">
                  <tr>
                    <th className="text-left px-4 py-3 text-sm font-medium text-neutral-400">Name</th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-neutral-400">Phone</th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-neutral-400">Email</th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-neutral-400">Company</th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-neutral-400">Tags</th>
                    <th className="text-left px-4 py-3 text-sm font-medium text-neutral-400">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {contacts.map((contact) => (
                    <tr
                      key={contact.id}
                      className="border-b border-neutral-800 hover:bg-neutral-800/50 cursor-pointer"
                      onClick={() => { setSelectedContact(contact); setEditOpen(true); }}
                    >
                      <td className="px-4 py-3 text-sm">{contact.name}</td>
                      <td className="px-4 py-3 text-sm font-mono">{contact.phone}</td>
                      <td className="px-4 py-3 text-sm text-neutral-400">{contact.email || "-"}</td>
                      <td className="px-4 py-3 text-sm text-neutral-400">{contact.company || "-"}</td>
                      <td className="px-4 py-3">
                        {contact.tags ? (
                          <div className="flex gap-1 flex-wrap">
                            {contact.tags.split(",").slice(0, 3).map((tag, i) => (
                              <Badge key={i} variant="secondary" className="text-xs">{tag.trim()}</Badge>
                            ))}
                          </div>
                        ) : (
                          <span className="text-neutral-600">-</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={() => { setSelectedContact(contact); setEditOpen(true); }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {contacts.length === 0 && (
                    <tr>
                      <td colSpan={6} className="text-center py-8 text-neutral-500">
                        No contacts found. Add some or import from CSV.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </ScrollArea>
          </CardContent>
        </Card>
      )}

      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="bg-neutral-900 border-neutral-800 max-w-md">
          <DialogHeader>
            <DialogTitle>
              {selectedContact ? "Edit Contact" : "Add Contact"}
            </DialogTitle>
          </DialogHeader>
          <ContactForm
            contact={selectedContact}
            onSave={() => { setEditOpen(false); mutate(); }}
            onDelete={selectedContact ? () => { setEditOpen(false); mutate(); } : undefined}
          />
        </DialogContent>
      </Dialog>

      <Dialog open={importOpen} onOpenChange={setImportOpen}>
        <DialogContent className="bg-neutral-900 border-neutral-800 max-w-md">
          <DialogHeader>
            <DialogTitle>Import Contacts</DialogTitle>
          </DialogHeader>
          <ImportForm onImport={() => { setImportOpen(false); mutate(); }} />
        </DialogContent>
      </Dialog>
    </div>
  );
}

function ContactForm({
  contact,
  onSave,
  onDelete,
}: {
  contact: Contact | null;
  onSave: () => void;
  onDelete?: () => void;
}) {
  const [name, setName] = useState(contact?.name ?? "");
  const [phone, setPhone] = useState(contact?.phone ?? "");
  const [email, setEmail] = useState(contact?.email ?? "");
  const [company, setCompany] = useState(contact?.company ?? "");
  const [notes, setNotes] = useState(contact?.notes ?? "");
  const [tags, setTags] = useState(contact?.tags ?? "");
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!name || !phone) return;
    setSaving(true);
    try {
      const data = { name, phone, email: email || undefined, company: company || undefined, notes: notes || undefined, tags: tags || undefined };
      if (contact) {
        await patchJSON(`/api/v1/contacts/${contact.id}`, data);
      } else {
        await postJSON("/api/v1/contacts", data);
      }
      onSave();
    } catch (e) {
      alert("Failed to save: " + e);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!contact || !confirm("Delete this contact?")) return;
    try {
      await deleteJSON(`/api/v1/contacts/${contact.id}`);
      onDelete?.();
    } catch (e) {
      alert("Failed to delete: " + e);
    }
  };

  return (
    <div className="space-y-3">
      <div>
        <label className="text-sm font-medium text-neutral-300">Name *</label>
        <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="John Doe" className="mt-1 bg-neutral-800 border-neutral-700" />
      </div>
      <div>
        <label className="text-sm font-medium text-neutral-300">Phone *</label>
        <Input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+6281234567890" className="mt-1 bg-neutral-800 border-neutral-700" />
      </div>
      <div>
        <label className="text-sm font-medium text-neutral-300">Email</label>
        <Input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="john@example.com" className="mt-1 bg-neutral-800 border-neutral-700" />
      </div>
      <div>
        <label className="text-sm font-medium text-neutral-300">Company</label>
        <Input value={company} onChange={(e) => setCompany(e.target.value)} placeholder="Acme Inc" className="mt-1 bg-neutral-800 border-neutral-700" />
      </div>
      <div>
        <label className="text-sm font-medium text-neutral-300">Notes</label>
        <Textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Any notes..." className="mt-1 bg-neutral-800 border-neutral-700" />
      </div>
      <div>
        <label className="text-sm font-medium text-neutral-300">Tags (comma separated)</label>
        <Input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="vip, warm, followup" className="mt-1 bg-neutral-800 border-neutral-700" />
      </div>
      <div className="flex gap-2 pt-2">
        <Button onClick={handleSave} disabled={saving || !name || !phone} className="flex-1 bg-orange-600 hover:bg-orange-700">
          {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
          Save
        </Button>
        {contact && onDelete && (
          <Button onClick={handleDelete} variant="outline" className="border-red-800 text-red-400">
            <Trash2 className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}

function ImportForm({ onImport }: { onImport: () => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<{ imported: number; duplicates: number; errors: string[] } | null>(null);

  const handleImport = async () => {
    if (!file) return;
    setImporting(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/v1/contacts/import-csv", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResult(data);
      if (data.imported > 0) {
        onImport();
      }
    } catch (e) {
      alert("Failed to import: " + e);
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="space-y-3">
      <p className="text-sm text-neutral-400">
        Upload a CSV file with columns: name, phone, email, company, notes, tags
      </p>
      <Input
        type="file"
        accept=".csv"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        className="bg-neutral-800 border-neutral-700"
      />
      {result && (
        <div className="bg-neutral-800 rounded p-3 text-sm">
          <p>Imported: {result.imported}</p>
          <p>Duplicates: {result.duplicates}</p>
          {result.errors.length > 0 && (
            <div className="mt-2 text-red-400">
              <p>Errors:</p>
              <ul className="list-disc list-inside">
                {result.errors.slice(0, 5).map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      <Button onClick={handleImport} disabled={importing || !file} className="w-full bg-green-700 hover:bg-green-600">
        {importing ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Upload className="h-4 w-4 mr-2" />}
        Import
      </Button>
    </div>
  );
}