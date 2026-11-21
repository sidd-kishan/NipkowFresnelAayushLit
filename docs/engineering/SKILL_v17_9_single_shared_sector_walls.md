# NipkowFresnelAayushLit — V17.9 engineering specification

**Revision:** 21 November 2026. **Primary source:** `nipkow_drum_v17_9_single_shared_sector_walls.py`. **Parent:** V17.8 (`nipkow_drum_v17_8_50slot_4mm_encoder_reinforced_print.py`).

## Change requested and implemented

**The stationary 1206 LED drum has exactly ONE shared radial sector separator at each 36° sector boundary.** No doubled +/-0.9° walls. Ten sectors means **10 physical walls**, with centre azimuths **0°, 36°, 72°, 108°, 144°, 180°, 216°, 252°, 288°, and 324°**. Each wall is **0.5 mm thick tangentially**, runs straight/radially from **R27.65 mm to R34.70 mm**, and extends over **Z0–100.5 mm**. It penetrates the stationary carrier wall by 0.35 mm and nominally clears the R36.0 mm rotating inner wall by 1.30 mm. Walls at 0°/180° define the visible/UV hemisphere boundary. The five sectors in each hemisphere remain assigned visible (0–4) and UV (5–9) respectively. No separate baffle STLs are generated; the walls are included in a single LED inner-drum mesh object.

**The alternate stationary LILYGO debugging drum is unchanged:** it has **one outward-facing board slot and TWO 0.5 mm side walls**, placed at 348° and 48° around the display pocket centred at 18°. Its wider opening accommodates the display board. Exactly **one** stationary drum is installed at any given time.

## Configuration retained from V17.8

| Feature | Value |
|---|---|
| Physical rotor sectors | 10 × 36° |
| Active visible/UV sectors | 5 + 5 |
| Nipkow apertures | 500 × Ø1.5 mm, straight radial |
| Aperture rows per sector | 50 |
| Axial row pitch | 2.0 mm |
| LED channel width | 1.5 mm |
| Horizontal LED separators | 49 full-circumference × 0.5 mm, plus two end lips |
| Hole-to-hole axial material web | 0.5 mm nominal |
| Start/end material margins | 0.5 mm each |
| Active scan height | 100.5 mm |
| Rotor OD / ID | 76 / 72 mm |
| Stationary LED carrier OD / ID | 56 / 52 mm |
| Encoder | 5 slots per sector, 50 total |
| Encoder/base thickness | 4 mm |
| Bearing journals | 2 × Ø80 mm × 10 mm |
| Axial inner bearing guards | 2 × Ø84.2 mm × 2 mm |
| Drive hub | Ø28 × 29 mm, 7 mm high, 45° gusset |
| Drive pulley | Integrated 40-tooth GT2-style prototype |
| D shaft bore | Ø5.2 mm nominal, 4.7 mm flat-to-round |
| Alignment | 10 Ø1.5 mm axial registration holes at R38.8 mm |

## Script usage and export behavior

1. Open the monolithic `.py` in Blender's Scripting workspace.
2. Set `SCENE_INNER_VARIANT = 'LED'` for the production LED carrier or `'LILYGO'` for the debug carrier.
3. Run the script. It intends to export three design meshes (rotor, LED inner, alternate LILYGO inner) and leave **exactly two mesh objects** in the final scene: one common rotor and one selected stationary inner.
4. Inspect the ten distinct separator walls at 36° spacing. No wall pair should appear around a shared boundary; the single wall should straddle the geometric boundary line.
5. Inspect every Boolean cut, ring connection, through-alignment opening and STL mesh in Blender and your slicer before fabricating.

Expected output STL filenames when Blender completes:

- `nipkow_v17_9_outer_50encoder_4mm_reinforced.stl`
- `nipkow_v17_9_inner_LED_10x0p5_shared_sector_walls.stl`
- `nipkow_v17_9_inner_LILYGO_2x0p5_slot_walls.stl`

## Mechanical and optical risk register

- Ten axial Ø1.5 mm registration holes at R38.8 mm penetrate bearing journals, leaving only **0.45 mm outer radial web**: **not validated for interference bearing fit**. Do not press-fit bearings without reworking this feature or demonstrating strength.
- PLA bearing journals can slip against bearing inner races; a positive, continuous journal interface and inner-race axial clamp are preferable. This revision **does not implement** a new bearing clamp.
- A full-height 0.5 mm wall with ~6.7 mm unsupported radial protrusion may be difficult to print. Verify support strategy, geometry union and toolpaths.
- 1.30 mm rotating-wall clearance still permits stray light; opacity and optical crosstalk must be tested, particularly between UV and visible halves.
- 40-tooth GT2 pulley is an illustrative printed tooth profile, **not yet belt-fit validated**.
- The existing 100 mm lens does not fully cover the 100.5 mm active scan section.
- Source compilation and isolated geometry execution **do not** establish watertight STL output; full Blender Boolean execution is not verified in this environment.

## V17.9 validation performed

- Python syntax compilation passed.
- Isolated `create_arc_boundary_ridges()` from the actual patched source was executed with a recording Blender primitive; it returned **ten** unique 0.5 mm walls at exactly the expected 36° angles.
- LILYGO's two-wall geometry constants and 50-slot encoder remain in the source.
- Unified patch reapplication reproduced the exact new monolithic source byte-for-byte.
