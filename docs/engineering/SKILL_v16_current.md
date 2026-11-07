---
name: nipkow-drum-lithography-v16-optimized
description: "Canonical engineering skill for the V16 optimized concentric Nipkow-drum lithography projector: 76 mm supported rotor, 45 scan lines over 99.4 mm, 32° optical window inside 10x36° symmetry, two rolling-contact lands, stationary cylindrical-Fresnel lens bays, separate vertical/top and horizontal/radial alignment holes, shallow demarcation dent, V13 encoder, empirical UV-dose calibration, and Blender generation/debug rules."
---

# Nipkow Drum Lithography Projector — Canonical V16 Optimized Engineering Skill

This file is the canonical project state for the **Nipkow DRUM lithography setup**.

It supersedes earlier project skills that assumed a 45 mm outer drum, 100 mm length, one continuous helical slit, one straight axial LED line, a 25 mm solid inner core, and a single lower 36° reflector/window. Those concepts remain useful as historical visualization experiments, but **must not be silently reintroduced into the V16 manufacturing design**. See [D-LEGACY-01].

The V16 optimized design is a supported nested concentric-cylinder scanner:

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

## 1.1 Locked V16 optimized mechanical baseline

Do not change these defaults unless the user explicitly requests a redesign:

```text
Main rotating drum OD                 76.0 mm
Main rotating drum ID                 72.0 mm
Outer drum wall                       2.0 mm
Active scan height                    99.4 mm
Alignment collar above scan           6.0 mm
Outer cylindrical shell height        105.4 mm
Separate closed base                  2.0 mm
Base OD                               76.0 mm

Rolling-contact lands                 2
Rolling-land OD                       80.0 mm
Rolling-land axial width              4.0 mm
Rolling-land local aligner holes      none
Rolling-land alignment policy         final shared coaxial cut only

Nipkow sectors                        10
Sector repeat                         36.0°
Rows per sector                       45
Row pitch                             2.2 mm
Aperture diameter                     1.6 mm
Clear axial web between holes         0.6 mm
Bottom aperture-edge margin           0.5 mm
Top aperture-edge margin              0.5 mm
Total Nipkow apertures                450

Inner LED/Fresnel carrier OD          56.0 mm
Inner carrier wall                    2.0 mm
Fresnel separator radial height       2.0 mm
Fin-tip OD                            60.0 mm
LED channel width                     1.7 mm
Horizontal separator width            0.5 mm
Vertical sector-boundary ridge width  0.5 mm

Stationary lens-guide count           10
Lens-guide outer radius               35.0 mm
Rotating drum inner radius            36.0 mm
Guide-to-drum nominal radial gap      1.0 mm
Cylindrical Fresnel stock length      100 mm
Cylindrical Fresnel width             20 mm
Cylindrical Fresnel thickness         2 mm

Top stationary alignment disk OD      80.0 mm
Top stationary alignment disk radius  40.0 mm

Vertical/top alignment holes          10
Vertical/top hole diameter            1.5 mm
Vertical/top hole center radius       38.8 mm
Vertical/top angular positions        18° + 36°k
Vertical/top Boolean policy           one final post-join cut per assembly

Horizontal/radial sight rows          1
Horizontal hole diameter              2.0 mm
Horizontal sight-row Z                102.4 mm
Horizontal relative angle             +14.0°
Horizontal inner/outer hole count     10 + 10
Horizontal-to-vertical separation     4.0°

Demarcation feature                   shallow segmented external dent
Demarcation dent depth                0.35 mm
Demarcation axial width               0.60 mm
Demarcation segment span              30° per 36° sector
Remaining wall under dent             1.65 mm

Decorative optical-registration cuts  none
Legacy D-shaped/overlap hole systems  removed
```

The 99.4 mm active height is exact:

\[
99.4=0.5+1.6+44(2.2)+0.5
\]

Thus 45 rows fit with exactly 0.5 mm material beyond the first and last 1.6 mm apertures while retaining a 0.6 mm clear axial web between adjacent holes.

This is the **optimized 45-line version**. The practical aggressive ceiling with 1.6 mm holes remains approximately 49 lines at 2.0 mm pitch, but that leaves only 0.4 mm web and is not the default physical prototype. See [D-V16-ROWS-01].

