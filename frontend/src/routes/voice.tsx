import { createFileRoute } from "@tanstack/react-router";
import { Mic, Play, Square, Trash2, Upload } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { AppShell } from "@/components/wms/app-shell";
import { Btn, Panel } from "@/components/wms/ui-bits";

export const Route = createFileRoute("/voice")({
  head: () => ({
    meta: [
      { title: "Voice Data Entry — Whitfield WMS" },
      {
        name: "description",
        content:
          "Capture inbound inventory hands-free: record or upload audio, review the transcript and confirm parsed item fields.",
      },
      { property: "og:title", content: "Voice Data Entry — Whitfield WMS" },
      {
        property: "og:description",
        content: "Hands-free inventory logging with transcript review and confidence scoring.",
      },
    ],
  }),
  component: VoicePage,
});

const parsed = [
  { field: "Barcode", value: "012345678905", confidence: 95 },
  { field: "Product", value: "Widget A — Steel Bracket", confidence: 88 },
  { field: "Weight", value: "2.5 lbs", confidence: 92 },
  { field: "Dimensions", value: '12in x 8in', confidence: 74 },
  { field: "Damage", value: "None reported", confidence: 61 },
];

function VoicePage() {
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [hasClip, setHasClip] = useState(false);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (recording) {
      timer.current = setInterval(() => setSeconds((s) => s + 1), 1000);
    } else if (timer.current) {
      clearInterval(timer.current);
    }
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, [recording]);

  const clock = `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;

  return (
    <AppShell
      crumbs={[{ label: "Dashboard", to: "/" }, { label: "Voice Pipeline" }]}
      title="Voice Data Entry"
    >
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel>
          <h3>Audio Capture</h3>
          <div className="mt-8 flex flex-col items-center">
            <button
              aria-label={recording ? "Stop recording" : "Start recording"}
              onClick={() => {
                if (recording) {
                  setHasClip(true);
                  toast.success("Recording captured");
                } else {
                  setSeconds(0);
                }
                setRecording((r) => !r);
              }}
              className={
                "grid size-20 place-items-center rounded-full bg-primary text-primary-foreground transition-transform hover:scale-105 " +
                (recording ? "pulse-record" : "")
              }
            >
              {recording ? <Square className="size-7" /> : <Mic className="size-8" />}
            </button>
            <p className="mt-4 text-sm text-muted-foreground">
              {recording
                ? `Recording... ${clock}`
                : hasClip
                  ? `Ready to upload · ${clock}`
                  : "Click to start recording"}
            </p>
            <div className="mt-6 flex gap-3">
              <Btn variant="secondary" disabled={!hasClip}>
                <Play className="size-4" /> Play
              </Btn>
              <Btn
                variant="secondary"
                disabled={!hasClip}
                onClick={() => {
                  setHasClip(false);
                  setSeconds(0);
                }}
              >
                <Trash2 className="size-4" /> Clear
              </Btn>
              <Btn disabled={!hasClip} onClick={() => toast.success("Audio uploaded for parsing")}>
                <Upload className="size-4" /> Upload
              </Btn>
            </div>
          </div>

          <div className="mt-8">
            <p className="label-xs text-muted-foreground uppercase">Or upload audio file</p>
            <label className="mt-2 flex h-[120px] cursor-pointer flex-col items-center justify-center rounded-md border-2 border-dashed border-border transition-colors hover:border-primary hover:bg-primary/5">
              <Upload className="size-8 text-muted-foreground" />
              <span className="mt-2 text-sm text-muted-foreground">
                Drag files here or click to browse
              </span>
              <span className="mt-1 text-[11px] text-muted-foreground">MP3, WAV, M4A · max 10MB</span>
              <input type="file" accept="audio/*" className="hidden" />
            </label>
          </div>
        </Panel>

        <Panel className="flex flex-col">
          <h3>Parsed Data</h3>
          <div className="mt-4 min-h-[160px] rounded-md border border-border bg-background p-4 font-mono text-[13px] leading-relaxed text-foreground">
            "Logging barcode zero one two three four five six seven eight nine zero five, Widget A
            steel bracket, weight two point five pounds, twelve by eight inches, no visible damage,
            store in aisle A row four bin twelve."
          </div>

          <div className="mt-4 space-y-3">
            {parsed.map((p) => (
              <div key={p.field} className="grid grid-cols-[110px_1fr_120px] items-center gap-3">
                <span className="label-xs text-muted-foreground uppercase">{p.field}</span>
                <span className="truncate font-mono text-[13px]">{p.value}</span>
                <div className="flex items-center gap-2">
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-secondary">
                    <div
                      className={
                        "h-full rounded-full " +
                        (p.confidence >= 85
                          ? "bg-primary"
                          : p.confidence >= 70
                            ? "bg-warning"
                            : "bg-destructive")
                      }
                      style={{ width: `${p.confidence}%` }}
                    />
                  </div>
                  <span className="w-8 text-right text-[11px] text-muted-foreground">
                    {p.confidence}%
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-auto flex justify-end gap-3 pt-6">
            <Btn variant="secondary">Discard</Btn>
            <Btn
              onClick={() =>
                toast.success("Item 012345678905 added to inventory", {
                  action: { label: "Undo", onClick: () => toast("Entry reverted") },
                })
              }
            >
              Confirm
            </Btn>
          </div>
        </Panel>
      </div>
    </AppShell>
  );
}
