"use client";

import { useState, useEffect } from "react";
import useSWR from "swr";
import { fetcher, postJSON, patchJSON, deleteJSON } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Loader2,
  Plus,
  Send,
  TestTube,
  Trash2,
  Radio,
  Mail,
  MessageSquare,
  Phone,
  AtSign,
} from "lucide-react";

interface Workspace {
  id: string;
  name: string;
  description?: string;
}

interface Channel {
  id: string;
  workspace_id: string;
  platform: string;
  label: string;
  mode: string;
  enabled: number;
  connected: number;
  username: string;
  phone: string;
  config: Record<string, string>;
  session_data: Record<string, unknown>;
  last_check?: string;
}

const PLATFORM_CFG: Record<
  string,
  {
    label: string;
    icon: typeof Radio;
    color: string;
    fields: { key: string; label: string; placeholder: string; secret?: boolean }[];
  }
> = {
  whatsapp: {
    label: "WhatsApp",
    icon: Phone,
    color: "bg-green-600",
    fields: [],
  },
  instagram: {
    label: "Instagram",
    icon: MessageSquare,
    color: "bg-pink-600",
    fields: [
      { key: "sessionid", label: "Session ID", placeholder: "Instagram sessionid cookie", secret: true },
    ],
  },
  twitter: {
    label: "Twitter / X",
    icon: AtSign,
    color: "bg-blue-600",
    fields: [
      { key: "auth_token", label: "Auth Token", placeholder: "x.com auth_token", secret: true },
      { key: "ct0", label: "CT0", placeholder: "x.com ct0 cookie", secret: true },
    ],
  },
  telegram: {
    label: "Telegram",
    icon: Send,
    color: "bg-sky-500",
    fields: [
      { key: "api_id", label: "API ID", placeholder: "From my.telegram.org" },
      { key: "api_hash", label: "API Hash", placeholder: "Telegram API hash", secret: true },
      { key: "session_string", label: "Session String", placeholder: "Telethon session string", secret: true },
    ],
  },
  email: {
    label: "Email",
    icon: Mail,
    color: "bg-amber-600",
    fields: [
      { key: "from_name", label: "From Name", placeholder: "BerkahKarya" },
      { key: "from_email", label: "From Email", placeholder: "marketing@berkahkarya.org" },
      { key: "brevo_api_key", label: "Brevo API Key", placeholder: "Optional", secret: true },
      { key: "smtp_host", label: "SMTP Host", placeholder: "Optional fallback" },
      { key: "smtp_port", label: "SMTP Port", placeholder: "587" },
      { key: "smtp_user", label: "SMTP User", placeholder: "user@example.com" },
      { key: "smtp_password", label: "SMTP Password", placeholder: "Optional", secret: true },
      { key: "imap_host", label: "IMAP Host", placeholder: "For reply tracking" },
      { key: "imap_password", label: "IMAP Password", placeholder: "Optional", secret: true },
    ],
  },
};

const MODE_OPTIONS = [
  { value: "cs", label: "CS", desc: "Customer Service" },
  { value: "coldcall", label: "Cold Outreach", desc: "Cold outreach DMs" },
  { value: "nurture", label: "Nurture", desc: "Lead nurturing" },
  { value: "support", label: "Support", desc: "Post-sale support" },
];

