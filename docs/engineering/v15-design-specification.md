---
name: nipkow-drum-lithography-v15
description: "Canonical engineering skill for the V15 concentric Nipkow-drum lithography projector: balanced 10x36° rotating drum, 78 mm active height, 30-row aperture lattice, stationary Fresnel-like LED carrier, optical/mechanical registration, V13 encoder, 25 mm projection-lens constraints, empirical UV-dose calibration, and Blender generation/debug rules."
---

# Nipkow Drum Lithography Projector — Canonical V15 Engineering Skill

This file is the canonical project state for the **Nipkow DRUM lithography setup**.

It supersedes earlier project skills that assumed a 45 mm outer drum, 100 mm length, one continuous helical slit, one straight axial LED line, a 25 mm solid inner core, and a single lower 36° reflector/window. Those concepts remain useful as historical visualization experiments, but **must not be silently reintroduced into the V15 manufacturing design**. See [D-LEGACY-01].

The V15 design is a nested concentric-cylinder scanner:

1. a **rotating outer Nipkow drum**;
2. a **stationary inner LED / Fresnel-like carrier**;
3. separate mechanical support for the two cylinders;
4. an optical encoder for rotating-drum phase;
5. separate relative optical registration between inner carrier, drum, and lens axis;
6. a 25 mm final projection lens retained as the current optical constraint;
7. a visible diagnostic channel that may be placed 180° opposite the UV exposure channel.

The Blender CAD should be printable, inspectable, self-validating, and should keep the inner and outer cylinders as **separate printable objects**.

---

# 1. STATUS LABELS

## 1.1 Locked mechanical baseline

Do not change these defaults unless the user explicitly requests a redesign:

```text
Outer drum OD                         66.0 mm
Outer drum wall                      2.0 mm
Active scan height                   78.0 mm
Alignment collar above scan          6.0 mm
Total cylindrical shell height       84.0 mm
Separate closed base                 2.0 mm
Expanded rotating base OD            76.0 mm

Nipkow sectors                       10
Sector repeat                        36.0°
Rows per sector                      30
Row pitch                            2.6 mm
Aperture diameter                    1.6 mm
Bottom aperture-edge margin          0.5 mm
Top aperture-edge margin             0.5 mm
Total Nipkow apertures               300

Inner carrier OD                     56.0 mm
Inner carrier wall                   2.0 mm
Fresnel separator radial height      2.0 mm
Fin-tip OD                           60.0 mm
Nominal radial clearance             1.0 mm
LED channel width                    1.7 mm
Separator width                      0.9 mm
```

The 78 mm active height is intentional:

\[
78.0=0.5+1.6+29(2.6)+0.5
\]

Thus 30 rows fit with exactly 0.5 mm of solid material beyond the first and last 1.6 mm apertures. See [D-HEIGHT-01].

## 1.2 Provisional optical defaults

These are engineering starting points, not proven optical truths:

```text
Final lens nominal diameter           25 mm
Broad illumination arc                25°
Precision exposure gate               6°
Virtual pupil distance                120 mm beyond outer surface
Maximum allowed generated tunnel tilt 30°
Current calculated worst tilt         about 28.3°
```

Keep them parameterized. Final choices must be driven by measured point-spread function, irradiance, field curvature, distortion, exposure threshold, and mechanical runout. See [D-OPTICS-01], [D-SKEPTICISM-01].

---

# 2. COORDINATE SYSTEM

Earlier slow-motion Blender simulations used world X as the horizontal drum axis. Current V15 manufacturing scripts use:

```text
Z = common cylinder / shaft axis
XY = circular cross-section
```

This is a CAD/printing convention; the physical machine may still mount the drum horizontally.

For V15:

```text
active optical wall     Z = 0 .. 78 mm
alignment collar        Z = 78 .. 84 mm
closed rotating base    Z = -2 .. 0 mm
motor hub               extends below Z = -2 mm
```

Keep the optical center based on the active region:

```python
ACTIVE_CENTER_Z = ACTIVE_WALL_HEIGHT_MM * 0.5
```

Do **not** move the optical center to the middle of the 84 mm shell when the alignment collar is added. See [D-ALIGN-BAND-01].

---

# 3. OUTER ROTATING DRUM

## 3.1 Body

```python
OUTER_DRUM_OD_MM = 66.0
OUTER_WALL_THICKNESS_MM = 2.0
OUTER_DRUM_ID_MM = 62.0
ACTIVE_WALL_HEIGHT_MM = 78.0
ALIGNMENT_BAND_HEIGHT_MM = 6.0
TOTAL_CYLINDER_HEIGHT_MM = 84.0
OUTER_BASE_THICKNESS_MM = 2.0
```

The 2 mm closed base is **separate from the active cylinder height**. Never subtract the base thickness from the 78 mm scan height. See [D-BASE-01].

## 3.2 Motor interface

Current baseline:

```text
NEMA 17 direct drive for prototype
nominal shaft             5 mm D-shaft
modeled D-bore            5.20 mm
flat-to-round dimension   about 4.70 mm
hub OD                    18 mm
hub length                10 mm
```

User preference:

- avoid set screws if possible;
- use a D-shaped interface;
- retain short shaft overhang;
- keep rotor close to the front motor bearing.

At low/moderate RPM a lightweight rotor may be directly driven. For larger diameter, higher RPM, or heavier optical hardware, recommend an additional bearing-supported shaft instead of cantilevering the complete rotor on the NEMA 17 shaft.

## 3.3 Scaling rule

For a thin cylindrical shell, rough polar inertia scales approximately as:

\[
I\propto Hr^3
\]

Therefore increasing **height** is relatively cheap mechanically while increasing **radius** is expensive. Going from 66 mm to 78 mm active height at the same radius raises idealized shell inertia only by about 18%, whereas increasing radius from 33 to 40 mm gives approximately 1.78× before height is included. This is why V15 increases axial height while retaining 66 mm OD. See [D-SCALE-01].