The alignment system is intentionally split into two different physical directions:

1. **vertical/top-view coaxial holes** through the top alignment structures;
2. **horizontal/radial sight holes** through the cylindrical collar walls.

Do not merge these into one Boolean system and do not reintroduce the older overlapping D-shaped cuts.

## 1.2 Provisional optical defaults

```text
Broad illumination arc                32°
Precision exposure gate               6°
Virtual pupil distance                140 mm beyond outer surface
Maximum allowed generated tunnel tilt 30°
Calculated V16 worst tunnel tilt      about 29.16°
```

The pupil distance changed from V15's 120 mm because the taller 99.4 mm active field otherwise drives the extreme 3D tunnel tilt above 30°. See [D-V16-PUPIL-01].

The 20 × 2 mm cylindrical Fresnel lens remains a stationary optical/mechanical element. Its nominal focal length is not treated as proof that the compact 76 mm geometry is optically optimal.

Final choices remain driven by measured PSF, irradiance, field curvature, distortion, exposure threshold, mechanical runout, red-visible/UV correlation, and actual printed clearance.

---

# 2. COORDINATE SYSTEM

Current manufacturing scripts use:

```text
Z  = common cylinder / shaft axis
XY = circular cross-section
```

The physical drum may still be mounted horizontally.

For V16:

```text
active optical wall       Z = 0 .. 99.4 mm
alignment collar          Z = 99.4 .. 105.4 mm
closed rotating base      Z = -2 .. 0 mm
motor-side rolling land   below the base
far-side rolling land     above the collar
stationary top disk       above the far-side rolling land
```

Keep:

```python
ACTIVE_CENTER_Z = ACTIVE_WALL_HEIGHT_MM * 0.5
```

Do not shift the optical center to the center of the total mechanical assembly.

The rolling lands remain outside the active scan lattice. The stationary carrier may extend axially through the center of the far-side rolling land because the rolling land is annular.

---

# 3. OUTER ROTATING DRUM AND ROLLING SUPPORT

## 3.1 Main body

```python
OUTER_DRUM_OD_MM = 76.0
OUTER_WALL_THICKNESS_MM = 2.0
OUTER_DRUM_ID_MM = 72.0
ACTIVE_WALL_HEIGHT_MM = 99.4
ALIGNMENT_BAND_HEIGHT_MM = 6.0
TOTAL_CYLINDER_HEIGHT_MM = 105.4
OUTER_BASE_THICKNESS_MM = 2.0
OUTER_BASE_OD_MM = 76.0
```

The body OD was increased from 66 mm to 76 mm to package the 20 × 2 mm flat cylindrical Fresnel strip with a more realistic printed-assembly clearance than the ~73 mm theoretical minimum. See [D-V16-LENS-OD-01].

## 3.2 Two rolling-contact lands

Use exactly two narrow smooth 360° rolling lands:

```text
count             2
OD                80 mm
axial width       4 mm
location          outside optical scan field
outside surface   continuous and smooth
alignment holes   simple round holes inward of rolling surface
```

The rotor can sit on two bearing-mounted parallel rollers/rails like a rock tumbler.

These lands reduce motor-shaft cantilever deflection and make the longer 99.4 mm active rotor mechanically practical. They do not reduce rotational inertia. See [D-V16-ROLLER-01].

## 3.3 Motor interface

Retain the NEMA-17 prototype drive, 5 mm nominal D-shaft, 5.20 mm modeled D-bore, ~4.70 mm flat-to-round dimension, 18 mm hub OD, and 10 mm hub length.

Use a gentle acceleration ramp, physical balancing, and encoder-truth exposure timing.

## 3.4 Scaling consequence

For a thin cylindrical shell:

\[
I\propto Hr^3
\]

The V16 move from 66 mm / 78 mm to 76 mm / 99.4 mm roughly doubles the idealized shell contribution:

\[
\frac{99.4}{78}\left(\frac{38}{33}\right)^3\approx1.95
\]

The actual complete rotor ratio differs because of the perforated shell, base, hub, and rolling lands.

The support rollers address shaft bending, not polar inertia.

---

# 4. NIPKOW APERTURE LATTICE

## 4.1 Tenfold balance

Keep:

```python
SECTOR_COUNT = 10
SECTOR_REPEAT_DEG = 36.0
```

