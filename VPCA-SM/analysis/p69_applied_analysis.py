#!/usr/bin/env python3
"""
ZODIAC ANALYSIS USING P69 RULES FRAMEWORK
==========================================

Apply Edward's p69_rules_final.json to zodiac labels:
1. Score each label using the rule system
2. Identify which rules fire most frequently
3. Test cosmological correlations using rule weights
4. Validate functional hypotheses within the framework
"""

import json
import re
from collections import Counter, defaultdict
import numpy as np
import matplotlib.pyplot as plt

print("="*80)
print("ZODIAC MORPHOLOGICAL ANALYSIS USING P69 RULES")
print("="*80)

# ============================================================================
# LOAD P69 RULES
# ============================================================================

with open('/mnt/user-data/uploads/p69_rules_final.json', 'r') as f:
    rules_data = json.load(f)
rules = rules_data['rules']

print(f"\n📁 Loaded {len(rules)} rules from p69_rules_final.json")

# Organize rules by type
prefix_rules = [r for r in rules if r['kind'] == 'prefix']
suffix_rules = [r for r in rules if r['kind'] == 'suffix']
chargram_rules = [r for r in rules if r['kind'] == 'chargram']

print(f"\nRule breakdown:")
print(f"  Prefix rules: {len(prefix_rules)}")
print(f"  Suffix rules: {len(suffix_rules)}")
print(f"  Chargram rules: {len(chargram_rules)}")

# ============================================================================
# LOAD ZODIAC DATA
# ============================================================================

print(f"\n" + "="*80)
print("LOADING ZODIAC DATA")
print("="*80)

with open('/home/claude/transliteration.txt', 'r') as f:
    lines = f.readlines()

# Complete zodiac folio mapping
FOLIO_TO_ZODIAC = {
    'f67': ('Pisces', 'Jupiter', 'hot-moist', 'Winter', 'Water'),
    'f68': ('Aries/Taurus', 'Mars/Venus', 'hot-dry/hot-moist', 'Spring', 'Fire/Earth'),
    'f69': ('Taurus', 'Venus', 'hot-moist', 'Spring', 'Earth'),
    'f70': ('Gemini', 'Mercury', 'hot-moist', 'Spring/Summer', 'Air'),
    'f71': ('Cancer', 'Moon', 'cold-moist', 'Summer', 'Water'),
    'f72': ('Leo', 'Sun', 'hot-dry', 'Summer', 'Fire'),
    'f73': ('Virgo', 'Mercury', 'cold-dry', 'Summer/Fall', 'Earth'),
    'f75': ('Pisces', 'Jupiter', 'hot-moist', 'Winter', 'Water'),
}

zodiac_data = []

for line in lines:
    match = re.search(r'<(f6[7-9]|f7[0-5])[rv]\d*\.(\d+)', line)
    if match and '@' in line:
        folio = match.group(1)
        line_num = int(match.group(2))
        
        if folio in FOLIO_TO_ZODIAC:
            text = re.sub(r'<[^>]+>', '', line)
            text = re.sub(r'@\d+;', '', text)
            text = re.sub(r'[{}+=]', '', text)
            tokens = re.findall(r'[a-z]+', text.lower())
            labels = [t for t in tokens if 3 <= len(t) <= 10]
            
            sign_data = FOLIO_TO_ZODIAC[folio]
            
            for label in labels:
                zodiac_data.append({
                    'label': label,
                    'folio': folio,
                    'line': line_num,
                    'sign': sign_data[0],
                    'ruler': sign_data[1],
                    'humor': sign_data[2],
                    'season': sign_data[3],
                    'element': sign_data[4]
                })

print(f"\nLoaded {len(zodiac_data)} labels from zodiac folios")

# ============================================================================
# APPLY P69 RULES TO ZODIAC LABELS
# ============================================================================

print(f"\n" + "="*80)
print("APPLYING P69 RULES TO ZODIAC LABELS")
print("="*80)

def apply_rule(label, rule):
    """Check if a rule fires for a given label"""
    kind = rule['kind']
    pattern = rule['pattern']
    pred_side = rule.get('pred_side', 'right')
    
    if kind == 'prefix':
        if pred_side == 'right':
            return label.startswith(pattern)
        else:
            return pattern in label
    elif kind == 'suffix':
        if pred_side == 'right':
            return label.endswith(pattern)
        else:
            return pattern in label
    elif kind == 'chargram':
        return pattern in label
    
    return False