---

# 4. NIPKOW APERTURE LATTICE

## 4.1 Tenfold balance

Use:

```python
SECTOR_COUNT = 10
SECTOR_REPEAT_DEG = 36.0
```

Every rotating geometry that removes material must be derived from one canonical sector and repeated by exact rotation:

\[
G_k=R_z(k\,36^\circ)G_0,\qquad k=0\ldots9
\]

This includes Nipkow apertures, encoder groups, shallow engraved markings, sight holes, and any lightening recesses.

The reason for 36° is not merely optical. Tenfold repetition reduces designed-in center-of-mass error, distributes holes around the circumference, gives ten scan events per revolution, lowers required RPM for a given scan-pass rate, and preserves structural bridges. See [D-BALANCE-01].

## 4.2 Aperture rows

```python
ROW_COUNT = 30
ROW_PITCH_MM = 2.60
APERTURE_DIAMETER_MM = 1.60
END_MARGIN_MM = 0.50
```

Centers:

```python
FIRST_ROW_CENTER_Z = 1.30
z_i = 1.30 + i*2.60
# i = 0 .. 29
```

The last center is 76.7 mm and the final aperture edge is at 77.5 mm, leaving 0.5 mm to Z=78 mm.

## 4.3 Slanted pattern

Within each 36° sector, the 30 aperture centers progress across the sector. Mechanical scan lattice and tunnel pointing direction are separate:

```text
aperture surface position = scan geometry
tunnel axis               = directional filtering / pupil coupling
```

Do not shift aperture surface centers merely to create Fresnel-like steering unless a calibrated pre-warp explicitly calls for it.

---

# 5. BOOLEAN RELIABILITY — CRITICAL BLENDER RULE

Several later Blender versions failed because they departed from the Boolean method that worked in V3.

For Nipkow apertures, prefer the V3-style sequence:

1. create every aperture cutter as an independent **closed cylinder**;
2. set radial/3D orientation at primitive creation time;
3. put all aperture cutters in a dedicated collection;
4. apply **one collection DIFFERENCE Boolean** to the shell;
5. delete cutter cylinders only **after** the Boolean applies successfully;
6. verify no cutter objects remain;
7. raise an error rather than exporting a bad STL.

Use:

```python
BOOLEAN_SOLVER = 'EXACT'
```

Prefer collection Boolean for the large aperture set. For simple encoder slots, individual primitive Boolean cuts remain acceptable because the V3 rectangular-slot method proved reliable. See [D-BOOLEAN-01].

---

# 6. V13 ROTATIONAL ENCODER — RETAIN IN V15

The optical encoder tracks:

\[
\theta_{drum}
\]

It is **not** the relative optical alignment system for the stationary inner cylinder.

Current retained encoder geometry:

```text
10 sectors
8 individual rectangular slots per sector
80 total slots
36° sector repetition
slot radial length             6.0 mm
slot center radius             27 mm
progressive tangential width   1.8 mm -> 0.6 mm
```

The discrete progressive slots can produce recognizable analog pulse shapes when the optical footprint is comparable to slot width.

### Sensor guidance

LDRs can be used for a slow proof-of-concept, but response time can become the limiting factor. At 60 RPM there is one revolution per second and 80 encoder events per second, or 12.5 ms/event. This is already marginal for many LDRs.

For higher RPM prefer a photodiode or phototransistor.

For two analog sensors, a useful normalized differential metric is:

\[
D_n=\frac{A-B}{A+B}
\]

or fixed-point:

\[
D_Q=\frac{(A-B)32768}{A+B}
\]

Use ADC DMA where practical. See [D-ENCODER-01].

---

# 7. INNER STATIONARY FRESNEL-LIKE LED CARRIER

## 7.1 Mechanical body

```python
INNER_CARRIER_OD_MM = 56.0
INNER_CARRIER_WALL_THICKNESS_MM = 2.0
INNER_CARRIER_ID_MM = 52.0
```

Full Fresnel-ring tip OD is 60 mm. Outer drum ID is 62 mm, so nominal plastic-to-plastic radial clearance is:

\[
(62-60)/2=1.0\text{ mm}
\]

This is a **nominal CAD clearance only**. Final clearance must include actual LED package height, PCB thickness, adhesive, wiring, print runout, motor/shaft eccentricity, and thermal movement. Do not treat 1.0 mm as sufficient after LEDs are mounted until the real stack is measured. See [D-CLEARANCE-01].

## 7.2 LED channel pitch correction

A key V14 correction: if LEDs sit **between** fins, fin centers must not be aligned to optical row centers.

V15 uses:

```text
LED channel width     1.7 mm
separator fin width   0.9 mm
pitch                 2.6 mm
```

Thus:

\[
1.7+0.9=2.6\text{ mm}
\]

The **30 LED channels**, not the fins, are centered on the 30 Nipkow row positions. There are 29 full internal separators plus narrow end retaining lips. See [D-CHANNEL-01].

## 7.3 Full 360° Fresnel-like horizontal rings

The horizontal separator ridges now continue around the **entire 360° inner cylinder**. Do not terminate them at only the 25° optical arc.

The outer edges of these rings may shift axially toward the active-height center:

- upper rings lean downward;
- lower rings lean upward;
- center rings are nearly neutral.

This is a source/baffle geometry, not a refractive Fresnel lens. Use the terminology **Fresnel-like faceted source aiming** or **dual-stage faceted ray steering**. Do not claim that the printed fins themselves refract light. See [D-FRESNEL-01].

## 7.4 Vertical sector-boundary ridges

The original ±12.5° vertical ribs were moved because they occupied the edge of the central optical arc.

Current design:

```text
10 vertical ribs
one at each 36° sector boundary
angles:
18°, 54°, 90°, 126°, 162°,
198°, 234°, 270°, 306°, 342°
```