All repeated rotating subtractive geometry remains 10-fold symmetric.

The rolling lands are full 360° rings and therefore intrinsically balanced. Their simple alignment holes repeat every 36°.

## 4.2 V16 optimized rows

```python
ROW_COUNT = 45
ROW_PITCH_MM = 2.20
APERTURE_DIAMETER_MM = 1.60
END_MARGIN_MM = 0.50
```

Centers:

```python
FIRST_ROW_CENTER_Z = 1.30
z_i = 1.30 + i*2.20
# i = 0 .. 44
```

Last center:

\[
98.1\text{ mm}
\]

Last aperture edge:

\[
98.9\text{ mm}
\]

Top margin:

\[
99.4-98.9=0.5\text{ mm}
\]

Clear axial web:

\[
2.2-1.6=0.6\text{ mm}
\]

Total apertures:

\[
45\times10=\boxed{450}
\]

## 4.3 Practical line-count envelope

```text
38 lines @ 2.6 mm pitch   robust
41 lines @ 2.4 mm pitch
45 lines @ 2.2 mm pitch   V16 optimized
49 lines @ 2.0 mm pitch   aggressive practical ceiling
```

The rolling supports address long-axis mechanics but do not strengthen the thin ligaments between neighboring holes.

## 4.4 Slanted pattern and pupil

The 45 rows still sweep the full 36° sector.

Keep aperture position and tunnel direction separate.

Use a provisional 140 mm pupil distance in V16 so the calculated worst 3D tunnel tilt remains about 29.16°, under the 30° guard.

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

# 6. V13 ROTATIONAL ENCODER — RETAIN IN V16

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

# 7. INNER STATIONARY FRESNEL-LIKE LED CARRIER AND LENS BAYS

## 7.1 Carrier

```text
carrier OD             56 mm
carrier wall           2 mm
carrier ID             52 mm
horizontal fin-tip OD  60 mm
```

The 72 mm rotating-drum ID leaves useful annular volume for the stationary cylindrical Fresnel lens and guide rails.

## 7.2 Forty-five LED channels

Keep the LED channel at 1.7 mm.

With 2.2 mm pitch:

\[
2.2-1.7=\boxed{0.5\text{ mm}}
\]

Therefore V16 has:

```text
45 LED channels
44 internal full separator rings
2 retaining lips
```

The channels are centered on the same 45 row coordinates as the outer Nipkow apertures.

The horizontal Fresnel-like separator rings remain full 360° rings.

## 7.3 Vertical sector-boundary ridges

Retain ten shared 0.5 mm axial ridges at:

```text
18°, 54°, 90°, 126°, 162°,
198°, 234°, 270°, 306°, 342°
```

## 7.4 Ten stationary lens guides

Add ten simple radial guide rails at those same shared boundaries.

Current V16 starting dimensions:

```text
guide count             10
guide tangential width  0.6 mm
guide outer radius      35.0 mm
guide height            99.4 mm
```

Each guide is shared by two neighboring 36° lens bays.

Intended cylindrical Fresnel stock:

```text
100 mm long
20 mm wide
2 mm thick
```

Nominal guide-tip radial clearance to the 72 mm drum ID:

\[
36-35.0=\boxed{1.0\text{ mm}}
\]

The guides are stationary and add no motor inertia. See [D-V16-LENS-GUIDE-01].

---

# 8. 36° MECHANICAL SECTOR VS 32° OPTICAL WINDOW VS 6° PRECISION GATE

Keep these three angular concepts separate.

## 8.1 Mechanical sector

The rotor remains:

\[
10\times36^\circ=360^\circ
\]

The **36° sector is not widened**. It is the balance and scan-repeat architecture.

## 8.2 Broad 32° optical / illumination region

V16 optimized widens the broad optical window from the earlier 25° starting value to:

\[
\boxed{32^\circ}
\]

This leaves:

\[
\frac{36^\circ-32^\circ}{2}
=
\boxed{2^\circ}
\]

of angular structural/guide margin on each side of every mechanical sector.

At the 76 mm drum diameter, the 32° chord is approximately:

\[
76\sin(16^\circ)\approx20.95\text{ mm}
\]

