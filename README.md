# NipkowFresnelAayushLit

### From mechanical television to Fresnel-inspired, open-source rotating-aperture lithography

**Project name:** `NipkowFresnelAayushLit`  
**Descriptive name:** NipkowFresnelAayushLit — Open-Source Rotating-Aperture Lithography with Dual-Stage Faceted Optical Steering

> **Naming note:** *Fresnel-inspired* refers to the faceted illumination-carrier geometry. The printed separators are not refractive Fresnel lenses.

> **Project licensing direction:** Apache License 2.0 for original repository content, with permissions and third-party exceptions documented in `LICENSE` and `NOTICE`. No patent application is currently being pursued.  

**Project status:** Concept and engineering exploration. The proposed 1–10 µm feature-size goal, exposure throughput, and multilayer alignment have **not** been experimentally validated.

## Why I am choosing openness over a patent — for now

I began this project after seeing a mechanical television and later a bitluni experiment using ultraviolet light and a phosphor screen. That chain of curiosity eventually led me from an electron-beam idea to a mechanically scanned photolithography concept. The natural next question was whether to patent the architecture.

I have decided **not to pursue a patent at this stage**. I recognize that this may mean sacrificing a future opportunity to claim exclusive commercial rights over ideas I have spent time developing. I am making that trade-off deliberately: I would rather let researchers, students, makers, and manufacturers build, test, criticize, modify, and improve the design than make access to it contingent on my permission.

Desktop 3D printing did not become accessible through the work of one person alone. Open designs, shared experiments, community iteration, and increasingly affordable manufacturing tools helped it grow into an ecosystem. I hope an openly documented approach to desktop lithography can invite a similar kind of experimentation, even if its technical hurdles are very different.

This is **not a claim that NipkowFresnelAayushLit is already a working micron-resolution lithography machine**. It is an invitation to subject the mechanical architecture, optical steering, dosing, alignment and calibration to real measurements and reproducible results.

I would appreciate recognition for the original work and for those who contribute improvements. More importantly, I want the project to be useful. **If the choice is between exclusive control of a speculative invention and giving others a chance to develop it, I am choosing openness for now.**

### Apache 2.0: what this commitment means

- I intend to publish the original software, scripts, documentation, and design source files supplied in this repository under the **Apache License, Version 2.0**, subject to the ownership and third-party exceptions stated in the files.
- Users may use, modify, distribute, and commercially exploit licensed material, while following the license's conditions regarding copies of the license, changed-file notices, retained notices and any applicable `NOTICE` content.
- Apache 2.0 includes a **contributor patent license** for applicable patent claims a contributor is authorized to license. It does **not** grant patents owned by unrelated third parties and does not guarantee freedom to operate.
- Copyright and attribution notices should be retained where required by the license, but **Apache 2.0 does not guarantee public fame, a citation in every article, a trademark endorsement, or that all improvements will be published back**. My request for scholarly/engineering credit is a community norm, not an extra legal restriction.
- Hardware is not identical to software: for downstream fabrication of physical devices, applicability of copyright and patent licenses may be different. A hardware-specific permissive license such as **CERN-OHL-P-2.0** is an option for future review. The present repository uses Apache 2.0 as the declared starting point; the license should not be represented as an all-purpose guarantee of hardware rights.
- This decision is **not a legal dedication of all ideas to the public domain**, nor a promise never to file any patent in the future. It means no application is being pursued now and publication is preferred; public disclosure may irreversibly narrow patent options in various jurisdictions.

See the repository's `LICENSE` and `NOTICE` files. Relevant official guidance: [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0), [applying Apache 2.0](https://www.apache.org/legal/apply-license.html), and [CERN Open Hardware Licence](https://cern-ohl.web.cern.ch/).

## Inspiration: from displaying an image to manufacturing one

This project began with a video of a **mechanical television**. A Nipkow disk creates a raster using rotating apertures arranged along a spiral. Light modulation turns that moving scan into an image—without a modern pixelated display.

Later, I saw **bitluni's simplified mechanical television experiment**, which used ultraviolet illumination to make a phosphor screen produce visible light. What interested me was the separation between the **scanner**, the **energy source**, and the **material that responds to the energy**.

