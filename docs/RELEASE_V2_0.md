# BIOCANVAS v2.0 Release Notes

## Overview

BIOCANVAS v2.0 delivers a production-ready docking workflow with real AutoDock Vina CLI execution, improved 3D results visualization, and clearer simulation-mode transparency.

## Key Capabilities

- Real docking execution via Vina CLI binary detection and subprocess orchestration.
- Deterministic simulation fallback when Vina is unavailable.
- Results pipeline returns and renders ligand `output_pdbqt` in the 3D viewer.
- Improved selector UX parity between visualization and docking flows.
- Surface toggle and viewer lifecycle stability improvements in Viewer3D.
- Clear simulated-result warning banner, badge, and watermark for result integrity.

## Backend Improvements

- Replaced fragile Python Vina binding dependency path with Vina CLI runtime usage.
- Added simulated ligand coordinate generation for complete protein-ligand visualization.
- Added `output_pdbqt` propagation in job result payload.

## Frontend Improvements

- Fixed Results step protein data fallback for library proteins.
- Fixed Docking run viewer fallback to use `proteinPdbData` when custom upload is absent.
- Fixed Viewer3D React hook ordering and asynchronous surface handling.
- Updated docking-step selectors to dropdown interaction pattern.

## Verification Summary

- Backend health: `active`, engine `ready`.
- End-to-end docking smoke test passed.
- Completed jobs return `simulated=false` with non-empty `output_pdbqt`.