This closely matches the nominal 20 mm flat cylindrical-Fresnel strip width and uses substantially more of each 36° sector than the old 25° window.

The 32° value is still a **broad illumination/configuration window**, not a claim that the entire curved field is simultaneously micron-sharp.

## 8.3 Precision exposure gate

Keep the initial precision gate independently tunable:

\[
\boxed{6^\circ}
\]

Use the narrow gate first for PSF, focus, dose, and distortion measurements. Widen the actual exposure duty only after measurements support it.

## 8.4 Lens-guide reach

The stationary lens guides now extend to:

\[
\boxed{35.0\text{ mm radius}}
\]

inside the rotating drum's:

\[
36.0\text{ mm inner radius}
\]

leaving:

\[
36.0-35.0=
\boxed{1.0\text{ mm}}
\]

nominal radial running clearance.

The guides must never intentionally touch the rotating drum.

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

If the full V15 active field were treated as approximately 78 mm axial × 14.3 mm circumferential at 32°, then mapping the complete field to one square would require roughly:

\[
78/14.3\approx5.45
\]

times more compression in one axis than the other.

A square projected tile may therefore require selected row subsets / smaller tile bands, cylindrical or anamorphic relay optics, digital pre-warp, and measured scan-coordinate mapping. A practical path may be to use the tall drum as multiple square-capable axial bands rather than forcing the entire 78 mm height into one instantaneous square image. See [D-SQUARE-01].

---

# 11. CYLINDRICAL FRESNEL + FINAL PROJECTION OPTICS

V16 introduces a stationary flat cylindrical Fresnel strip in the annular space.

Current mechanical lens target:

```text
stock length     100 mm
width            20 mm
thickness        2 mm
nominal focal    about 10 mm for the selected stock part
```

The 76 mm drum is a mechanical packaging compromise, not an optical proof.

Important:

- 76 mm solves the mechanical-clearance problem more robustly than the ~73 mm theoretical minimum;
- it does not prove that the compact source-to-lens spacing is optically optimal;
- actual coupling must be measured;
- the ten stationary lens guides let any/all 36° sectors accept lens strips;
- a UV sector and red inspection sector can be placed 180° apart.

The lens and its guides remain stationary while the Nipkow drum rotates around them.

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

# 14. V16 ALIGNMENT SYSTEM — KEEP VERTICAL AND HORIZONTAL HOLES SEPARATE

V16 deliberately removes the complicated optical-registration glyph system.

Use **simple round holes only**, but keep the two hole directions conceptually and geometrically separate.

## 14.1 Vertical / top-view coaxial holes

Use exactly ten top-view alignment holes:

```text
count                 10
diameter              1.5 mm
center radius         38.8 mm
angles                18° + 36°k
k                     0..9
```

The top stationary alignment disk is:

```text
OD                    80.0 mm
radius                40.0 mm
```

The 1.5 mm hole at 38.8 mm radius leaves:

\[
40-(38.8+0.75)=0.45\text{ mm}
\]

outer material margin.

The vertical/top holes are cut with the same XY coordinates through the relevant inner and outer top structures.

**Boolean rule:**

- do not cut the inner top disk early and then re-cut it later;
- do not cut separate holes into each rolling land;
- do not retain an older collar/D-shaped top hole;
- perform exactly **one authoritative final post-join vertical/top alignment cut on the inner assembly**;
- perform exactly **one authoritative final post-join vertical/top alignment cut on the joined outer rotor**.

This rule exists because multiple overlapping alignment Booleans produced D-shaped and doubled openings during V16 development.

## 14.2 Horizontal / radial sight-hole row

Keep one horizontal/radial sight-hole row through both cylindrical walls:

```text
hole diameter         2.0 mm
row Z                 102.4 mm
holes on inner        10
holes on outer        10
relative angle        +14.0° within each 36° sector
```

The same angular and axial coordinates must be used on inner and outer cylinders.

These horizontal holes are real through-holes because their purpose is direct radial sight alignment between the stationary Fresnel carrier and the rotating outer collar.

They are **not** the same feature as the vertical/top coaxial holes.

## 14.3 Separation between the two systems

The vertical/top holes sit on the 18° shared sector boundaries.

The horizontal row sits at +14°.

Therefore:

\[
18^\circ-14^\circ=\boxed{4^\circ}
\]