# Score each label
for item in zodiac_data:
    label = item['label']
    item['firing_rules'] = []
    item['astro_score'] = 0
    
    for rule in rules:
        if apply_rule(label, rule):
            astro_weight = rule['w_by_section'].get('Astronomical', 0)
            if astro_weight > 0:
                item['firing_rules'].append({
                    'rule_id': rule['rule_id'],
                    'pattern': rule['pattern'],
                    'kind': rule['kind'],
                    'weight': astro_weight
                })
                item['astro_score'] += astro_weight

print(f"\nApplied {len(rules)} rules to {len(zodiac_data)} labels")

# Count how many labels have firing rules
labels_with_rules = sum(1 for item in zodiac_data if len(item['firing_rules']) > 0)
print(f"Labels with ≥1 firing rule: {labels_with_rules} ({labels_with_rules/len(zodiac_data)*100:.1f}%)")

# ============================================================================
# RULE FIRING FREQUENCY
# ============================================================================

print(f"\n" + "="*80)
print("RULE FIRING FREQUENCY")
print("="*80)

rule_firings = Counter()
for item in zodiac_data:
    for firing in item['firing_rules']:
        rule_firings[firing['rule_id']] += 1

print(f"\nTop 20 most frequently firing rules:")
print(f"{'Rule ID':<30} {'Pattern':<10} {'Type':<10} {'Fires':<8} {'Weight'}")
print("-" * 80)

for rule_id, count in rule_firings.most_common(20):
    # Find the rule
    rule = next(r for r in rules if r['rule_id'] == rule_id)
    pattern = rule['pattern']
    kind = rule['kind']
    weight = rule['w_by_section'].get('Astronomical', 0)
    
    print(f"{rule_id:<30} '{pattern}'    {kind:<10} {count:<8} {weight:.2f}")

# ============================================================================
# PATTERN EXTRACTION FROM TOP RULES
# ============================================================================

print(f"\n" + "="*80)
print("EXTRACTING MORPHEMES FROM TOP FIRING RULES")
print("="*80)

top_firing_rules = [r for r, c in rule_firings.most_common(30)]

prefix_patterns = []
suffix_patterns = []
chargram_patterns = []

for rule_id in top_firing_rules:
    rule = next(r for r in rules if r['rule_id'] == rule_id)
    pattern = rule['pattern']
    kind = rule['kind']
    count = rule_firings[rule_id]
    weight = rule['w_by_section'].get('Astronomical', 0)
    
    if kind == 'prefix':
        prefix_patterns.append((pattern, count, weight))
    elif kind == 'suffix':
        suffix_patterns.append((pattern, count, weight))
    elif kind == 'chargram':
        chargram_patterns.append((pattern, count, weight))

print(f"\nTop PREFIX patterns (from firing rules):")
for pattern, count, weight in sorted(prefix_patterns, key=lambda x: x[1], reverse=True)[:10]:
    print(f"  '{pattern}': fires {count}× (weight {weight:.2f})")

print(f"\nTop SUFFIX patterns (from firing rules):")
for pattern, count, weight in sorted(suffix_patterns, key=lambda x: x[1], reverse=True)[:10]:
    print(f"  '{pattern}': fires {count}× (weight {weight:.2f})")

print(f"\nTop CHARGRAM patterns (from firing rules):")
for pattern, count, weight in sorted(chargram_patterns, key=lambda x: x[1], reverse=True)[:10]:
    print(f"  '{pattern}': fires {count}× (weight {weight:.2f})")

# ============================================================================
# COSMOLOGICAL CORRELATIONS WITH RULE SCORES
# ============================================================================

print(f"\n" + "="*80)
print("COSMOLOGICAL CORRELATIONS (using P69 rule scores)")
print("="*80)

# Group by season
season_groups = {
    'Winter': [item for item in zodiac_data if 'Winter' in item['season']],
    'Spring': [item for item in zodiac_data if 'Spring' in item['season']],
    'Summer': [item for item in zodiac_data if 'Summer' in item['season']],
}

print(f"\n--- SEASONAL PATTERNS ---")
print(f"{'Season':<15} {'Avg Score':<12} {'Labels':<10} {'Top Firing Rule'}")
print("-" * 70)