My first thought was: *Could the same moving apertures selectively project electrons, turning the mechanism into an electron-beam writing system?* Electron beams can indeed pass through small apertures, but space-charge effects, scattering, vacuum requirements, aperture interception, and electron focusing make a practical mechanical electron-beam writer substantially more difficult.

That led to a simpler question:

> **Why change the photons into electrons? Why not change what receives the light?**

A television uses scanning light to produce a transient picture. Photolithography uses patterned light exposure to create a persistent chemical pattern in photoresist. Instead of projecting onto a visible phosphor screen, the same broad principle of controlled spatial illumination could expose a resist-coated substrate.

The resulting idea is to explore a **Nipkow drum** rather than a flat disk: a rotating cylindrical aperture pattern surrounding a stationary illumination structure, with angular position measured by an encoder. An electronically driven UV LED array can be synchronized to the moving apertures to form scan lines at the wafer through suitable optics.

The current **V15** architecture uses concentric cylinders, **10 balanced 36° sectors**, **30 aperture rows per sector** (300 apertures in total), and a provision for a separate visible inspection channel. Earlier experiments investigated a single continuous helix and different row counts. These are design specifications, not measured lithographic capabilities.

## Comparison with other desktop lithography approaches

### 1. Imaging architecture

| Characteristic | MSLA / LCD mask | DMD / DLP projection | Single-spot laser direct writing | Proposed Nipkow drum |
|---|---|---|---|---|
| Pattern formation | Programmable transmissive LCD pixels | Programmable micromirror array | Focused laser scanned over resist | Rotating helical apertures with timed illumination |
| Typical exposure geometry | Whole image field | Image field / step-and-repeat | Sequential spot or vector/raster path | Multiple scan lines potentially operating in parallel |
| Imaging modulator | LCD stack | DMD | Beam modulation and scanning mechanism | Mechanical apertures |
| Proprietary imaging device required | Usually | Usually | Not inherently | **No, by design** |
| Moving parts in patterning engine | None required for one field | None required for one field | Scanner and/or stages | Rotating drum, plus any positioning stages |
| Main strength | Cheap full-field exposure | Precise, rapid programmable projection | Flexible direct writing | Open mechanical scanner and possible line parallelism |
| Main challenge | UV losses and panel limitations | Specialized DMD subsystem and optics | Serial scan time for single spot | Optical resolution, scan duty cycle, vibration, and registration |

### 2. Where source power goes

| Consideration | MSLA / LCD | DMD / DLP | Laser direct writing | Nipkow drum |
|---|---|---|---|---|
| Significant optical hurdle | LCD polarizers, pixel aperture and absorption | Mirror efficiency, rejected light and projection optics | Steering and focusing optics | Opaque drum blocks light outside openings |
| Direct path without electronic spatial-light-modulator layer | No | No | Yes | **Yes** |
| UV wavelength flexibility | LCD-dependent | Device/coating-dependent | Laser and optics-dependent | Drum material and optics-dependent |
| Efficiency advantage guaranteed? | No | No | No | **No—must measure delivered wafer dose** |

**Important:** Eliminating an LCD or DMD does not eliminate optical loss. A rotating aperture can block most incident light. The appropriate comparison is *useful irradiance and dose delivered to the resist*, not component count alone. Positioning and timing sources near the active apertures might reduce wasted illumination, but this needs experimental validation.

### 3. Scanning and throughput

| Consideration | MSLA / LCD | DMD / DLP | Single-spot laser | Nipkow drum |
|---|---|---|---|---|
| Concurrent addressable regions | Many pixels | Many micromirrors | One spot | Potentially multiple illuminated aperture channels |
| Primary scanning mechanism | Electronic frame | Electronic frame / field stepping | Beam or XY motion | Rotational motion and helical geometry |
| Exposure speed depends on | Dose, optical power, field area | Dose, power, field stepping | Dwell time, path length, dose | Active channel count, aperture duty cycle, dose, synchronization |
| Potential advantage | High full-field concurrency | High full-field concurrency | Concentrated optical power | Parallel mechanical scan lines |
| Important caveat | Pixel pitch and UV delivery limit fine features | Optics and DMD pitch limit fine features | Multibeam systems also exist | **30 aperture rows per sector do not necessarily mean 30 lines are exposed simultaneously** |