These ribs run axially over the active 78 mm region, divide the inner cylinder into ten 36° sectors, leave the central 25° optical region unobstructed, and allow LED strips to occupy more of each 36° sector. See [D-VERTICAL-RIDGE-01].

---

# 8. 36° MECHANICAL SECTOR VS 25° OPTICAL ARC VS 6° PRECISION GATE

These are three different concepts.

## 8.1 36° mechanical repetition

\[
360^\circ/10=36^\circ
\]

This is the balance and scan-event architecture.

## 8.2 Broad 25° optical / illumination region

```python
LED_ACTIVE_ARC_DEG = 25.0
```

At a 66 mm drum diameter, the 25° chord is approximately:

\[
66\sin(12.5^\circ)\approx14.3\text{ mm}
\]

The 36° chord is:

\[
66\sin(18^\circ)\approx20.4\text{ mm}
\]

The 25° active window therefore retains useful geometric margin relative to a nominal 25 mm lens aperture. However, the physical LED carrier can now mechanically host LED strips over **more of the 36° sector**, because the vertical ribs have moved to sector boundaries. Treat 25° as a calibrated optical starting window, not a mechanical hard stop. See [D-WINDOW-01].

## 8.3 6° precision exposure gate

```python
PRECISION_GATE_DEG = 6.0
```

The precision gate exists because a broad curved-drum field can suffer field curvature, defocus, coma, astigmatism, pupil clipping, and timing-dependent blur.

For radius 33 mm, the sag of a 25° full window relative to the tangent plane is:

\[
s=33(1-\cos12.5^\circ)\approx0.78\text{ mm}
\]

A 6° full gate has:

\[
s=33(1-\cos3^\circ)\approx0.045\text{ mm}
\]

about 45 µm of geometric sag before lens effects.

Therefore V15 must keep **illumination width** and **precision exposure width** independent. Begin validation with the narrow gate and widen only after measured focus/PSF validation. See [D-GATE-01].

---

# 9. DUAL-STEERING CONCEPT

## 9.1 Stage A — LED / fin source aiming

Upper LED channels are biased toward the optical center; lower channels are biased upward. This attempts to improve coupling of a tall source into the final lens pupil.

## 9.2 Stage B — angled Nipkow tunnels

The 1.6 mm apertures become short tilted tunnels through the 2 mm drum wall.

They do **not** bend light. They preferentially transmit rays already traveling near their tunnel axis.

Design intent:

```text
LED / source channel
        ->
Fresnel-like source/baffle aiming
        ->
angled Nipkow tunnel
        ->
lens pupil
```

## 9.3 Shared pupil model

Current script uses:

```python
PUPIL_DISTANCE_FROM_OUTER_SURFACE_MM = 120.0
```

This is provisional. The script should calculate every tunnel direction from actual aperture surface coordinates toward a sector-local virtual pupil. Current generated geometry caps maximum allowed tunnel tilt at 30°; the latest numerical check produced a worst case of about 28.3°.

Do not hard-code this as a physical truth. It changes with pupil distance, height, sector sweep, and aperture position. See [D-STEERING-01].

---

# 10. WHAT DUAL STEERING CAN AND CANNOT DO

Potential benefits over straight fins + radial apertures:

- higher fraction of useful LED light reaching the lens;
- more uniform brightness from top to bottom;
- reduced off-axis pupil clipping;
- reduced stray light;
- improved directional isolation between rows;
- lower electrical power for equivalent useful irradiance;
- easier subsequent geometric calibration.

It does **not** automatically make a square tile.

If the full V15 active field were treated as approximately 78 mm axial × 14.3 mm circumferential at 25°, then mapping the complete field to one square would require roughly:

\[
78/14.3\approx5.45
\]

times more compression in one axis than the other.

A square projected tile may therefore require selected row subsets / smaller tile bands, cylindrical or anamorphic relay optics, digital pre-warp, and measured scan-coordinate mapping. A practical path may be to use the tall drum as multiple square-capable axial bands rather than forcing the entire 78 mm height into one instantaneous square image. See [D-SQUARE-01].

---

# 11. 25 MM FINAL LENS — CORRECT INTERPRETATION

Do not confuse **lens clear aperture** with **maximum object size**. A 25 mm lens can image an object larger than 25 mm.

The governing issues are:

- field angle;
- focal length;
- working distance;
- entrance pupil;
- image circle;
- aberrations;
- numerical aperture;
- vignetting;
- desired reduction ratio.

The 66 mm drum diameter remains attractive because the 36° chord is about 20.4 mm, and the 25° broad optical chord is only about 14.3 mm. But field quality cannot be inferred from diameter alone. The actual 25 mm UV asphere must be characterized or modeled using focal length, NA, clear aperture, material, wavelength range, and field performance. See [D-LENS-01].

---

# 12. 1.6 MM APERTURE VS 1–10 µm TARGET

This is a major unresolved optical risk.

If a 1.6 mm aperture were directly imaged to 10 µm, the required linear reduction would be:

\[
1600\mu m/10\mu m=160:1
\]

For 1 µm it would be 1600:1.

Do not claim that a single 25 mm singlet/asphere automatically provides this over a useful field.

Treat 1.6 mm as the **mechanically printable prototype aperture**, not proof of final feature size. Possible future routes include a smaller secondary optical stop, projection objective, relay reduction stage, smaller printed/etched aperture, multi-stage imaging, or a different optical architecture.

The decisive measurement is the substrate-plane PSF / developed feature, not drum-hole diameter alone. See [D-RESOLUTION-01].

---

# 13. OPTICAL REGISTRATION VS ROTATIONAL ENCODER

These are different subsystems.

## 13.1 Encoder role

The V13/V15 encoder measures:

\[
\theta_{drum}
\]

during operation.

## 13.2 Inner/outer optical registration role

The stationary inner Fresnel/LED cylinder must also be aligned with:

