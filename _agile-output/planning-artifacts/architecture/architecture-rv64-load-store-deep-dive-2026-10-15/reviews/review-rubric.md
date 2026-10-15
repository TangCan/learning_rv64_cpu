# Good-spine rubric review

**Verdict: revise before handoff.** The spine covers the feature’s major divergence points, maps the single Spec capability and PRD requirements, and explicitly closes the operational envelope. One source link is malformed, and the YAML frontmatter has invalid indentation that may prevent tools from reading the document metadata.

## Findings

### High

1. **Frontmatter is not valid YAML.** The `type` key has a leading space while the other top-level keys do not (` type: architecture-spine`). A YAML parser may reject this inconsistent indentation, breaking metadata consumers and deterministic lint. Align `type` with the other keys and rerun the spine linter.

2. **The PRD source path resolves to the wrong directory.** From this spine’s directory, `../prds/.../prd.md` resolves under `planning-artifacts/architecture/prds/`; the actual PRD is under `planning-artifacts/prds/`. Change it to `../../prds/.../prd.md` and verify the link target exists.

### Medium

3. **AD-1’s immutability rule is only partly enforceable.** “Each unit is an immutable `<unit_id>-vN.md`” does not say how edits are handled, while the next sentence suggests a current-version index that is absent from the Structural Seed. Clarify that published versions are never edited in place and identify the index location, or remove the index requirement if no index is intended. This will prevent independently written units from choosing different revision practices.

4. **The evidence rule relies on an external convention without showing the minimum contract.** AD-3 says to use separate `type` and `status` fields “using the learning-record convention,” but the spine does not state the permitted values or cite the exact conventions file in `companions`. Since evidence rows underpin all three cases, link the convention explicitly (or summarize the required labels) so story authors can apply this rule without guessing.

## Checklist

- **Real divergence points:** Mostly covered. Canonical ownership, snapshot provenance, evidence status, core-specific stage naming, and follow-up isolation are material cross-story decisions. AD-1 and AD-5 overlap somewhat, but their rules remain understandable.
- **AD enforceability:** AD-2 through AD-6 are actionable. AD-1 has the revision/index ambiguity described above. AD-3’s external schema dependency should be directly linked.
- **Deferred:** Appropriate for trace-harness scope, the SD tuple/write endpoint, optional runtime execution, and downstream planning mechanics. None invites two stories to silently choose conflicting architecture; the SD details are explicitly assigned to the story.
- **Spec capability mapping:** CAP-1 is mapped to AD-1 through AD-4, and FR-1 through FR-7 have a row or grouped mapping. No capability is omitted.
- **Operational envelope:** Explicitly decided for this feature: existing local Git checkout and GitHub Markdown, no deployed runtime/provider/infrastructure, Git commits preserve history, ignored checkouts stay separate. Adequate at feature altitude.
- **Technology verification:** Only Markdown, Git, and GitHub rendering are named; these are existing project/platform choices and no version-sensitive technology claim is introduced.
- **Brownfield alignment:** The follow-up is intentionally separated from the completed RVA23 stage; no contradictory implementation claim is evident. The structural seed reflects the stated repository artifacts.
- **Frontmatter / Mermaid:** Frontmatter indentation issue is noted above. The Mermaid `graph TD` is syntactically plausible and has a non-empty dependency flow; no placeholder graph found.

## Required disposition

Fix both High findings, resolve AD-1’s version/index ambiguity, and make the evidence convention directly discoverable. Then run the deterministic spine linter and verify all frontmatter source links.
