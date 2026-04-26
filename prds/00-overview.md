# PRD: ORCA Overview

## Purpose
ORCA is a lightweight tool for automatically reading in-game mining deposit HUD codes, resolving deposit metadata, and presenting the results via a desktop GUI and browser-friendly overlay.

## Problem Statement
Star Citizen players need a fast, reliable way to capture deposit scan codes without manually typing values while in combat or mining. The scanner must tolerate ship movement and HUD sway, work with OCR, and provide a responsive overlay experience.

## Goals
- Automatically capture deposit codes from the HUD using a configurable capture region.
- Stabilize capture through anchor-based auto-alignment.
- Resolve deposit metadata from RockType data and scan signatures.
- Provide a browser-friendly overlay for live scan results.
- Keep the architecture modular so components can be refactored or extended without changing core behavior.

## Scope
### In scope
- Raster capture from the game window using a user-adjustable capture region.
- Anchor template matching for reliable alignment.
- OCR prediction through Ollama and the configured model.
- Local configuration stored in `config.json` and managed by a dedicated config service.
- A web overlay server using Flask.

### Out of scope
- Server-side or multi-user overlay synchronization.
- Remote OCR providers beyond local Ollama.
- Full game automation or direct input synthesis.

## Success Criteria
- The scanner consistently reads deposit codes under normal gameplay conditions.
- The tool recovers from capture drift through anchor realignment.
- The architecture supports future refactors by clearly separating config, domain, state, and services.
- Documentation exists for product goals and architectural decisions.

## Quality Requirements
- Configuration and runtime behavior should be separated to keep the capture pipeline simple.
- The system should be easy to test and reason about.
- Domain data should be represented with explicit typed models rather than raw dictionaries.
- New features should not require broad global mutable state.

## Operation model
- The tool operates in two phases: configuration, then capture.
- Configuration sets the OCR model and defines detection boundaries for the large auto-adjust area and the smaller OCR capture region.
- Once configured, the capture pipeline should run independently, with hotkeys driving the live scan flow.
- The application should avoid broad global mutable state for runtime capture behavior and instead pass configuration and pipeline state explicitly where possible.

## Current capabilities
- `main.py` orchestrates startup, service initialization, hotkeys, and the GUI.
- `config_service.py` loads and persists settings through typed models.
- `domain/models.py` contains business types for deposits, scan signatures, capture regions, and results.
- `state/` captures runtime state for scanning, overlays, and service runtime.
- `services/` contains capture, alignment, Ollama, and configuration services.
- `core/anchor/` implements anchor tracking and template matching.
- `web.py` hosts the overlay server.