- the rotating drum sector geometry;
- the final lens optical axis.

Define:

\[
\Delta\theta=\theta_{drum-reference}-\theta_{inner-reference}
\]

and axial offset:

\[
\Delta z
\]

Assembly should seek:

\[
\Delta\theta\approx0,\qquad\Delta z\approx0
\]

The user explicitly distinguished the rotational encoder from this relative optical-alignment problem. See [D-REGISTRATION-01].

---

# 14. ALIGNMENT COLLAR AND THROUGH-SIGHT HOLES

## 14.1 Keep aligners away from scan holes

Optical alignment holes must not intersect the active Nipkow scan line.

Therefore V15 adds:

```python
ALIGNMENT_BAND_HEIGHT_MM = 6.0
```

above the 78 mm active region.

Physical shell:

```text
Z = 0 .. 78 mm     scan region
Z = 78 .. 84 mm    alignment collar
```

Sight-hole levels:

```python
SIGHT_Z_LEVELS_MM = (
    79.5,
    82.5,
)
```

The Nipkow steering center remains at Z=39 mm. See [D-ALIGN-BAND-01].

## 14.2 Through-sight registration

Current sight hole:

```text
diameter = 2.0 mm
relative angular line = +16.5° from sector center
```

This lies in the structural margin between:

```text
25° optical edge = +12.5°
36° sector edge  = +18°
```

The rotating outer drum repeats the alignment pair every 36° so material removal remains balanced. The inner stationary cylinder contains corresponding alignment holes.

Two heights are used so visual coincidence verifies more than a single-point angular alignment.

These holes may also be used with a visible LED, IR LED, or photodiode for electronic relative alignment. See [D-SIGHT-01].

---

# 15. SHALLOW ALIGNMENT MARKINGS

The drum and inner carrier require visible angular markings for assembly and calibration.

The marking system should show:

```text
36° mechanical sector
25° broad optical/LED arc
6° precision exposure gate
0° optical center
```

Recommended references within one sector:

```text
-18°   sector boundary
-12.5° broad optical edge
-3°    precision edge
0°     center
+3°    precision edge
+12.5° broad optical edge
+18°   sector boundary
```

## 15.1 Depth

Current design permits:

```python
MARKING_DEPTH_MM = 0.60
```

on a 2 mm wall/base/flange.

This leaves:

\[
2.0-0.6=1.4\text{ mm}
\]

of local material. Markings must remain **blind recesses**, not accidental through-slots.

## 15.2 Balance rule

On the rotating drum, never carve a unique large `HOME`, sector number, arrow, or asymmetric notch.

If material is removed, repeat it identically every 36°.

Unique labels may be printed with ink, painted, placed on the stationary carrier, optically encoded with negligible mass, or deliberately counterbalanced. See [D-MARK-01].

---

# 16. STRUCTURAL LIGHTENING

Removing material can reduce rotor mass, filament, print time, and rotational inertia.

Any deliberate rotating-part lightening pocket must obey 10-fold symmetry.

Prefer broad shallow recesses over narrow sharp stress risers.

Avoid aggressive removal:

- around Nipkow apertures;
- at the base-to-wall junction;
- around the D-bore/hub;
- around encoder slot edges;
- at the open rim;
- near thin ligament intersections.

See [D-MARK-DEPTH-01].

---

# 17. RPM, SCAN RATE, AND NEMA 17

With ten repeated sectors:

\[
f_{scan}=\frac{RPM}{60}\times10
\]

Examples:

```text
60 RPM   -> 10 scan events/s
120 RPM  -> 20 scan events/s
180 RPM  -> 30 scan events/s
300 RPM  -> 50 scan events/s
```

For visible persistence/debugging, roughly 20–30 scan events/s can be useful.

For lithography, photoresist integrates dose over repeated scans; naked-eye POV is not required.

Encoder feedback should determine exposure phase. Do not assume microstep commands equal true drum angle. See [D-RPM-01].

---

# 18. SPIN-COATER RPM AND RESIST THICKNESS

A CD-ROM-drive spin coater can provide a practical empirical resist process.

But:

> **spin RPM is not UV exposure dose.**

Use spin-coater RPM and time to establish a repeatable film thickness:

\[
t_{resist}\propto RPM^{-n}
\]

with empirical exponent \(n\) determined by the actual resist/process.

Example test recipes:

```text
2000 RPM / 30 s
3000 RPM / 30 s
4000 RPM / 30 s
```

Characterize the film rather than guessing thickness. Then calibrate exposure independently. See [D-SPIN-01].

---

# 19. EMPIRICAL EXPOSURE CALIBRATION

With ten sectors:

\[
f_{pass}=\frac{10\,RPM}{60}=\frac{RPM}{6}
\]

For a 6° precision gate, drum angular speed is:

\[
\omega=6\,RPM\quad\text{degrees/s}
\]

so one 6° crossing lasts:

\[
t_{pass}=\frac{6}{6\,RPM}=\frac{1}{RPM}\text{ s}
\]

At 60 RPM:

\[
t_{pass}\approx16.7\text{ ms}
\]

A practical first calibration is therefore:

```text
fixed resist recipe
fixed LED current
fixed optics
fixed RPM
vary number of passes
develop identically
inspect result
```

Example ladder:

```text
10
20
40
80
160 passes
```

This produces an empirical process window without initially requiring an absolute mJ/cm² meter.

Later calibrate absolute dose with a UV photodiode/radiometer. See [D-DOSE-01].

---

# 20. UV EXPOSURE + 180° RED VISIBLE INSPECTION CHANNEL

A useful future configuration is:

```text
one UV exposure sector
+
one visible red diagnostic sector
180° opposite
```

Because:

\[
180^\circ=5\times36^\circ
\]

this maps exactly onto the ten-sector architecture.

Conceptually:

```text
               visible camera / lens
                        ↑
                 red LED sector
                      180°
                        │
                 rotating drum
                        │
                  UV LED sector
                        ↓
                  UV projection lens
                        ↓
                       wafer
```

## 20.1 Timing offset

The red channel is half a revolution away.

\[
\Delta t=\frac{30}{RPM}\text{ s}
\]

Examples:

```text
60 RPM  -> 0.500 s
120 RPM -> 0.250 s
180 RPM -> 0.167 s
```

## 20.2 What the red channel can measure

The red image can be a real-time proxy for:

- scan stability;
- spatial distortion;
- synchronization;
- row dropout;
- relative brightness uniformity;
- pattern geometry.

It cannot be assumed to be an absolute UV dosimeter.

After calibration:

\[
E_{UV}\approx K\,S_R
\]

and a relative dose map may be estimated from integrated red signal.

Absolute UV dose should still be anchored periodically to a UV photodiode, calibrated radiometer, or calibrated UV sensor. See [D-RED-UV-01].

---

# 21. SQUARE-TILE PROJECTION STRATEGY

Do not claim:

```text
angled LED fins + angled holes = square projection
```

That is not generally true.

The square-tile strategy combines:

1. controlled illumination direction;
2. directional aperture filtering;
3. narrow high-quality exposure gate;
4. optical magnification/reduction;
5. optional cylindrical/anamorphic correction;
6. software pre-warp;
7. measured scan mapping.

The calibration function is conceptually:

\[
(\theta,row)\rightarrow(x,y)_{substrate}
\]

Measure it, then invert it:

\[
(x,y)_{desired}\rightarrow(\theta,row,LED\ timing)
\]

Do not assume constant angular velocity automatically gives a perfectly Cartesian raster. See [D-SQUARE-01], [D-PREWARP-01].

---

# 22. KEY SKEPTICISMS / FAILURE MODES

V15 must explicitly test these rather than argue them away.

## 22.1 Étendue

A large divergent LED source cannot have all of its flux magically compressed into a small pupil.

The defensible design claim is:

> V15 intentionally rejects unwanted angular rays and attempts to increase the fraction of *useful* rays.

Expected consequence:

\[
P_{transmitted}<P_{LED}
\]

This is acceptable if delivered PSF and exposure uniformity improve.

## 22.2 LED is not a point source

A 1616 LED package has a finite emitting die and broad emission pattern.

The printed terrace defines package orientation but not perfect collimation.

Test the actual LED package.

## 22.3 Angled holes do not bend rays

The tunnel is a directional baffle/filter, not a refractive element.

Use accurate terminology.

## 22.4 3D-print accuracy

Printed plastic is not the precision optical element.

Use printing for degree-scale orientation, mechanical registration, baffles, and mounting. Use optical calibration for fine correction.

## 22.5 Lens aberrations

The final 25 mm asphere may have good on-axis performance but poor wide-field performance.

Potential issues include coma, astigmatism, field curvature, chromatic focal shift, and vignetting. This is why the 6° precision gate exists.

## 22.6 Mechanical runout

Even mathematically balanced CAD can wobble because of print density, shaft fit, hub eccentricity, layer variation, wiring, encoder features, and bearing alignment.

Tenfold symmetry minimizes designed-in imbalance; it does not guarantee a dynamically balanced assembled rotor.

## 22.7 LED heating

UV output changes with junction temperature. The stationary inner carrier needs thermal planning. Do not assume printed polymer is an adequate heatsink.

## 22.8 Photoresist nonlinearity

LED current and developed feature size are not necessarily linear. Measure dose-response.

## 22.9 UV material compatibility

Printed polymer may fluoresce, yellow, embrittle, or scatter UV. Test the actual print material.

## 22.10 Wiring

A 30-row, multi-sector LED carrier needs stationary cable routing, axial wiring channels, strain relief, and thermal/current budgeting. Do not route wires through the rotating interface.

See [D-SKEPTICISM-01].

---

# 23. MINIMUM EXPERIMENTAL VALIDATION PROGRAM

## 23.1 Mechanical

Measure:

- static balance;
- radial runout;
- axial runout;
- vibration vs RPM;
- missed steps / motor load;
- inner/outer clearance with real LEDs installed.

## 23.2 Alignment

Verify:

- two sight holes coincide;
- 36°/25°/6° markings register;
- encoder phase is stable;
- optical maximum transmission defines software phase offset.

## 23.3 Optical steering coupon

Build a small coupon with approximately:

```text
0°
5°
10°
15°
20°
25°
```

tunnel/LED aiming cases.

Measure:

- transmitted power;
- spot position;
- spot size;
- pupil coupling.

## 23.4 Field test

Project a calibration grid and measure distortion, focus vs position, brightness uniformity, and PSF across the precision gate.

## 23.5 Exposure ladder

With a fixed spin-coat recipe, expose:

```text
10 / 20 / 40 / 80 / 160 passes
```

Develop identically and record resolved line width, under/overexposure, edge quality, and resist clearing.

## 23.6 Visible red twin

Compare red diagnostic image against UV exposure outcomes. Derive an empirical red-to-UV spatial correction map while retaining an actual UV sensor for absolute calibration.

---

# 24. BLENDER IMPLEMENTATION RULES

## 24.1 Separate printable objects

Always preserve:

```text
OUTER_DRUM_PRINTABLE
INNER_LED_CARRIER_PRINTABLE
```

Do not accidentally join the two cylinders.

## 24.2 Avoid fragile structural unions

Previous structural Boolean UNION operations caused body collapse/disappearance.

Prefer overlapping/touching closed printable submeshes and object-level joins where the slicer can merge them. Use Boolean DIFFERENCE primarily for intentional cuts. If a true manifold union becomes necessary, validate after each operation.

## 24.3 Cutters

Delete cutters only after successful Boolean application.

After build:

```python
leftover_cutters = [
    obj.name
    for obj in bpy.data.objects
    if obj.name.startswith("CUT_")
]
assert not leftover_cutters
```

