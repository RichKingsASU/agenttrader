import { serve } from "https://deno.land/std@0.224.0/http/server.ts";

const GEMINI_API_KEY = Deno.env.get("GEMINI_API_KEY");
const GEMINI_MODEL = Deno.env.get("GEMINI_MODEL") ?? "gemini-2.0-flash-thinking";
const GEMINI_ENDPOINT = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

if (!GEMINI_API_KEY) {
  console.error("GEMINI_API_KEY is not set.");
}

const SYSTEM_INSTRUCTION = `
You are an autonomous systems architect, technical writer, DevOps engineer, and operations engineer.
Your job is to take any high-level plan provided in the request and expand it into a complete execution blueprint with:
- Executive Summary
- Architecture
- Detailed Specification
- SOP Library
- Work Plan
- Code, Configs, and Commands
- Risk, Security, and Monitoring
- Validation & Handoff Checklist
- Final Recommendations

Follow the behavior rules in your system instructions.
Ask clarifying questions only when absolutely necessary.
`;

serve(async (req: Request): Promise<Response> => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Use POST with JSON {plan}." }), {
      status: 405,
      headers: { "Content-Type": "application/json" }
    });
  }

  if (!GEMINI_API_KEY) {
    return new Response(JSON.stringify({ error: "GEMINI_API_KEY missing." }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }

  let body: { plan?: string };
  try {
    body = await req.json();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON." }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }

  const plan = body.plan?.trim();
  if (!plan) {
    return new Response(JSON.stringify({ error: "Missing 'plan'." }), {
      status: 400,
      headers: { "Content-Type": "application/json" }
    });
  }

  const payload = {
    contents: [
      {
        role: "user",
        parts: [
          { text: SYSTEM_INSTRUCTION },
          { text: `High-level plan:\n\n${plan}` }
        ]
      }
    ]
  };

  try {
    const res = await fetch(`${GEMINI_ENDPOINT}?key=${encodeURIComponent(GEMINI_API_KEY)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const text = await res.text();
      return new Response(JSON.stringify({ error: "Gemini API error", body: text }), {
        status: 502,
        headers: { "Content-Type": "application/json" }
      });
    }

    const data = await res.json();
    const text =
      data?.candidates?.[0]?.content?.parts
        ?.map((p: { text?: string }) => p.text ?? "")
        .join("") ?? "";

    return new Response(JSON.stringify({ result: text }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: "Internal error", detail: String(err) }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
});
