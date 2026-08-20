import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { Loader2, Mic, Play, Square, Trash2, Upload } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { AppShell } from "@/components/wms/app-shell";
import { Btn, Field, Panel, Select } from "@/components/wms/ui-bits";
import { ProtectedRoute } from "@/lib/protected-route";
import { ticketsAPI, voiceAPI } from "@/lib/api";

export const Route = createFileRoute("/voice")({
  head: () => ({
    meta: [
      { title: "Voice Assistance — Whitfield WMS" },
      {
        name: "description",
        content:
          "Capture inbound inventory hands-free: record or upload audio, review the transcript and confirm parsed item fields.",
      },
    ],
  }),
  component: VoicePageWrapper,
});

type Draft = {
  id: string;
  ticket_id: string;
  transcript: string;
  parsed_data: {
    product_name?: string;
    width?: number;
    height?: number;
    weight?: number;
    fragile?: boolean;
    damage?: { flag: boolean; note: string | null };
  };
  confidence_scores: Record<string, number>;
};

function VoiceContent() {
  const [ticketId, setTicketId] = useState("");
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isParsing, setIsParsing] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [barcode, setBarcode] = useState("");
  const [overrideWeight, setOverrideWeight] = useState("");

  const timer = useRef<ReturnType<typeof setInterval> | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const { data: ticketsData, isLoading: ticketsLoading } = useQuery({
    queryKey: ["voice-tickets"],
    queryFn: () => ticketsAPI.getAll(0, 50),
    staleTime: 30000,
  });
  const tickets = (ticketsData as { tickets?: any[] } | undefined)?.tickets ?? [];

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

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        stream.getTracks().forEach((t) => t.stop());
      };
      recorder.start();
      mediaRecorderRef.current = recorder;
      setSeconds(0);
      setRecording(true);
    } catch (error) {
      toast.error("Microphone access denied or unavailable");
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
    toast.success("Recording captured");
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAudioBlob(file);
    setAudioUrl(URL.createObjectURL(file));
  };

  const clearClip = () => {
    setAudioBlob(null);
    setAudioUrl(null);
    setSeconds(0);
    setDraft(null);
  };

  const handleUploadAndParse = async () => {
    if (!audioBlob) return;
    if (!ticketId) {
      toast.error("Select a ticket before uploading");
      return;
    }
    setIsUploading(true);
    try {
      const file =
        audioBlob instanceof File ? audioBlob : new File([audioBlob], "recording.webm", { type: audioBlob.type });
      const transcribeRes = await voiceAPI.transcribe(file);
      const transcript = transcribeRes.transcript;

      setIsUploading(false);
      setIsParsing(true);
      const draftRes = await voiceAPI.parse(ticketId, transcript);
      setDraft(draftRes as Draft);
      setOverrideWeight(String((draftRes as Draft).parsed_data?.weight ?? ""));
      toast.success("Audio transcribed and parsed");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to process audio");
    } finally {
      setIsUploading(false);
      setIsParsing(false);
    }
  };

  const handleConfirm = async () => {
    if (!draft) return;
    if (!barcode.trim()) {
      toast.error("Barcode is required to confirm");
      return;
    }
    const weight = parseFloat(overrideWeight);
    if (!weight || weight <= 0) {
      toast.error("Enter a valid weight");
      return;
    }
    setIsConfirming(true);
    try {
      const item = await voiceAPI.confirm(draft.id, { barcode: barcode.trim(), override_weight: weight });
      toast.success(`Item ${(item as any).barcode || barcode} added to inventory`);
      setDraft(null);
      setBarcode("");
      setOverrideWeight("");
      clearClip();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to confirm item");
    } finally {
      setIsConfirming(false);
    }
  };

  const handleDiscard = () => {
    setDraft(null);
    setBarcode("");
    setOverrideWeight("");
    clearClip();
    toast("Draft discarded");
  };

  const scores = draft?.confidence_scores ?? {};
  const parsedRows = draft
    ? [
        { field: "Product", value: draft.parsed_data?.product_name ?? "—", confidence: scores["product_name"] },
        { field: "Weight", value: draft.parsed_data?.weight ? `${draft.parsed_data.weight} lbs` : "—", confidence: scores["weight"] },
        {
          field: "Dimensions",
          value:
            draft.parsed_data?.width && draft.parsed_data?.height
              ? `${draft.parsed_data.width}in x ${draft.parsed_data.height}in`
              : "—",
          confidence: scores["width"],
        },
        {
          field: "Damage",
          value: draft.parsed_data?.damage?.flag
            ? draft.parsed_data.damage.note || "Damage reported"
            : "None reported",
          confidence: scores["damage"],
        },
      ]
    : [];

  return (
    <AppShell
      crumbs={[{ label: "Dashboard", to: "/" }, { label: "Voice Assistance" }]}
      title="Voice Assistance"
    >
      <div className="mb-4">
        <label className="label-xs text-secondary-foreground">Target Ticket *</label>
        <Select
          className="mt-1 w-full max-w-sm"
          value={ticketId}
          onChange={(e) => setTicketId(e.target.value)}
          disabled={ticketsLoading}
        >
          <option value="">{ticketsLoading ? "Loading tickets..." : "Select a ticket"}</option>
          {tickets.map((t: any) => (
            <option key={t.id} value={t.ticket_id}>
              {t.ticket_id} · {t.status}
            </option>
          ))}
        </Select>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Panel>
          <h3>Audio Capture</h3>
          <div className="mt-8 flex flex-col items-center">
            <button
              aria-label={recording ? "Stop recording" : "Start recording"}
              onClick={() => (recording ? stopRecording() : startRecording())}
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
                : audioBlob
                  ? `Ready to upload · ${clock}`
                  : "Click to start recording"}
            </p>
            <div className="mt-6 flex gap-3">
              <Btn
                variant="secondary"
                disabled={!audioUrl}
                onClick={() => audioRef.current?.play()}
              >
                <Play className="size-4" /> Play
              </Btn>
              <Btn variant="secondary" disabled={!audioBlob} onClick={clearClip}>
                <Trash2 className="size-4" /> Clear
              </Btn>
              <Btn disabled={!audioBlob || isUploading || isParsing} onClick={handleUploadAndParse}>
                {isUploading || isParsing ? (
                  <Loader2 className="size-4 animate-spin" />
                ) : (
                  <Upload className="size-4" />
                )}
                {isUploading ? "Transcribing..." : isParsing ? "Parsing..." : "Upload"}
              </Btn>
            </div>
            {audioUrl && <audio ref={audioRef} src={audioUrl} className="hidden" />}
          </div>

          <div className="mt-8">
            <p className="label-xs text-muted-foreground uppercase">Or upload audio file</p>
            <label className="mt-2 flex h-[120px] cursor-pointer flex-col items-center justify-center rounded-md border-2 border-dashed border-border transition-colors hover:border-primary hover:bg-primary/5">
              <Upload className="size-8 text-muted-foreground" />
              <span className="mt-2 text-sm text-muted-foreground">
                Drag files here or click to browse
              </span>
              <span className="mt-1 text-[11px] text-muted-foreground">MP3, WAV, M4A, WEBM</span>
              <input
                ref={fileInputRef}
                type="file"
                accept="audio/*"
                className="hidden"
                onChange={handleFileUpload}
              />
            </label>
          </div>
        </Panel>

        <Panel className="flex flex-col">
          <h3>Parsed Data</h3>
          <div className="mt-4 min-h-[100px] rounded-md border border-border bg-background p-4 font-mono text-[13px] leading-relaxed text-foreground">
            {draft?.transcript || "Transcript will appear here after upload."}
          </div>

          {draft && (
            <>
              <div className="mt-4 space-y-3">
                {parsedRows.map((p) => (
                  <div key={p.field} className="grid grid-cols-[110px_1fr_120px] items-center gap-3">
                    <span className="label-xs text-muted-foreground uppercase">{p.field}</span>
                    <span className="truncate font-mono text-[13px]">{p.value}</span>
                    {typeof p.confidence === "number" && (
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-secondary">
                          <div
                            className={
                              "h-full rounded-full " +
                              (p.confidence >= 0.85
                                ? "bg-primary"
                                : p.confidence >= 0.7
                                  ? "bg-warning"
                                  : "bg-destructive")
                            }
                            style={{ width: `${Math.round(p.confidence * 100)}%` }}
                          />
                        </div>
                        <span className="w-8 text-right text-[11px] text-muted-foreground">
                          {Math.round(p.confidence * 100)}%
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="mt-4 grid grid-cols-2 gap-3">
                <div>
                  <label className="label-xs text-secondary-foreground">Barcode *</label>
                  <Field
                    className="mt-1"
                    value={barcode}
                    onChange={(e) => setBarcode(e.target.value)}
                    placeholder="Scan or enter barcode"
                  />
                </div>
                <div>
                  <label className="label-xs text-secondary-foreground">Confirmed Weight (lbs) *</label>
                  <Field
                    type="number"
                    className="mt-1"
                    value={overrideWeight}
                    onChange={(e) => setOverrideWeight(e.target.value)}
                  />
                </div>
              </div>
            </>
          )}

          <div className="mt-auto flex justify-end gap-3 pt-6">
            <Btn variant="secondary" disabled={!draft} onClick={handleDiscard}>
              Discard
            </Btn>
            <Btn disabled={!draft || isConfirming} onClick={handleConfirm}>
              {isConfirming && <Loader2 className="size-4 animate-spin" />}
              Confirm
            </Btn>
          </div>
        </Panel>
      </div>
    </AppShell>
  );
}

function VoicePageWrapper() {
  return (
    <ProtectedRoute requiredRoles={["OWNER", "MANAGER", "STAFF"]}>
      <VoiceContent />
    </ProtectedRoute>
  );
}
