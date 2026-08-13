import "server-only";

import { parseHealthResponse } from "./health-response";

export type ApiHealth =
  { available: true; status: "ok" } | { available: false; message: string };

function getApiBaseUrl(): string {
  const value = process.env.API_BASE_URL;

  if (!value) {
    throw new Error("API_BASE_URL is not configured");
  }

  return value;
}

export async function getApiHealth(): Promise<ApiHealth> {
  const healthUrl = new URL("/health", getApiBaseUrl());
  let response: Response;

  try {
    response = await fetch(healthUrl, {
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
    });
  } catch {
    return {
      available: false,
      message: "FastAPIへ接続できませんでした。",
    };
  }

  if (!response.ok) {
    return {
      available: false,
      message: `FastAPIがHTTP ${response.status}を返しました。`,
    };
  }

  const health = parseHealthResponse(await response.json());
  return { available: true, status: health.status };
}
