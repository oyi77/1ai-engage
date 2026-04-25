"use client";

import { useState } from "react";
import useSWR from "swr";
import { fetcher, fetchBroadcastLists, createBroadcastList, fetchBroadcastSends, getBroadcastStats, type BroadcastList, type BroadcastSend } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Megaphone, Plus, Users, Send, Mail, BarChart3 } from "lucide-react";

const sendStatusColors: Record<string, string> = {
  draft: "bg-gray-500",
  scheduled: "bg-yellow-500",
  sending: "bg-blue-500",
  completed: "bg-green-500",
  cancelled: "bg-red-500",
};

export default function BroadcastsPage() {
  const [lists, setLists] = useState<BroadcastList[]>([]);
  const [sends, setSends] = useState<BroadcastSend[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [newList, setNewList] = useState({ name: "", description: "" });

  const { data: listsData, mutate: mutateLists } = useSWR("/api/v1/broadcast-lists", fetcher as any, {
    onSuccess: (d: any) => { setLists(d.lists || []); setLoading(false); },
  });

  const { data: sendsData, mutate: mutateSends } = useSWR("/api/v1/broadcast-sends", fetcher as any, {
    onSuccess: (d: any) => { setSends(d.sends || []); },
  });

  const { data: stats } = useSWR("/api/v1/broadcasts/stats/overview", fetcher as any);

  const handleCreateList = async () => {
    if (!newList.name) return;
    await createBroadcastList(newList);
    setNewList({ name: "", description: "" });
    setCreateOpen(false);
    mutateLists();
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Megaphone className="h-6 w-6" />
          Broadcasts
        </h1>
        <Button onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4 mr-1" />
          New List
        </Button>
      </div>

      {stats && (
        <div className="grid grid-cols-3 gap-4">
          <Card><CardContent className="pt-4 text-center"><div className="text-2xl font-bold">{stats.total_lists}</div><div className="text-xs text-muted-foreground">Lists</div></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><div className="text-2xl font-bold">{stats.total_sends}</div><div className="text-xs text-muted-foreground">Campaigns</div></CardContent></Card>
          <Card><CardContent className="pt-4 text-center"><div className="text-2xl font-bold">{stats.total_recipients}</div><div className="text-xs text-muted-foreground">Recipients</div></CardContent></Card>
        </div>
      )}

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Create Broadcast List</DialogTitle></DialogHeader>
          <div className="space-y-4 mt-4">
            <div>
              <label className="text-sm font-medium">Name</label>
              <Input value={newList.name} onChange={(e) => setNewList({ ...newList, name: e.target.value })} placeholder="List name" />
            </div>
            <div>
              <label className="text-sm font-medium">Description</label>
              <Textarea value={newList.description} onChange={(e) => setNewList({ ...newList, description: e.target.value })} rows={2} placeholder="List description" />
            </div>
            <Button onClick={handleCreateList} className="w-full">Create List</Button>
          </div>
        </DialogContent>
      </Dialog>

      <Tabs defaultValue="lists">
        <TabsList>
          <TabsTrigger value="lists"><Users className="h-4 w-4 mr-1" /> Lists</TabsTrigger>
          <TabsTrigger value="campaigns"><Send className="h-4 w-4 mr-1" /> Campaigns</TabsTrigger>
        </TabsList>

        <TabsContent value="lists" className="space-y-3 mt-4">
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">Loading...</div>
          ) : lists.length === 0 ? (
            <Card><CardContent className="text-center py-8 text-muted-foreground">No broadcast lists yet.</CardContent></Card>
          ) : (
            lists.map((list) => (
              <Card key={list.id}>
                <CardContent className="flex items-center justify-between pt-4">
                  <div>
                    <div className="font-medium">{list.name}</div>
                    {list.description && <div className="text-sm text-muted-foreground">{list.description}</div>}
                    <div className="text-xs text-muted-foreground mt-1">{list.total_recipients} recipients</div>
                  </div>
                  <div className="flex items-center gap-2">
                    {list.is_active ? (
                      <Badge className="bg-green-500">Active</Badge>
                    ) : (
                      <Badge variant="secondary">Inactive</Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        <TabsContent value="campaigns" className="space-y-3 mt-4">
          {sends.length === 0 ? (
            <Card><CardContent className="text-center py-8 text-muted-foreground">No campaigns yet. Create a broadcast list first, then start a campaign.</CardContent></Card>
          ) : (
            sends.map((send) => (
              <Card key={send.id}>
                <CardContent className="pt-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="font-medium">{send.name}</div>
                    <Badge className={sendStatusColors[send.status] || "bg-gray-500"}>{send.status}</Badge>
                  </div>
                  {send.subject && <div className="text-sm text-muted-foreground">{send.subject}</div>}
                  <div className="text-xs text-muted-foreground line-clamp-2">{send.content}</div>
                  <div className="grid grid-cols-5 gap-2 text-center text-xs">
                    <div><div className="font-bold">{send.total_recipients}</div><div className="text-muted-foreground">Total</div></div>
                    <div><div className="font-bold text-blue-500">{send.sent_count}</div><div className="text-muted-foreground">Sent</div></div>
                    <div><div className="font-bold text-green-500">{send.delivered_count}</div><div className="text-muted-foreground">Delivered</div></div>
                    <div><div className="font-bold text-purple-500">{send.opened_count}</div><div className="text-muted-foreground">Opened</div></div>
                    <div><div className="font-bold text-orange-500">{send.clicked_count}</div><div className="text-muted-foreground">Clicked</div></div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}