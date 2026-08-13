import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("server-only", () => ({}));

import { getApiHealth } from "./fastapi";

describe("getApiHealth", () => {
  beforeEach(() => {
    process.env.API_BASE_URL = "http://fastapi.test:8000";
  });

  afterEach(() => {
    delete process.env.API_BASE_URL;
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("calls the uncached health endpoint and validates its response", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ status: "ok" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(getApiHealth()).resolves.toEqual({
      available: true,
      status: "ok",
    });
    expect(fetchMock).toHaveBeenCalledWith(
      new URL("http://fastapi.test:8000/health"),
      expect.objectContaining({
        cache: "no-store",
        signal: expect.any(AbortSignal),
      }),
    );
  });

  it("returns an unavailable state when FastAPI cannot be reached", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("offline")));

    await expect(getApiHealth()).resolves.toEqual({
      available: false,
      message: "FastAPIへ接続できませんでした。",
    });
  });

  it("returns an unavailable state for an unsuccessful HTTP response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(null, { status: 503 })),
    );

    await expect(getApiHealth()).resolves.toEqual({
      available: false,
      message: "FastAPIがHTTP 503を返しました。",
    });
  });

  it("throws when the server-only API URL is missing", async () => {
    delete process.env.API_BASE_URL;

    await expect(getApiHealth()).rejects.toThrow(
      "API_BASE_URL is not configured",
    );
  });

  it("throws when FastAPI returns an invalid success response", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          new Response(JSON.stringify({ status: "unknown" }), { status: 200 }),
        ),
    );

    await expect(getApiHealth()).rejects.toThrow(
      "FastAPI returned an invalid health response",
    );
  });

  it("returns an unavailable state when the health check times out", async () => {
    const timeoutSignal = new AbortController().signal;

    const timeoutSpy = vi
      .spyOn(AbortSignal, "timeout")
      .mockReturnValue(timeoutSignal);

    const fetchMock = vi
      .fn()
      .mockRejectedValue(new DOMException("Timed out", "TimeoutError"));

    vi.stubGlobal("fetch", fetchMock);

    await expect(getApiHealth()).resolves.toEqual({
      available: false,
      message: "FastAPIへ接続できませんでした。",
    });

    expect(timeoutSpy).toHaveBeenCalledWith(5_000);

    expect(fetchMock).toHaveBeenCalledWith(
      new URL("http://fastapi.test:8000/health"),
      {
        cache: "no-store",
        signal: timeoutSignal,
      },
    );
  });
});
