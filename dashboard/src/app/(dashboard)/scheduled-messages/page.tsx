"use client";

import { useState } from "react";
import useSWR from "swr";
import { fetcher, fetchScheduledMessages, createScheduledMessage, getScheduledStats, type ScheduledMessage } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { CalendarClock, Plus, Trash2, Clock, Mail, MessageSquare, CheckCircle, XCircle, Loader2 } from "lucide-react";

const statusConfig: Record<string, { color: string; icon: React.ReactNode }> = {
  pending: { color: "bg-yellow-500", icon: <Clock className="h-4 w-4" /> },
  processing: { color: "bg-blue-500", icon: <Loader2 className="h-4 w-4 animate-spin" /> },
  sent: { color: "bg-green-500", icon: <CheckCircle className="h-4 w-4" /> },
  failed: { color: "bg-red-500", icon: <XCircle className="h-4 w-4" /> },
  cancelled: { color: "bg-gray-500", icon: <XCircle className="h-4 w-4" /> },
};

export default function ScheduledMessagesPage() {
  const [messages, setMessages] = useState<ScheduledMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [newMsg, setNewMsg] = useState({ content: "", subject: "", scheduled_at: "", channel: "email" });
  const [stats, setStats] = useState<{ pending: number; sent: number; failed: number; processing: number; total: number } | null>(null);

  const { data, mutate } = useSWR("/api/v1/scheduled-messages", fetcher as any, {
    onSuccess: (d: any) => { setMessages(d.messages); setLoading(false); },
  });

  const { data: statsData } = useSWR("/api/v1/scheduled-messages/stats/overview", fetcher as any, {
    onSuccess: (d: any) => setStats(d),
  });

  const handleCreate = async () => {
    if (!newMsg.content || !newMsg.scheduled_at) return;
    await createScheduledMessage({
      content: newMsg.content,
      subject: newMsg.subject || undefined,
      scheduled_at: newMsg.scheduled_at,
      channel: newMsg.channel,
    });
    setNewMsg({ content: "", subject: "", scheduled_at: "", channel: "email" });
    setCreateOpen(false);
    mutate();
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Cancel this scheduled message?")) return;
    try {
      const res = await fetch(`/api/v1/scheduled-messages/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error(`API ${res.status}`);
      mutate();
    } catch (err) {
      console.error("Failed to delete message:", err);
    }
  };

  const channelIcons: Record<string, React.ReactNode> = {
    email: <Mail className="h-4 w-4" />,
    whatsapp: <MessageSquare className="h-4 w-4" />,
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <CalendarClock className="h-6 w-6" />
          Scheduled Messages
        </h1>
        <Button onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4 mr-1" />
          Schedule Message
        </Button>
      </div>

      {stats && (
        <div className="grid grid-cols-4 gap-4">
          <Card><CardContent className="pt-4 text-center"><div className="text-2xl font-bold text-yellow-500">{stats.pending}</div><div className="text-xs text-muted-foreground">Pending</div></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><div className="text-2xl font-bold text-blue-500">{stats.processing}</div><div className="text-xs text-muted-foreground">Processing</div></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><div className="text-2xl font-bold text-green-500">{stats.sent}</div><div className="text-xs text-muted-foreground">Sent</div></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><div className="text-2xl font-bold text-red-500">{stats.failed}</div><div className="text-xs text-muted-foreground">Failed</div></CardContent></Card>
        </div>
      )}

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Schedule Message</DialogTitle></DialogHeader>
          <div className="space-y-4 mt-4">
            <div>
              <label className="text-sm font-medium">Channel</label>
              <select className="w-full border rounded p-2" value={newMsg.channel} onChange={(e) => setNewMsg({ ...newMsg, channel: e.target.value })}>
                <option value="email">Email</option>
                <option value="whatsapp">WhatsApp</option>
              </select>
            </div>
            {newMsg.channel === "email" && (
              <div>
                <label className="text-sm font-medium">Subject</label>
                <Input value={newMsg.subject} onChange={(e) => setNewMsg({ ...newMsg, subject: e.target.value })} placeholder="Email subject" />
              </div>
            )}
            <div>
              <label className="text-sm font-medium">Content</label>
              <Textarea value={newMsg.content} onChange={(e) => setNewMsg({ ...newMsg, content: e.target.value })} rows={4} placeholder="Message content" />
            </div>
            <div>
              <label className="text-sm font-medium">Schedule At</label>
              <Input type="datetime-local" value={newMsg.scheduled_at} onChange={(e) => setNewMsg({ ...newMsg, scheduled_at: e.target.value })} />
            </div>
            <Button onClick={handleCreate} className="w-full">Schedule Message</Button>
          </div>
        </DialogContent>
      </Dialog>

      {loading ? (
        <div className="text-center py-12 text-muted-foreground">Loading scheduled messages...</div>
      ) : messages.length === 0 ? (
        <Card><CardContent className="text-center py-12 text-muted-foreground">No scheduled messages yet.</CardContent></Card>
      ) : (
        <div className="space-y-3">
          {messages.map((msg) => {
            const config = statusConfig[msg.status] || statusConfig.pending;
            return (
              <Card key={msg.id}>
                <CardContent className="flex items-center gap-4 pt-4">
                  <div className="flex-shrink-0">{channelIcons[msg.channel] || <Mail className="h-4 w-4" />}</div>
                  <div className="flex-1 min-w-0">
                    {msg.subject && <div className="font-medium truncate">{msg.subject}</div>}
                    <div className="text-sm text-muted-foreground line-clamp-2">{msg.content}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      Scheduled: {new Date(msg.scheduled_at).toLocaleString()}
                    </div>
                  </div>
                  <Badge className={config.color}>{msg.status}</Badge>
                  {(msg.status === "pending" || msg.status === "failed") && (
                    <Button size="sm" variant="ghost" onClick={() => handleDelete(msg.id)} className="text-destructive">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}