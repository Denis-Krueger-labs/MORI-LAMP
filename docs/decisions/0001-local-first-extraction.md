# ADR 0001: Local-first listing extraction

- Status: Accepted
- Date: 2026-09-01

## Context

MORI // LAMP needs to convert unstructured job listings into its strict `Job` schema.

Job listings and candidate profiles may contain personal, sensitive, or strategically valuable information. Sending this material to a hosted language-model API would introduce an external trust boundary, possible usage fees, and dependency on a third-party service.

The extractor should provide the best practical extraction quality while respecting two hard constraints:

1. Nothing leaves the user’s laptop.
2. Extraction creates no usage-based fees.

## Decision

The first real listing extractor will run locally.

The extraction architecture will:

- Use a locally executed model or deterministic parser
- Avoid hosted inference APIs
- Avoid usage-based services
- Keep raw listings and candidate information on the device
- Expose a provider-independent Python interface
- Validate extracted output through the existing Pydantic models
- Verify extracted statements against the raw listing through grounding checks
- Reject invalid or ungrounded results instead of silently repairing them
- Keep the final interpretation and application decision under human control

No specific runtime or model is selected by this decision.

Runtime and model selection will happen through a repeatable evaluation against known fixtures instead of being embedded directly into the pipeline.

## Consequences

### Benefits

- Candidate and listing data remain local
- Extraction can operate without internet access
- There are no per-request fees
- Runtimes and models can be replaced without redesigning the pipeline
- Schema validation and grounding remain independent of model behaviour
- Extraction quality can be measured against stable expectations

### Trade-offs

- Local inference may be slower than hosted inference
- Model downloads may require substantial disk space
- Available RAM and VRAM limit model size
- Installation and hardware compatibility require additional work
- Local models can still hallucinate or misclassify information
- Model licences must be reviewed before distribution or commercial use

## Follow-up work

1. Define the provider-independent extractor interface
2. Create an evaluation harness using the existing ProSec fixture
3. Define measurable extraction-quality criteria
4. Research compatible local runtimes and models
5. Benchmark promising candidates on the target laptop
6. Select the best configuration satisfying the privacy and cost constraints
7. Connect extraction, schema validation, and grounding through one CLI workflow
