# N6 VALIDATION PRE-REGISTRATION

**⚠️ THIS FILE IS LOCKED AND IMMUTABLE ⚠️**

**Created:** 2025-11-22T09:02:47.874642
**Random Seed:** 1763802167

## Held-Out Test Set

Total folios: 183
Held out: 27 (14.8%)

**Held-out folios:**
```
f100r
f104r
f104v
f112r
f18v
f19r
f21r
f24r
f26r
f29v
f2v
f30r
f32r
f37v
f47v
f50v
f51r
f52v
f55v
f56r
f57v
f73r
f80r
f81r
f84v
f87r
f93v
```

## N6 Validation Tests (All Must Pass)

### Held-out stem prediction
- **Threshold:** p < 0.01 vs permutation baseline
- **Description:** N5 hypotheses must predict held-out stem meanings above chance

### Drawing-consistency prediction
- **Threshold:** p < 0.05 vs random assignment
- **Description:** Botanical stems appear in plant folios, astronomical in astronomical

### Phrase-level alignment
- **Threshold:** p < 0.01 vs random Latin phrases
- **Description:** Multi-word expressions match real medieval pharmaceutical phrases

### Entropy reduction
- **Threshold:** 95% bootstrap CI shows reduction
- **Description:** Voynich→Latin mapping reduces word order entropy

### Cross-language comparison
- **Threshold:** p < 0.01, single best-fit language
- **Description:** PMI network similarity identifies Latin > other languages

### Expert evaluation
- **Threshold:** kappa > 0.6 inter-rater agreement
- **Description:** Medieval Latin experts agree glosses are plausible

## Passing Criteria

ALL 6 tests must pass. Failure = iterate N5 with new hypotheses + different holdout set.

## Critical Rules

1. **Never examine held-out folios until N6 execution**
2. **N5 hypotheses generated without knowledge of held-out data**
3. **No post-hoc adjustment of thresholds**
4. **If N6 fails, use DIFFERENT held-out set for next iteration**
5. **Report results honestly regardless of outcome**

## Manifest Hash

```
e0cd30e1ab55a840f25553803fad658bd2f3894e31eb3cd5bcd8d7ffa55bdd94
```

Any modification to this file invalidates N6 validation.
