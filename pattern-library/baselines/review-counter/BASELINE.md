# Baseline — review-counter

| | |
|---|---|
| Captured | 2026-08-27 |
| From | pattern-lab v009 |
| Hero frame | t=5.2s |
| Renderer | hyperframes 0.8.16, Chrome headless 152.0.7977.30, GSAP 3.14.2 |
| Fonts | Bricolage Grotesque + Inter Tight, Google Fonts CDN |

## Verified at 1:1

- No text-block collisions (`guard()` clean, 69px clear of canvas bottom)
- No borders, rules or underlines anywhere in frame
- Counter reel: alpha-masked, no seams under digits
- Drift field active across full 7s, nothing frozen
- Contrast: 127/127 WCAG AA via `npm run check`

## Known-open, accepted at capture

- Lower-right empties around 5.5s
- Closing line is small relative to the headline above it

## Regression use only

Diff a re-render of this same composition against these frames. Do NOT open
these as creative reference for a new video — see the warning in LIBRARY.md.