If **N independently illuminated channels** operate simultaneously at the same address rate as a single laser spot, the drum has a *theoretical N-fold addressing-rate* advantage over that **single-spot** comparator. It does **not** imply 50× actual wafer throughput, and it is not directly comparable to the full-field parallelism of LCD/DMD projectors.

### 4. Light-source interchangeability

| Source | MSLA / LCD | DMD / DLP | Laser writer | Proposed Nipkow drum |
|---|---|---|---|---|
| 405 nm UV | Common | Possible | Possible | Initial candidate |
| 365 nm UV | Panel-dependent | Device-dependent | Possible with suitable source/optics | Initial candidate |
| Deep UV | Specialized implementation | Specialized implementation | Specialized implementation | Requires suitable material, shutter, and optics |
| Tin-plasma EUV (~13.5 nm) | Conventional LCD unsuitable | Conventional DMD unsuitable | Entirely different EUV optics | **Not a plug-in swap**: vacuum, reflective optics, debris control, and compatible scanner materials required |

The goal is **control-architecture modularity**: keeping scan geometry and timing concepts separate from the particular light source. It does not mean a single optical/mechanical assembly works across all wavelengths.

### 5. Current readiness

| Metric | Existing desktop lithography approaches | Nipkow drum project |
|---|---|---|
| Patterned-resist demonstrations | Available for LCD, DLP and laser approaches | Not yet demonstrated |
| Target feature size | Varies widely by system and optics | **1–10 µm research target, unverified** |
| Dose uniformity | System-dependent, measurable | To be measured |
| Overlay / multilayer registration | Implemented on some aligners | To be developed and tested |
| Bill of materials | Ranges from low-cost DIY to professional instruments | Not finalized |
| Reproducible open design | Possible, with component-dependent restrictions | Core project objective |

## Design evolution: from Blender visualization to V15 engineering

The project retains two useful design specifications. They describe **different generations**, not two competing definitions of the current hardware.

### Generation 1 — Helical drum simulation (`SKILL_1.md`)

The original simulation explored whether a rotating Nipkow aperture and synchronized LEDs could reconstruct a raster image. It was designed as a **one-input Blender generator**: supply the 3D printer's reliable XY feature size, and the model derives conservative geometry, creates the assembly, synchronizes light flashes to the helix position, and produces an animated smiley-face projection.

| Early simulation property | Specification |
|---|---|
| Drum geometry | Horizontal 45 mm nominal OD × 100 mm length |
| Inner core | Stationary, 25 mm diameter |
| Aperture layout | One continuous helical slit |
| Illumination | 16 LEDs in one straight axial row |
| Optical region | Single 36° arc |
| Animation | Slow-motion, phase-synchronized LEDs and illustrative rays |
| Physical speed reference | 2,000 RPM target, **not** the Blender playback speed |
| Deliverable | Self-validating, monolithic Blender script: Run Script → Play |

This stage established **scan timing, raster mapping, visualization, and code-generation checks**. Its depicted rays were conceptual rather than a validated optical model. It remains a historical demonstration and should not be treated as the manufacturing geometry.

### Generation 2 — Concentric Nipkow lithography scanner (`SKILL(2).md`, V15)

V15 turns the initial animation concept into a **printable, mechanically balanced, calibration-oriented exposure architecture**. It replaces the continuous slit with an aperture lattice repeated identically around the rotor, separates angular encoding from inner/outer cylinder alignment, and introduces source aiming, optical gating, dose calibration, and a proposed visible diagnostic path.

| Current V15 property | Design baseline |
|---|---|
| Rotating outer drum | 66 mm OD; 2 mm wall |
| Active scan height | 78 mm, plus a 6 mm non-scanning alignment collar |
| Balanced scan lattice | 10 × 36° sectors; 30 rows per sector; **300 apertures** |
| Aperture geometry | 1.6 mm diameter; 2.6 mm row pitch |
| Stationary inner carrier | 56 mm OD, with full-circumference Fresnel-like separator rings |
| LED channels | 30 axial row channels, 1.7 mm channel width + 0.9 mm separator |
| Optical exposure regions | 25° broad illumination arc; independently adjustable 6° precision gate |
| Position feedback | 80-slot rotating encoder, with separate sight-hole optical registration |
| Final optics constraint | Nominal 25 mm lens; actual focus and image quality **unverified** |
| Diagnostic option | Red visible inspection sector 180° opposite the UV exposure sector |
| Resolution objective | **1–10 µm**, not yet demonstrated |

