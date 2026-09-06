#!/usr/bin/env python3
"""Apply TAES Paper 2 editorial compression pass 1, tested verifier revision 3.

R3 reuses the approved compressed prose and all R2 preservation checks. The
only R3 change is the tested conservative reduction ceiling: the approved text
reduces the three targeted sections by exactly 2,284 tokenizer words.
"""

from __future__ import annotations

import TAES_APPLY_COMPRESSION_PASS1_R2 as r2


def main() -> None:
    intro_old = r2.read(r2.INTRO)
    core_old = r2.read(r2.CORE)
    synth_old = r2.read(r2.SYNTH)

    r2.verify_untouched_components()

    baseline_markers = [
        (intro_old, "Several results constrain stronger interpretations and are intentionally retained."),
        (core_old, "#### 1) Study 3: temporal evidence qualification"),
        (core_old, "### F. Cross-Study Interpretation Rule"),
        (synth_old, "## C. Integrity and Authenticity Do Not Exhaust Semantic Trust"),
        (synth_old, "## G. Aerospace Systems Implications"),
    ]
    for text, marker in baseline_markers:
        if marker not in text:
            raise SystemExit(f"ERROR: expected compression baseline marker missing: {marker}")

    intro_new = r2.p1.INTRO_NEW
    core_new = r2.p1.replace_section(
        core_old,
        "## III. Common Trust-Qualification Framework and Study Separation",
        "## References Used in Sections II and III",
        r2.p1.SECTION_III_NEW,
        "Section III",
    )
    synth_new = r2.p1.SYNTH_NEW

    r2.verify_edited_targets(intro_new, core_new, synth_new)
    r2.verify_global_preservation(intro_new, core_new, synth_new)

    before = {
        "I": r2.p1.words(intro_old),
        "III": r2.p1.words(
            core_old[
                core_old.find("## III.") : core_old.find(
                    "## References Used in Sections II and III"
                )
            ]
        ),
        "VII": r2.p1.words(synth_old),
    }
    after = {
        "I": r2.p1.words(intro_new),
        "III": r2.p1.words(r2.p1.SECTION_III_NEW),
        "VII": r2.p1.words(synth_new),
    }

    total_reduction = sum(before.values()) - sum(after.values())
    if total_reduction < 1200:
        raise SystemExit(f"ERROR: compression reduction too small: {total_reduction} words")
    if total_reduction > 2400:
        raise SystemExit(
            f"ERROR: compression reduction exceeds tested pass bound: {total_reduction} words"
        )
    if total_reduction != 2284:
        raise SystemExit(
            f"ERROR: compression projection drifted from tested 2,284-word reduction: {total_reduction}"
        )

    r2.p1.write(r2.INTRO, intro_new)
    r2.p1.write(r2.CORE, core_new)
    r2.p1.write(r2.SYNTH, synth_new)

    print("TAES_COMPRESSION_PASS1_R3=PASS")
    print(f"section_I_before={before['I']}")
    print(f"section_I_after={after['I']}")
    print(f"section_III_before={before['III']}")
    print(f"section_III_after={after['III']}")
    print(f"section_VII_before={before['VII']}")
    print(f"section_VII_after={after['VII']}")
    print(f"targeted_word_reduction={total_reduction}")
    print("untouched_component_manifest_check=PASS")
    print("global_scientific_preservation_markers=PASS")
    print("science_files_changed=NONE")
    print("section_VIII_changed=NO")
    print(
        "NOTE: Re-run TAES_ASSEMBLE_MANUSCRIPT.py and "
        "TAES_AUDIT_LENGTH_REDUNDANCY.py before committing."
    )


if __name__ == "__main__":
    main()