## 24.4 Blender API compatibility

Do not rely on:

```python
action.fcurves
obj.animation_data.action.fcurves
```

Do not animate:

```python
active_material_index
```

Do not assume `BLENDER_EEVEE_NEXT` exists.

For geometry generation, Cycles/GPU acceleration generally does not speed Blender Boolean construction significantly because Booleans are CPU-side.

## 24.5 Final validation

Generated scripts must run:

```python
compile(code, filename, "exec")
```

before delivery.

Include runtime assertions for:

- 10×36° closure;
- exact row count;
- exact 0.5 mm end margins;
- 1.7 + 0.9 = 2.6 mm;
- positive clearances;
- maximum tunnel tilt;
- separate final objects;
- no leftover cutters;
- encoder slot count;
- alignment band outside active scan region.

---

# 25. USER INTERACTION / DELIVERY PREFERENCES

For this project:

- prefer complete monolithic Blender Python when a full revision is requested;
- preserve earlier working methods rather than rewriting geometry unnecessarily;
- when asked for a **drop-in code change**, give only the replacement snippet;
- when asked for a **patch**, generate a `.patch` file and the exact `patch` command;
- do not re-explain the entire architecture when the user asks only for code changes;
- use explicit dimensions and equations;
- distinguish provisional optical assumptions from locked mechanical dimensions;
- keep integral imaging / glasses-free 3D separate unless directly relevant.

---

# 26. CANONICAL V15 FILE LINEAGE

```text
V3
  reliable distinct rectangular encoder slots;
  primitive Boolean behavior became the reliability reference.

V13
  progressive individual encoder slots;
  10 sectors x 8 slots;
  80 total slots.

V14
  separate outer drum and inner LED carrier;
  exposed row/fin pitch mismatch;
  Boolean regression on Nipkow apertures.

V14 fixed
  restored V3-style collection Boolean for apertures.

V15
  78 mm / 30-row active region;
  dual steering;
  25° illumination arc;
  6° precision gate;
  optical registration;
  shallow symmetric markings;
  sight holes.

V15 alignment-band patch
  moved aligner holes entirely above scan region.

V15 full-ring patch
  made Fresnel horizontal ridges full 360°.

V15 sector-boundary patch
  moved vertical ridges to 36° sector boundaries,
  enabling more of every 36° sector to carry LED strips.
```

Current reference implementation:

```text
nipkow_drum_v15_sector_boundary_vertical_ridges.py
```

---

# 27. DO NOT REGRESS TO THESE SUPERSEDED ASSUMPTIONS

Unless explicitly requested, do not revert to:

- 45 mm outer diameter;
- 100 mm active height as fixed baseline;
- 25 mm solid inner core;
- one continuous helical slit;
- straight axial LED line as current manufacturing architecture;
- LED arc only on one single lower sector;
- fin centers aligned directly to Nipkow rows;
- 1.0 mm + 1.7 mm = 2.7 mm pitch;
- base thickness counted inside active height;
- sight holes inside active scan region;
- vertical ribs at ±12.5°;
- unique mass-removing HOME notch on rotor;
- full 25° arc assumed to be micron-sharp simultaneously;
- red visible channel treated as an absolute UV dosimeter;
- stepper commanded position treated as true exposure angle.

---

# 28. DISCUSSION CITATION CONVENTION

The citations below are **project-conversation provenance**, not external literature citations.

They preserve why a design choice exists.

Format:

```text
[D-ID]
Date / phase
User decision or question
Engineering consequence incorporated into V15
```

Future revisions should keep these IDs when a rule remains active and add a new ID when a rule is superseded.

# 29. VERBOSE DISCUSSION CITATIONS / DESIGN PROVENANCE

## [D-LEGACY-01] — 2026-09-26 — Earlier simulation architecture

Earlier skill versions locked a 25 mm stationary core, 45 mm outer drum, 100 mm length, straight axial LED line, and continuous helical slit.

V15 supersedes that as the manufacturing/lithography baseline.

Reason for retaining this citation:

- prevents confusion between the older educational slow-motion simulation and the current nested printable drum;
- explains why old project files may contradict V15.

Implementation consequence:

> Treat legacy continuous-helix files as historical visualization references only.

## [D-BASE-01] — 2026-10-12 — Base thickness is separate

User clarification:

> “the base thickness should be seperate from the equation it should be 2mm so the 66mm height should be on top of the 2 mm base”

Engineering consequence:

- active cylinder height is independent of the 2 mm base;
- V15 keeps 78 mm active height above a separate 2 mm base.

## [D-HEIGHT-01] — 2026-10-12 to 2026-10-17 — End margins and row count

User required:

> “the 66mm cylinder wall has 0.5 mm on both sides left beside the end holes”

The 1.6 mm aperture + 2.6 mm pitch logic was subsequently refactored.

For 30 rows, exact closure is:

\[
0.5+1.6+29(2.6)+0.5=78.0\text{ mm}
\]

Engineering consequence:

- V15 active height = 78 mm;
- 30 rows;
- exact 0.5 mm edge margins.

## [D-BALANCE-01] — 2026-10-12 — Why 36°

User rationale:

> “the choice of 36 degree was to have a symetry as the drum has to fight gravity and punched hole should not make the weight lop sided”

Engineering consequence:

- ten exact 36° repeated sectors;
- rotating material removal must repeat identically;
- no unique carved mass-heavy HOME feature.

## [D-CHANNEL-01] — 2026-10-14 / V14-to-V15 correction — LED grooves

User requested an inner cylinder with O-ring-like ridges:

> “these ridges need to be 1 mm in width and 2mm in height and 1.7 mm apart to hold the leds strip”

A 1.0 + 1.7 mm layout gives 2.7 mm and drifts from the 2.6 mm optical row pitch.

Engineering consequence:

