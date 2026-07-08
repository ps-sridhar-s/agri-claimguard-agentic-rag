import { ChangeEvent, useMemo, useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";

export type ClaimPayload = {
  farmer_name: string;
  district: string;
  crop: string;
  season: string;
  date_of_loss: string;
  loss_reason: string;
  policy_id: string;
  area: string;
  estimated_loss: string;
  query: string;
};

type ClaimFormProps = {
  onResult: (result: unknown, claim: ClaimPayload) => void;
  onLog?: (message: string, tone?: "info" | "success" | "error") => void;
};

const initialForm: ClaimPayload = {
  farmer_name: "Ram Kumar",
  district: "Anantapur",
  crop: "Groundnut",
  season: "Kharif",
  date_of_loss: "2025-08-15",
  loss_reason: "Drought",
  policy_id: "PMFBY-2025",
  area: "4.2 acres",
  estimated_loss: "68000",
  query: "What is the eligibility for drought compensation?",
};

export default function ClaimForm({ onResult, onLog }: ClaimFormProps) {
  const [form, setForm] = useState<ClaimPayload>(initialForm);
  const [images, setImages] = useState<FileList | null>(null);
  const [pdfs, setPdfs] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const completion = useMemo(() => {
    const required = [
      form.farmer_name,
      form.district,
      form.crop,
      form.season,
      form.policy_id,
      form.loss_reason,
      form.date_of_loss,
      form.area,
      form.estimated_loss,
      form.query,
    ];

    return Math.round((required.filter(Boolean).length / required.length) * 100);
  }, [form]);

  const updateField = (field: keyof ClaimPayload, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const handleFileChange = (
    event: ChangeEvent<HTMLInputElement>,
    setter: (files: FileList | null) => void,
  ) => {
    setter(event.target.files);
  };

  const submit = async () => {
    setLoading(true);
    setError("");
    setSuccess("");
    onLog?.(`Submitting claim for ${form.farmer_name || "the farmer"}...`, "info");

    try {
      const endpoint = import.meta.env.VITE_API_URL || "/query";
      const response = await axios.post(endpoint, form, {
        headers: { "Content-Type": "application/json" },
      });
      const recommendation = response?.data?.recommendation ?? "received";
      const answer = response?.data?.answer ?? "The multi-agent review has completed.";
      const message = `Claim submitted successfully. Recommendation: ${recommendation}. ${answer}`;
      setSuccess(message);
      onLog?.(message, "success");
      onResult(response.data, form);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Request failed. Ensure the backend is running and the Vite proxy is available.";
      setError(message);
      onLog?.(`Submission failed: ${message}`, "error");
      onResult(null, form);
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.article
      className="claim-form glass-panel"
      id="claims"
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="section-heading compact">
        <div>
          <span className="eyebrow">Claim intake</span>
          <h2>Submit claim</h2>
        </div>
        <span className="completion-pill">{completion}%</span>
      </div>

      <div className="form-grid">
        <label>
          <span>Farmer Name</span>
          <input
            value={form.farmer_name}
            onChange={(event) => updateField("farmer_name", event.target.value)}
          />
        </label>
        <label>
          <span>Crop</span>
          <input value={form.crop} onChange={(event) => updateField("crop", event.target.value)} />
        </label>
        <label>
          <span>District</span>
          <input
            value={form.district}
            onChange={(event) => updateField("district", event.target.value)}
          />
        </label>
        <label>
          <span>Season</span>
          <select value={form.season} onChange={(event) => updateField("season", event.target.value)}>
            <option>Kharif</option>
            <option>Rabi</option>
            <option>Zaid</option>
          </select>
        </label>
        <label>
          <span>Policy Number</span>
          <input
            value={form.policy_id}
            onChange={(event) => updateField("policy_id", event.target.value)}
          />
        </label>
        <label>
          <span>Loss Reason</span>
          <input
            value={form.loss_reason}
            onChange={(event) => updateField("loss_reason", event.target.value)}
          />
        </label>
        <label>
          <span>Date</span>
          <input
            type="date"
            value={form.date_of_loss}
            onChange={(event) => updateField("date_of_loss", event.target.value)}
          />
        </label>
        <label>
          <span>Area</span>
          <input value={form.area} onChange={(event) => updateField("area", event.target.value)} />
        </label>
        <label>
          <span>Estimated Loss</span>
          <input
            inputMode="numeric"
            value={form.estimated_loss}
            onChange={(event) => updateField("estimated_loss", event.target.value)}
          />
        </label>
        <label>
          <span>Upload Images</span>
          <input
            accept="image/*"
            multiple
            type="file"
            onChange={(event) => handleFileChange(event, setImages)}
          />
        </label>
        <label>
          <span>Upload PDFs</span>
          <input
            accept="application/pdf"
            multiple
            type="file"
            onChange={(event) => handleFileChange(event, setPdfs)}
          />
        </label>
      </div>

      <label className="query-field">
        <span>AI Query</span>
        <textarea
          value={form.query}
          onChange={(event) => updateField("query", event.target.value)}
          rows={3}
        />
      </label>

      <div className="upload-summary">
        <span>{images?.length ?? 0} images</span>
        <span>{pdfs?.length ?? 0} PDFs</span>
      </div>

      <div className="form-actions">
        <button className="primary-action" disabled={loading} onClick={submit} type="button">
          {loading ? "Submitting claim" : "Submit claim"}
        </button>
        {error && <p className="error">{error}</p>}
        {success && <p className="success">{success}</p>}
      </div>
    </motion.article>
  );
}
