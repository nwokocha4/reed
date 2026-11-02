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

def build_pdf(path, pages, title="Lead and Copper Rule - censored-data estimation method"):
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
    ("1. Data and reporting basis - Lead 90th-percentile estimation from censored tap data", [
        "This note specifies the estimation method for the 90th percentile of "
        "lead and copper tap concentrations when some results are censored "
        "(detection limits). The data for each system, monitoring period, and "
        "contaminant are the reported sample values with their qualifiers. "
        "Only the roster in systems.csv defines which system-period cells are "
        "reported; results rows for other periods never count.",
        "Unit conversion is per row: a value reported in ug/L is divided by "
        "1000 to give mg/L. Each row converts by its own unit; the file "
        "carries mixed units and no column-wide assumption is valid.",
        "A result is censored when its qualifier is U or begins with <, or "
        "when its converted concentration is zero or below. Other qualifiers "
        "(including J and B) are detects and are used at face value. A blank "
        "value field is unparseable and the row is skipped.",
        "Only LEAD and COPPER rows are used; rows for any other contaminant "
        "are ignored.",
    ]),
    ("2. Lognormal regression on order statistics (ROS)", [
        "Take the natural log of every detected concentration. Sort all "
        "observations (detects and censored limits) in joint ascending order "
        "by converted concentration. A censored limit ranks below a detect "
        "reported at the same numeric value, because the true concentration "
        "is at or below the limit.",
        "Assign each rank i = 1..n the Cunnane plotting position "
        "p = (i - 0.4) / (n + 0.2) and the standard normal quantile z of p. "
        "Regress the log-detects on their normal quantiles (ordinary least "
        "squares): the fitted line gives the lognormal location and scale. "
        "The regression uses detects only; censored limits are never "
        "regressed, only imputed.",
        "Impute each censored observation from the fitted line at its own "
        "rank quantile. The completed log-sample is the observed log-detects "
        "plus the imputed values. Its mean mu and sample standard deviation "
        "sigma (denominator n - 1) are the lognormal parameters.",
        "The 90th percentile estimate is p90 = exp(mu + z_0.90 * sigma), "
        "where z_0.90 is the 0.90 quantile of the standard normal. Report "
        "p90 in mg/L rounded half up to four decimals.",
    ]),
    ("3. Sampling uncertainty - one-sided upper confidence limit", [
        "The reported finding accounts for sampling uncertainty through a "
        "one-sided upper 95 percent confidence limit on the lognormal 90th "
        "percentile, by the delta method. Its standard error is "
        "se = sigma * sqrt(1/n + z_0.90^2 / (2*(n-1))). "
        "The upper limit is UCL95 = exp(mu + z_0.90 * sigma + z_0.95 * se), "
        "where z_0.95 is the 0.95 quantile of the standard normal. Report "
        "UCL95 in mg/L rounded half up to four decimals.",
        "A cell exceeds the action level when its UCL95 is greater than the "
        "action level: 0.010 mg/L for lead, 1.3 mg/L for copper. The point "
        "estimate alone never decides the finding; a p90 below the action "
        "level with a UCL95 above it is an exceedance.",
    ]),
    ("4. Degenerate and edge cells", [
        "An empty cell (no usable rows for the roster system, period, and "
        "contaminant) reports n = 0, n_censored = 0, p90 = 0.0000, "
        "UCL95 = 0.0000, and no exceedance.",
        "A cell whose only usable rows are censored reports the minimum "
        "limit: p90 and UCL95 both equal the smallest censored concentration "
        "in mg/L.",
        "A cell with exactly one detected value among any number of censored "
        "values reports the detected value for both p90 and UCL95. A cell "
        "with a single usable row (n = 1) reports that row's concentration "
        "for both. A cell with zero fitted variance reports UCL95 = p90.",
        "Rounded half-up worked check. Completed log values "
        "-5.80914, -5.65599, -5.52146, -5.29832, -5.11600 with mu = -5.48018 "
        "and sigma = 0.27506 give p90 = exp(-5.48018 + 1.28155 * 0.27506) = "
        "0.0059 mg/L and UCL95 = 0.0087 mg/L at n = 10.",
    ]),
]