- separator width corrected to 0.9 mm;
- channel width remains 1.7 mm;
- total pitch = 2.6 mm;
- in V15 the **channels**, not fin centers, are aligned to optical rows.

## [D-FRESNEL-01] — 2026-10-17 — Fresnel-like source shaping

User proposed:

> “what if insted of straight fins we angle the top towards downward and the bottom fins towards the upwards looking like a fresnell structure”

Engineering consequence:

- top separators bias downward;
- bottom separators bias upward;
- terminology is “Fresnel-like” rather than claiming a true refractive Fresnel lens.

## [D-STEERING-01] — 2026-10-17 — Angle Nipkow holes too

User asked:

> “so we can angle the drum holes aswell? to make the projection more compact”

Engineering consequence:

- aperture surface lattice stays fixed;
- tunnel axis may aim toward a common pupil;
- tunnel is treated as directional filtering, not refraction.

## [D-SQUARE-01] — 2026-10-17 — Square tile objective

User asked whether the configuration can:

> “achive square tile projection”

Engineering consequence:

- square projection remains a system-level target;
- dual steering alone is not claimed to make the tile square;
- preserve room for cylindrical/anamorphic optics and digital pre-warp;
- consider smaller axial tile bands.

## [D-SKEPTICISM-01] — 2026-10-17 — Project loopholes

User explicitly requested:

> “what are the other loop holes in in the entire convearstion afor nipkow drum based lithography projectior and how can we address for for v15”

Engineering consequence:

V15 must explicitly validate:

- 1.6 mm aperture vs micron feature target;
- 25 mm lens field/aberrations;
- curved-drum defocus;
- finite LED source size;
- étendue;
- print accuracy;
- runout;
- encoder bandwidth;
- dose;
- thermal behavior;
- UV material behavior;
- calibration complexity.

## [D-LENS-01] — 2026-10-12 / 2026-10-17 — Round 25 mm lens vs rectangular field

User corrections:

> “the window is rectangular and the lense is round”

and:

> “one axis is already 66mm in length which is greater than 25mm”

Engineering consequence:

- lens aperture is not equated with object height;
- field angle, focal length, image circle, NA, aberrations, and magnification are separated;
- 66 mm OD remains attractive because 36° chord ≈20.4 mm.

## [D-GATE-01] — 2026-10-17 — Broad illumination vs precision field

Project reasoning identified that a broad 25° curved window creates substantial surface sag.

Engineering consequence:

- retain 25° as broad illumination/configuration window;
- use an independently adjustable narrow precision gate;
- current V15 default = 6°.

## [D-RESOLUTION-01] — 2026-10-17 — Micron target not proven by aperture

The project target remains approximately 1–10 µm.

Engineering consequence:

- 1.6 mm printed aperture is a prototype mechanical feature;
- micron feature size must be experimentally demonstrated;
- relay/objective or smaller optical stop may be required.

## [D-ENCODER-01] — 2026-10-12 — Analog encoder path

User wanted analog optical sensing and progressive slot geometry.

Engineering consequence:

- preserve V13 progressive encoder;
- LDR acceptable only for slow proof;
- reserve photodiode/phototransistor upgrade path;
- encoder measures rotor angle, not inner/outer registration.

## [D-REGISTRATION-01] — 2026-10-17 — Encoder is not cylinder alignment

User correction:

> “the optical encoder was for the position of the nipkow drum rotational position we need optical alignment of both inner fresnell cylinder and drum”

Engineering consequence:

- separate rotor encoder from relative optical registration;
- include matching marks and sight-hole alignment between cylinders.

## [D-SIGHT-01] — 2026-10-17 — Visible physical registration holes

User requested:

> “add a visible hole through both cylinders to aling aswell”

Engineering consequence:

- physical through-sight registration added;
- multiple Z levels used;
- outer holes repeated symmetrically.

## [D-ALIGN-BAND-01] — 2026-10-17 — Move aligners away from scan

User asked:

> “the optical aligners shold be away frm the nipkow scan line right”

Engineering consequence:

- 6 mm non-scanning alignment collar above active region;
- sight holes moved to approximately 79.5 and 82.5 mm;
- active steering center remains based on the 78 mm region.

## [D-MARK-01] — 2026-10-17 — Angular markings

User requested markings:

> “to align the 2 cylinders with respect to each other and the ~25 degree arc and 36 degree arc markings for led strips and vairous other markings but make sure they are not lop sided as any removed material must be symitirical”

Engineering consequence:

- 36°, 25°, 6°, center references;
- rotating engraving repeated every 36°;
- no asymmetric carved labels.

## [D-MARK-DEPTH-01] — 2026-10-17 — 0.6 mm recesses

User specified:

> “removing material also reduces print times and weight so we can cut upto 0.6 mm deep”

Engineering consequence:

- shallow marking default raised to 0.6 mm;
- still blind, not through;
- use symmetry for any lightening.

## [D-BOOLEAN-01] — V3/V14 debugging — Aperture Boolean reliability

Observed project history:

- individual/simple V3 geometry reliably created visible slots;
- later complex/curved Boolean variants sometimes left cutters or failed to produce openings;
- V14 initially regressed.

Engineering consequence:

- restore V3-style cutter collection Boolean;
- delete cutters only after successful application;
- fail loudly on leftover cutters.

## [D-CLEARANCE-01] — V14/V15 inner carrier

Current nominal geometry gives 1 mm radial clearance between 60 mm fin-tip OD and 62 mm drum ID.

Engineering consequence:

- this is a CAD baseline only;
- final LED/PCB stack must be measured before printing final rotor.

## [D-WINDOW-01] — 2026-10-17 — Mechanically stable optical span

User asked for a mechanically stable window span within 10×36° balance.

Engineering consequence:

- 25° became the conservative broad optical starting point;
- 11° total structural separation remains inside each 36° repetition;
- after later vertical-ridge changes, the inner carrier can physically host LEDs over more of the 36° sector while calibration may still choose ~25° active.

