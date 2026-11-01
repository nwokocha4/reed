"""Reference PDF builder using only the Python standard library.

Writes a minimal but valid multi-page PDF with Helvetica text. No third-party
packages required. Handles WinAnsi (latin-1) characters; anything outside that
range is replaced.
"""
import re

def _esc(s):
    s = s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    out = []
    for ch in s:
        o = ord(ch)
        if o > 255:
            out.append("?")
        elif o >= 32 or ch in ("\t",):
            out.append(ch)
        else:
            out.append("?")
    return "".join(out)

def _wrap(text, width=92):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            while len(w) > width:
                lines.append(w[:width])
                w = w[width:]
            cur = w
    if cur:
        lines.append(cur)
    return lines

def build_pdf(path, pages, title="Lead and Copper Rule - compliance excerpts"):
    # pages: list of (heading, body_paragraphs[])
    content_objs = []
    for heading, paras in pages:
        ops = []
        ops.append("BT /F1 13 Tf 72 750 Td 15 TL (%s) Tj ET" % _esc(heading))
        y = 728
        ops.append("BT /F1 9 Tf 72 %d Td 12 TL" % y)
        for p in paras:
            for line in _wrap(p):
                ops.append("(%s) Tj T*" % _esc(line))
            ops.append("() Tj T*")
        ops.append("ET")
        content_objs.append("\n".join(ops).encode("latin-1", errors="replace"))

    n_pages = len(content_objs)
    # object numbering: 1 catalog, 2 pages, then per page: page obj + content obj, then font obj
    ids = {}
    nxt = 3
    page_ids = []
    for _ in range(n_pages):
        pid, cid = nxt, nxt + 1
        nxt += 2
        page_ids.append((pid, cid))
    font_id = nxt

    objs = {}
    kids = " ".join("%d 0 R" % p for p, _ in page_ids)
    objs[1] = "<< /Type /Catalog /Pages 2 0 R >>"
    objs[2] = "<< /Type /Pages /Kids [%s] /Count %d >>" % (kids, n_pages)
    for (pid, cid), content in zip(page_ids, content_objs):
        objs[pid] = ("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                     "/Resources << /Font << /F1 %d 0 R >> >> /Contents %d 0 R >>" % (font_id, cid))
        objs[cid] = "<< /Length %d >>\nstream\n" % len(content) + "__BYTES__" + "\nendstream"
    objs[font_id] = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"

    out = bytearray()
    out += b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
    offsets = {}
    order = sorted(objs.keys())
    # stash byte contents
    blobs = {cid: c for (_, cid), c in zip(page_ids, content_objs)}
    for oid in order:
        offsets[oid] = len(out)
        out += ("%d 0 obj\n" % oid).encode("ascii")
        body = objs[oid]
        if "__BYTES__" in body:
            pre, post = body.split("__BYTES__")
            out += pre.encode("ascii") + blobs[oid] + post.encode("ascii")
        else:
            out += body.encode("ascii")
        out += b"\nendobj\n"
    xref_pos = len(out)
    out += ("xref\n0 %d\n" % (max(order) + 1)).encode("ascii")
    out += b"0000000000 65535 f \n"
    for oid in range(1, max(order) + 1):
        out += ("%010d 00000 n \n" % offsets[oid]).encode("ascii")
    out += ("trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
            % (max(order) + 1, xref_pos)).encode("ascii")
    with open(path, "wb") as f:
        f.write(bytes(out))

PAGES = [
    ("40 CFR 141.80(c) - action levels and percentile (excerpts)", [
        "(c) Lead and copper action levels and method for determining whether there is an exceedance "
        "of the action level. Action levels must be determined based on tap water samples that must be "
        "considered for inclusion under 141.86(e).",
        "(1) The lead action level is exceeded if the 90th percentile concentration of lead as specified "
        "in paragraph (c)(3) of this section is greater than 0.010 mg/L.",
        "(2) The copper action level is exceeded if the 90th percentile concentration of copper as "
        "specified in paragraph (c)(3) of this section is greater than 1.3 mg/L.",
        "(3) For purposes of this subpart, the 90th percentile concentration must be derived as follows. "
        "The results of all lead or copper samples taken during a tap sampling period must be placed in "
        "ascending order from the sample with the lowest concentration to the sample with the highest "
        "concentration. Each sampling result must be assigned a number, in ascending order beginning with "
        "the number 1 for the sample with the lowest concentration. The number assigned to the sample with "
        "the highest concentration must be equal to the total number of samples taken.",
        "(B) The number of samples taken during the tap sampling period must be multiplied by 0.9.",
        "(C) The 90th percentile concentration is the concentration in the numbered sample yielded after "
        "multiplying the number of samples by 0.9.",
        "(D) For water systems that collect five samples per tap sampling period, the 90th percentile "
        "concentration is the average of the highest and second highest concentration from the results "
        "in paragraph (c)(3)(i)(A) of this section.",
        "(E) For a water system that is allowed by the State to collect fewer than five samples in "
        "accordance with 141.86(a)(2) or has failed to meet their required minimum number of samples and "
        "collected fewer than five samples, the sample result with the highest concentration from the "
        "results in paragraph (c)(3)(i)(A) of this section is considered the 90th percentile value.",
    ]),
    ("40 CFR 141.86(a)-(e) - tap site tiers and sampling (excerpts)", [
        "(a) Selection of sampling sites. Tier 1 sampling sites consist of single family structures with "
        "lead service lines or copper pipes with lead solder installed after 1982. Tier 2 sites consist of "
        "buildings with similar plumbing materials. Tier 3 sites consist of single family structures with "
        "copper pipes with lead solder installed before 1983. Systems must use Tier 1 sites when available.",
        "Copper tiering keys on copper pipe with lead solder. A site may therefore carry a lead tier that "
        "differs from its copper tier, and eligibility is evaluated separately for each contaminant.",
        "(b) Sequential sampling at sites with lead service lines. At a site where the State has approved "
        "sequential sampling, the compliance sample for lead is the fifth liter drawn after stagnation. The "
        "first liter is informational only and is not used for compliance when a required pair is present. "
        "When only one liter of a required pair is present the site is excluded. Sequential sampling applies "
        "to lead only. Copper at these sites is reported as a single sample and is not subject to the pair "
        "rule.",
        "(c) Numbers of samples. The table below gives the required minimum number of samples by population "
        "served under standard monitoring and under reduced monitoring. Population-served changes move a "
        "system across minimum-count rows mid-record where applicable.",
    ]),
    ("Required minimum sample counts by population served", [
        "POPULATION SERVED | STANDARD SITES | REDUCED SITES.",
        "Row 1: population greater than 100,000 | standard 100 sites | reduced 50 sites.",
        "Row 2: population 10,001 to 100,000 | standard 60 sites | reduced 30 sites.",
        "Row 3: population 3,301 to 10,000 | standard 40 sites | reduced 20 sites.",
        "Row 4: population 501 to 3,300 | standard 20 sites | reduced 10 sites.",
        "Row 5: population 101 to 500 | standard 10 sites | reduced 5 sites.",
        "Row 6: population 100 or fewer | standard 5 sites | reduced 5 sites.",
        "Use the standard column unless a valid reduction approval covering the period is on file, in which "
        "case use the reduced column for that period. A population change mid-record moves the system to the "
        "row matching the population served in that period.",
    ]),
    ("State guidance worked example - five-sample averaging", [
        "Nevada Division of Environmental Protection, Bureau of Safe Drinking Water, Guidance for Small Water "
        "Systems, Section V, Example 2. Ordered lead results in mg/L: 0.008, 0.009, 0.010, 0.013, 0.016.",
        "Guidance text: If five samples are required: 5 x 0.9 = 4.5. The average of the 4th and 5th highest "
        "sample value reported is the 90th percentile. Computation: (0.013 + 0.016) / 2 = 0.0145 mg/L, which "
        "the document reports as below the then-current lead action level of 0.015 mg/L.",
        "The same document restates the rule: in situations in which only 5 samples are taken, the average "
        "of the two with the highest levels is taken to determine the 90th percentile level.",
    ]),
    ("40 CFR 141.86(e) - invalid sample results (excerpt)", [
        "(e) Invalid sample results. The State may invalidate a sample result for cause, including sampling "
        "error, laboratory error, or a documented data quality objection. A result invalidated under this "
        "paragraph is not included in the determination of the 90th percentile under 141.80(c)(3).",
        "A result the system itself marks invalid is not excluded on that mark alone. The exclusion takes "
        "effect only where the State has approved the invalidation for that sample. The approval record "
        "carries the sample identifier, the approval type, and the dates that bound the approval. The "
        "collection date of the sample must fall on or after the effective date and on or before the expiry "
        "date of the approval.",
        "A result flagged invalid without a matching approved invalidation is used exactly as reported, "
        "including where the reported value is the highest in the set. Systems therefore receive no credit "
        "for self reported invalidation.",
    ]),
    ("Office guidance - reduced monitoring frequency and worked example", [
        "40 CFR 141.86(d) permits the State to reduce the number of samples a system collects where the "
        "system holds a current reduction approval and has demonstrated a stable record. This office adopts "
        "the following convention, which controls over the general expectation that reduced monitoring "
        "follows a clean record.",
        "Office convention for an annual reduction. Where an annual reduction approval covers the monitoring "
        "period, the schedule is REDUCED_ANNUAL when the period carries no exceedance, the required minimum "
        "count is met, and at least one of the two preceding periods in the system record carries an "
        "exceedance. The excursion is the justification for the reduction, not the obstacle to it. A system "
        "with annual approval and no exceedance in the preceding two periods takes STANDARD_SEMIANNUAL.",
        "Office convention for a triennial reduction. Where a triennial reduction approval covers the "
        "monitoring period, the schedule is REDUCED_TRIENNIAL when the period carries no exceedance, the "
        "required minimum count is met, and neither the current period nor either of the two preceding "
        "periods carries an exceedance. Where an annual approval and a triennial approval both cover the "
        "same period and the triennial conditions are met, the triennial result controls.",
        "Worked example. A system at 600 population served holds an annual reduction approval effective "
        "1 March 2024. Its lead 90th percentile is 0.0130 mg/L in January 2024, above the action level, and "
        "0.0036 mg/L in February 2024. In March 2024 the lead 90th percentile is 0.0036 mg/L and ten samples "
        "are on file against a reduced minimum of ten. The two preceding periods include one exceedance, so "
        "the March schedule is REDUCED_ANNUAL. Had the January result been at or below the action level, no "
        "preceding exceedance would exist and the March schedule would be STANDARD_SEMIANNUAL.",
    ]),
]
