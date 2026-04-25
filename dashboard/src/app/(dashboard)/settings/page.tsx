"use client";

import { useState } from "react";
import useSWR from "swr";
import {
  fetchWAHAServers,
  createWAHAServer,
  updateWAHAServer,
  deleteWAHAServer,
  testWAHAServer,
  type WAHAServer,
  type TestResult,
} from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Settings, Plus, Trash2, Zap, Star, Eye, EyeOff, Loader2, CheckCircle, XCircle } from "lucide-react";

export default function SettingsPage() {
  const { data: serversData, mutate } = useSWR("/api/v1/settings/waha-servers", fetchWAHAServers);
  const servers = serversData ?? [];

  const [editOpen, setEditOpen] = useState(false);
  const [editServer, setEditServer] = useState<WAHAServer | null>(null);
  const [formLabel, setFormLabel] = useState("");
  const [formUrl, setFormUrl] = useState("");
  const [formApiKey, setFormApiKey] = useState("");
  const [formDefault, setFormDefault] = useState(0);
  const [showKey, setShowKey] = useState(false);
  const [saving, setSaving] = useState(false);

  const [testResults, setTestResults] = useState<Record<number, TestResult>>({});
  const [testing, setTesting] = useState<Set<number>>(new Set());

  function openCreate() {
    setEditServer(null);
    setFormLabel("");
    setFormUrl("");
    setFormApiKey("");
    setFormDefault(0);
    setShowKey(false);
    setEditOpen(true);
  }

  function openEdit(s: WAHAServer) {
    setEditServer(s);
    setFormLabel(s.label);
    setFormUrl(s.url);
    setFormApiKey(s.api_key);
    setFormDefault(s.is_default);
    setShowKey(false);
    setEditOpen(true);
  }

  async function handleSave() {
    if (!formLabel || !formUrl || !formApiKey) return;
    setSaving(true);
    try {
      if (editServer) {
        await updateWAHAServer(editServer.id, {
          label: formLabel,
          url: formUrl,
          api_key: formApiKey,
          is_default: formDefault,
        });
      } else {
        await createWAHAServer({
          label: formLabel,
          url: formUrl,
          api_key: formApiKey,
          is_default: formDefault,
        });
      }
      mutate();
      setEditOpen(false);
    } catch (e) {
      alert("Save failed: " + e);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Delete this WAHA connection?")) return;
    try {
      await deleteWAHAServer(id);
      mutate();
    } catch (e) {
      alert("Delete failed: " + e);
    }
  }

  async function handleTest(id: number) {
    setTesting((prev) => new Set(prev).add(id));
    try {
      const result = await testWAHAServer(id);
      setTestResults((prev) => ({ ...prev, [id]: result }));
    } catch (e) {
      setTestResults((prev) => ({ ...prev, [id]: { success: false, message: String(e), sessions_count: 0 } }));
    } finally {
      setTesting((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Settings className="h-6 w-6" />
          Settings
        </h1>
      </div>

      <Card className="bg-neutral-900 border-neutral-800">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">WAHA Connections</CardTitle>
          <Button onClick={openCreate} size="sm" className="bg-orange-600 hover:bg-orange-700">
            <Plus className="h-4 w-4 mr-1" /> Add Connection
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          {servers.length === 0 ? (
            <div className="text-center py-8 text-neutral-500">
              No WAHA connections configured. Click &quot;Add Connection&quot; to get started.
            </div>
          ) : (
            <div className="divide-y divide-neutral-800">
              {servers.map((s) => {
                const testResult = testResults[s.id];
                const isTesting = testing.has(s.id);
                return (
                  <div key={s.id} className="px-4 py-3 flex items-center justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm">{s.label}</span>
                        {s.is_default === 1 && (
                          <Badge className="text-xs bg-orange-600">
                            <Star className="h-3 w-3 mr-0.5" /> Default
                          </Badge>
                        )}
                        {testResult && (
                          testResult.success ? (
                            <Badge className="text-xs bg-green-700">
                              <CheckCircle className="h-3 w-3 mr-0.5" /> Connected ({testResult.sessions_count})
                            </Badge>
                          ) : (
                            <Badge className="text-xs bg-red-700">
                              <XCircle className="h-3 w-3 mr-0.5" /> {testResult.message.slice(0, 40)}
                            </Badge>
                          )
                        )}
                      </div>
                      <p className="text-xs text-neutral-500 mt-0.5 truncate">{s.url}</p>
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      <Button
                        onClick={() => handleTest(s.id)}
                        variant="outline"
                        size="sm"
                        className="border-neutral-700 text-neutral-400 hover:text-white"
                        disabled={isTesting}
                      >
                        {isTesting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Zap className="h-3.5 w-3.5" />}
                        <span className="ml-1 hidden sm:inline">Test</span>
                      </Button>
                      <Button
                        onClick={() => openEdit(s)}
                        variant="outline"
                        size="sm"
                        className="border-neutral-700 text-neutral-400 hover:text-white"
                      >
                        Edit
                      </Button>
                      <Button
                        onClick={() => handleDelete(s.id)}
                        variant="outline"
                        size="sm"
                        className="border-red-900 text-red-400 hover:bg-red-950"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="bg-neutral-900 border-neutral-800">
          <DialogHeader>
            <DialogTitle>{editServer ? "Edit WAHA Connection" : "Add WAHA Connection"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-neutral-300">Label</label>
              <Input
                value={formLabel}
                onChange={(e) => setFormLabel(e.target.value)}
                placeholder="e.g. Primary WAHA"
                className="bg-neutral-800 border-neutral-700 mt-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-neutral-300">URL</label>
              <Input
                value={formUrl}
                onChange={(e) => setFormUrl(e.target.value)}
                placeholder="http://localhost:3010 or https://waha.example.com"
                className="bg-neutral-800 border-neutral-700 mt-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-neutral-300">API Key</label>
              <div className="relative mt-1">
                <Input
                  value={formApiKey}
                  onChange={(e) => setFormApiKey(e.target.value)}
                  type={showKey ? "text" : "password"}
                  placeholder="Your WAHA API key"
                  className="bg-neutral-800 border-neutral-700 pr-10"
                />
                <button
                  onClick={() => setShowKey(!showKey)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-300"
                >
                  {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="isDefault"
                checked={formDefault === 1}
                onChange={(e) => setFormDefault(e.target.checked ? 1 : 0)}
                className="rounded border-neutral-700 bg-neutral-800"
              />
              <label htmlFor="isDefault" className="text-sm text-neutral-300">Set as default connection</label>
            </div>
            <Button
              onClick={handleSave}
              disabled={saving || !formLabel || !formUrl || !formApiKey}
              className="w-full bg-orange-600 hover:bg-orange-700"
            >
              {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              {editServer ? "Save Changes" : "Add Connection"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}