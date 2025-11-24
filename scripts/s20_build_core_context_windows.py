#!/usr/bin/env python3
import os
import sys

def load_core_stems(core_path):
    core = {}
    with open(core_path, "r", encoding="utf-8") as f:
        header = None
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if header is None:
                header = parts
                col_idx = {c: i for i, c in enumerate(header)}
                # required columns in s13
                for c in ("token", "semantic_family", "role_group"):
                    if c not in col_idx:
                        raise RuntimeError(f"[S20] Core file missing required column: {c}")
                continue
            token = parts[col_idx["token"]]
            family = parts[col_idx["semantic_family"]]
            role_group = parts[col_idx["role_group"]]
            core[token] = (family, role_group)
    return core

def load_tokens(tokens_path):
    tokens = []
    with open(tokens_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                # too short, skip
                continue
            # p6_folio_tokens.tsv example:
            # token  folio  header_blob  line_idx  pos_idx
            token = parts[0].strip()
            folio = parts[1].strip()
            # Treat penultimate as line-id, last as position
            if len(parts) >= 4:
                line_id = parts[-2].strip()
                pos = parts[-1].strip()
            else:
                line_id = ""
                pos = ""
            tokens.append({
                "token": token,
                "folio": folio,
                "line_id": line_id,
                "pos": pos,
            })
    return tokens

def main():
    base = os.environ.get("BASE", os.getcwd())
    core_path = os.path.join(base, "PhaseS/out/s13_semantic_core_report.tsv")
    tokens_path = os.environ.get("TOKENS_PATH", os.path.join(base, "PhaseS/out/p6_folio_tokens.tsv"))
    out_path = os.path.join(base, "PhaseS/out/s20_core_context_windows.tsv")

    print(f"[S20] BASE        = {base}")
    print(f"[S20] CORE_PATH   = {core_path}")
    print(f"[S20] TOKENS_PATH = {tokens_path}")
    print(f"[S20] OUT_PATH    = {out_path}")

    if not os.path.exists(core_path):
        raise RuntimeError(f"[S20] Core file not found: {core_path}")
    if not os.path.exists(tokens_path):
        raise RuntimeError(f"[S20] Tokens file not found: {tokens_path}")

    core = load_core_stems(core_path)
    print(f"[S20] Core stems: {len(core)}")

    tokens = load_tokens(tokens_path)
    print(f"[S20] Total tokens loaded: {len(tokens)}")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as out:
        header = [
            "family",
            "role_group",
            "token",        # centre token (core stem)
            "folio",
            "line_id",
            "pos",
            "left2",
            "left1",
            "right1",
            "right2",
        ]
        out.write("\t".join(header) + "\n")

        n_windows = 0
        N = len(tokens)

        def get_tok(idx):
            if idx < 0 or idx >= N:
                return ""
            return tokens[idx]["token"]

        for i, rec in enumerate(tokens):
            tok = rec["token"]
            if tok not in core:
                continue
            family, role_group = core[tok]
            left2 = get_tok(i - 2)
            left1 = get_tok(i - 1)
            right1 = get_tok(i + 1)
            right2 = get_tok(i + 2)

            row = [
                family,
                role_group,
                tok,
                rec["folio"],
                rec["line_id"],
                rec["pos"],
                left2,
                left1,
                right1,
                right2,
            ]
            out.write("\t".join(row) + "\n")
            n_windows += 1

    print(f"[S20] Windows built: {n_windows}")

if __name__ == "__main__":
    main()