function slugify(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

export default function ChannelsPage() {
  const [selectedWs, setSelectedWs] = useState<string>("");
  const [testing, setTesting] = useState<string | null>(null);
  const [sending, setSending] = useState<string | null>(null);
  const [dmInputs, setDmInputs] = useState<Record<string, { target: string; message: string }>>({});
  const [cfgInputs, setCfgInputs] = useState<Record<string, Record<string, string>>>({});
  const [addOpen, setAddOpen] = useState(false);
  const [newCh, setNewCh] = useState({ platform: "telegram", label: "", mode: "cs" });

  const { data: wsData, mutate: mutWs } = useSWR<{ workspaces: Workspace[] }>(
    "/api/v1/channels/workspaces",
    fetcher
  );
  const { data: chData, mutate: mutCh } = useSWR<{ channels: Channel[] }>(
    selectedWs
      ? `/api/v1/channels/channels?workspace_id=${selectedWs}`
      : "/api/v1/channels/channels",
    fetcher
  );

  const workspaces = wsData?.workspaces ?? [];
  const channels = chData?.channels ?? [];

  const { data: personasData } = useSWR<{ personas: { id: string; name: string; scope: string }[] }>(
    "/api/v1/personas",
    fetcher
  );
  const personas = personasData?.personas ?? [];

  const { data: assignmentsData } = useSWR<{ assignments: { channel_id: string; mode: string; persona_id: string; persona_name: string }[] }>(
    channels.length > 0 ? "/api/v1/personas/assignments" : null,
    fetcher
  );
  const assignments = assignmentsData?.assignments ?? [];

  useEffect(() => {
    if (!selectedWs && workspaces.length > 0) setSelectedWs(workspaces[0].id);
  }, [workspaces, selectedWs]);

  useEffect(() => {
    const inputs: Record<string, Record<string, string>> = {};
    for (const ch of channels) {
      if (ch.config && typeof ch.config === "object") inputs[ch.id] = { ...ch.config };
    }
    setCfgInputs(inputs);
  }, [channels]);

  async function saveConfig(id: string) {
    await patchJSON(`/api/v1/channels/channels/${id}`, { config: cfgInputs[id] || {} });
    mutCh();
  }
  async function toggleMode(id: string, mode: string) {
    await patchJSON(`/api/v1/channels/channels/${id}`, { mode });
    mutCh();
  }
  async function toggleEnabled(id: string, en: boolean) {
    await patchJSON(`/api/v1/channels/channels/${id}`, { enabled: en ? 1 : 0 });
    mutCh();
  }
  async function testChannel(id: string) {
    setTesting(id);
    try {
      const res = await fetch(`/api/v1/channels/channels/${id}/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-API-Key": "dev" },
      });
      const d = await res.json();
      const result = d.data || d;
      alert(result.success ? `Connected as @${result.username}` : `Failed: ${result.error}`);
    } catch (e) {
      alert(`Error: ${e}`);
    } finally {
      setTesting(null);
      mutCh();
    }
  }
  async function sendDM(id: string) {
    const dm = dmInputs[id];
    if (!dm?.target || !dm?.message) return;
    setSending(id);
    try {
      const res = await fetch(`/api/v1/channels/channels/${id}/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-API-Key": "dev" },
        body: JSON.stringify({ recipient: dm.target, message: dm.message }),
      });
      const d = await res.json();
      alert(d.sent ? `Sent to ${dm.target}` : `Failed: ${JSON.stringify(d)}`);
    } catch (e) {
      alert(`Error: ${e}`);
    } finally {
      setSending(null);
    }
  }
  async function delChannel(id: string) {
    if (!confirm("Delete this channel?")) return;
    await deleteJSON(`/api/v1/channels/channels/${id}`);
    mutCh();
  }
  async function createChannel() {
    const wsId = selectedWs || workspaces[0]?.id || "default";
    await postJSON("/api/v1/channels/channels", {
      workspace_id: wsId,
      platform: newCh.platform,
      label: newCh.label || PLATFORM_CFG[newCh.platform]?.label || newCh.platform,
      mode: newCh.mode,
      config: {},
    });
    setAddOpen(false);
    setNewCh({ platform: "telegram", label: "", mode: "cs" });
    mutCh();
  }
  async function createWorkspace() {
    const name = prompt("Workspace name:");
    if (!name) return;
    await postJSON("/api/v1/channels/workspaces", { id: slugify(name), name });
    mutWs();
    setSelectedWs(slugify(name));
  }

  async function assignPersona(channelId: string, mode: string, personaId: string) {
    if (!personaId) {
      await deleteJSON(`/api/v1/personas/assignments/${encodeURIComponent(channelId)}/${mode}`);
    } else {
      await postJSON("/api/v1/personas/assignments", { channel_id: channelId, mode, persona_id: personaId });
    }
  }

  function getPersonaForChannel(chId: string, mode: string) {
    return assignments.find((a) => a.channel_id === chId && a.mode === mode);
  }

  function filteredPersonas(scope: string) {
    return personas.filter((p) => p.scope === scope || p.scope === "universal");
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Radio className="h-6 w-6 text-orange-500" /> Channels
        </h1>
        <div className="flex items-center gap-2">
          <Select value={selectedWs} onValueChange={(v) => v && setSelectedWs(v)}>
            <SelectTrigger className="w-56 bg-neutral-900 border-neutral-800">
              <SelectValue placeholder="Select workspace" />
            </SelectTrigger>
            <SelectContent>
              {workspaces.map((ws) => (
                <SelectItem key={ws.id} value={ws.id}>
                  {ws.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm" onClick={createWorkspace} className="border-neutral-700">
            <Plus className="h-3 w-3 mr-1" /> Workspace
          </Button>
          <Dialog open={addOpen} onOpenChange={setAddOpen}>
            <DialogTrigger
              render={<Button size="sm" className="bg-orange-600 hover:bg-orange-700" />}
            >
              <Plus className="h-3 w-3 mr-1" /> Add Channel
            </DialogTrigger>
            <DialogContent className="bg-neutral-900 border-neutral-800">
              <DialogHeader>
                <DialogTitle>Add Channel</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Platform</Label>
                    <Select value={newCh.platform} onValueChange={(v) => v && setNewCh({ ...newCh, platform: v })}>
                    <SelectTrigger className="bg-neutral-800 border-neutral-700">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(PLATFORM_CFG).map(([k, c]) => {
                        const I = c.icon;
                        return (
                          <SelectItem key={k} value={k}>
                            <span className="flex items-center gap-2">
                              <I className="h-3 w-3" />
                              {c.label}
                            </span>
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Label</Label>
                  <Input
                    value={newCh.label}
                    onChange={(e) => setNewCh({ ...newCh, label: e.target.value })}
                    placeholder={`My ${PLATFORM_CFG[newCh.platform]?.label || "Channel"}`}
                    className="bg-neutral-800 border-neutral-700"
                  />
                </div>
                <div>
                  <Label>Mode</Label>
                    <Select value={newCh.mode} onValueChange={(v) => v && setNewCh({ ...newCh, mode: v })}>
                    <SelectTrigger className="bg-neutral-800 border-neutral-700">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {MODE_OPTIONS.map((m) => (
                        <SelectItem key={m.value} value={m.value}>
                          {m.label} &mdash; {m.desc}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={createChannel} className="w-full bg-orange-600 hover:bg-orange-700">
                  Create Channel
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {channels.length === 0 && (
        <p className="text-center text-neutral-500 py-12">
          No channels yet. Click &ldquo;Add Channel&rdquo; to get started.
        </p>
      )}

      {channels.map((ch) => {
        const pcfg = PLATFORM_CFG[ch.platform] || PLATFORM_CFG.whatsapp;
        const PIcon = pcfg.icon;
        const lcfg = cfgInputs[ch.id] || {};
        return (
          <Card key={ch.id} className="bg-neutral-900 border-neutral-800">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2 text-base">
                  <div className={`p-1.5 rounded ${pcfg.color} text-white`}>
                    <PIcon className="h-4 w-4" />
                  </div>
                  {ch.label}
                  <span className="text-neutral-500 font-normal text-sm">{pcfg.label}</span>
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Select value={ch.mode} onValueChange={(v) => v && toggleMode(ch.id, v)}>
                    <SelectTrigger className="h-7 w-32 bg-neutral-800 border-neutral-700 text-xs">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {MODE_OPTIONS.map((m) => (
                        <SelectItem key={m.value} value={m.value}>
                          {m.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Badge
                    variant={ch.connected ? "default" : "secondary"}
                    className={ch.connected ? "bg-green-600 text-xs" : "bg-neutral-700 text-xs"}
                  >
                    {ch.connected ? (ch.username ? `@${ch.username}` : "Connected") : "Disconnected"}
                  </Badge>
                  <Button
                    size="sm"
                    variant={ch.enabled ? "destructive" : "outline"}
                    className="h-7 text-xs"
                    onClick={() => toggleEnabled(ch.id, !ch.enabled)}
                  >
                    {ch.enabled ? "Disable" : "Enable"}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-7 text-xs border-neutral-700"
                    onClick={() => testChannel(ch.id)}
                    disabled={testing === ch.id}
                  >
                    {testing === ch.id ? <Loader2 className="h-3 w-3 animate-spin" /> : <TestTube className="h-3 w-3" />}
                    Test
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-7 text-xs text-neutral-500 hover:text-red-500"
                    onClick={() => delChannel(ch.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <span className="text-xs text-neutral-500 w-14">Persona:</span>
                <select
                  value={getPersonaForChannel(ch.id, ch.mode)?.persona_id || ""}
                  onChange={(e) => assignPersona(ch.id, ch.mode, e.target.value)}
                  className="h-7 rounded-md bg-neutral-800 border border-neutral-700 text-xs px-2 flex-1 max-w-xs"
                >
                  <option value="">Default</option>
                  {filteredPersonas(ch.mode === "cs" || ch.mode === "support" ? "cs" : ch.mode === "coldcall" || ch.mode === "nurture" ? "outreach" : "universal").map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
                <span className="text-xs text-neutral-600">
                  {getPersonaForChannel(ch.id, ch.mode)?.persona_name || "Inherited"}
                </span>
              </div>
              {pcfg.fields.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs text-neutral-500">
                    {ch.platform === "instagram" && "Login to Instagram web \u2192 DevTools \u2192 Application \u2192 Cookies"}
                    {ch.platform === "twitter" && "Login to x.com \u2192 DevTools \u2192 Application \u2192 Cookies"}
                    {ch.platform === "telegram" && "Get API credentials from my.telegram.org, generate session string with Telethon"}
                    {ch.platform === "email" && "Configure email sending credentials"}
                  </p>
                  <div className="grid grid-cols-2 gap-2">
                    {pcfg.fields.map((f) => (
                      <div key={f.key} className="space-y-1">
                        <Label className="text-xs text-neutral-400">{f.label}</Label>
                        <Input
                          placeholder={f.placeholder}
                          value={lcfg[f.key] || ""}
                          type={f.secret ? "password" : "text"}
                          onChange={(e) =>
                            setCfgInputs({
                              ...cfgInputs,
                              [ch.id]: { ...lcfg, [f.key]: e.target.value },
                            })
                          }
                          className="bg-neutral-800 border-neutral-700 font-mono text-xs"
                        />
                      </div>
                    ))}
                  </div>
                  <Button
                    size="sm"
                    onClick={() => saveConfig(ch.id)}
                    className="bg-orange-600 hover:bg-orange-700 text-xs"
                  >
                    Save Config
                  </Button>
                </div>
              )}
              {(ch.connected || ch.enabled) && ch.platform !== "whatsapp" && (
                <div className="border-t border-neutral-800 pt-3 space-y-2">
                  <p className="text-xs text-neutral-500">
                    {ch.platform === "email" ? "Send a test email" : "Send a test DM"}
                  </p>
                  <div className="flex gap-2">
                    <Input
                      placeholder={ch.platform === "email" ? "recipient@example.com" : "@username"}
                      value={dmInputs[ch.id]?.target || ""}
                      onChange={(e) => setDmInputs({ ...dmInputs, [ch.id]: { ...dmInputs[ch.id], target: e.target.value } })}
                      className={ch.platform === "email" ? "w-52 bg-neutral-800 border-neutral-700 text-sm" : "w-40 bg-neutral-800 border-neutral-700 text-sm"}
                    />
                    <Input
                      placeholder="Message"
                      value={dmInputs[ch.id]?.message || ""}
                      onChange={(e) => setDmInputs({ ...dmInputs, [ch.id]: { ...dmInputs[ch.id], message: e.target.value } })}
                      className="bg-neutral-800 border-neutral-700 text-sm"
                    />
                    <Button
                      size="sm"
                      onClick={() => sendDM(ch.id)}
                      disabled={sending === ch.id}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      {sending === ch.id ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : ch.platform === "email" ? (
                        <Mail className="h-3 w-3" />
                      ) : (
                        <Send className="h-3 w-3" />
                      )}
                      Send
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
