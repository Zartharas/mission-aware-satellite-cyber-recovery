# TAES Paper 2 Figure 1 Visual QA

**QA date:** 2026-09-06  
**Target:** IEEE Transactions on Aerospace and Electronic Systems  
**Scientific rerun authorized or required:** No  
**Current status:** `REVISION_2_GENERATOR_READY__EXACT_MAC_RENDER_QA_PENDING`

## 1. Scope

This QA evaluates the publication display proposed to replace qualitative Table V. Figure 1 is a manuscript-level synthesis of three separately frozen experiments. The QA does not alter or reinterpret any Study 3, Study 4, or Study 6 result.

## 2. Revision 1 generation record

The first local Mac generation reported:

- `TAES_FIGURE1_GENERATION=PASS`
- font: Arial
- width: 7.16 in
- height: 4.65 in
- PDF SHA-256: `7be2c4d38b677daf82678a01d558277092ae52eb24807d7d41a2ba6c4eec74b5`
- PNG SHA-256: `6b0f433c570d2f78c54ae594ad6d87d9691639b147f9fbdfc2c2cd302e54a0aa`
- qualitative-synthesis, non-integrated-experiment, and Study-3-only contact controls: PASS

The generated files remained untracked, as required.

## 3. Revision 1 visual defect

A reproduction of the committed revision-1 layout exposed a material display defect: several long body strings could extend beyond their panel bounds and visually cross into adjacent panels. The cause was the generator's reliance on Matplotlib `wrap=True` inside narrow axes. That flag does not reliably constrain text to the panel width.

Decision:

`REVISION_1_REJECTED_FOR_PUBLICATION_INSERTION`

The revision-1 PDF and PNG must not be committed, cited as final, or inserted into the manuscript.

This is a presentation defect only. It does not affect the manuscript science, Table V content, or any frozen study result.

## 4. Revision 2 design correction

`TAES_GENERATE_FIGURE1.py` was revised to:

- use explicit deterministic line wrapping instead of `wrap=True`;
- increase figure height from 4.65 in to 5.15 in while retaining 7.16-in two-column width;
- slightly shorten panel prose without changing its scientific meaning;
- preserve three parallel panels with no connecting arrows;
- preserve the labels `Three separately frozen experiments`, `qualitative synthesis only`, `No pooled population`, and `no experimental data flow between panels`;
- preserve the statement that only Study 3 models contact;
- add a renderer-based panel-text overflow guard that terminates generation if any registered panel text crosses the axes bounds.

Revision-2 required scientific content remains:

### Study 3
- visible signature/freshness/received-authorization/contact-dependent evidence;
- hidden authorization truth;
- validly signed `V5` semantic falsity;
- truthful pre-onset cache boundary;
- K4 reduces selected modeled exposure without eliminating persistent `V5` qualification for `B0/S1`.

### Study 4
- signed producer claims, vote threshold, and synthetic provenance-domain count;
- hidden authorization truth;
- same-size subsets can differ because of provenance-domain composition;
- provenance can delay systematic unsafe qualification, cause earlier benign rejection for selected subsets, and have null threshold effects.

### Study 6
- signature, digest, provenance, reproduced build, review, and approval signals;
- objective baseline correctness;
- `APPROVED_BAD_SOURCE` remains qualified when all six gate-visible assurance signals are true;
- stronger composition closes selected modeled states while increasing sensitivity to benign assurance-signal loss.

## 5. Reproduced revision-2 visual assessment

A non-Arial reproduction of the revision-2 layout was visually inspected before the repository generator was updated.

Assessment:

- panel text stayed within panel boundaries;
- no cross-panel text collision was observed;
- three panels read as parallel rather than sequential;
- no arrows or pipeline cues were present;
- grayscale presentation remained legible because the figure relies on black text, black borders, and light-gray headers rather than color coding;
- `APPROVED_BAD_SOURCE` remained explicit;
- Study-3-only contact scope remained explicit;
- the anti-pooling and no-data-flow labels remained visible.

This reproduction is sufficient to reject revision 1 and approve the revision-2 layout strategy. It is not a substitute for inspection of the exact Arial-rendered Mac PNG that will be used to produce the canonical figure files.

## 6. Exact-render gate

Before Figure 1 can replace Table V, the revised generator must be rerun on the canonical Mac checkout and must report at least:

- `TAES_FIGURE1_GENERATION=PASS`
- `layout_revision=2`
- `panel_text_overflow_check=PASS`
- `figure_claim_scope=QUALITATIVE_SYNTHESIS_ONLY`
- `integrated_experiment_implied=NO`
- `contact_model_scope=STUDY3_ONLY`

The resulting revision-2 PNG should then receive exact visual inspection at two-column width before the PDF/PNG are tracked and before Table V is removed.

## 7. Gate verdict

Current verdict:

`PASS_REVISION_2_LAYOUT_STRATEGY__EXACT_ARIAL_MAC_RENDER_VISUAL_QA_PENDING`

No manuscript insertion, Table-V deletion, figure-file commit, or portal submission is authorized by this intermediate QA record.
