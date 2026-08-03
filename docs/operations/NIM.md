# NVIDIA NIM Operations

## Provider boundary

Four Pillars uses the hosted NVIDIA NIM OpenAI-compatible chat-completions endpoint for LLM generation and LLM-as-judge evaluation. The application does not silently route to another provider. Calculation-only endpoints remain available without a key; AI report jobs fail clearly when `NVIDIA_NIM_API_KEY` is absent.

## Configuration

```env
NVIDIA_NIM_API_KEY=nvapi-...
NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NIM_MODEL=nvidia/llama-3.3-nemotron-super-49b-v1.5
NIM_EVAL_MODEL=nvidia/llama-3.3-nemotron-super-49b-v1.5
NIM_TIMEOUT_SECONDS=120
NIM_MAX_RETRIES=3
NIM_MAX_SCHEMA_REPAIRS=1
```

The model values are configuration because the free hosted catalog and account entitlements can change. Operators must select a free model currently available to the NVIDIA account and record the chosen model in deployment configuration. The generated report, trace, and manifest record the actual configured model.

## Request contract

The client sends `POST /chat/completions` with Bearer authentication, the selected model, system and user messages, bounded temperature/max tokens, and `response_format={"type":"json_object"}`. Calculation JSON and user notes are serialized inside an explicit untrusted `<input>` boundary. The model is instructed that user notes are data rather than executable instructions.

## Reliability

Network failures, timeouts, HTTP 408, HTTP 429, and server errors are retried. `Retry-After` is honored when it contains a numeric delay; otherwise exponential delays are capped. Other client errors fail immediately. A response must contain `choices[0].message.content`, parse to one JSON object, and validate against the Pydantic response model. One repair round may request the same complete object with the validation error and JSON Schema. Further failure ends the job.

## Offline tests

Normal CI uses `httpx.MockTransport` to test headers, endpoint shape, JSON parsing, schema repair, rate-limit retry, and terminal errors without spending NIM quota or exposing a secret. Run:

```bash
pytest -m 'not nim_live'
```

## Live model tests

Live tests are opt-in and skipped when `NVIDIA_NIM_API_KEY` is not present. They verify that the configured hosted model returns valid JSON for a deterministic fixture and that the judge can score a report. Run locally:

```bash
pytest -m nim_live -vv
python scripts/nim_eval.py
```

The repository workflow `nim-eval.yml` runs only through manual dispatch and requires the `NVIDIA_NIM_API_KEY` repository secret. It must not run on contributions from untrusted forks because a prompt could attempt to exfiltrate secrets.

## Cost and privacy

Use low temperature and bounded max tokens. Do not send data that the user has not authorized for hosted processing. Production logs record model name, attempt count, repair count, latency, status, and prompt hashes—not raw birth data, personal notes, or generated text. Apply retention and deletion to locally stored report artifacts independently of NVIDIA account policies.

## Incident response

If NIM becomes unavailable, keep the job failed or queued according to operator policy and continue serving deterministic calculations. Do not switch providers under the same model label. If schema-valid but unsafe content increases, pin the last known prompt/model combination, run the judge set, inspect failures, and release a prompt or model configuration update with recorded evaluation results.