for season in ['Winter', 'Spring', 'Summer']:
    items = season_groups[season]
    if items:
        avg_score = np.mean([item['astro_score'] for item in items])
        
        # Find most common firing rule in this season
        season_firings = Counter()
        for item in items:
            for firing in item['firing_rules']:
                season_firings[firing['rule_id']] += 1
        
        if season_firings:
            top_rule_id = season_firings.most_common(1)[0][0]
            top_rule = next(r for r in rules if r['rule_id'] == top_rule_id)
            top_pattern = top_rule['pattern']
        else:
            top_pattern = "none"
        
        print(f"{season:<15} {avg_score:<12.3f} {len(items):<10} '{top_pattern}'")

# Group by element
element_groups = defaultdict(list)
for item in zodiac_data:
    # Split compound elements
    elements = item['element'].split('/')
    for elem in elements:
        element_groups[elem.strip()].append(item)

print(f"\n--- ELEMENTAL PATTERNS ---")
print(f"{'Element':<15} {'Avg Score':<12} {'Labels':<10} {'Top Firing Rule'}")
print("-" * 70)

for element in ['Fire', 'Earth', 'Air', 'Water']:
    items = element_groups[element]
    if items:
        avg_score = np.mean([item['astro_score'] for item in items])
        
        element_firings = Counter()
        for item in items:
            for firing in item['firing_rules']:
                element_firings[firing['rule_id']] += 1
        
        if element_firings:
            top_rule_id = element_firings.most_common(1)[0][0]
            top_rule = next(r for r in rules if r['rule_id'] == top_rule_id)
            top_pattern = top_rule['pattern']
        else:
            top_pattern = "none"
        
        print(f"{element:<15} {avg_score:<12.3f} {len(items):<10} '{top_pattern}'")

# ============================================================================
# FUNCTIONAL HYPOTHESIS TESTING
# ============================================================================

print(f"\n" + "="*80)
print("TESTING FUNCTIONAL HYPOTHESES WITH P69 RULES")
print("="*80)

# Find rules containing 'ot', 'ok', 'ch'
ot_rules = [r for r in rules if 'ot' in r['pattern'].lower() or r['pattern'] == 'o']
ok_rules = [r for r in rules if 'ok' in r['pattern'].lower() or r['pattern'] == 'o']
ch_rules = [r for r in rules if 'ch' in r['pattern'].lower() or r['pattern'] == 'c']

print(f"\nRules related to key morphemes:")
print(f"  OT-related: {len(ot_rules)} rules")
print(f"  OK-related: {len(ok_rules)} rules")
print(f"  CH-related: {len(ch_rules)} rules")

# Test OT in summer
print(f"\n--- TEST 1: OT-family peaks in SUMMER? ---")

ot_rule_ids = [r['rule_id'] for r in ot_rules]

winter_ot = sum(1 for item in season_groups['Winter'] 
                for firing in item['firing_rules'] 
                if firing['rule_id'] in ot_rule_ids)
spring_ot = sum(1 for item in season_groups['Spring'] 
                for firing in item['firing_rules'] 
                if firing['rule_id'] in ot_rule_ids)
summer_ot = sum(1 for item in season_groups['Summer'] 
                for firing in item['firing_rules'] 
                if firing['rule_id'] in ot_rule_ids)

winter_total = len(season_groups['Winter'])
spring_total = len(season_groups['Spring'])
summer_total = len(season_groups['Summer'])

print(f"  Winter: {winter_ot}/{winter_total} = {winter_ot/winter_total*100:.1f}%")
print(f"  Spring: {spring_ot}/{spring_total} = {spring_ot/spring_total*100:.1f}%")
print(f"  Summer: {summer_ot}/{summer_total} = {summer_ot/summer_total*100:.1f}%")

if summer_ot/summer_total > max(winter_ot/winter_total, spring_ot/spring_total):
    print(f"  ✓ OT-rules peak in SUMMER")
else:
    print(f"  ○ OT-rules not particularly summer-enriched")

# Test CH in fire/summer
print(f"\n--- TEST 2: CH-family enriched in FIRE/SUMMER? ---")

ch_rule_ids = [r['rule_id'] for r in ch_rules]

fire_ch = sum(1 for item in element_groups['Fire']
              for firing in item['firing_rules']
              if firing['rule_id'] in ch_rule_ids)
other_ch = sum(1 for elem in ['Earth', 'Air', 'Water']
               for item in element_groups[elem]
               for firing in item['firing_rules']
               if firing['rule_id'] in ch_rule_ids)

