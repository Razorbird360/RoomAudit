import { useState, useCallback, useRef } from "react";
import { motion } from "motion/react";
import { Upload } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { ResultCard } from "@/components/ResultCard";
import type { InspectResult } from "@/components/ResultCard";

export function Inspect() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<InspectResult | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setDragOver(false);
      const dropped = e.dataTransfer.files[0];
      if (dropped && dropped.type.startsWith("image/")) {
        handleFile(dropped);
      }
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragOver(false);
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selected = e.target.files?.[0];
      if (selected) {
        handleFile(selected);
      }
    },
    [handleFile]
  );

  const handleSubmit = useCallback(async () => {
    if (!file) return;
    setLoading(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("http://localhost:8000/inspect", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const data = (await res.json()) as InspectResult;
      setResult(data);
    } catch {
      toast.error("Inspection failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, [file]);

  return (
    <div className="flex flex-col items-center gap-6 py-12 mx-auto max-w-lg">
      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
        }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={cn(
          "w-full rounded-lg border-2 border-dashed p-8 text-center cursor-pointer transition-colors",
          dragOver
            ? "border-primary bg-muted"
            : "border-border hover:border-primary/50"
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleInputChange}
        />

        {preview ? (
          <img
            src={preview}
            alt="Selected room"
            className="mx-auto max-h-64 rounded-md object-contain"
          />
        ) : (
          <div className="flex flex-col items-center gap-2 text-muted-foreground">
            <Upload className="size-8" />
            <p className="font-body text-sm">
              Drop a room image here or click to browse
            </p>
          </div>
        )}
      </div>

      <button
        type="button"
        disabled={!file || loading}
        onClick={handleSubmit}
        className="bg-primary text-primary-foreground px-6 py-2.5 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <motion.span
              className="inline-block size-4 rounded-full border-2 border-primary-foreground border-t-transparent"
              animate={{ rotate: 360 }}
              transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
            />
            Inspecting...
          </span>
        ) : (
          "Inspect Room"
        )}
      </button>

      {result && <ResultCard result={result} />}
    </div>
  );
}