At approximately 38.8 mm radius, that is about:

\[
2R\sin(2^\circ)\approx2.71\text{ mm}
\]

between the projected hole axes.

This separation is intentional. The older +16.5° horizontal position was too close to the 18° top hole and contributed to the D-shaped overlap appearance.

Do not move the horizontal row back toward 18° unless the complete overlap geometry is revalidated.

See [D-V16-ALIGN-SPLIT-01] and [D-V16-D-HOLE-01].

---

# 15. REGISTRATION / DEMARCATION MARKING POLICY

Do not generate the earlier decorative 36° / 32° / 6° optical-registration glyphs.

Allowed V16 registration geometry:

1. ten simple vertical/top round coaxial holes;
2. one matched horizontal/radial round-hole row on inner and outer cylindrical walls;
3. the shallow segmented demarcation dent after the active Nipkow region;
4. simple 0.5 mm vertical sector-boundary ridges on the stationary carrier.

Do not generate:

- nested arc symbols;
- chevrons;
- radial tick forests;
- bullseye recesses;
- dotted fence-glyph traces;
- compound decorative registration structures;
- duplicate pre-join plus post-join alignment cuts;
- local rolling-land alignment-hole Booleans;
- legacy D-shaped collar holes.

## 15.1 Shallow demarcation dent

The boundary immediately after the horizontal sight-hole row must **not** be a through-wall slit.

Use:

```text
dent depth             0.35 mm
drum wall              2.00 mm
remaining wall         1.65 mm
axial groove width     0.60 mm
segment span           30° per 36° sector
```

The groove is cut only into the **external surface**.

Purpose:

- preserve the visual/assembly boundary;
- avoid an unnecessary circumferential stress breakpoint;
- keep the inner wall structurally continuous.

This feature is a dent/groove, not a sight path.

See [D-V16-SHALLOW-DENT-01].

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

# 17. RPM, SCAN RATE, NEMA-17, AND ROLLER SUPPORT

Ten sectors still give:

\[
f_{scan}=\frac{RPM}{60}\times10
\]

```text
60 RPM   -> 10 scan events/s
120 RPM  -> 20 scan events/s
180 RPM  -> 30 scan events/s
300 RPM  -> 50 scan events/s
```

The two rolling-contact lands and two bearing-mounted support rails/rollers are part of the V16 mechanical architecture.

They carry most radial load and reduce motor-shaft cantilever deflection. They do **not** reduce polar inertia.

Use:

- gentle acceleration ramps;
- measured encoder phase;
- static/dynamic balancing;
- smooth roller surfaces;
- identical rolling-land diameters.

Do not let the roller contact the perforated optical wall or the small scan-line separator features.

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

- one corresponding outer/inner sight hole coincides at the selected 36° sector;
- 36°/32°/6° markings register;
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
32°
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

## 24.5 V16 mechanical implementation additions

Generated V16 scripts must additionally verify:

- exactly two rolling-contact lands;
- no local alignment-hole Boolean is applied inside `create_rolling_land()`;
- 45 rows and 450 Nipkow cutters;
- 0.6 mm axial web between 1.6 mm apertures;
- 0.5 mm horizontal LED separator width;
- 99.4 mm active height fits within 100 mm lens stock;
- ten stationary lens guides;
- lens-guide tip radius = 35.0 mm;
- guide tip remains 1.0 mm inside the 72 mm drum ID;
- broad optical window = 32° within a fixed 36° mechanical sector;
- 2° angular margin on each side of the broad optical window;
- top stationary alignment disk OD = 80 mm;
- vertical/top alignment holes = 10 × 1.5 mm at 38.8 mm radius;
- vertical/top hole positions = 18° + 36°k;
- exactly one final post-join inner vertical/top alignment Boolean;
- exactly one final post-join outer vertical/top alignment Boolean;
- no earlier inner top-hole Boolean remains;
- no legacy D-shaped/collar outer top-hole Boolean remains;
- no per-rolling-land alignment-hole Boolean remains;
- horizontal sight row = 10 inner + 10 outer holes;
- horizontal hole diameter = 2.0 mm;
- horizontal sight-row Z = 102.4 mm;
- horizontal relative angle = +14.0°;
- horizontal-to-vertical angular separation = 4.0°;
- shallow demarcation dent depth = 0.35 mm;
- demarcation dent does not penetrate the 2 mm wall;
- remaining wall below dent = 1.65 mm;
- provisional 140 mm pupil keeps calculated tunnel tilt below 30°;
- Python source compiles before delivery.

