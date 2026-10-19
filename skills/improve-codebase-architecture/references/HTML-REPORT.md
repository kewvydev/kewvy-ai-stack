# Static Architecture Report

Adapted from the selected upstream report guidance. This replaces its executable
CDN/Mermaid scaffold; do not copy the upstream script block into a local report.

Generate a unique report in the OS temporary directory. Use inline CSS, static
SVG or escaped plain-text diagrams. Do not include scripts, event handlers,
external fonts/styles/images, remote embeds, javascript URLs or Mermaid with loose
security. The report must render without network access or executable JavaScript.

Treat all repository-derived content as untrusted text: titles, paths, source
excerpts, domain terms, labels, commit messages and diagram text. HTML-escape it
before interpolation, including quotes when placing text in attributes. Prefer
text nodes; never interpolate repository content into CSS, URLs or raw SVG markup.
Do not embed secrets or private payloads. Preview is not permission to publish.

Start with this static scaffold, replacing each uppercase label with escaped text:

```html
<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Architecture review</title>
<style>
  body { margin: 2rem auto; max-width: 70rem; padding: 0 1rem; font: 1rem/1.6 system-ui; color: #17202a; background: #fafafa; }
  section { margin: 1.5rem 0; padding: 1.5rem; border: 1px solid #ccd1d1; background: white; }
  .comparison { display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: 1rem; }
  pre { white-space: pre-wrap; overflow-wrap: anywhere; padding: 1rem; background: #f2f3f4; }
</style>
<header><h1>Architecture review</h1><p>ESCAPED_SCOPE_AND_LIMITS</p></header>
<main>
  <section>
    <h2>ESCAPED_CANDIDATE_TITLE</h2>
    <p><strong>Files:</strong> ESCAPED_PATHS</p>
    <p><strong>Observed friction:</strong> ESCAPED_PROBLEM</p>
    <p><strong>Proposed change:</strong> ESCAPED_SOLUTION</p>
    <div class="comparison">
      <div><h3>Before</h3><pre>ESCAPED_BEFORE_DIAGRAM</pre></div>
      <div><h3>After</h3><pre>ESCAPED_AFTER_DIAGRAM</pre></div>
    </div>
    <p><strong>Benefits and costs:</strong> ESCAPED_TRADEOFFS</p>
    <p><strong>Recommendation:</strong> ESCAPED_STRENGTH_AND_REASON</p>
  </section>
</main>
</html>
```

List meaningful exclusions and unavailable evidence. End with the candidate the
user should consider first and the decisions needed before implementing it.