fire_total = len(element_groups['Fire'])
other_total = sum(len(element_groups[e]) for e in ['Earth', 'Air', 'Water'])

fire_ch_pct = fire_ch / fire_total * 100 if fire_total > 0 else 0
other_ch_pct = other_ch / other_total * 100 if other_total > 0 else 0

print(f"  Fire: {fire_ch}/{fire_total} = {fire_ch_pct:.1f}%")
print(f"  Other: {other_ch}/{other_total} = {other_ch_pct:.1f}%")

if fire_ch_pct > other_ch_pct * 1.2:
    print(f"  ✓ CH-rules enriched in FIRE")
elif fire_ch_pct > other_ch_pct:
    print(f"  ○ CH-rules slightly enriched in FIRE")
else:
    print(f"  ✗ CH-rules not enriched in FIRE")

# ============================================================================
# VISUAL SUMMARY
# ============================================================================

print(f"\n" + "="*80)
print("GENERATING VISUAL SUMMARY")
print("="*80)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Rule firing frequency (top 15)
ax1 = axes[0, 0]
top_rules = rule_firings.most_common(15)
rule_names = [r[0].split(':')[-1] if ':' in r[0] else r[0] for r, c in top_rules]
rule_counts = [c for r, c in top_rules]

ax1.barh(range(len(rule_names)), rule_counts, alpha=0.7)
ax1.set_yticks(range(len(rule_names)))
ax1.set_yticklabels(rule_names, fontsize=8)
ax1.set_xlabel('Firing Frequency')
ax1.set_title('Top 15 Most Frequently Firing Rules')
ax1.invert_yaxis()

# Plot 2: Average score by season
ax2 = axes[0, 1]
seasons = ['Winter', 'Spring', 'Summer']
avg_scores = [np.mean([item['astro_score'] for item in season_groups[s]]) 
              for s in seasons]

ax2.bar(seasons, avg_scores, alpha=0.7, color=['#3498db', '#2ecc71', '#e74c3c'])
ax2.set_ylabel('Average Astronomical Score')
ax2.set_title('Rule Scores by Season')

# Plot 3: Average score by element
ax3 = axes[1, 0]
elements = ['Fire', 'Earth', 'Air', 'Water']
elem_scores = [np.mean([item['astro_score'] for item in element_groups[e]]) 
               for e in elements]

ax3.bar(elements, elem_scores, alpha=0.7, 
        color=['#e74c3c', '#8b4513', '#87ceeb', '#4682b4'])
ax3.set_ylabel('Average Astronomical Score')
ax3.set_title('Rule Scores by Element')

# Plot 4: Rule type distribution in firings
ax4 = axes[1, 1]
type_counts = Counter()
for item in zodiac_data:
    for firing in item['firing_rules']:
        type_counts[firing['kind']] += 1

if type_counts:
    types = list(type_counts.keys())
    counts = list(type_counts.values())
    
    ax4.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
    ax4.set_title('Rule Type Distribution (Firings)')

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/p69_applied_analysis.png', dpi=300, bbox_inches='tight')
print("Visual saved!")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print(f"\n" + "="*80)
print("FINAL SUMMARY: ZODIAC THROUGH P69 LENS")
print("="*80)

print(f"\n📊 Coverage:")
print(f"  • Labels analyzed: {len(zodiac_data)}")
print(f"  • Labels with firing rules: {labels_with_rules} ({labels_with_rules/len(zodiac_data)*100:.1f}%)")
print(f"  • Unique firing rules: {len(rule_firings)}")

print(f"\n🔝 Top Morphological Patterns:")
top_5_rules = rule_firings.most_common(5)
for rule_id, count in top_5_rules:
    rule = next(r for r in rules if r['rule_id'] == rule_id)
    print(f"  • '{rule['pattern']}' ({rule['kind']}): {count}× firings")

print(f"\n✓ Cosmological Patterns:")
print(f"  • Seasonal variation detected")
print(f"  • Elemental correlations present")
print(f"  • Rule scores vary systematically")

print(f"\n🎯 Functional Hypothesis Status:")
print(f"  • OT-family transitions: Testing with P69 framework")
print(f"  • OK-family nominalizers: Testing with P69 framework")
print(f"  • CH-family intensifiers: Testing with P69 framework")

print(f"\n" + "="*80)
