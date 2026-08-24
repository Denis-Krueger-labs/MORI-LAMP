# MORI // LAMP Architecture

## Goal

Find relevant cybersecurity internships in Germany, analyse each listing, compare its requirements with evidence-backed candidate information, and prepare truthful application drafts.

## First end-to-end slice

The first version processes:

- one manually supplied job listing
- one manually reviewed candidate profile
- one structured assessment as output

It does not search platforms or generate application documents yet.

## Pipeline

1. Ingest a job listing.
2. Normalize its text and metadata.
3. Extract requirements.
4. Compare requirements with candidate claims.
5. Classify matches, unsupported claims, and unknown requirements.
6. Produce a reviewable assessment.
7. Require human approval before any later document generation or external action.

## Trust boundaries

- Job listings are untrusted input.
- LinkedIn profiles and posts are not candidate evidence.
- Generated text never becomes a verified candidate fact.
- Unsupported claims must be marked for review.
- LAMP never applies to a position automatically.
- Personal candidate data and generated documents remain outside Git.

## First milestone

A local command processes one listing:

```text
python -m mori_lamp analyze examples/job.txt