## 24.6 Final validation

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

# 26. CANONICAL V15 → V16 FILE LINEAGE

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
  32° illumination arc;
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

V15 balanced single-alignment patch
  reduced registration to one sight-hole row;
  removed bullseye recesses;
  added one 360° demarcation groove after the Nipkow Boolean;
  reduced shared vertical boundary ridges to 0.5 mm;
  repeated all inner 36° markings across all ten sectors;
  added outward-flared fences from +/-12.5° to +/-18°.
```

V16 optimized — current canonical state
  76 mm main drum OD / 72 mm ID;
  99.4 mm active height;
  45 rows at 2.2 mm pitch;
  450 apertures;
  two 80 mm OD rolling-contact lands outside optical field;
  ten stationary lens guides to 35.0 mm radius;
  32° broad optical window inside fixed 36° mechanical sectors;
  6° precision exposure gate retained;
  80 mm stationary top alignment disk;
  ten 1.5 mm vertical/top coaxial holes at 38.8 mm radius;
  one final post-join vertical/top Boolean per inner/outer assembly;
  matched 2.0 mm horizontal/radial sight-hole row on both cylinders;
  horizontal sight angle moved to +14°;
  4° separation from 18° vertical/top sector-boundary holes;
  legacy D-shaped/collar cuts removed;
  local rolling-land alignment-hole Booleans removed;
  shallow 0.35 mm segmented demarcation dent replaces through-wall slit;
  decorative optical-registration glyphs removed;
  pupil distance = 140 mm to retain <30° calculated tunnel tilt.

Current reference implementation:

```text
nipkow_drum_v16_optimized_32deg_shallow_demarcation.py
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
- full 32° arc assumed to be micron-sharp simultaneously;
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

Project reasoning identified that a broad 32° curved window creates substantial surface sag.

Engineering consequence:

- retain 32° as broad illumination/configuration window;
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

Engineering consequence at that stage:

- physical through-sight registration added;
- multiple Z levels were initially used;
- outer holes repeated symmetrically.

Superseded for the current V15 by [D-SINGLE-ALIGN-FENCE-01], which reduces registration to one Z row.

## [D-ALIGN-BAND-01] — 2026-10-17 — Move aligners away from scan

User asked:

> “the optical aligners shold be away frm the nipkow scan line right”

Engineering consequence at that stage:

- 6 mm non-scanning alignment collar above active region;
- sight holes were initially moved to approximately 79.5 and 82.5 mm;
- active steering center remained based on the 78 mm region.

Current V15 keeps the same 6 mm collar but uses only one sight row at Z=81.0 mm. See [D-SINGLE-ALIGN-FENCE-01].

## [D-MARK-01] — 2026-10-17 — Angular markings

User requested markings:

> “to align the 2 cylinders with respect to each other and the ~32 degree arc and 36 degree arc markings for led strips and vairous other markings but make sure they are not lop sided as any removed material must be symitirical”

Engineering consequence:

- 36°, 32°, 6°, center references;
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

- 32° became the conservative broad optical starting point;
- 11° total structural separation remains inside each 36° repetition;
- after later vertical-ridge changes, the inner carrier can physically host LEDs over more of the 36° sector while calibration may still choose ~32° active.

## [D-VERTICAL-RIDGE-01] — 2026-10-17 — Move axial ribs to sector boundaries

User requested:

> “make the virtcal ridge away from the arc window and make these virtcal ridges around so that more 36 degree arc can have led strips”

Engineering consequence:

- vertical ribs moved to 18°, 54°, 90°, 126°, 162°, 198°, 234°, 270°, 306°, 342°;
- each boundary is represented by one shared physical ridge;
- ridge tangential width is now 0.5 mm;
- full 360° horizontal Fresnel-like rings retained;
- more of each 36° sector is available for LEDs.

## [D-SINGLE-ALIGN-FENCE-01] — 2026-10-18 — Single sight row, simple ring, full sector pattern, outward fences

User refinement:

> “only one row of alignment holes are needed ... no special recess needed just a simple demarcation ring booleened after the nipkow window ... make all the 36 degree arcs on the inner cylinder also patterned and make viritcle ridges of 0.5 mm ... the active window arc should be fenced outwards towards the boundaries of the 36 degree arc”

Engineering consequence:

- reduce alignment system from two Z rows to one circumferential row centered at Z=81 mm;
- use 10 matching holes on the outer drum and 10 on the stationary inner carrier;
- remove special bullseye/target recesses;
- add one shallow 360° outer demarcation groove after the Nipkow-window Boolean;
- repeat the complete 36°/32°/6° inner registration pattern in all ten sectors rather than only at 0° and 180°;
- use exactly 10 shared 0.5 mm vertical ridges at 36° boundaries;
- add two 0.5 mm outward-flared fences per sector, beginning at +/-12.5° on the carrier surface and reaching +/-18° at the outer fin radius;
- retain 66 mm OD, 78 mm active height, 6 mm collar, 30 rows, 2.6 mm pitch, and the 10×36° balance architecture.

Balance analysis:

- one 360° groove is rotationally symmetric;
- 10 sight holes repeat every 36°;
- 10 boundary ridges repeat every 36°;
- 20 fences are paired left/right and repeat every 36°;
- therefore no new first-order CAD imbalance is introduced by this revision.

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

## [D-V16-LENS-OD-01] — 2026-11-02 — 76 mm drum around 20 × 2 mm cylindrical Fresnel

User selected the practical 76 mm OD over the theoretical ~73 mm minimum because the latter leaves only about 0.5 mm nominal corner clearance.

Engineering consequence:

- V16 main drum OD = 76 mm;
- wall = 2 mm;
- ID = 72 mm;
- existing 60 mm fin-tip envelope retained;
- base OD matches the drum.

## [D-V16-LENS-GUIDE-01] — 2026-11-07 — Guides from all stationary sectors

User required guides extending from the inner drum in all sectors to hold the lens.

Engineering consequence:

- ten shared stationary guide rails;
- one at each 36° sector boundary;
- neighboring sectors share a guide;
- guide outer radius approximately 35.0 mm;
- guides remain stationary.

## [D-V16-ROLLER-01] — 2026-11-07 — Rock-tumbler support

User proposed external support fins so the drum can rest on two rails/rollers and reduce motor-shaft bowing.

Engineering consequence:

- use only two dedicated smooth rolling-contact lands;
- current V16 land OD = 80 mm;
- land width = 4 mm;
- lands stay outside the active optical field;
- alignment holes remain inward of the rolling OD.

## [D-V16-ROWS-01] — 2026-11-07 — Increase scan-line count

User agreed that roller support permits more axial scan lines.

Engineering consequence:

- V16 optimized = 45 rows at 2.2 mm pitch;
- active height = 99.4 mm;
- 0.6 mm axial web retained;
- 450 apertures total;
- 49 rows at 2.0 mm pitch remains an aggressive ceiling, not baseline.

## [D-V16-SIMPLE-ALIGN-01] — 2026-11-07 — Simple holes only

User clarified:

> “the fresnell drum has simple holes we just need to keep that across loose the opticsl registration pattern”

Engineering consequence:

- simple round holes are the common registration language;
- remove decorative 36/25/6 registration glyphs from active V16 CAD;
- retain the shallow segmented demarcation dent.

## [D-V16-PUPIL-01] — V16 numerical geometry validation

For the 76 mm OD / 45-row / 99.4 mm geometry:

```text
120 mm pupil distance -> about 31.48° worst tunnel tilt
140 mm pupil distance -> about 29.16° worst tunnel tilt
```

Engineering consequence:

- V16 provisional pupil distance = 140 mm;
- 30° safety guard retained.

---

## [D-V16-WINDOW-32-01] — 2026-11-07 — Widen optical window inside fixed 36° sector

User approved increasing the broad optical window after the 76 mm drum and stationary lens-guide optimization.

Engineering consequence:

- keep the mechanical sector fixed at 36°;
- increase broad optical/illumination window from 32° to 32°;
- retain the 6° precision exposure gate;
- retain 2° angular margin on each side of every sector;
- extend stationary lens-guide tips from 34.3 mm to 35.0 mm radius;
- preserve 1.0 mm nominal radial clearance to the 72 mm-ID rotating drum;
- do not let stationary guides touch the rotor.

