export type HealthResponse = {
  status: "ok";
};

export function parseHealthResponse(value: unknown): HealthResponse {
  if (
    typeof value !== "object" ||
    value === null ||
    !("status" in value) ||
    value.status !== "ok"
  ) {
    throw new Error("FastAPI returned an invalid health response");
  }

  return { status: "ok" };
}
