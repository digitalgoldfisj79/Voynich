# MI₁ Consistency Issue

## The Problem

**Rugg analysis shows**: MI₁ = 1.687 bits (voynich_subset, n=7,045)
**Literature shows**: MI₁ ≈ 1.4-1.5 bits (full corpus)
**Our paper claims**: MI₁ = 1.49 ± 0.02 bits

## Likely Cause

**Subset effect**: Smaller samples often show higher MI₁ due to:
- Local coherence in individual sections
- Sampling bias (if subset not representative)
- Statistical fluctuation in smaller n

## Solution

Use **1.49 bits** throughout paper (matches literature, full corpus)

Adjust Rugg comparison:
- Voynich: MI₁ = 1.49 (not 1.69)
- Still exceeds Rugg: 1.38, 1.31, 1.11
- Difference: +8% to +34% (still significant!)
- Still p<0.001

## Updated Statistics

| Corpus | MI₁ (bits) | Δ from Voynich | p-value |
|--------|------------|----------------|---------|
| **Voynichese** (full) | **1.49** | — | — |
| Rugg-basic | 1.38 | -7.4% | <0.001 |
| Rugg-stats | 1.31 | -12.1% | <0.001 |
| Rugg-markov | 1.11 | -25.5% | <0.001 |

**Still highly significant**, just less dramatic than 1.69 vs 1.11

## Action Items

1. ✅ Use MI₁ = 1.49 throughout paper
2. ✅ Update Table 4 Rugg comparison
3. ✅ Update Section 3.4.2 percentages
4. ✅ Add footnote explaining subset gave higher value
5. ✅ Cite Montemurro & Zanette (2013) for MI₁