---

# 30. FINAL V16 OPTIMIZED CHECKLIST

Before generating or modifying V16 CAD, verify:

- [ ] main rotating drum OD = 76 mm;
- [ ] main rotating drum ID = 72 mm;
- [ ] wall = 2 mm;
- [ ] active scan height = 99.4 mm;
- [ ] alignment collar = 6 mm;
- [ ] separate base = 2 mm;
- [ ] 10 exact 36° sectors;
- [ ] 45 rows per sector;
- [ ] 2.2 mm row pitch;
- [ ] 1.6 mm apertures;
- [ ] 0.6 mm clear axial web;
- [ ] exact 0.5 mm aperture-edge margins;
- [ ] 450 Nipkow apertures total;
- [ ] V3-style collection Boolean retained for Nipkow tunnels;
- [ ] V13 80-slot encoder retained;
- [ ] exactly two rolling-contact lands;
- [ ] rolling lands = 80 mm OD and 4 mm wide unless explicitly changed;
- [ ] rolling lands lie outside optical region;
- [ ] no local rolling-land alignment-hole Boolean;
- [ ] inner carrier OD = 56 mm;
- [ ] fin-tip OD = 60 mm;
- [ ] 45 LED channels;
- [ ] LED channel width = 1.7 mm;
- [ ] horizontal separator = 0.5 mm;
- [ ] full 360° horizontal Fresnel-like rings;
- [ ] exactly 10 shared 0.5 mm vertical sector ridges;
- [ ] exactly 10 stationary lens guides;
- [ ] lens-guide outer radius = 35.0 mm;
- [ ] lens guides remain inside 36 mm rotating inner radius;
- [ ] nominal lens-guide/drum radial gap = 1.0 mm;
- [ ] 100 mm lens stock covers 99.4 mm active region;
- [ ] broad optical/illumination window = 32°;
- [ ] mechanical sector remains 36°;
- [ ] 2° optical margin remains on each sector side;
- [ ] precision exposure gate remains 6° and independently tunable;
- [ ] top stationary alignment disk OD = 80 mm;
- [ ] vertical/top alignment holes = exactly 10;
- [ ] vertical/top hole diameter = 1.5 mm;
- [ ] vertical/top hole center radius = 38.8 mm;
- [ ] vertical/top hole angles = 18° + 36°k;
- [ ] exactly one final post-join vertical/top Boolean on inner assembly;
- [ ] exactly one final post-join vertical/top Boolean on outer rotor;
- [ ] no earlier duplicate top-hole Boolean;
- [ ] no legacy D-shaped/collar top-hole cut;
- [ ] horizontal/radial inner sight holes = 10;
- [ ] horizontal/radial outer sight holes = 10;
- [ ] horizontal hole diameter = 2.0 mm;
- [ ] horizontal sight-row Z = 102.4 mm;
- [ ] horizontal relative angle = +14.0°;
- [ ] horizontal-to-vertical angular separation = 4.0°;
- [ ] horizontal and vertical hole systems are kept separate;
- [ ] demarcation feature is a shallow external dent, not a slit;
- [ ] demarcation dent depth = 0.35 mm;
- [ ] remaining wall below demarcation dent = 1.65 mm;
- [ ] demarcation axial width = 0.60 mm;
- [ ] demarcation segment span = 30° per 36° sector;
- [ ] no decorative optical-registration glyphs;
- [ ] provisional pupil distance = 140 mm;
- [ ] calculated tunnel tilt remains <30°;
- [ ] actual LED/PCB/lens clearance physically checked;
- [ ] motor acceleration is gentle;
- [ ] assembled rotor is physically balanced;
- [ ] UV dose calibrated empirically and eventually absolutely;
- [ ] red visible channel remains a calibrated proxy only;
- [ ] no leftover Boolean cutters;
- [ ] outer and inner parts remain separate printable objects;
- [ ] Python source compiles before delivery;
- [ ] Blender visual inspection confirms round, non-overlapping alignment holes.

---

# 31. FINAL DESIGN PRINCIPLE

V16 should not be presented as a device whose optical performance is already proven.

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
