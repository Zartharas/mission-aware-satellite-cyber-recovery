# TAES Paper 2 Figure 1 Visual QA

**QA date:** 2026-09-06  
**Target:** IEEE Transactions on Aerospace and Electronic Systems  
**Scientific rerun authorized or required:** No  
**Current status:** `REVISION_2_APPROVED_FOR_MANUSCRIPT_INSERTION__FINAL_PAGE_QA_STILL_PENDING`

## 1. Scope

This QA evaluates the publication display proposed to replace qualitative Table V. Figure 1 is a manuscript-level synthesis of three separately frozen experiments. The QA does not alter or reinterpret any Study 3, Study 4, or Study 6 result.

## 2. Revision 1 generation record and rejection

The first local Mac generation reported:

- font: Arial;
- width: 7.16 in;
- height: 4.65 in;
- PDF SHA-256: `7be2c4d38b677daf82678a01d558277092ae52eb24807d7d41a2ba6c4eec74b5`;
- PNG SHA-256: `6b0f433c570d2f78c54ae594ad6d87d9691639b147f9fbdfc2c2cd302e54a0aa`.

A reproduction of the revision-1 layout exposed a material display defect: several long body strings could extend beyond their panel bounds and visually cross into adjacent panels. The cause was reliance on Matplotlib `wrap=True` inside narrow axes.

Decision:

`REVISION_1_REJECTED_FOR_PUBLICATION_INSERTION`

This was a presentation defect only. It did not affect any manuscript result or frozen study evidence.

## 3. Revision 2 correction

`TAES_GENERATE_FIGURE1.py` revision 2:

- uses explicit deterministic line wrapping;
- increases height to 5.15 in while retaining 7.16-in two-column width;
- preserves three parallel panels with no connecting arrows;
- preserves the labels `Three separately frozen experiments`, `qualitative synthesis only`, `No pooled population`, and `no experimental data flow between panels`;
- preserves the statement that only Study 3 models contact;
- adds a renderer-based text-overflow guard that fails generation if registered panel text leaves its axes bounds.

## 4. Revision 2 exact Mac generation record

The canonical Mac checkout generated revision 2 with:

- `TAES_FIGURE1_GENERATION=PASS`;
- `layout_revision=2`;
- `font=Arial`;
- `figure_width_in=7.16`;
- `figure_height_in=5.15`;
- `panel_text_overflow_check=PASS`;
- PDF SHA-256: `4872707261c8a8b6b747e76b9166b4ad7ae426e43d7bd9ffe272e4c5ea6f4ff8`;
- PNG SHA-256: `7d22964bdae052b35b4680e1b09f3209f1c99bb1d157a0f995dcd2a6445e6698`;
- `figure_claim_scope=QUALITATIVE_SYNTHESIS_ONLY`;
- `integrated_experiment_implied=NO`;
- `contact_model_scope=STUDY3_ONLY`.

The exact Mac renderer therefore verified that all registered panel text remained within panel bounds under Arial.

## 5. Independent layout visual assessment

A separately rendered revision-2 reproduction was visually inspected.

Assessment:

- all panel text remained within its panel;
- no cross-panel collisions were visible;
- the three studies read as parallel rather than sequential;
- no arrows or pipeline cues were present;
- grayscale readability was strong because the design uses black text, black borders, white panels, and light-gray headers rather than color dependence;
- `APPROVED_BAD_SOURCE` remained explicit in Study 6;
- persistent `V5` and the K4 limitation remained explicit in Study 3;
- provenance conditionality and null effects remained explicit in Study 4;
- anti-pooling and no-data-flow labels remained prominent;
- the footer explicitly states that the panels are a qualitative manuscript synthesis and that only Study 3 models contact.

The independently inspected reproduction used the same revision-2 geometry and text layout but was not the exact Mac PNG byte stream. The exact Mac render was validated by the generator's renderer-based overflow check and recorded hashes. Final placement, scale, and page-level appearance remain subject to the mandatory publisher-facing PDF visual-QA gate.

## 6. Scientific claim controls

Revision 2 preserves the intended bounded interpretation:

### Study 3
- gate-visible signature/freshness/received-authorization/contact-dependent evidence;
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
- signature, digest, provenance, reproduced-build, review, and approval signals;
- objective baseline correctness;
- `APPROVED_BAD_SOURCE` remains qualified when all six gate-visible assurance signals are true;
- stronger composition closes selected modeled states while increasing sensitivity to benign assurance-signal loss.

## 7. Gate verdict

Current verdict:

`PASS_REVISION_2_FIGURE_APPROVED_FOR_MANUSCRIPT_INSERTION`

Authorized next actions:

1. replace qualitative Table V with the approved Fig. 1 reference and caption;
2. retain Tables I-IV unchanged;
3. bind the revision-2 PDF and PNG hashes into the component manifest;
4. reassemble the development manuscript;
5. verify that citation order and scientific controls still pass;
6. track the figure assets and regenerated manuscript canonically after hash verification.

This QA does not authorize portal submission. Final rendered-page inspection remains required during the publisher-facing PDF visual-QA gate.
