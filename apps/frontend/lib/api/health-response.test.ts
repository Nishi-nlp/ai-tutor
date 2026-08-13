import { describe, expect, it } from "vitest";

import { parseHealthResponse } from "./health-response";

describe("parseHealthResponse", () => {
  it("accepts the FastAPI health response", () => {
    expect(parseHealthResponse({ status: "ok" })).toEqual({ status: "ok" });
  });

  it.each([null, {}, { status: "down" }, { status: 200 }])(
    "rejects an invalid response: %j",
    (value) => {
      expect(() => parseHealthResponse(value)).toThrow(
        "FastAPI returned an invalid health response",
      );
    },
  );
});
