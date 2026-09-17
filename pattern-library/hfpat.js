/* ===========================================================================
   hfpat.js — HyperFrames pattern library
   Chris AI Systems. Every pattern here shipped in a render that passed a
   native-resolution defect pass. Nothing goes in until it has.

   Paths are ROOT-RELATIVE. HyperFrames serves from the project root and treats
   parent traversal (../) as a hard lint error, so junction the library in as
   `pattern-library` rather than reaching out of the project. See LIBRARY.md.

   Usage inside a HyperFrames composition:

     <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
     <script src="pattern-library/hfpat.js"></script>
     <script>
       HFPat.eases();                       // register measured eases first
       const tl = gsap.timeline({ paused: true });
       HFPat.counterReel(tl, "#odo", { to: 256 });
       HFPat.riseIn(tl, ["#c3","#c2","#c1"], { at: 0.45 });
       HFPat.driftField(tl, "#stack");
       window.__timelines["main"] = tl;
     </script>

   Determinism rules this library obeys, because HyperFrames renders by
   seeking a paused timeline: no Date.now, no Math.random, no fetch, no
   onUpdate that depends on play order. Every pattern is pure fromTo.
   =========================================================================== */

(function (global) {
  "use strict";

  var HFPat = {};

  /* -------------------------------------------------------------------------
     EASES
     expDecay is not a stock GSAP ease. It was measured off a professionally
     produced reference video: a phone mockup rising over frames 452-557 at
     25fps. Its trajectory fits exponential decay with k = 0.9/s, i.e.
     exp(-3.78 * p) across a 4.2s duration. Rebuilt against the original it
     converged to 1.9% mean error over a 249px travel.

     Use expDecay for anything entering and settling. It is the single
     highest-value thing in this library — stock power/expo eases do not
     match it, and the difference is visible.
     ------------------------------------------------------------------------- */
  var K = 3.78;
  var DEN = 1 - Math.exp(-K);

  HFPat.eases = function () {
    if (!global.gsap) throw new Error("hfpat: GSAP must load before hfpat.js");
    gsap.registerEase("expDecay", function (p) {
      return (1 - Math.exp(-K * p)) / DEN;
    });
    // slower settle for large or heavy elements
    gsap.registerEase("expDecaySlow", function (p) {
      var k = 2.6, d = 1 - Math.exp(-k);
      return (1 - Math.exp(-k * p)) / d;
    });
    // faster decay for the `punch` feel. Same family as expDecay, higher k, so
    // it arrives sooner and spends less of its tail creeping the last pixels.
    // AUTHORED by extrapolating k, not measured off a reference like expDecay.
    gsap.registerEase("expDecayFast", function (p) {
      var k = 5.4, d = 1 - Math.exp(-k);
      return (1 - Math.exp(-k * p)) / d;
    });
    return HFPat;
  };

  /* -------------------------------------------------------------------------
     FEEL — the variety engine, motion axis

     WHY THIS EXISTS. On 2026-08-27 two cold sessions were given deliberately
     opposite creative briefs (restrained/editorial vs bold/high-energy) and
     produced the SAME SLIDE. Left rail 141px in both, at every timestamp. The
     library was portable and had no variety.

     Part of the cause was measurable: `opts.ease` appeared ZERO times in this
     file. Every ease was baked at 7 call sites, so every rise in every scene of
     every video decayed on one house curve. Motion feel is the most legible
     fingerprint a piece has, and it could not be changed.

     A FEEL is a named set of eases, one per ROLE. Builders ask for a role
     rather than naming a curve, so a scene can be TOLD how it should move.

     `house` reproduces the exact values this library shipped with, so nothing
     already built changes. Switching feels is opt-in.

     Grounded in measurement where possible:
       calm    — PayCloud: 1 hard cut in 85s, peak frame diff 35.6
       punch   — Buff/Fresco: 233ms median transition, peak frame diff 178.7
     `editorial` and `mech` are AUTHORED, not measured. Marked as such below.
     ------------------------------------------------------------------------- */

  var FEELS = {
    // exact shipping values — do not edit, this is the no-change baseline
    house: {
      enter: "expDecay", settle: "power2.out", pop: "back.out(2.4)",
      drift: "none", copy: "power3.out", copySub: "power2.out"
    },
    // MEASURED off PayCloud: gentle peaks, nothing snaps
    calm: {
      enter: "expDecaySlow", settle: "power1.out", pop: "power2.out",
      drift: "none", copy: "power2.out", copySub: "power1.out"
    },
    // MEASURED off Buff/Fresco: fast in, hard overshoot
    punch: {
      enter: "expDecayFast", settle: "back.out(1.8)", pop: "back.out(3.4)",
      drift: "none", copy: "power4.out", copySub: "power3.out"
    },
    // AUTHORED, not measured. Long settles, no overshoot anywhere.
    editorial: {
      enter: "expDecaySlow", settle: "power2.out", pop: "power2.out",
      drift: "none", copy: "power2.out", copySub: "power1.out"
    },
    // AUTHORED, not measured. Linear-ish, machine-like, no organic decay.
    mech: {
      enter: "power1.inOut", settle: "none", pop: "power1.out",
      drift: "none", copy: "power1.out", copySub: "power1.out"
    }
  };

  var ACTIVE = "house";

  /* Set the active feel for everything built after this call.
     Throws on an unknown name rather than silently falling back — a typo'd
     feel that quietly renders as `house` is exactly the failure this whole
     engine exists to end. */
  HFPat.feel = function (name) {
    if (!FEELS[name]) {
      throw new Error("hfpat: unknown feel '" + name + "'. Known: " +
                      Object.keys(FEELS).join(", "));
    }
    ACTIVE = name;
    return HFPat;
  };

  HFPat.feels = function () { return Object.keys(FEELS); };
  HFPat.activeFeel = function () { return ACTIVE; };

  /* Resolution order: an explicit opts.ease ALWAYS wins, then the active
     feel's ease for that role. A builder never names a curve directly. */
  function EASE(opts, role) {
    if (opts && opts.ease) return opts.ease;
    var f = FEELS[ACTIVE];
    if (!f || !f[role]) {
      throw new Error("hfpat: feel '" + ACTIVE + "' has no role '" + role + "'");
    }
    return f[role];
  }

  /* -------------------------------------------------------------------------
     LAYOUT — the variety engine, composition axis

     WHY THIS EXISTS, and why the feel engine below it was NOT enough.
     On 2026-08-27 five renders of one composition at five different feels were
     put in front of Chris. His verdict: "This really doesn't add any variation.
     The slight speed adjustments are NOT noticeable by a human." He was right,
     and the test was designed to be able to say so.

     "A true variation is a design variation of the same concept." His examples:
     a horizontal flip; a reversed build with the number roller bottom-left and
     the cards entering from the top down.

     THE RULE THAT MAKES MIRROR WORK: mirror SWAPS POSITIONS, it does not flip
     pixels. `transform: scaleX(-1)` on the frame would mirror the type too and
     every word would read backwards. So the rail moves to the right edge, the
     field moves left, the stack tilt inverts its sign, and the type is never
     transformed at all.

     Vertical works the same way. `invert` does not rotate anything — the rail
     anchors to the bottom and entrance travel changes sign, so riseIn becomes a
     fall from above while every glyph stays upright.
     ------------------------------------------------------------------------- */

  /* TWO layouts, and that is the decision, not a starting point.
     All four were rendered and shown to Chris 2026-08-27:
       standard      good
       mirror        good
       invert        BROKEN  — the rail lands through the headline
       mirrorInvert  REJECTED — "looks awkward"
     His call: "maybe we just get consistency on standard and mirror. Those
     seem pretty much the easier ones to really get consistent. And we get two
     variations per pattern, that's enough to not just come across as pure
     template."
     The vertical axis is REMOVED rather than left broken. Chris adds variation
     alts himself over time; a half-working layout in the table would get used. */
  var LAYOUTS = {
    standard: { flipX: false },
    mirror:   { flipX: true  }
  };

  var LAYOUT = "standard";

  HFPat.layouts = function () { return Object.keys(LAYOUTS); };
  HFPat.activeLayout = function () { return LAYOUT; };

  /* Apply a layout to a composition.
     Selectors are passed in because the library does not own the markup — the
     composition does. Throws on an unknown layout rather than falling back:
     a typo'd layout that silently renders `standard` is the same failure the
     feel engine already closed.

     opts.rail   selector for the block that carries the number and copy
     opts.field  selector for the block that carries the cards
     opts.margin frame margin in px (default 140, the tokens.css value)
     opts.tilt   the field's resting tilt in deg (default -7) */
  HFPat.layout = function (name, opts) {
    if (!LAYOUTS[name]) {
      throw new Error("hfpat: unknown layout '" + name + "'. Known: " +
                      Object.keys(LAYOUTS).join(", "));
    }
    LAYOUT = name;
    opts = opts || {};
    var L = LAYOUTS[name];
    var margin = opts.margin == null ? 140 : opts.margin;
    var tilt = opts.tilt == null ? -7 : opts.tilt;

    var rail = opts.rail ? document.querySelector(opts.rail) : null;
    var field = opts.field ? document.querySelector(opts.field) : null;

    if (rail) {
      // Horizontal: move the whole rail across, never mirror its contents.
      if (L.flipX) {
        rail.style.left = "auto";
        rail.style.right = margin + "px";
        rail.style.textAlign = "right";
      } else {
        rail.style.right = "auto";
        rail.style.left = margin + "px";
        rail.style.textAlign = "left";
      }
    }

    if (field) {
      if (L.flipX) {
        field.style.right = "auto";
        field.style.left = "-20px";
      } else {
        field.style.left = "auto";
      }
      // The tilt is what makes a mirrored stack read as designed rather than
      // as the same stack shoved left. Flipping the sign mirrors the rake.
      // GSAP OWNS TRANSFORM on these elements — driftField animates the field
      // and riseIn animates the cards. Writing style.transform here silently
      // fights GSAP and the whole timeline stalls: measured 2.4MB/16s render
      // dropping to 173KB/59s, with the counter reel rendering blank. The
      // composition's own comment warned about exactly this: "padding, not
      // transform — GSAP owns transform on this element."
      // Set rotation THROUGH GSAP so there is one owner.
      var inner = field.querySelector(".hfp-field-stack") || field;
      if (global.gsap && gsap.set) {
        gsap.set(inner, { rotation: L.flipX ? -tilt : tilt });
      }
    }

    return HFPat;
  };

  /* -------------------------------------------------------------------------
     COUNTER REEL — mechanical odometer
     Builds digit strips in the DOM and rolls each to its target. Lower digits
     spin more, which is what makes it read as a physical drum rather than a
     number swap.

     The container must already exist and be empty. One .reel per digit is
     created inside it. Style comes from tokens.css (.hfp-reel).

     opts:
       to        (int)    final value                         default 256
       digits    (int)    number of reels                     default from `to`
       spins     (array)  extra full rotations per digit, left to right
                          default derived: leftmost 2, +2 each digit right
       duration  (sec)    roll time of the leftmost digit     default 2.6
       stagger   (sec)    extra duration per digit rightward  default 0.35
       at        (sec)    timeline position                   default 0.45
       height    (px)     reel window height; must match CSS  default 258
     ------------------------------------------------------------------------- */
  HFPat.counterReel = function (tl, selector, opts) {
    opts = opts || {};
    var host = typeof selector === "string" ? document.querySelector(selector) : selector;
    if (!host) throw new Error("hfpat.counterReel: no element for " + selector);

    var to = opts.to == null ? 256 : opts.to;
    var str = String(to);
    var n = opts.digits || str.length;
    str = str.padStart(n, "0");

    var H = opts.height || 258;
    var at = opts.at == null ? 0.45 : opts.at;

    // ENFORCED: total roll = duration + (n-1)*stagger. Documenting that formula
    // did not stop a cold session spending 3.12s of a 7s piece on the counter,
    // so derive it instead. Pass `budget` (seconds the roll may occupy) and the
    // timing falls out of the digit count.
    var dur, stag;
    if (opts.budget != null) {
      var ratio = opts.staggerRatio == null ? 0.105 : opts.staggerRatio;
      dur  = opts.budget / (1 + (n - 1) * ratio);
      stag = dur * ratio;
    } else {
      dur  = opts.duration || 2.6;
      stag = opts.stagger == null ? 0.35 : opts.stagger;
    }

    var spins = opts.spins;
    if (!spins) {
      spins = [];
      for (var i = 0; i < n; i++) spins.push(2 + i * 2 + (i === n - 1 ? 1 : 0));
    }

    host.innerHTML = "";
    for (var d = 0; d < n; d++) {
      var reel = document.createElement("div");
      reel.className = "hfp-reel";
      var strip = document.createElement("div");
      strip.className = "hfp-strip";

      var reps = spins[d] + 2, html = "";
      for (var r = 0; r < reps; r++) {
        for (var v = 0; v <= 9; v++) html += "<span>" + v + "</span>";
      }
      strip.innerHTML = html;

      // ENFORCED: the checker flags these runtime-built nodes and they do not
      // exist in anyone's HTML, so the library sets its own suppressions.
      // All three, always — the trigger is where the strip lands, not digit
      // count, so there is no safe subset.
      strip.setAttribute("data-layout-allow-overlap", "");
      strip.setAttribute("data-layout-allow-overflow", "");
      strip.setAttribute("data-layout-allow-occlusion", "");
      var sp = strip.children;
      for (var q = 0; q < sp.length; q++) {
        sp[q].setAttribute("data-layout-allow-overlap", "");
        sp[q].setAttribute("data-layout-allow-overflow", "");
        sp[q].setAttribute("data-layout-allow-occlusion", "");
      }

      reel.appendChild(strip);
      host.appendChild(reel);

      var target = parseInt(str[d], 10);
      var end = -((spins[d] * 10) + target) * H;
      tl.fromTo(strip, { y: 0 },
        { y: end, duration: dur + d * stag, ease: EASE(opts, "enter") }, at);
    }

    // OPTICAL ALIGNMENT IS NOT AUTOMATED. Three attempts failed, all the same
    // way — measuring a box that is not the ink:
    //   1. em constant (0.6em): wrong by half; back-solving a measured 24.7px
    //      offset on a landed 6 gives ~0.498em.
    //   2. probing span index 0: that is always the glyph "0", never the digit
    //      that lands. Measured the wrong character to align a different one.
    //   3. Range.getBoundingClientRect(): returns the ADVANCE box. Measured
    //      -4px against a real 20-25px offset, and because the figures are
    //      tabular the advance is identical for every digit — so the
    //      "digit-specific" correction was digit-independent. Same flaw as 1.
    // Canvas measureText().actualBoundingBoxLeft is not a fix either: canvas
    // has no font-variant-numeric, so it measures the PROPORTIONAL glyph while
    // the reel renders tabular. Predicted 23.0px for "1" (rendered 23.3, good)
    // and 14.0px for "6" (rendered 20-25, wrong). No canvas API exposes tnum.
    //
    // The correct fix is a MEASURED per-digit lookup for the shipped face,
    // generated once by rendering each digit at 246px in a 172px cell and
    // alpha-scanning the leftmost inked column — the same "measured constant
    // with its provenance recorded" precedent as expDecay. Until that exists,
    // set margin-left yourself from your own 1:1 measurement. Reference reads,
    // plus or minus 3px: "1" ~23.3px, "6" ~20-24.7px.

    // barely-there weight drop as it lands; sells the mass of the drum
    if (opts.settle !== false) {
      tl.fromTo(host,
        { scale: 1.012, transformOrigin: "0% 50%" },
        { scale: 1, duration: 1.1, ease: EASE(opts, "settle") },
        at + dur * 0.98);
    }
    return HFPat;
  };

  /* -------------------------------------------------------------------------
     RISE IN — the measured entrance
     Elements enter from below and settle on expDecay.

     ORDERING RULE: pass the array TOP-MOST ON SCREEN FIRST.

     From the physics, not intuition: elements rise from below, so one still
     travelling sits LOWER than its resting place and encroaches on whatever is
     beneath it. Whatever is beneath it is a later DOM sibling, and later
     siblings paint on top — so a lagging element is always hidden by the thing
     it encroaches on.

     Therefore the LAST element to arrive must be the one with nothing below
     it. Order top to bottom and every element lags into space that is still
     empty. Zero overlap by construction.

     Backwards, this is a REAL overlap, not a checker artefact — no
     data-layout-allow-* fixes it, because the layout is fine and the timing is
     not. Body text sits genuinely under the next card for about a second.

     opts:
       travel   (px)   distance travelled          default 1106
       duration (sec)  per element                 default 4.2
       at       (sec)  timeline position           default 0.45
       stagger  (sec)  between elements            default 0.26
       tilt     (deg)  entry rotation, alternating default 1.2 (0 disables)
       fade     (bool) fade in as well as move     default true
     ------------------------------------------------------------------------- */
  HFPat.riseIn = function (tl, selectors, opts) {
    opts = opts || {};
    var list = Array.isArray(selectors) ? selectors : [selectors];
    var travel = opts.travel == null ? 1106 : opts.travel;
    var dur = opts.duration || 4.2;
    var at = opts.at == null ? 0.45 : opts.at;
    var stag = opts.stagger == null ? 0.26 : opts.stagger;
    var tilt = opts.tilt == null ? 1.2 : opts.tilt;
    var fade = opts.fade !== false;

    // ENFORCED: order is derived, not trusted. Elements rise from below, so one
    // still travelling sits lower than rest and encroaches on the card beneath
    // it — a later DOM sibling, which paints on top. The last to arrive must
    // therefore be the element with nothing below it. Sorting by resting
    // top position makes that true regardless of how the caller ordered the
    // array. Getting this wrong is a REAL overlap no suppression can fix; it
    // has now been introduced twice by hand, so it is no longer done by hand.
    if (opts.autoOrder !== false) {
      var resolved = list.map(function (sel, i) {
        var el = typeof sel === "string" ? document.querySelector(sel) : sel;
        return { sel: sel, el: el, i: i };
      });
      var missing = resolved.filter(function (r) { return !r.el; });
      if (missing.length) {
        // A silent no-op here reintroduces the exact bug autoOrder prevents,
        // and no gate can catch the result. Fail loudly instead.
        throw new Error("hfpat.riseIn: autoOrder could not resolve " +
          missing.map(function (m) {
            return typeof m.sel === "string" ? m.sel : "element at index " + m.i;
          }).join(", ") +
          ". Pass autoOrder:false to order manually, top-most on screen first.");
      }

      // Sort on the OFFSETPARENT CHAIN SUM — the untransformed document-space
      // top. Two rejected alternatives, both of which shipped silent bugs:
      //
      //   getBoundingClientRect().top — the top-most CORNER once an ancestor
      //   is rotated. Rotating by theta lifts it by w*sin(theta)/2 about the
      //   centre, so order survives only while  pitch > w*sin(|theta|)  —
      //   748*sin(7deg)=91.2px against a 300px pitch is safe, but it inverts
      //   at pitch <= 91px or |theta| >= asin(300/748) = 23.6deg.
      //
      //   bare offsetTop — transform-immune, but measured relative to
      //   offsetParent, so it is NOT comparable across different parents. A
      //   card at offsetTop 500 inside one parent and another at offsetTop 100
      //   inside a lower parent sort inverted, silently, which is the original
      //   bug back again.
      //
      // Summing the chain fixes both: comparable across parents AND immune to
      // transforms, because offsetTop is layout, not paint.
      function docTop(el) {
        var y = 0;
        for (var n = el; n; n = n.offsetParent) y += n.offsetTop;
        return y;
      }

      // One unmeasurable element among measurable ones is the DANGEROUS case,
      // not the harmless one: it sorts to the front on a zero and reorders
      // every visible card. An earlier version tested `every` here, which fired
      // only when ALL were unmeasurable — exactly backwards. There is no safe
      // bbox fallback either: one hidden element would silently downgrade the
      // whole call from transform-immune back to transform-dependent.
      var unmeasurable = resolved.filter(function (r) {
        return r.el.offsetParent === null && r.el.offsetTop === 0;
      });
      if (unmeasurable.length) {
        throw new Error("hfpat.riseIn: autoOrder cannot measure " +
          unmeasurable.map(function (m) {
            return typeof m.sel === "string" ? m.sel
                 : (m.el.id ? "#" + m.el.id : "element at index " + m.i);
          }).join(", ") +
          " (display:none or detached at call time). Order them yourself, " +
          "top-most on screen first, and pass autoOrder:false.");
      }
      resolved.sort(function (a, b) { return docTop(a.el) - docTop(b.el); });
      list = resolved.map(function (r) { return r.sel; });
    }

    list.forEach(function (sel, i) {
      var from = { y: travel };
      var to = { y: 0, duration: dur, ease: EASE(opts, "enter") };
      if (fade) { from.opacity = 0; to.opacity = 1; }
      if (tilt) { from.rotate = (i % 2 === 1 ? tilt : -tilt * 0.8); to.rotate = 0; }
      tl.fromTo(sel, from, to, at + i * stag);
    });
    return HFPat;
  };

  /* -------------------------------------------------------------------------
     DRIFT FIELD — ambient background motion
     A slow linear translate across the whole composition duration so a
     background layer never freezes. Dead-still backgrounds read as broken
     in short pieces; this is the cheapest fix.

     Keep the range small. Anything past about +/-4% and the layer visibly
     evacuates the frame by the end.

     opts:
       fromPct  default  1.4
       toPct    default -1.3
       duration default  7
       at       default  0
     ------------------------------------------------------------------------- */
  HFPat.driftField = function (tl, selector, opts) {
    opts = opts || {};
    tl.fromTo(selector,
      { yPercent: opts.fromPct == null ? 1.4 : opts.fromPct },
      { yPercent: opts.toPct == null ? -1.3 : opts.toPct,
        duration: opts.duration || 7, ease: EASE(opts, "drift") },
      opts.at || 0);
    return HFPat;
  };

  /* -------------------------------------------------------------------------
     STAR POP — rating row
     Snaps in one at a time with a small overshoot. Injects inline SVG so
     there is no icon-font or network dependency in the render.
     ------------------------------------------------------------------------- */
  var STAR =
    '<svg class="hfp-star" viewBox="0 0 24 24" fill="currentColor">' +
    '<path d="M12 2.6l2.9 5.9 6.5.95-4.7 4.58 1.11 6.47L12 17.45 6.19 20.5 ' +
    '7.3 14.03 2.6 9.45l6.5-.95L12 2.6z"/></svg>';

  HFPat.starPop = function (tl, selector, opts) {
    opts = opts || {};
    var host = typeof selector === "string" ? document.querySelector(selector) : selector;
    if (!host) throw new Error("hfpat.starPop: no element for " + selector);
    var count = opts.count || 5;
    var html = "";
    for (var i = 0; i < count; i++) html += STAR;
    host.innerHTML = html;
    tl.from(host.children, {
      scale: 0, opacity: 0, duration: 0.42,
      ease: EASE(opts, "pop"), stagger: opts.stagger == null ? 0.085 : opts.stagger
    }, opts.at == null ? 2.7 : opts.at);
    return HFPat;
  };

  /* -------------------------------------------------------------------------
     COPY IN — headline and supporting line
     Two-part text entry. The headline carries weight, the sub follows it in.
     No underline, no rule: separation is spacing. That is deliberate — see
     the note in LIBRARY.md about decoration being the thing that breaks.
     ------------------------------------------------------------------------- */
  HFPat.copyIn = function (tl, headSel, subSel, opts) {
    opts = opts || {};
    var at = opts.at == null ? 2.25 : opts.at;
    tl.from(headSel, { opacity: 0, y: 26, duration: 0.75, ease: EASE(opts, "copy") }, at);
    if (subSel) {
      tl.from(subSel, { opacity: 0, y: 16, duration: 0.6, ease: EASE(opts, "copySub") },
        at + (opts.gap == null ? 0.7 : opts.gap));
    }
    return HFPat;
  };

  /* -------------------------------------------------------------------------
     CARD PITCH — derive the stack, do not hand-tune it
     ENFORCED. The example's 300/600/900 tops are right for the example's
     content and nothing else. At 4 digits with one-line bodies they pushed the
     bottom card through the canvas edge; with a mixed line count they produced
     gaps of 41px and 83px in one stack. Both were caught by cold sessions
     re-deriving the pitch by hand, which is work the library should do.

     Measures the real rendered heights and distributes the cards evenly inside
     the frame, so the pitch survives any content change.

       HFPat.cardPitch(["#c1","#c2","#c3"], { top: 96, bottom: 96 });

     opts:
       top / bottom (px)  margin inside the canvas   default 96
       gap          (px)  force a fixed gap instead of distributing
       height       (px)  canvas height              default 1080

     Returns the gap it used. Warns to console if bodies differ in height,
     because an uneven stack is almost always an accidental line-count mismatch.
     ------------------------------------------------------------------------- */
  HFPat.cardPitch = function (selectors, opts) {
    opts = opts || {};
    var top = opts.top == null ? 96 : opts.top;
    var bot = opts.bottom == null ? 96 : opts.bottom;
    var H = opts.height || 1080;

    var els = selectors.map(function (s) {
      return typeof s === "string" ? document.querySelector(s) : s;
    }).filter(Boolean);
    if (els.length < 2) return 0;

    var hs = els.map(function (el) { return el.offsetHeight; });
    var total = hs.reduce(function (a, b) { return a + b; }, 0);
    var gap = opts.gap != null
      ? opts.gap
      : (H - top - bot - total) / (els.length - 1);

    // Was: warn and then apply the negative gap anyway — which wrote tops
    // producing the exact overlap guardMotion exists to catch, from the
    // function meant to prevent it. A warning you then ignore is not a check.
    if (gap < 0) {
      throw new Error("hfpat.cardPitch: content is " +
        Math.round(-gap * (els.length - 1)) + "px taller than the frame allows " +
        "(gap would be " + Math.round(gap) + "px). Shorten bodies, reduce " +
        "margins, or drop a card. Nothing was written.");
    }
    var spread = Math.max.apply(null, hs) - Math.min.apply(null, hs);
    if (spread > 8) {
      console.warn("hfpat.cardPitch: card heights differ by " + Math.round(spread) +
                   "px — usually a mismatched body line count. Uneven gaps will read as a bug.");
    }

    var y = top;
    els.forEach(function (el, i) {
      el.style.top = Math.round(y) + "px";
      y += hs[i] + gap;
    });
    return Math.round(gap);
  };

  /* -------------------------------------------------------------------------
     GUARD MOTION — the collision `check` cannot see
     A card that is still travelling sits lower than its resting place and can
     cover the one beneath it. `check` does not test card-over-card text
     occlusion AT ALL — verified by stripping every suppression and re-running:
     12 findings, none of them this. Suppressed or not, the checker is blind to
     it, so the only defences are ordering (riseIn autoOrder) and this.

     This is closed-form. Each element starts at `at + i*stagger` and its offset
     is travel * (1 - ease(p)); the minimum gap over the entrance window needs
     no rendering. Catches hand-set tops too, which autoOrder cannot.

       HFPat.guardMotion([
         { top: 96,  height: 259 },
         { top: 396, height: 259 },
         { top: 696, height: 259 },
       ], { travel: 940, duration: 3.4, stagger: 0.28 });

     Throws on any negative gap, naming the pair, the time and the depth.
     ------------------------------------------------------------------------- */
  HFPat.guardMotion = function (cards, opts) {
    opts = opts || {};
    var travel = opts.travel == null ? 1106 : opts.travel;
    var dur = opts.duration || 4.2;
    var stag = opts.stagger == null ? 0.26 : opts.stagger;
    var at = opts.at == null ? 0.45 : opts.at;
    var warnAt = opts.warnBelow == null ? 16 : opts.warnBelow;

    // F7: "I checked nothing" must not look like "I found no problem".
    if (!Array.isArray(cards) || cards.length < 2) {
      throw new Error("hfpat.guardMotion: needs at least 2 cards; got " +
        (Array.isArray(cards) ? cards.length : typeof cards) +
        ". Nothing was checked.");
    }
    // F6: malformed input previously went NaN, and NaN < 0 is false, so a
    // broken call passed as a clean run. Loudest possible failure instead.
    cards.forEach(function (c, i) {
      if (!c || !isFinite(c.top) || !isFinite(c.height)) {
        throw new Error("hfpat.guardMotion: card " + i +
          " needs finite top and height; got top=" + (c && c.top) +
          " height=" + (c && c.height));
      }
    });

    // F1: ANIMATION ORDER IS INDEPENDENT OF GEOMETRY. The defect this exists
    // to catch is correct tops with a reversed entrance sequence, and the
    // first version could not express it — it tied stagger index to array
    // index, so it only ever detected an unsorted array and reported static
    // rest geometry at t=at. Pair cards by position, sequence them by `order`.
    var geo = cards.map(function (c, i) {
      return { top: c.top, height: c.height,
               order: c.order == null ? i : c.order, idx: i };
    }).sort(function (a, b) { return a.top - b.top; });

    function ease(p) {
      if (p <= 0) return 0;
      if (p >= 1) return 1;
      return (1 - Math.exp(-K * p)) / DEN;
    }
    function offset(card, t) {
      return travel * (1 - ease((t - (at + card.order * stag)) / dur));
    }

    // F3: closed-form, not sampled. gap(t) is piecewise-smooth and its extremum
    // for a reversed sequence sits exactly on a stagger kink, which a 1/60 grid
    // misses unless stagger happens to be a multiple of 1/60. Evaluate the
    // kinks and both endpoints; that set provably contains the minimum.
    var times = [at];
    cards.forEach(function (c, i) {
      var o = geo[i].order;
      times.push(at + o * stag, at + o * stag + dur);
    });
    times.push(at + (cards.length - 1) * stag + dur);
    times = times.filter(function (t) { return isFinite(t); });

    var worst = null;
    times.forEach(function (t) {
      for (var i = 0; i < geo.length - 1; i++) {
        var gap = (geo[i + 1].top + offset(geo[i + 1], t)) -
                  (geo[i].top + geo[i].height + offset(geo[i], t));
        // Deterministic under ties: keep the EARLIEST time. A tie count > 1
        // is itself signal — it means the stack is uniformly pitched, so every
        // pair fails identically.
        if (worst === null || gap < worst.gap - 1e-9) {
          worst = { gap: gap, t: t, a: geo[i].idx, b: geo[i + 1].idx, ties: 1 };
        } else if (Math.abs(gap - worst.gap) <= 1e-9) {
          worst.ties++;
          if (t < worst.t) { worst.t = t; worst.a = geo[i].idx; worst.b = geo[i + 1].idx; }
        }
      }
    });

    if (worst.gap < 0) {
      throw new Error("hfpat.guardMotion: card " + worst.a + " is covered by card " +
        worst.b + " by " + Math.abs(worst.gap).toFixed(1) + "px at t=" +
        worst.t.toFixed(4) + "s. `check` cannot see this class at all. Order " +
        "top-most first (riseIn autoOrder), shorten the entrance, or widen the gap." +
        (worst.ties > 1 ? " (" + worst.ties + " pairs fail identically — the stack is uniformly pitched.)" : ""));
    }
    // F5: a 4px gap reads as touching. Silence only above warnBelow.
    if (worst.gap < warnAt) {
      console.warn("hfpat.guardMotion: minimum gap is only " +
        worst.gap.toFixed(1) + "px at t=" + worst.t.toFixed(4) +
        "s (cards " + worst.a + "/" + worst.b + "). Reads as touching.");
    }
    return Math.round(worst.gap * 10) / 10;
  };

  /* -------------------------------------------------------------------------
     LAYOUT GUARD — run before rendering, not after
     Text collisions are geometry, not taste. `npm run check` does not catch
     them because they are within tolerance. This does.

     Pass the blocks you positioned absolutely, top to bottom. Throws on any
     overlap and on anything running past the canvas.

       HFPat.guard([
         {name:"eyebrow", top:132, size:23, lines:1, lh:1.35},
         {name:"caption", top:748, size:92, lines:2, lh:1.08},
         {name:"sub",     top:976, size:25, lines:1, lh:1.4},
       ], 1080);
     ------------------------------------------------------------------------- */
  HFPat.guard = function (blocks, canvasHeight) {
    var problems = [], prev = null;
    blocks.forEach(function (b) {
      var bottom = b.top + b.size * (b.lines || 1) * (b.lh || 1.2);
      if (prev && b.top < prev.bottom) {
        problems.push(b.name + " (top " + b.top + ") starts inside " +
          prev.name + " (ends " + Math.round(prev.bottom) + ")");
      }
      if (canvasHeight && bottom > canvasHeight) {
        problems.push(b.name + " runs " + Math.round(bottom - canvasHeight) +
          "px past the canvas");
      }
      prev = { name: b.name, bottom: bottom };
    });
    if (problems.length) throw new Error("hfpat.guard:\n  " + problems.join("\n  "));
    return true;
  };

  global.HFPat = HFPat;
})(typeof window !== "undefined" ? window : this);
