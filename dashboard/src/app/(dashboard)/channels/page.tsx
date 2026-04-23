"use client";

import { useState } from "react";
import useSWR from "swr";
import { fetcher, postJSON, type WANumber } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2, Plug, Send, TestTube, Radio } from "lucide-react";

interface ChannelStatus {
  channel: string;
  wa_number_id: string;
  enabled: boolean;
  connected: boolean;
  username: string;
  last_check: string;
  label: string;
}

export default function ChannelsPage() {
  const { data: waData, isLoading: waLoad } = useSWR<{ numbers: WANumber[] }>("/api/v1/agents/wa/sessions", fetcher);
  const [selectedWA, setSelectedWA] = useState<string>("");
  const [testing, setTesting] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [dmTarget, setDmTarget] = useState("");
  const [dmMessage, setDmMessage] = useState("");
  const [cookieInputs, setCookieInputs] = useState<Record<string, Record<string, string>>>({});

  const waId = selectedWA || waData?.numbers[0]?.id || "";
  const { data: channelData, mutate } = useSWR<{ channels: Record<string, ChannelStatus> }>(
    waId ? `/api/v1/channels/${waId}` : null,
    fetcher
  );

  if (waLoad) {
    return <div className="p-6 flex items-center justify-center h-[50vh]"><Loader2 className="h-8 w-8 animate-spin text-orange-500" /></div>;
  }

  const channels = channelData?.channels ?? {};
  const igCookies = cookieInputs.instagram || {};
  const twCookies = cookieInputs.twitter || {};

  async function saveCookies(channel: string, cookies: Record<string, string>) {
    await postJSON(`/api/v1/channels/${waId}/${channel}/cookies`, { cookies });
    mutate();
  }

  async function toggleChannel(channel: string, enabled: boolean) {
    await postJSON(`/api/v1/channels/${waId}/${channel}/enable`, { enabled });
    mutate();
  }

  async function testChannel(channel: string) {
    setTesting(channel);
    try {
      const res = await fetch(`/api/v1/channels/${waId}/${channel}/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Api-Key": "dev" },
      });
      const data = await res.json();
      if (data.success) {
        alert(`Connected as @${data.username}`);
      } else {
        alert(`Connection failed: ${data.error}`);
      }
    } catch (e) {
      alert(`Test error: ${e}`);
    } finally {
      setTesting(null);
      mutate();
    }
  }

  async function sendTestDM(channel: string) {
    if (!dmTarget || !dmMessage) return;
    setSending(true);
    try {
      const res = await fetch(`/api/v1/channels/${waId}/${channel}/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Api-Key": "dev" },
        body: JSON.stringify({ username: dmTarget, message: dmMessage }),
      });
      const data = await res.json();
      alert(data.status === "sent" ? `DM sent to @${dmTarget}` : `Failed: ${JSON.stringify(data)}`);
    } catch (e) {
      alert(`Send error: ${e}`);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Channels</h1>
        <Select value={selectedWA} onValueChange={(v) => v && setSelectedWA(v)}>
          <SelectTrigger className="w-56 bg-neutral-900 border-neutral-800">
            <SelectValue placeholder="Select WA Number" />
          </SelectTrigger>
          <SelectContent>
            {waData?.numbers.map((n) => (
              <SelectItem key={n.id} value={n.id}>{n.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {Object.entries(channels).map(([channel, status]) => (
        <Card key={channel} className="bg-neutral-900 border-neutral-800">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Radio className="h-4 w-4" />
                {status.label || channel}
              </CardTitle>
              <div className="flex items-center gap-2">
                <Badge variant={status.connected ? "default" : "secondary"} className={status.connected ? "bg-green-600" : "bg-neutral-700"}>
                  {status.connected ? `@${status.username}` : "Disconnected"}
                </Badge>
                <Button
                  size="sm"
                  variant={status.enabled ? "destructive" : "outline"}
                  className="h-7 text-xs"
                  onClick={() => toggleChannel(channel, !status.enabled)}
                >
                  {status.enabled ? "Disable" : "Enable"}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="h-7 text-xs border-neutral-700"
                  onClick={() => testChannel(channel)}
                  disabled={testing === channel}
                >
                  {testing === channel ? <Loader2 className="h-3 w-3 animate-spin" /> : <TestTube className="h-3 w-3" />}
                  Test
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {channel === "instagram" && (
              <div className="space-y-2">
                <p className="text-xs text-neutral-500">
                  Login to Instagram web → DevTools → Application → Cookies → copy <code className="text-orange-400">sessionid</code> value
                </p>
                <div className="flex gap-2">
                  <Input
                    placeholder="sessionid cookie value"
                    value={igCookies.sessionid || ""}
                    onChange={(e) => setCookieInputs({ ...cookieInputs, instagram: { ...igCookies, sessionid: e.target.value } })}
                    className="bg-neutral-800 border-neutral-700 font-mono text-sm"
                  />
                  <Button size="sm" onClick={() => saveCookies("instagram", igCookies)} className="bg-orange-600 hover:bg-orange-700">
                    Save
                  </Button>
                </div>
              </div>
            )}

            {channel === "twitter" && (
              <div className="space-y-2">
                <p className="text-xs text-neutral-500">
                  Login to x.com → DevTools → Application → Cookies → copy <code className="text-orange-400">auth_token</code> and <code className="text-orange-400">ct0</code>
                </p>
                <div className="grid grid-cols-3 gap-2">
                  <Input
                    placeholder="auth_token"
                    value={twCookies.auth_token || ""}
                    onChange={(e) => setCookieInputs({ ...cookieInputs, twitter: { ...twCookies, auth_token: e.target.value } })}
                    className="bg-neutral-800 border-neutral-700 font-mono text-sm"
                  />
                  <Input
                    placeholder="ct0"
                    value={twCookies.ct0 || ""}
                    onChange={(e) => setCookieInputs({ ...cookieInputs, twitter: { ...twCookies, ct0: e.target.value } })}
                    className="bg-neutral-800 border-neutral-700 font-mono text-sm"
                  />
                  <Button size="sm" onClick={() => saveCookies("twitter", twCookies)} className="bg-orange-600 hover:bg-orange-700">
                    Save
                  </Button>
                </div>
              </div>
            )}

            {status.connected && (
              <div className="border-t border-neutral-800 pt-3 space-y-2">
                <p className="text-xs text-neutral-500">Send a test DM</p>
                <div className="flex gap-2">
                  <Input
                    placeholder="@username"
                    value={dmTarget}
                    onChange={(e) => setDmTarget(e.target.value)}
                    className="w-40 bg-neutral-800 border-neutral-700 text-sm"
                  />
                  <Input
                    placeholder="Message text"
                    value={dmMessage}
                    onChange={(e) => setDmMessage(e.target.value)}
                    className="bg-neutral-800 border-neutral-700 text-sm"
                  />
                  <Button size="sm" onClick={() => sendTestDM(channel)} disabled={sending} className="bg-blue-600 hover:bg-blue-700">
                    {sending ? <Loader2 className="h-3 w-3 animate-spin" /> : <Send className="h-3 w-3" />}
                    Send
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      ))}

      {!waId && (
        <p className="text-center text-neutral-500 py-12">Select a WA number to configure channels</p>
      )}
    </div>
  );
}
