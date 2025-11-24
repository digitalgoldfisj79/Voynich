#!/usr/bin/env python3
import sys, csv, os

def infer_suffix(token):
    """Very simple EVA suffix heuristic."""
    t = token.strip()
    if not t:
        return "NA"
    # Longish endings first
    for suf in ("aiin", "aiir", "aiir", "ain", "ain", "eedy", "ody", "edy"):
        if t.endswith(suf):
            return suf
    # Common 2–3 glyph endings
    for suf in ("dy", "ey", "ol", "al", "ar", "am", "in", "iin", "y"):
        if t.endswith(suf):
            return suf
    # Fallback: last 2 chars
    return t[-2:] if len(t) >= 2 else t

def main(slots_path, out_path):
    with open(slots_path, "r", encoding="utf-8", newline="") as f_in, \
         open(out_path, "w", encoding="utf-8", newline="") as f_out:
        reader = csv.reader(f_in, delimiter="\t")
        writer = csv.writer(f_out, delimiter="\t", lineterminator="\n")

        try:
            header = next(reader)
        except StopIteration:
            print("[s29_suffix] ERROR: empty input", file=sys.stderr)
            sys.exit(1)

        # Normal expected header from s29
        if "suffix" in header:
            # Already has suffix; just copy cleanly and exit
            writer.writerow(header)
            for row in reader:
                if not row or all(c.strip() == "" for c in row):
                    continue
                writer.writerow(row)
            return

        header = header + ["suffix"]
        writer.writerow(header)

        # Build a name→index map for safety
        name_to_idx = {name: i for i, name in enumerate(header) if name}

        tok_idx = name_to_idx.get("token", None)
        if tok_idx is None:
            print("[s29_suffix] ERROR: 'token' column not found in header:", header, file=sys.stderr)
            sys.exit(1)

        for row in reader:
            if not row or all(c.strip() == "" for c in row):
                continue
            # Pad short rows to header length
            if len(row) < len(header) - 1:
                row = row + [""] * (len(header) - 1 - len(row))
            token = row[tok_idx].strip() if tok_idx < len(row) else ""
            if not token:
                # Broken line; skip
                continue
            suf = infer_suffix(token)
            writer.writerow(row + [suf])

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: s29_add_slot_suffixes.py SLOTS_PATH OUT_PATH", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
