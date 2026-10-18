---
name: nipkow-helical-drum-blender-simulation
description: "One-input skill for generating and self-validating a complete Blender simulation of a horizontal helical-slit Nipkow drum. Input only the 3D printer's reliable XY feature size in mm; derive safe geometry, build the full monolithic script, validate it, and return Run Script -> Play output."
---

# Nipkow Helical Drum Blender Simulation — One-Input Version

This skill must be usable by a weak or literal model with minimal reasoning.

The user should be able to provide only:

`printer_precision_mm = <number>`

Example:

`printer_precision_mm = 0.20`

Interpret this as:

> the printer's smallest reliable XY feature size in millimeters.

Do not ask for nozzle size, layer height, material, or slicer settings unless the user explicitly wants a manufacturing-grade design. For the Blender simulation, this single number is enough.

The skill must then:

1. derive conservative printable geometry;
2. preserve the agreed projector architecture;
3. generate one complete monolithic Blender Python script;
4. self-validate the generated script before returning it;
5. include runtime assertions inside the Blender script;
6. make the finished scene playable with only **Run Script -> Play**.

---

# 1. SINGLE REQUIRED INPUT

The only required user input is:

```text
printer_precision_mm
```

Accepted examples:

```text
0.10
0.20
0.30
0.40
0.50
```

Treat the number as a positive finite millimeter value.

If the value is missing, ask exactly one question:

> What is your printer's reliable XY feature size in mm?

Do not ask anything else.

If the value is provided, do not ask follow-up questions. Generate the result immediately.

---

# 2. INPUT VALIDATION

Before doing anything else:

```python
assert printer_precision_mm > 0
assert printer_precision_mm < 5.0
```

Recommended practical interpretation:

- `< 0.05 mm`: unusually fine; allow, but print a warning;
- `0.05–0.50 mm`: normal useful range for this simulation;
- `0.50–1.00 mm`: coarse; increase feature sizes automatically;
- `> 1.00 mm`: very coarse; generate the visualization, but clearly mark it as a coarse demonstrator;
- `>= 5.0 mm`: reject as invalid for this design.

Never silently produce negative, zero, NaN, or infinite dimensions.

---

# 3. LOCKED ARCHITECTURE

Never change these unless the user explicitly requests a redesign.

## Coordinate system

- X = drum axis
- Y = tangential lateral direction
- Z = vertical direction
- negative Z = projection direction toward floor/screen

## Inner core

- stationary
- diameter = **25 mm**
- coaxial with outer drum

## Outer drum

- horizontal axis
- rotating
- default length = **100 mm**
- default nominal outer diameter = **45 mm**
- diameter may automatically increase if printer-derived clearances require it

## LEDs

Critical:

- LEDs form one straight line along X;
- LEDs are NOT arranged around the circumference;
- LEDs stand radially upright;
- LEDs sit on the lower side of the stationary core;
- one cross-sectional X slice shows one LED;
- the longitudinal side view shows the whole LED row.

## Arc reflector/window

Critical:

- separate object from LEDs;
- thin cylindrical arc shell;
- curved in the YZ cross-section;
- extends straight along X;
- centered on lower optical direction;
- default angular width = 36 degrees.

## Helical slit

- one continuous helix;
- belongs to outer rotor;
- crosses the lower optical window as the drum rotates.

## Projection

- directed downward toward a floor/screen plane.

---

# 4. DERIVE ALL PRINTABLE DIMENSIONS FROM ONE NUMBER

Let:

```python
P = printer_precision_mm
```

Use these conservative rules.

## 4.1 Minimum printable wall

```python
wall_thickness_mm = max(4.0 * P, 1.20)
```

## 4.2 Helical slit width

```python
slit_width_mm = max(2.5 * P, 0.30)
```

The slit must not be smaller than the assumed reliable printable feature size.

## 4.3 General moving-part radial clearance

```python
radial_clearance_mm = max(4.0 * P, 1.50)
```

