# AutoML Data Curator Architecture

This document describes the technical architecture and pipeline structure of the AutoML Data Curator.

## Overview

The AutoML Data Curator is a modular Python ETL framework designed to scrape web sources, validate their raw responses, automatically repair layout mismatches via Bright Data Scraper Studio's healing API, clean, deduplicate, score quality, and export LLM-ready datasets.

## Component Block Diagram

```mermaid
graph TD
    A[Scraper Studio API] -->|Raw JSON| B(Validator)
    B -->|Is Valid| C(Cleaner)
    B -->|Is Invalid / Empty| H(Self-Healing Healer)
    H -->|Trigger Repair Proposal| A
    C -->|Stripped Text| D(Deduplicator)
    D -->|Exact & Cosine Deduped| E(Quality Scorer)
    E -->|Scored Metadata| F(Exporter)
    F -->|JSONL File| G[LLM Training Ready Export]

    subgraph Monitoring & Ops
        M[FastAPI Dashboard]
        L[Discord Alerter]
        D_Log[Repair Logs]
    end
    
    B -.-> L
    H -.-> D_Log
    M -.->|Health Status Check| B
```

## Folder Layout
- `scrapers/`: Setup scraper schemas and manager interaction classes.
- `pipeline/`: Standard ETL units (runner, cleaner, deduplicator, scorer, exporter).
- `healing/`: Prompt-generation logic and repair execution wrappers.
- `monitoring/`: Core FastAPI operations board and instant notification webhooks.