The Fresnel-like printed ribs and angled aperture tunnels are **directional baffles/source-aiming features**, not proven refractive lenses. Likewise, the visible red channel is intended to diagnose scan stability and distortion; it cannot substitute for calibrated absolute UV dose measurement.

### Fresnel-inspired illumination carrier and dual-stage faceted optical steering

V15 adds a **stationary cylindrical illumination carrier** with circumferential separator ridges inspired by Fresnel-style stepped geometry. This is not a glass Fresnel lens: the printed ridges mechanically position, separate and baffle LED channels, and their angles may help direct *useful* source emission toward the projection optics. The design deliberately treats that as an experimentally testable hypothesis.

| V15 source and aperture feature | Geometry or intended function |
|---|---|
| Inner stationary carrier | 56 mm outer diameter; 2 mm wall |
| Horizontal Fresnel-like separators | Full 360° rings around the inner cylinder |
| LED channels | 30 axial row channels, each 1.7 mm wide |
| Channel separators | 0.9 mm wide, 2 mm nominal radial ridge height; 2.6 mm row pitch |
| Facet directions | Upper channels biased downward, lower channels upward, center nearly neutral, toward optical center |
| Vertical boundary ribs | Ten ribs at the 36° sector boundaries, avoiding the central optical arc |
| Rotating outer drum | 1.6 mm apertures formed as angled tunnels through a 2 mm wall |
| Aperture-tunnel function | Directionally filter rays aimed toward a sector-local virtual lens pupil; **do not refract or bend light** |
| Broad versus precision region | 25° candidate illumination arc and independent 6° precision gate |

**Two-stage proposed optical path:**

```text
stationary UV LED channel
  -> Fresnel-like faceted carrier / source aiming & baffling
  -> angled moving Nipkow aperture / directional filtering
  -> wavelength-compatible projection objective
  -> photoresist-coated substrate
```

The purpose is to investigate **higher useful pupil coupling, reduced stray light, and more uniform wafer-plane irradiance**, not to claim that all emitted LED light can be concentrated through the lens. Optical étendue, the finite LED emitting area, aperture duty cycle, absorption, and field aberrations remain hard constraints. Narrow tunnels can improve directional selectivity while also **reducing total transmitted power**.

**Validation:** Compare straight and tilted LED/tunnel coupons; measure pupil power, wafer-plane spot size (point-spread function), field uniformity, and developed resist patterns. The approximate 25 mm final lens diameter is not evidence of a particular resolution; the 1–10 µm feature goal is still unverified.

### What changed, and why

| Engineering question | Early simulation | V15 design response |
|---|---|---|
| How should an image be scanned? | A single continuous helix crossing an axial LED row | Ten sector-repeated sets of discrete aperture rows |
| How can the rotor avoid designed-in imbalance? | Not the central focus | Exact 36° repetition of material-removing features |
| How is exposure synchronized? | Computed helix crossing times | Physical rotary encoder plus calibrated phase mapping |
| How are inner and outer elements aligned? | Visual geometry | Separate through-sight holes in a non-scanning collar |
| How is the source light managed? | Conceptual rays | 360° separator rings, directional aperture tunnels, pupil-coupling tests |
| How is useful exposure controlled? | LED ON/OFF demonstration | Broad illumination region separated from a narrow precision gate |
| How is dose established? | Not a physical exposure model | Repeatable photoresist processing and experimental scan-pass exposure ladders |
| How can patterns be inspected? | Virtual screen | Proposed opposing red-light diagnostic/inspection channel |
| How is micron-scale performance established? | Not demonstrated | Measure developed features, point-spread function, aberrations, runout, and overlay |

### Development status and next verification steps

The V15 model is an **engineering specification and test plan**, not proof that a printed scanner can resolve micrometre features. A 1.6 mm mechanical opening does not become a 1–10 µm feature merely because the light passes through a 25 mm lens. The optical train, effective aperture, demagnification, aberrations, source extent, dose and mechanical placement error must all be tested.

Recommended experimental sequence:

1. Print the inner carrier and outer rotor as **separate parts**; measure assembled clearances and runout.
2. Validate rotor encoder phase separately from relative inner/outer optical alignment.
3. Test transmitted irradiance, spot position, spot size and pupil coupling with source/tunnel aiming coupons.
4. Measure field distortion and derive the mapping from `(drum angle, row)` to `(substrate x, y)` for software pre-warp.
5. Produce a photoresist exposure ladder using a controlled spin-coat process and repeated scan passes; later anchor dose using a calibrated UV sensor.
6. Only after reproducible developed structures are demonstrated, evaluate the red diagnostic channel against UV exposure results and investigate multilayer overlay.

> **Documentation convention:** Treat `SKILL(2).md` (V15) as the current mechanical baseline and `SKILL_1.md` as the legacy educational animation specification. Neither file alone establishes experimentally validated lithographic resolution.

## What this project is testing

The central hypothesis is not that mechanical scanning is automatically faster or more precise than electronic projection. It is that a **3D-printable, encoder-synchronized, multi-aperture drum** may provide a useful alternative imaging architecture without depending on a proprietary electronic spatial light modulator.

The proof will come from measurements of:

- Developed photoresist feature width and line spacing.
- Wafer-plane irradiance, accumulated dose, and exposure uniformity.
- Scan-line placement, distortion, drum runout, and timing jitter.
- Throughput in patterned area per unit time.
- Registration accuracy between successive exposures.

**The original spark remains simple:** What if the mechanism that once *displayed* an image could instead *manufacture* one?


---

## Prior-art research and patent possibilities (historical analysis; no filing planned)

> **Current decision:** Open publication takes priority over patent filings. This section is preserved to show the known prior-art landscape and the technical features examined; it is not a current patent filing plan.

> **Status and scope (18 October 2026):** This is an engineering-focused invention disclosure and preliminary patent landscape, **not a legal opinion**, a novelty determination, a freedom-to-operate analysis, or a statement that a patent has been filed. It deliberately records potential inventive directions—including weak or speculative ones—without presenting them as established claims. Consult a qualified patent professional before publishing additional enabling disclosures or making filing decisions.

### Why this research was conducted

The broad concept of mechanically scanning light using Nipkow apertures is old. The project therefore should **not** assume that a claim such as “using a Nipkow drum to expose photoresist” is automatically new. The narrower engineering combinations might be worth studying: a concentric, mechanically balanced lithography scanner; faceted source-side LED aiming with moving direction-selective aperture tunnels; separate encoder and optical-registration subsystems; and a UV exposure sector paired with a visible diagnostic sector.

Patentability and commercial value are separate questions:

- **Patentability:** Novelty, inventive step/non-obviousness, industrial applicability and applicable statutory restrictions, assessed against published and unpublished-to-us earlier work.
- **Strategic value:** Whether exclusivity, defensive protection or licensing leverage justifies filing, prosecution, maintenance and possible enforcement costs.
- **Freedom to operate:** Whether building or selling a product may implicate another party's *currently enforceable* claims; obtaining one's own patent does not grant freedom to practice the design.
- **Open-source compatibility:** Public CAD/firmware repositories and patent ownership can coexist, but software/hardware copyrights, patent grants, non-commercial conditions and open-hardware certification must be handled explicitly.

### Candidate inventions and claim directions

The ratings below are **investigation priorities, not probabilities** of patent issuance.

