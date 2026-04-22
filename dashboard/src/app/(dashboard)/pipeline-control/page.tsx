"use client";

import { useState } from "react";
import { postJSON, type PipelineScript } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Play, Loader2, MapPin, Search } from "lucide-react";

const STATIC_SCRIPTS: PipelineScript[] = [
  { key: "scrape", script: "scraper.py" },
  { key: "enrich", script: "enricher.py" },
  { key: "research", script: "researcher.py" },
  { key: "generate", script: "generator.py" },
  { key: "review", script: "reviewer.py" },
  { key: "blast", script: "blaster.py" },
  { key: "track", script: "reply_tracker.py" },
  { key: "followup", script: "followup.py" },
  { key: "sync", script: "sheets_sync.py" },
];

const LOCATIONS = [
  "Jakarta", "Surabaya", "Bandung", "Bali", "Yogyakarta",
  "Semarang", "Medan", "Makassar", "Malang", "Palembang",
];

const RECOMMENDED_QUERIES = [
  "Digital Agency", "Coffee Shop", "Restaurant", "Clinic", "E-commerce",
  "Law Firm", "Real Estate", "Gym Fitness", "Beauty Salon", "Dental Clinic",
  "Hotel", "Photography Studio", "Accounting Firm", "Interior Design", "Bakery",
  "Catering Service", "Logistics Company", "IT Consulting", "Fashion Boutique", "Car Dealer",
];

export default function PipelineControlPage() {
  const [query, setQuery] = useState("Digital Agency");
  const [location, setLocation] = useState("Jakarta");
  const [running, setRunning] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, string>>({});

  const scripts = STATIC_SCRIPTS;
  const fullQuery = `${query} in ${location}`;

  async function runScript(scriptObj: PipelineScript) {
    const { key, script } = scriptObj;
    setRunning(script);
    setResults((prev) => ({ ...prev, [key]: "Running..." }));
    try {
      const args = query && script === "scraper.py" ? { query: fullQuery } : {};
      const res = await postJSON<{ status?: string; message?: string; ok?: boolean; error?: string }>(`/api/v1/agents/stages/${key}/start`, { args });
      setResults((prev) => ({ ...prev, [key]: res.status === "success" || res.ok ? `Started in background` : `Error: ${res.message || res.error}` }));
    } catch (e: any) {
      setResults((prev) => ({ ...prev, [key]: `Failed: ${e.message || e}` }));
    }
    setRunning(null);
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Run Pipeline</h1>

      <Card className="bg-neutral-900 border-neutral-800">
        <CardHeader><CardTitle className="flex items-center gap-2"><Search className="h-4 w-4" />Search Query</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. Coffee Shop"
              className="bg-neutral-800 border-neutral-700 flex-1"
            />
            <Select value={location} onValueChange={(v) => v && setLocation(v)}>
              <SelectTrigger className="w-44 bg-neutral-800 border-neutral-700">
                <MapPin className="h-3 w-3 mr-1 text-neutral-400" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LOCATIONS.map((loc) => (
                  <SelectItem key={loc} value={loc}>{loc}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="rounded-md bg-neutral-800/50 border border-neutral-700 px-3 py-2 text-sm">
            <span className="text-neutral-500">Full query: </span>
            <span className="text-orange-400 font-mono">{fullQuery}</span>
          </div>

          <div>
            <p className="text-xs text-neutral-500 mb-2">Recommended searches — click to apply:</p>
            <div className="flex flex-wrap gap-2">
              {RECOMMENDED_QUERIES.map((q) => (
                <button
                  key={q}
                  onClick={() => setQuery(q)}
                  className={`text-xs px-2.5 py-1 rounded-full border transition-colors ${
                    query === q
                      ? "bg-orange-600 border-orange-600 text-white"
                      : "bg-neutral-800 border-neutral-700 text-neutral-300 hover:border-orange-600 hover:text-orange-400"
                  }`}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {scripts.map((s) => (
          <Card key={s.key} className="bg-neutral-900 border-neutral-800">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold capitalize">{s.key}</h3>
                <Badge variant="secondary" className="bg-neutral-800 text-xs">{s.script}</Badge>
              </div>
              {results[s.key] && (
                <p className={`text-xs mb-2 ${results[s.key].startsWith("Error") || results[s.key].startsWith("Failed") ? "text-red-400" : "text-green-400"}`}>
                  {results[s.key]}
                </p>
              )}
              <Button
                onClick={() => runScript(s)}
                disabled={running !== null}
                className="w-full bg-orange-600 hover:bg-orange-700"
              >
                {running === s.script ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Play className="h-4 w-4 mr-2" />}
                Run
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

