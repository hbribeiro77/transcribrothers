/** Formato do job retornado pela API (subset usado no frontend). */

export type JobStatus = {
  id: string;
  status: string;
  source_kind?: string;
  drive_url: string;
  file_id: string;
  error_message: string | null;
  result_markdown: string | null;
  steps_json: Record<string, unknown>;
  created_at?: string | null;
  updated_at?: string | null;
};