| Candidate feature | Preliminary potential | What could be technically distinctive | Main challenge / evidence required |
|---|---|---|---|
| Nipkow scanning applied to photoresist | Low / uncertain | Repurpose rotary-aperture imaging for a persistent lithographic exposure | Very broad claim; long history of rotary optical scanning and photolithography |
| Nested stationary inner carrier and rotating cylindrical aperture shell | Moderate | Compact coaxial scan/source architecture with independently supported and registered bodies | Find earlier cylindrical scanners and related exposure machines; characterize actual packaging and alignment benefit |
| Ten balanced 36° sectors with 30 rows per sector | Low–moderate | Symmetric material removal while producing ten repeated scan events per revolution | Symmetry and replication are familiar engineering tools; show unexpected measurable advantage, not merely a chosen count |
| Angled source facets + angled aperture tunnels | Moderate, highly prior-art sensitive | **Specific non-refractive** LED carrier, directional baffling and sector-local pupil targeting integrated with the rotating drum | Nipkow collectors including Fresnel elements are documented; prove a new geometry/control relationship and net useful wafer irradiance |
| Independently timed illumination channels and 6° precision exposure gate | Moderate | Encoder-coordinate exposure control with narrow high-quality field and digital pre-warp | Electronic gating/encoders are established; demonstrate a particular correction or dose-uniformity mechanism |
| Separate rotor encoder and relative optical registration | Moderate | A rotary angular tracker plus through-sight registration of inner source carrier, outer drum, and objective | Registration is known; novelty may be in the arrangement, calibration sequence, or resulting error correction |
| UV exposure sector and red inspection sector separated by 180° | Moderate–potentially interesting | Two sector-local optical channels tied to the same mechanical coordinate system, with measured red-to-UV correction | A second light color alone is weak; demonstrate a real calibration/control loop, not just a simultaneous visual preview |
| Swappable source module | Low–moderate | Source-independent scan and timing control with wavelength-specific interchangeable optics/isolation | Modularity is common; EUV is **not** a plug-in interchange of LEDs |
| Fresnel-like continuous 360° ridges and 36° boundary ribs | Moderate, dependent on claims | A specifically manufacturable faceted LED carrier that preserves channel alignment and unobstructed optical sectors | Printed plastic is not a Fresnel refractive optic; ordinary fins/baffles can be obvious |
| Fully printable/open-source/AI-assisted production | Low standing alone | Reproducible hardware and documentation strategy | These are important project benefits but do not by themselves show inventive technical subject matter |

### The potentially strongest integrated system

An invention-disclosure title to explore—not an assertion of patentability:

**“Encoder-Synchronized Multi-Sector Rotating-Aperture Lithography System with Faceted Illumination, Relative Optical Registration, and Visible Exposure Diagnostics.”**

Possible independent areas for a professional claim analysis:

1. **Apparatus:** a concentric stationary faceted light carrier and a rotating aperture drum, with a calibrated pupil-coupling geometry and objective.
2. **Exposure method:** mapping true encoder phase and aperture-row identity through a measured `(angle, row) → (wafer x, wafer y)` calibration, electronically gating irradiation and aggregating controlled scan-pass dose.
3. **Registration method:** separately determining rotor phase and stationary-to-rotor/lens alignment from dedicated physical references, rather than treating commanded motor position as an optical coordinate.
4. **Diagnostics method:** using an opposite-sector visible illumination path as a measured proxy for scan placement/brightness, calibrated against actual UV measurements to detect drift or adjust exposure.
5. **Mechanical manufacturing arrangement:** constructing a tenfold-balanced, perforated drum with non-scanning registration collar and repeat-symmetric removed mass, potentially in combination with the calibrated illumination subsystem.

None of these paragraphs are legal claims. The best protectable subject matter, if any, may emerge from measured optical registration, dose correction, or field-mapping improvements during prototype testing.

### Patent-prior-art starting points

These are **concrete search leads** for closer claim-by-claim examination, not a complete survey and not a finding of infringement. Patent status shown by databases may be incomplete or jurisdiction-dependent. Critically, older or expired documents may still constitute **prior art** even where their claims are no longer enforceable.

