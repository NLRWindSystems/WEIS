# Experimental Features

This directory contains experimental and unfinished features that were previously part of WEIS.
They have been moved here because they are untested and not integrated with the main WEIS glue code.

These features are excluded from code coverage.

If you choose to use them, do so at your own risk. They may require additional development, dependencies, or configurations that are not documented or supported by the NLR team. They may also contain hardcoded paths or assumptions that are specific to the original developer's environment.

## Contents

### ftw — Surrogate Model Design Coupling

Surrogate modeling workflow: run a Design of Experiments (DOE) via WEIS, train surrogate models (using the `smt` library), and predict outputs for new design points.

**Status:** Untested. Contains a hardcoded developer path in `surrogate_model.py`. The `ftw_design_coupling.py` file is an empty stub. Depends on the `smt` package which is not in the main WEIS environment.

### dtqpy — Direct Transcription with Quadratic Programming

A Python implementation of direct transcription methods for optimal control problems using quadratic programming.

**Status:** Untested within WEIS. Has its own internal test suite but is not integrated with the main WEIS test infrastructure.