## 4.4 Reflector/window thickness

```python
arc_thickness_mm = max(2.5 * P, 0.55)
```

## 4.5 LED carrier thickness

```python
led_carrier_thickness_mm = max(2.0 * P, 0.50)
```

## 4.6 Visual ray radius

This is a visualization feature, not a manufactured dimension.

```python
ray_radius_mm = max(0.20, 1.5 * P)
```

## 4.7 Outer slit flash radius

Visualization only:

```python
flash_radius_mm = max(1.50, 5.0 * P)
```

## 4.8 Arc inner radius

Default optical/mechanical starting point:

```python
arc_inner_radius_mm = 15.0
```

But validate that it lies outside the 12.5 mm core radius:

```python
arc_inner_radius_mm >= 12.5 + radial_clearance_mm
```

Therefore derive:

```python
arc_inner_radius_mm = max(
    15.0,
    12.5 + radial_clearance_mm
)
```

## 4.9 Outer drum radius

The outer drum inner surface must sit outside:

- core;
- LED stack;
- reflector/window;
- radial clearance.

Use:

```python
required_inner_radius_mm = (
    arc_inner_radius_mm
    + arc_thickness_mm
    + radial_clearance_mm
)
```

Then derive nominal outer drum radius:

```python
outer_drum_radius_mm = max(
    22.5,
    required_inner_radius_mm + wall_thickness_mm
)
```

and:

```python
outer_drum_diameter_mm = 2.0 * outer_drum_radius_mm
```

Thus the familiar 45 mm drum remains the default when it fits, but automatically grows for coarse printers.

Do not shrink the 25 mm inner core.

---

# 5. LED DEFAULTS

Use:

```python
LED_COUNT = 16
LED_PACKAGE_X_MM = 1.60
LED_PACKAGE_Y_MM = 1.60
LED_VISUAL_HEIGHT_MM = 1.20
DRUM_LENGTH_MM = 100.0
LED_STRIP_MARGIN_MM = 6.0
```

Axial strip length:

```python
strip_length_mm = DRUM_LENGTH_MM - 2 * LED_STRIP_MARGIN_MM
```

Axial pitch:

```python
led_pitch_mm = strip_length_mm / (LED_COUNT - 1)
```

Validation:

```python
assert led_pitch_mm > LED_PACKAGE_X_MM
```

If this fails, automatically reduce LED count until it passes.

Never allow overlapping LED bodies in the generated Blender geometry.

---

# 6. HELIX GEOMETRY

Use one turn by default:

```python
HELIX_TURNS = 1.0
```

Helix local angle at axial position x:

```text
u = (x - x_min) / (x_max - x_min)

theta0(x) =
    theta_start
    + 2*pi*HELIX_TURNS*u
```

Use:

```python
theta_start = -pi/2
theta_target = -pi/2
```

Rotor crossing phase:

```text
phi_cross(x) =
    (theta_target - theta0(x)) mod 2*pi
```

Normalized crossing fraction:

```text
cross_fraction(x) =
    phi_cross(x) / (2*pi)
```

This crossing fraction determines exactly when each LED may flash.

Do not use arbitrary row-delay blinking when helix synchronization is requested.

---

# 7. RASTER RULE

Use the current agreed mapping:

```text
one drum revolution = one image column
one LED             = one image row
```

For every column:

1. rotor begins revolution;
2. helix successively reaches LED crossing phases;
3. for each row:
   - inspect image pixel;
   - if pixel OFF: LED stays OFF;
   - if pixel ON:
     - LED flashes;
     - internal ray appears;
     - outer slit flash appears;
     - external ray appears;
     - projected pixel appears.

The logical gate is:

```text
LED_output =
    image_pixel
    AND
    helix_crossing_gate
```

---

# 8. DEFAULT TEST IMAGE

Use a procedural binary smiley.

No external image file.

Recommended raster:

```python
RASTER_X = 24
RASTER_Y = LED_COUNT
```