## [D-VERTICAL-RIDGE-01] — 2026-10-17 — Move axial ribs to sector boundaries

User requested:

> “make the virtcal ridge away from the arc window and make these virtcal ridges around so that more 36 degree arc can have led strips”

Engineering consequence:

- vertical ribs moved to 18°, 54°, 90°, 126°, 162°, 198°, 234°, 270°, 306°, 342°;
- full 360° horizontal Fresnel-like rings retained;
- more of each 36° sector is available for LEDs.

## [D-SCALE-01] — 2026-10-17 — Increase dimensions selectively

User asked whether increasing the 66 mm scale could gain more from Fresnel-like steering while respecting the stepper.

Engineering consequence:

- increase axial height before diameter;
- V15 moves active height to 78 mm;
- retain 66 mm OD for inertia and 25 mm lens compatibility.

## [D-RPM-01] — Project scan-rate reasoning

Ten sectors give:

\[
f_{scan}=\frac{10\,RPM}{60}
\]

Engineering consequence:

- 60/120/180 RPM -> 10/20/30 scan events/s;
- encoder angle, not commanded microsteps, gates exposure.

## [D-SPIN-01] — 2026-10-18 — CD-ROM spin coater

User asked:

> “Instead of speculating on the dosage dilivered can base it of a rpm of a spin coater based on a wafer stuck to cdrom drive?”

Engineering consequence:

- spin RPM is used to establish repeatable resist thickness;
- it is not treated as UV dose;
- exposure is calibrated separately by passes/current/RPM.

## [D-DOSE-01] — 2026-10-18 — Exposure by passes

Engineering consequence:

- build an exposure ladder in scan passes;
- only later convert to absolute mJ/cm² with a calibrated UV sensor;
- account for resist nonlinearity and LED thermal drift.

## [D-RED-UV-01] — 2026-10-18 — Opposite visible inspection sector

User proposed:

> “in one 36 degree sector facing downward we can have a uv led and another 36 degree sector which 180 degree apart can we have a visible red led strip so that the images formed by the visible the opposite side can give realtime visual inspection mechanism and can the dosage dilived be related?”

Engineering consequence:

- UV and red sectors may be paired exactly five 36° sectors apart;
- red path is a real-time spatial/timing diagnostic;
- red-to-UV dose relationship requires calibration;
- absolute UV dose remains anchored by a UV photodiode/radiometer.

## [D-PREWARP-01] — Project optical calibration strategy

The mechanically curved scan is not assumed to map perfectly to Cartesian substrate coordinates.

Engineering consequence:

- measure \((\theta,row)\rightarrow(x,y)\);
- invert the mapping for digital pre-warp;
- do not depend solely on perfect printed geometry.

## [D-OPTICS-01] — V15 optical assumptions are parameters, not facts

The project repeatedly explored 25 mm aspheres, cylindrical lenses, angled LED terraces, angled aperture tunnels, and pupil steering.

Engineering consequence:

- preserve focal length, pupil distance, illumination arc, precision gate, and tunnel-angle cap as tunable parameters;
- never present them as verified until measured with the actual lens and LED hardware.

---

# 30. FINAL V15 CHECKLIST

Before generating or modifying V15 CAD, verify:

- [ ] Outer OD = 66 mm unless explicitly changed.
- [ ] Outer wall = 2 mm.
- [ ] Active scan height = 78 mm.
- [ ] Alignment collar = 6 mm above scan region.
- [ ] Base thickness = separate 2 mm.
- [ ] 10 exact 36° sectors.
- [ ] 30 rows per sector.
- [ ] 2.6 mm row pitch.
- [ ] 1.6 mm apertures.
- [ ] Exact 0.5 mm end-hole margins.
- [ ] 300 Nipkow apertures total.
- [ ] V3-style collection Boolean for aperture cutting.
- [ ] V13 80-slot progressive encoder retained unless explicitly changed.
- [ ] Encoder and inner/outer optical registration treated separately.
- [ ] Inner OD = 56 mm.
- [ ] Full 360° horizontal Fresnel-like separator rings.
- [ ] 30 LED channels centered on row coordinates.
- [ ] LED channel = 1.7 mm.
- [ ] Separator = 0.9 mm.
- [ ] 10 vertical ridges on 36° sector boundaries.
- [ ] 25° broad optical window retained as a tunable starting point.
- [ ] 6° precision gate retained as independent parameter.
- [ ] Sight holes live in alignment collar, not scan region.
- [ ] Rotating sight holes/markings repeat symmetrically.
- [ ] Marking depth <= 0.6 mm unless structural analysis justifies more.
- [ ] Outer and inner cylinders remain separate printable objects.
- [ ] Actual LED package/PCB clearance checked.
- [ ] 25 mm lens limitations stated honestly.
- [ ] 1–10 µm resolution not claimed without measurement.
- [ ] UV dose calibrated empirically and eventually absolutely.
- [ ] Red visible channel, if used, is treated as calibrated proxy only.
- [ ] No leftover Boolean cutters.
- [ ] Python source compiles before delivery.
- [ ] If user asks for a patch, provide `.patch` + exact command.
- [ ] If user asks for “changes only,” do not add explanatory prose.

---

# 31. FINAL DESIGN PRINCIPLE

V15 should not be presented as a device whose optical performance is already proven.

It is an **instrumented, mechanically symmetric, calibration-friendly lithography scanner architecture** designed so uncertain quantities can be measured independently.

The design philosophy is:

\[
\boxed{
\text{mechanical symmetry}
+
\text{controlled illumination}
+
\text{directional apertures}
+
\text{encoder truth}
+
\text{relative optical registration}
+
\text{empirical dose calibration}
+
\text{software pre-warp}
}
\]

The project succeeds by making each speculative optical claim falsifiable with a small experiment rather than embedding unverified assumptions into the mechanical design.