| Publication | Subject / why it matters | Preliminary distinction to investigate |
|---|---|---|
| [EP0539691A2](https://patents.google.com/patent/EP0539691A2/en) | **Nipkow scanner with pinhole geometry and light collectors, including Fresnel lenses, mirrors or microlenses, intended to improve light utilization and reduce unevenness** | **Very relevant to the Fresnel aspect.** V15 uses printed faceted LED-separator/aiming geometry and tilted aperture tunnels rather than claiming a refractive Fresnel microlens collector; verify whether this combination is genuinely non-obvious |
| [JP3019754B2](https://patents.google.com/patent/JP3019754B2/en) | Nipkow-disk optical scanner | Establishes rotary-aperture scanning as a mature art; read claims and cited families |
| [US6545265B1](https://patents.google.com/patent/US6545265B1/en) | Confocal microscopic imaging and patterned optical scanning | Search for disclosed scan arrangement, alignment and synchronization details before treating it as an anticipation reference |
| [US5283684A](https://patents.google.com/patent/US5283684A/en) | Construction of confocal microscope components | Relevant to optical pinhole/component manufacturing; do not assume it teaches lithography |
| [WO2020077780A1](https://patents.google.com/patent/WO2020077780A1/en) | Multi-aperture Nipkow scanning disk for a confocal 3D measurement device | Materials, aperture creation and scan-band geometries may inform scope |
| [EP1953580A2](https://patents.google.com/patent/EP1953580A2/en) | Confocal optical scanning systems; discusses high loss in conventional Nipkow illumination | Background for throughput/dose assertions, not a measurement of V15 |
| [US1973203A](https://patents.google.com/patent/US1973203A/en) | Historical Nipkow/optical-element design reference | Verify the original disclosure and patent family before making specific novelty assertions |
| [DE102018114162B4](https://patents.google.com/patent/DE102018114162B4/en) | Rotating perforated optical imaging design | Compare aperture, imaging and scanning claims in the actual specification |

**Further search queries for formal diligence:** `cylindrical Nipkow scanner photolithography`; `rotating drum maskless exposure photoresist`; `rotating aperture exposure apparatus semiconductor`; `spinning disk UV lithography`; `angled pinhole pupil relay`; `Fresnel collector Nipkow LED`; `rotating mask image-writing`; `multiwavelength confocal scanning registration`; `encoder corrected lithographic raster`; and `multi-sector visible alignment ultraviolet exposure`. Search Google Patents, Espacenet, WIPO PATENTSCOPE, USPTO and InPASS, including related patent families, non-patent publications, dissertations, commercial manuals and videos.

### Specific technical differences to demonstrate

An inventor's claim is much stronger when an arrangement produces a **measurable technical effect** than when it is only visually different.

| Hypothesis | A/B comparison | Evidence worth publishing or preserving |
|---|---|---|
| Faceted LED carrier increases *useful* pupil-coupled light | Straight channels vs faceted channels, identical LEDs and current | Wafer-plane irradiance, pupil throughput, variation across 30 rows, stray light |
| Angled tunnel produces better exposure-field control | Radial holes vs calibrated inclined holes | Transmitted power **and** substrate point-spread function, aberrations, vignetting |
| Ten-sector balanced rotor improves scan placement | Balanced V15 vs intentionally characterized imbalance, same speed | Radial/axial runout, vibration spectrum and developed line-placement error |
| Precision-gate control limits field error | 25° broad gate vs 6° narrow gate | Feature width, edge placement, distortion, exposure dose and throughput penalty |
| Visible/UV paired sectors form a useful closed loop | No correction vs red-camera/encoder-calibrated correction | Residual placement error, brightness drift, UV-dose prediction error and repeatability |
| Separate optical registration enables better multilayer overlay | Encoder-only alignment vs through-sight plus measured phase calibration | Two-layer overlay error across wafer or tile |
| Multiple independent channels increase useful throughput | Single channel vs N concurrent channels, matched resist dose | Actual developed area per minute, electrical energy per useful patterned area |

### Open-source, defensive publication, and licensing choices (options considered)

| Route | What it provides | Caveat |
|---|---|---|
| Publish entirely as open hardware, no patent | Fast peer review, reproducibility and potential defensive publication | Does not provide an exclusive right; subsequent third-party improvements can still be patented |
| File patent, grant broad royalty-free patent rights with open-hardware release | Potential defensive leverage and community assurance | Patent filing/prosecution costs remain; patent license terms need expert drafting |
| Patent and dual-license separate commercial activities | Possible licensing income | A non-commercial limitation typically conflicts with claims of fully open hardware; check the chosen definition and license |
| Publish a dated defensive technical disclosure | Helps document prior art against later claims | Cannot necessarily restore patent rights already lost by disclosure; content should be enabling and findable |
| Keep unfiled details confidential temporarily | Preserves some options while counsel searches prior art | Reduces immediate openness; cannot undo earlier disclosures |

**Patent ownership is not incompatible with open hardware**, but simply placing an STL, design description or firmware online is **not necessarily** an express patent license. Define permissions for making, using, modifying, selling, distributing and downstream improvements in a clearly chosen hardware/software/documentation licensing framework. If the goal is OSHWA-style open hardware, examine whether any field-of-use restriction conflicts with that commitment.

### India-first filing and disclosure considerations (reference only)

- India’s **Patents Act, 1970, Section 31** contains limited exceptions for specified notified exhibitions and learned-society publication; it is **not a general assurance** that an ordinary LinkedIn/GitHub publication enjoys a 12-month grace period. See [official Section 31](https://www.ipindia.gov.in/acts/patent-act-1970/section-31).
- An Indian filing may begin with a **provisional specification**, but a complete specification generally must follow **within 12 months**; there is no ordinary extension of that deadline. See [official Section 9](https://www.ipindia.gov.in/acts/patent-act-1970/section-9) and [Patent Office filing overview](https://www.ipindia.gov.in/filing-process).
- An Indian Patent Office guidance document lists the basic individual e-filing application fee as **₹1,600**, but total statutory charges and professional drafting/search/prosecution fees can be substantially higher; verify the latest category and fee schedule before paying. See [IPO guidance](https://ipindia.gov.in/storage/content-media/i3ENZcn1Q3LOzL4KtcyZza7Sh1Nx2PDg2PPNif11.pdf).
- Prior public disclosures, including GitHub commits, videos, README revisions, publications and presentations, can matter to novelty. Preserve **timestamps, commit histories, files and exact public/private status**. Private project conversations are not automatically public disclosure, but do not assume all AI tools or sharing configurations have identical confidentiality terms.
- A provisional specification is not a placeholder slogan: disclose the actual inventive concept with enough engineering detail to support later claims. Later-added matter may not obtain the original priority date.
- Whether the invention is patent-eligible, whether it belongs to the inventor or an employer, and whether foreign filings or secrecy restrictions apply require jurisdiction-specific professional review.

### Suggested invention-disclosure dossier (also useful for open provenance)

Before any filing decision, assemble a private dated package containing:

1. V1-to-V15 version timeline and dated changes, including the discontinued continuous-helix model and the current 300-aperture architecture.
2. Dimensioned CAD/STEP/STL, cross-sections, exploded diagrams, and production drawings of the **66 mm OD** rotor and **56 mm OD** stationary carrier.
3. Schematic and dimensional explanation of all **30 LED channels**, full-ring faceted separators, ten 36° vertical boundaries, angled tunnels, 25° illumination arc, 6° precision gate and common pupil model.
4. Exact 36° repetition/balancing rationale, 80 encoder slots, sight-hole alignment collar and optical-registration procedure.
5. Firmware/software timing and correction algorithms, including recorded encoder phase and `(angle, row) ↔ (x, y)` calibration mapping.
6. UV/visible opposite-sector optical layouts, sensor design, and any measured mapping from visible signal to UV dose—clearly distinguishing **hypothesis** from results.
7. Optical data: LED spectrum and source size, irradiance, transmission, PSF, image-field distortion, pupil coupling, thermal drift and exposure calibration.
8. Mechanical and resist-process data: assembled clearances, runout/vibration, spin coating, developed lines/spaces, wafer overlay, dose-response and throughput.
9. A claim-feature/prior-art mapping matrix with publication numbers, earliest priority dates, jurisdictions, exact claim elements and your differentiating evidence.
10. A public-disclosure log with precise links, release tags and dates, plus your desired open-hardware and commercial-permission strategy.

### Overall assessment

**Worth a formal search:** Yes—particularly the integrated *faceted stationary source carrier + direction-selective rotating apertures + encoder-calibrated exposure/registration + dual-sector diagnostics*.

**Established patentability:** No. The most important Fresnel/Nipkow prior art makes broad “Fresnel plus Nipkow” claims especially vulnerable. Narrow claims may be possible only if the specific implementation and its technical effect survive a prior-art and obviousness analysis.

**Current project choice:** Publish the work openly under Apache 2.0 for the repository materials as stated in `LICENSE` and `NOTICE`, retain dated attribution and provenance, and use experimental reproducibility to guide future work. No patent filing is planned at this stage. The earlier filing analysis remains below as transparent historical research, not a call to pursue exclusivity.



## Project design source documents

- [V15 canonical engineering specification](docs/engineering/v15-design-specification.md) — the current mechanical baseline, Fresnel-like faceted illumination geometry, alignment, dose calibration, and optical uncertainties.
- [Legacy helical-drum simulation specification](docs/legacy/helical-drum-simulation.md) — the earlier single-helix, one-input Blender demonstration. Historical reference only; it does not supersede V15.

The engineering specifications describe proposed designs, not verified lithographic performance.