The smiley should contain:

- circular face outline;
- two eyes;
- curved lower smile.

The image must progressively appear as scanning proceeds.

---

# 9. REQUIRED VISUAL OBJECTS

The monolithic Blender script must create objects with these names.

## Mechanical

```text
ROTOR_MASTER
OUTER_DRUM
CONTINUOUS_HELICAL_SLIT
STATIONARY_25MM_CORE
STATIONARY_SHAFT
THIN_ARC_WINDOW_REFLECTOR
LED_AXIAL_CARRIER
```

## LEDs

```text
LED_OFF_00
LED_OFF_01
...
LED_FLASH_00
LED_FLASH_01
...
```

## Optical visualization

```text
OUTER_SLIT_FLASH
INTERNAL_RAY
EXTERNAL_RAY
OUTER_CROSS_GUIDE
SCREEN_CURSOR
```

## Screen

```text
PROJECTION_SCREEN
GRID_...
PIXEL_...
```

The user must be able to hide:

```text
OUTER_DRUM
```

to inspect the internals.

---

# 10. RAY MODEL

The optical rays are conceptual geometric rays.

Never claim full optical ray tracing.

## Internal ray

```text
LED -> outer slit crossing
```

Name:

```text
INTERNAL_RAY
```

## External ray

```text
outer slit crossing -> projected pixel
```

Name:

```text
EXTERNAL_RAY
```

For a ray cylinder between points p1 and p2:

```python
d = p2 - p1
L = d.length

location = (p1 + p2) / 2

rotation_quaternion =
    d.to_track_quat('Z', 'Y')

scale_x = ray_radius
scale_y = ray_radius
scale_z = L / 2
```

Use a depth-2 unit cylinder so this scale convention is correct.

---

# 11. OUTER DRUM FLASH

Create:

```text
OUTER_SLIT_FLASH
```

It must:

- be emissive;
- be slightly outside the physical drum surface;
- share the same axial X as the active LED;
- occur at the same crossing phase;
- be visible only for ON image pixels.

Do not bury the flash inside the drum shell.

Recommended display radius:

```python
flash_radius_mm
```

derived from printer precision as above.

This is a visibility aid, not a physical flash size.

---

# 12. CAMERA RULE

The lower optical crossing is underneath the drum.

Therefore the default camera must be at a lower oblique side angle.

Do not default to a high camera looking down, because it can hide:

```text
OUTER_SLIT_FLASH
```

behind the drum body.

If the flash is not visible, debug in this order:

1. camera occlusion;
2. object visibility keyframes;
3. flash radius;
4. crossing phase;
5. material emission.

Do not immediately rewrite the helix math.

---

# 13. SLOW-MOTION DEFAULTS

The physical target is:

```text
2000 RPM
33.333 revolutions/s
30 ms/revolution
```

But the Blender demo must be intentionally slowed.

Use:

```python
FPS = 60
FRAMES_PER_REV = 192
LED_FLASH_FRAMES = 12
RAY_FLASH_FRAMES = 12
```

This yields:

```text
3.2 seconds per visible revolution
0.2 seconds visible flash
```

Clearly label these as visualization timing.

Do not imply that 3.2 seconds/revolution is the real scanner speed.

---

# 14. BLENDER API SAFETY RULES

Never depend on:

```python
action.fcurves
obj.animation_data.action.fcurves
```

Never animate:

```python
active_material_index
```

Do not assume a particular Eevee enum.

Prefer:

```python
object.keyframe_insert(...)
```

For flashes, use:

```python
hide_viewport
hide_render
```

keyframes.

For rotor motion, keying every frame is acceptable for robustness.

Support both material socket names when needed:

```text
Emission
Emission Color
```

Never require external packages.

Never require add-ons.

---

# 15. SELF-VALIDATION — REQUIRED

Every generated Blender script must contain a validation function.

Use a function named:

```python
validate_design()
```

It must check at least:

