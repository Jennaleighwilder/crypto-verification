# Threshold Provenance

**Frozen date:** 2025-02-23  
**Method:** Fixed ex-ante; not tuned on full dataset.

| Threshold | Value | Purpose |
|-----------|-------|---------|
| THRESHOLD_CRISIS | -0.35 | NashEq < this → CRISIS BREWING |
| THRESHOLD_STEADY | 0.35 | NashEq > this → STEADY |
| THRESHOLD_SHOCK_HIGH | -0.38 | Shock coeff 0.75 |
| THRESHOLD_SHOCK_MID | -0.35 | Shock coeff 0.72 (if geo_risk > 0.7) |
| THRESHOLD_SHOCK_LOW | -0.30 | Shock coeff 0.65 |

**Commit at freeze:** Update after `git add` + `git commit` of threshold constants.