```python
assert abs(INNER_CORE_DIAMETER_MM - 25.0) < 1e-9

assert PRINTER_PRECISION_MM > 0
assert PRINTER_PRECISION_MM < 5.0

assert SLIT_WIDTH_MM >= 2.0 * PRINTER_PRECISION_MM

assert WALL_THICKNESS_MM >= 3.0 * PRINTER_PRECISION_MM

assert ARC_THICKNESS_MM >= 2.0 * PRINTER_PRECISION_MM

assert ARC_INNER_RADIUS_MM > INNER_CORE_DIAMETER_MM / 2.0

assert OUTER_DRUM_DIAMETER_MM > INNER_CORE_DIAMETER_MM

assert LED_COUNT >= 2

assert LED_PITCH_MM > LED_SIZE_X_MM

assert ARC_WINDOW_DEG > 0
assert ARC_WINDOW_DEG < 180

assert RASTER_Y == LED_COUNT

assert FPS > 0
assert FRAMES_PER_REV > 0
assert LED_FLASH_FRAMES > 0
assert RAY_FLASH_FRAMES > 0
```

After geometry creation, also check object existence:

```python
required_objects = [
    "ROTOR_MASTER",
    "OUTER_DRUM",
    "CONTINUOUS_HELICAL_SLIT",
    "STATIONARY_25MM_CORE",
    "STATIONARY_SHAFT",
    "THIN_ARC_WINDOW_REFLECTOR",
    "OUTER_SLIT_FLASH",
    "INTERNAL_RAY",
    "EXTERNAL_RAY",
    "PROJECTION_SCREEN",
]

for name in required_objects:
    assert bpy.data.objects.get(name) is not None
```

Check LED count:

```python
for i in range(LED_COUNT):
    assert bpy.data.objects.get(f"LED_OFF_{i:02d}") is not None
    assert bpy.data.objects.get(f"LED_FLASH_{i:02d}") is not None
```

Check crossing fractions:

```python
for f in cross_fraction:
    assert 0.0 <= f < 1.0
```

At end print:

```text
SELF VALIDATION: PASS
```

If any assertion fails, allow Blender to raise the assertion rather than silently continuing.

---

# 16. GENERATOR-SIDE VALIDATION — REQUIRED

Before returning the generated script to the user, the generating model/tool must validate the source code itself.

Minimum:

```python
compile(code, filename, "exec")
```

If available, also scan the source text for banned patterns:

```python
banned = [
    ".action.fcurves",
    "action.fcurves",
    "active_material_index",
]

for item in banned:
    assert item not in code
```

Also assert required strings exist:

```python
required_strings = [
    "validate_design",
    "OUTER_SLIT_FLASH",
    "INTERNAL_RAY",
    "EXTERNAL_RAY",
    "THIN_ARC_WINDOW_REFLECTOR",
    "STATIONARY_25MM_CORE",
    "PRINTER_PRECISION_MM",
]

for item in required_strings:
    assert item in code
```

This validation happens before giving the file to the user.

---

# 17. ONE-SHOT OUTPUT CONTRACT

If user says:

```text
printer precision 0.2 mm
```

do not ask follow-up questions.

Generate a complete script whose top begins conceptually like:

```python
PRINTER_PRECISION_MM = 0.20

WALL_THICKNESS_MM = max(4.0 * PRINTER_PRECISION_MM, 1.20)
SLIT_WIDTH_MM = max(2.5 * PRINTER_PRECISION_MM, 0.30)
RADIAL_CLEARANCE_MM = max(4.0 * PRINTER_PRECISION_MM, 1.50)
ARC_THICKNESS_MM = max(2.5 * PRINTER_PRECISION_MM, 0.55)
LED_CARRIER_THICKNESS_MM = max(2.0 * PRINTER_PRECISION_MM, 0.50)
```

Then derive the rest automatically.

The returned Blender file must be:

```text
Run Script
then
Press Play
```

No manual keyframing.

No external assets.

No additional setup.

---

# 18. CONSOLE REPORT

The generated script must print a compact design report.

Include:

```text
PRINTER PRECISION
CORE DIAMETER
OUTER DRUM DIAMETER
WALL THICKNESS
SLIT WIDTH
RADIAL CLEARANCE
ARC THICKNESS
ARC INNER RADIUS
LED COUNT
LED PITCH
RASTER SIZE
FPS
FRAMES PER REV
TARGET PHYSICAL RPM
SELF VALIDATION
```

Example ending:

```text
============================================================
NIPKOW DESIGN READY
Printer precision       : 0.200 mm
Core diameter           : 25.000 mm
Slit width              : 0.500 mm
Wall thickness          : 1.200 mm
...
SELF VALIDATION         : PASS
Run Script complete. Press PLAY.
============================================================
```

---

# 19. FAIL-SAFE BEHAVIOR

A weak model may be tempted to improvise. Do not.

If uncertain:

- preserve the 25 mm core;
- preserve the straight axial LED line;
- preserve radial LED orientation;
- preserve the separate arc reflector/window;
- preserve the horizontal X-axis drum;
- preserve helix-phase synchronization;
- preserve outer flash and two rays;
- preserve slow-motion playback;
- preserve self-validation.

Do not invent a different geometry.

Do not revert to a circumferential LED arc.

Do not flatten LEDs.

Do not remove the arc reflector.

Do not replace the helix with separate windows unless explicitly requested.

---

# 20. COMMON WRONG VERSIONS — NEVER GENERATE THESE

Wrong:

```text
LED LED LED arranged around circumference
```

Correct:

```text
X AXIS ------------------------------------>

|  |  |  |  |  |  |  |  |  |
LED LED LED LED LED LED LED LED
straight axial line
```

Wrong cross-section:

```text
many LEDs visible around core
```

Correct cross-section:

```text
outer drum
   arc reflector
       |
       | one LED
    25 mm core
```

Wrong timing:

```text
row timer -> LED flash
```

Correct timing:

```text
rotor phase
   +
helix geometry
   ->
crossing phase
   ->
image bit gate
   ->
LED flash
```

Wrong ray:

```text
LED -> arbitrary screen point
```

Correct:

```text
LED
  ->
actual slit crossing
  ->
screen pixel
```

---

# 21. PHYSICAL CAUTION

The Blender ray is conceptual.

Do not claim this proves:

- optical focus;
- diffraction limit;
- brightness;
- irradiance;
- depth of field;
- lens efficiency;
- real projected spot size.

Those require further optical design.

The single printer-precision input is sufficient for the simulation generator, not for final manufacturing qualification.

---

# 22. FINAL CHECKLIST

Before returning any generated script, verify all boxes:

- [ ] only required user input was printer precision;
- [ ] printer precision parsed in mm;
- [ ] 25 mm stationary core preserved;
- [ ] horizontal X-axis drum;
- [ ] outer drum rotating;
- [ ] one continuous helix;
- [ ] LEDs in straight X-axis line;
- [ ] LEDs radially upright;
- [ ] separate cylindrical arc reflector;
- [ ] one revolution maps to one image column;
- [ ] one LED maps to one image row;
- [ ] crossings derived from helix math;
- [ ] OFF image pixel -> no LED flash;
- [ ] ON image pixel -> LED flash;
- [ ] ON image pixel -> outer slit flash;
- [ ] ON image pixel -> internal ray;
- [ ] ON image pixel -> external ray;
- [ ] smiley progressively rasterizes;
- [ ] lower camera can see outer flash;
- [ ] OUTER_DRUM can be hidden for internals;
- [ ] no Action.fcurves dependency;
- [ ] no active_material_index animation;
- [ ] generated Python source compiles;
- [ ] banned-pattern scan passes;
- [ ] in-script validate_design() exists;
- [ ] Blender script prints SELF VALIDATION: PASS;
- [ ] final user workflow is Run Script -> Play.
