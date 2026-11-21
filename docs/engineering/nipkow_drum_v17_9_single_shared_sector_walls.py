# =====================================================================
# NipkowFresnelAayushLit — V17.9 (2026-11-21)
# ONE ROTOR + TWO INTERCHANGEABLE INNER DESIGN VARIANTS (2 in scene).
#
# ROTOR (single printable object):
#   500 × Ø1.5 mm straight radial scan apertures (50 rows × 10 sectors),
#   100.5 mm active height, 2.0 mm axial pitch, 0.5 mm end margins,
#   Ø80 × 10 mm bearing journals, Ø84.2 × 2 mm inner bearing guards,
#   50 encoder slots, 4mm thick drive/encoder base, integral 40T GT2 + D bore.
#   Motor-bearing journal is reinforced by an inner annular load bridge.
#
# STATIONARY LED DRUM (single printable object; V17.9 sector-wall update):
#   49 × 0.5 mm continuous 360-degree axial row-separator rings plus
#   two 0.5 mm end lips. ONE radial 0.5 mm fin at EACH shared boundary
#   between the ten 36-degree sectors: exactly 10 fins, at 0, 36, ... 324°.
#   Five sectors are visible; five are UV. All fins are integral, not STLs.
#
# OPTIONAL DEBUG INNER DRUM (interchangeable printable component):
#   one outward-facing LILYGO T-Display-S3 AMOLED 1.91-inch board pocket,
#   nominal 60x25.5x10 mm module. Same upper D-shaped shaft interface,
#   same alignment flange. ONE debug opening is framed by TWO integral
#   0.5 mm dividers, spaced wider than 36 deg to clear the board envelope.
#   Prints as a separate alternative to the LED carrier, never installed
#   simultaneously with it. Three distinct STL files, two assembly parts.
#
# ALIGNMENT: 10 real Ø1.5 mm axial THROUGH holes at R38.8 mm, spaced 36°.
#   Applied in a SINGLE final Boolean to the ENTIRE assembled rotor;
#   go through BOTH 10 mm journals AND BOTH 2 mm bearing guards.
#   Match 10 through-holes in the stationary top flange.
#   CRITICAL: only 0.45 mm solid web to Ø80 journal OD remains.
#
# FINAL scene: EXACTLY two mesh objects, OUTER + chosen INNER variant.
# STLs: rotor, normal LED inner, and alternative LILYGO inner (3 files).
# No separate baffle, pulley or guards printed.
#
# CAUTION: source validation is not Blender Boolean/mesh verification.
#   Some meshes are overlapping joins rather than proven manifold unions.
#   Verify STL slicer union, hole opening and bearing fit before printing.
# =====================================================================

import bpy
import bmesh
import math
from mathutils import Vector

# =====================================================================
# GLOBAL / QUALITY SETTINGS
# =====================================================================

BOOLEAN_SOLVER = 'EXACT'

# Switch to True for quicker geometry checks.
# FINAL PRINT should normally use False.
FAST_PREVIEW = False

if FAST_PREVIEW:
    DRUM_CIRCLE_VERTICES = 96
    APERTURE_CIRCLE_VERTICES = 12
    ARC_SEGMENTS = 12
else:
    DRUM_CIRCLE_VERTICES = 256
    APERTURE_CIRCLE_VERTICES = 32
    ARC_SEGMENTS = 28

AUTO_EXPORT_STL = True

OUTER_STL_FILENAME = "nipkow_v17_9_outer_50encoder_4mm_reinforced.stl"
INNER_STL_FILENAME = "nipkow_v17_9_inner_LED_10x0p5_shared_sector_walls.stl"
DEBUG_STL_FILENAME = "nipkow_v17_9_inner_LILYGO_2x0p5_slot_walls.stl"

# Final scene will contain OUTER plus ONLY one of these two inner drums.
# Both inner variants are still exported in one execution for convenience.
SCENE_INNER_VARIANT = 'LILYGO'  # 'LILYGO' or 'LED'
assert SCENE_INNER_VARIANT in ('LILYGO', 'LED')

# PRINT CONFIGURATION: geometry already uses a vertical Z drum axis with the
# drive hub below the base. Do not tilt the printed part: upright (0deg) keeps
# encoder bridges in the strong XY deposition planes and bearing journals
# circular in XY. The hub-down build REQUIRES organic/manual supports beneath
# the lower bearing seat/shoulder and the encoder disk's exposed annulus.
PRINT_AXIS_TILT_DEG = 0.0
PRINT_BUILD_ORIENTATION = 'Z_VERTICAL_HUB_DOWN'
RECOMMENDED_LAYER_HEIGHT_MM = 0.16


# =====================================================================
# MASTER GEOMETRY
# =====================================================================

# V17: 50 holes per sector, axial pitch 2.0 mm, diameter 1.5 mm.
#    0.5 + 1.5 + 49*2.0 + 0.5 = 100.5 mm.
# 100.0 mm UV stock lens cannot cover the entire active height.
ACTIVE_WALL_HEIGHT_MM = 100.5

# Dedicated non-scanning alignment collar above the active scan region.
ALIGNMENT_BAND_HEIGHT_MM = 6.0

TOTAL_CYLINDER_HEIGHT_MM = (
    ACTIVE_WALL_HEIGHT_MM
    + ALIGNMENT_BAND_HEIGHT_MM
)

ROW_COUNT = 50
ROW_PITCH_MM = 2.00

APERTURE_DIAMETER_MM = 1.50
APERTURE_RADIUS_MM = APERTURE_DIAMETER_MM * 0.5

END_MARGIN_MM = 0.50

FIRST_ROW_CENTER_Z = END_MARGIN_MM + APERTURE_RADIUS_MM
LAST_ROW_CENTER_Z = (
    FIRST_ROW_CENTER_Z
    + (ROW_COUNT - 1) * ROW_PITCH_MM
)

LAST_APERTURE_EDGE_Z = LAST_ROW_CENTER_Z + APERTURE_RADIUS_MM

TOP_REMAINING_MARGIN_MM = (
    ACTIVE_WALL_HEIGHT_MM
    - (LAST_ROW_CENTER_Z + APERTURE_RADIUS_MM)
)

ACTIVE_CENTER_Z = ACTIVE_WALL_HEIGHT_MM * 0.5

# =====================================================================
# ANGULAR / OPTICAL ARCHITECTURE
# =====================================================================

SECTOR_COUNT = 10
SECTOR_REPEAT_DEG = 36.0

# The Nipkow diagonal spans the complete mechanically symmetric 36 degree
# sector, centered about each sector center.
SLANT_SWEEP_DEG = 32.0

# Broad LED illumination region.
LED_ACTIVE_ARC_DEG = 32.0
LED_ACTIVE_HALF_ARC_DEG = LED_ACTIVE_ARC_DEG * 0.5

# Narrow region intended initially for precision exposure/calibration.
PRECISION_GATE_DEG = 6.0
PRECISION_HALF_GATE_DEG = PRECISION_GATE_DEG * 0.5

# Legacy V16 steering constants retained as inactive references only.
# V17 actually cuts holes in their local radial directions with ZERO tilt.
PUPIL_DISTANCE_FROM_OUTER_SURFACE_MM = 140.0  # unused by V17 hole builder
MAX_ALLOWED_TUNNEL_TILT_DEG = 30.0            # unused by V17 hole builder

# =====================================================================
# OUTER ROTATING DRUM
# =====================================================================

OUTER_DRUM_OD_MM = 76.0
OUTER_DRUM_RADIUS_MM = OUTER_DRUM_OD_MM * 0.5

OUTER_WALL_THICKNESS_MM = 2.0
OUTER_DRUM_ID_MM = (
    OUTER_DRUM_OD_MM
    - 2.0 * OUTER_WALL_THICKNESS_MM
)
OUTER_DRUM_INNER_RADIUS_MM = OUTER_DRUM_ID_MM * 0.5

# Reinforced encoder/base below the 100.5 mm active wall.
OUTER_BASE_THICKNESS_MM = 4.0  # V17.8: 2x in-plane shear area, 4x ideal plate bending strength
# Ensure base/shell are mechanically interpenetrating rather than merely
# touching at a zero-overlap Z=0 face. Slicer must still Boolean-union meshes.
OUTER_SHELL_BASE_JOIN_OVERLAP_MM = 1.50

# Expanded motor/encoder disk.
OUTER_BASE_OD_MM = OUTER_DRUM_OD_MM
OUTER_BASE_RADIUS_MM = OUTER_BASE_OD_MM * 0.5

# Motor D-shaft hub.
OUTER_HUB_OD_MM = 28.0
OUTER_HUB_RADIUS_MM = OUTER_HUB_OD_MM * 0.5
# Extended outboard hub keeps the belt clear of the motor-side 6816 bearing.
# The original 10 mm hub was axially INSIDE the bearing and could not be belted.
OUTER_HUB_LENGTH_MM = 29.0
# Hub extends 0.5 mm INTO the solid encoder/base disk for slicer continuity.
# Belt torque still requires checking the printed hub-to-base joint.
OUTER_HUB_BASE_AXIAL_OVERLAP_MM = 0.50
HUB_ROOT_GUSSET_HEIGHT_MM = 7.00 # 45deg 14->21mm radius ramp in hub-down print
HUB_ROOT_GUSSET_TOP_RADIUS_MM = 21.00
# Conical gusset rises 7 mm while its radius expands 7 mm: 45-degree slope.
HUB_ROOT_GUSSET_PRINT_SLOPE_DEG = math.degrees(math.atan2(
    HUB_ROOT_GUSSET_HEIGHT_MM,
    HUB_ROOT_GUSSET_TOP_RADIUS_MM - OUTER_HUB_RADIUS_MM))
HUB_ROOT_GUSSET_BASE_OVERLAP_MM = 0.50

OUTER_D_BORE_DIAMETER_MM = 5.20
OUTER_D_BORE_RADIUS_MM = OUTER_D_BORE_DIAMETER_MM * 0.5
OUTER_D_FLAT_TO_ROUND_MM = 4.70
OUTER_D_FLAT_X = (
    OUTER_D_FLAT_TO_ROUND_MM
    - OUTER_D_BORE_RADIUS_MM
)


# =====================================================================
# V16 COAXIAL TOP ALIGNMENT SIGHT HOLES
# =====================================================================

# One simple round sight path per 36° sector boundary.  The same XY positions
# are cut through the stationary inner top disk AND every overlapping outer
# rotating top/support layer, so the holes are genuinely see-through in top view.
COAXIAL_ALIGNMENT_HOLE_COUNT = SECTOR_COUNT
COAXIAL_ALIGNMENT_HOLE_DIAMETER_MM = 1.50
COAXIAL_ALIGNMENT_HOLE_RADIUS_MM = COAXIAL_ALIGNMENT_HOLE_DIAMETER_MM * 0.5
COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM = 38.80
COAXIAL_ALIGNMENT_CUT_OVERSHOOT_MM = 3.00

# =====================================================================
# V16 ROLLING-CONTACT SUPPORT LANDS
# =====================================================================

# Two smooth 360 degree 80 mm journals carry standard 6816 bearings.
# They have 2 mm-thick INNER axial stop shoulders, not a rock-tumbler drive.
# The 100 mm OD outer bearing rings sit in the stationary bearing housings.
# WARNING: R38.8 registration bores DO PERFORATE the journals (0.45mm web).
ROLLING_LAND_COUNT = 2
ROLLING_LAND_AXIAL_WIDTH_MM = 10.0
ROLLING_LAND_RADIAL_HEIGHT_MM = 2.0
ROLLING_LAND_OUTER_RADIUS_MM = (
    OUTER_DRUM_RADIUS_MM + ROLLING_LAND_RADIAL_HEIGHT_MM
)
ROLLING_LAND_OUTER_OD_MM = 2.0 * ROLLING_LAND_OUTER_RADIUS_MM

# Nominal journal-to-shoulder and shoulder-to-body overlaps are 0.30 mm.
# A small join-only overlap is not a substitute for mechanical load testing.
ROLLING_LAND_INNER_RADIUS_MM = OUTER_DRUM_RADIUS_MM - 1.5
ROLLING_LAND_AXIAL_OVERLAP_MM = 0.30

# 6816 bearing inner-race axial stop on the side facing the optical region.
# NSK/NTN reference dimensions indicate 84 to 84.5 mm shaft abutment OD.
# This is a TWO-MILLIMETRE-THICK AXIAL SHOULDER, not a shorter 10 mm seat.
BEARING_GUARD_COUNT = 2
BEARING_GUARD_AXIAL_WIDTH_MM = 2.00
BEARING_GUARD_OUTER_OD_MM = 84.20
BEARING_GUARD_OUTER_RADIUS_MM = BEARING_GUARD_OUTER_OD_MM * 0.5
BEARING_GUARD_INNER_RADIUS_MM = 35.50
BEARING_GUARD_TO_BODY_OVERLAP_MM = 0.30
BEARING_GUARD_TO_JOURNAL_OVERLAP_MM = 0.30

# Inboard guard faces touch the inward-facing bearing inner rings.
# Neither guard overlaps the scanned 0..100.5 mm active optical interval.
BEARING_GUARD_LOWER_Z1_MM = -OUTER_BASE_THICKNESS_MM + BEARING_GUARD_TO_BODY_OVERLAP_MM
BEARING_GUARD_LOWER_Z0_MM = BEARING_GUARD_LOWER_Z1_MM - BEARING_GUARD_AXIAL_WIDTH_MM
BEARING_GUARD_UPPER_Z0_MM = TOTAL_CYLINDER_HEIGHT_MM - BEARING_GUARD_TO_BODY_OVERLAP_MM
BEARING_GUARD_UPPER_Z1_MM = BEARING_GUARD_UPPER_Z0_MM + BEARING_GUARD_AXIAL_WIDTH_MM

# V17.3+: GT2-STYLE TEETH ON THE D-SHAFT DRIVE STUB.
# 40T x 2mm pitch: pitch diameter 25.465mm, tip diameter ~24.957mm.
# Grooves approximate rather than certified GT2 profiles.
# Rounded groove / belt clearance is an APPROXIMATION, not certified GT2.
BELT_DRIVE_PROFILE = 'GT2_2MM_ROUNDED_PROTOTYPE'
GT2_TOOTH_COUNT = 40
GT2_PITCH_MM = 2.00
GT2_PITCH_LINE_DIFFERENTIAL_MM = 0.254
GT2_PITCH_RADIUS_MM = GT2_TOOTH_COUNT * GT2_PITCH_MM / (2.0 * math.pi)
GT2_TIP_RADIUS_MM = GT2_PITCH_RADIUS_MM - GT2_PITCH_LINE_DIFFERENTIAL_MM
GT2_GROOVE_DEPTH_MM = 0.75
GT2_ROOT_RADIUS_MM = GT2_TIP_RADIUS_MM - GT2_GROOVE_DEPTH_MM
GT2_BELT_WIDTH_MM = 6.00
GT2_TOOTH_FACE_WIDTH_MM = 6.40  # 0.20 mm axial nominal extra per side
GT2_FLANGE_AXIAL_WIDTH_MM = 1.00
GT2_FLANGE_OUTER_OD_MM = 32.00   # custom flange OD for stronger 40T hub
GT2_FLANGE_OUTER_RADIUS_MM = GT2_FLANGE_OUTER_OD_MM * 0.5
GT2_FLANGE_INNER_RADIUS_MM = 12.50 # overlaps solid Ø28 hub
GT2_PROFILE_SAMPLES_PER_TOOTH = 28
GT2_CUTTER_OUTER_RADIUS_MM = OUTER_HUB_RADIUS_MM + 1.50
GT2_CENTER_FROM_OUTBOARD_END_MM = 6.00
GT2_CENTER_Z_MM = (-OUTER_BASE_THICKNESS_MM - OUTER_HUB_LENGTH_MM
                   + GT2_CENTER_FROM_OUTBOARD_END_MM)
GT2_TOOTH_Z0_MM = GT2_CENTER_Z_MM - GT2_TOOTH_FACE_WIDTH_MM / 2.0
GT2_TOOTH_Z1_MM = GT2_CENTER_Z_MM + GT2_TOOTH_FACE_WIDTH_MM / 2.0
GT2_OUTBOARD_FLANGE_Z0_MM = GT2_TOOTH_Z0_MM - GT2_FLANGE_AXIAL_WIDTH_MM
GT2_INBOARD_FLANGE_Z1_MM = GT2_TOOTH_Z1_MM + GT2_FLANGE_AXIAL_WIDTH_MM
# Retain existing 25 mm hub, 5.2 mm D bore and remove the old V-groove.

# V17.3: matching GUARD openings, NOT holes in the Ø80 bearing journal.
BEARING_GUARD_VIEW_HOLE_COUNT = COAXIAL_ALIGNMENT_HOLE_COUNT
BEARING_GUARD_VIEW_HOLE_RADIUS_MM = COAXIAL_ALIGNMENT_HOLE_RADIUS_MM
BEARING_GUARD_VIEW_HOLE_CENTER_RADIUS_MM = COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM
BEARING_GUARD_VIEW_CUTTER_OVERSHOOT_MM = 0.50
BEARING_GUARD_CONTACT_START_RADIUS_MM = ROLLING_LAND_OUTER_RADIUS_MM
BEARING_GUARD_VIEW_TO_BORE_RADIAL_CLEARANCE_MM = (
    BEARING_GUARD_CONTACT_START_RADIUS_MM
    - (BEARING_GUARD_VIEW_HOLE_CENTER_RADIUS_MM
       + BEARING_GUARD_VIEW_HOLE_RADIUS_MM))

# V17.4 COAXIAL REGISTRATION: now genuine full-length through-holes.
# At R38.8, each Ø1.5 mm bore lies outside the Ø76 rotor shell (R38),
# but inside the Ø80 bearing journal (R40). The 0.45 mm bearing OD web
# is thin. All ten axial holes are cut AFTER outer pieces are joined.
# Matching ten stationary top-flange through-holes stay at the same XY.
# No hidden blind sockets and no later overlapping guard/journal geometry.
ROLLING_LAND_ALIGNMENT_HOLE_DIAMETER_MM = COAXIAL_ALIGNMENT_HOLE_DIAMETER_MM
ROLLING_LAND_ALIGNMENT_HOLE_RADIUS_MM = COAXIAL_ALIGNMENT_HOLE_RADIUS_MM
ROLLING_LAND_ALIGNMENT_HOLE_CENTER_RADIUS_MM = COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM
ROLLING_LAND_ALIGNMENT_HOLE_COUNT = COAXIAL_ALIGNMENT_HOLE_COUNT
ROLLING_LAND_ALIGNMENT_OUTER_WEB_MM = (
    ROLLING_LAND_OUTER_RADIUS_MM
    - ROLLING_LAND_ALIGNMENT_HOLE_CENTER_RADIUS_MM
    - ROLLING_LAND_ALIGNMENT_HOLE_RADIUS_MM
)

# Shift BOTH 10 mm bearing journals outward by the shoulder thickness.
# Overlap 0.30 mm inside each guard to avoid merely face-touching meshes.
ROLLING_LAND_LOWER_Z1_MM = (
    BEARING_GUARD_LOWER_Z0_MM + BEARING_GUARD_TO_JOURNAL_OVERLAP_MM
)
ROLLING_LAND_LOWER_Z0_MM = (
    ROLLING_LAND_LOWER_Z1_MM - ROLLING_LAND_AXIAL_WIDTH_MM
)
ROLLING_LAND_UPPER_Z0_MM = (
    BEARING_GUARD_UPPER_Z1_MM - BEARING_GUARD_TO_JOURNAL_OVERLAP_MM
)
ROLLING_LAND_UPPER_Z1_MM = (
    ROLLING_LAND_UPPER_Z0_MM + ROLLING_LAND_AXIAL_WIDTH_MM
)

# V17.8: an *internal*, axisymmetric journal-to-base load bridge.
# It spans 3mm into the lower 10mm journal, crosses the guard and 4mm base,
# and overlaps the shell down to Z=-0.5mm. Outer R37.90 stays 0.15mm
# inside the nearest edge of the R38.8 / Ø1.5 alignment-hole cylinder.
# The bridge does not enter the active scanning region (Z>=0).
MOTOR_LOAD_BRIDGE_R_INNER_MM = 34.00
MOTOR_LOAD_BRIDGE_R_OUTER_MM = 37.90
MOTOR_LOAD_BRIDGE_Z0_MM = ROLLING_LAND_LOWER_Z1_MM - 3.00
MOTOR_LOAD_BRIDGE_Z1_MM = -0.50
MOTOR_LOAD_BRIDGE_HEIGHT_MM = (
    MOTOR_LOAD_BRIDGE_Z1_MM - MOTOR_LOAD_BRIDGE_Z0_MM
)


# =====================================================================
# V13-STYLE ROTATIONAL ENCODER
# =====================================================================

ENCODER_SECTOR_COUNT = 10
ENCODER_SECTOR_REPEAT_DEG = 36.0
ENCODER_SLOTS_PER_SECTOR = 5
ENCODER_SECTOR_MARGIN_DEG = 3.0

ENCODER_SLOT_RADIAL_LENGTH_MM = 6.0
ENCODER_SLOT_CENTER_RADIUS_MM = 27.0

ENCODER_SLOT_MAX_WIDTH_MM = 1.80
ENCODER_SLOT_MIN_WIDTH_MM = 0.60

ENCODER_SLOT_Z_OVERSHOOT_MM = 0.75

ENCODER_ACTIVE_SPAN_DEG = (
    ENCODER_SECTOR_REPEAT_DEG
    - 2.0 * ENCODER_SECTOR_MARGIN_DEG
)

ENCODER_SLOT_ANGLE_STEP_DEG = (
    ENCODER_ACTIVE_SPAN_DEG
    / (ENCODER_SLOTS_PER_SECTOR - 1)
)

TOTAL_ENCODER_SLOTS = (
    ENCODER_SECTOR_COUNT
    * ENCODER_SLOTS_PER_SECTOR
)

# Conservative 2D inner-radius tangential-web approximation for adjacent
# tapered encoder slots. Exact minimum distance is independently measured
# using polygons in V17.8_VALIDATION.csv (not a substitute for slicer check).
def encoder_inner_radius_web_estimate():
    r = ENCODER_SLOT_CENTER_RADIUS_MM - ENCODER_SLOT_RADIAL_LENGTH_MM / 2.0
    seq = []
    for sector in range(ENCODER_SECTOR_COUNT):
        for k in range(ENCODER_SLOTS_PER_SECTOR):
            t = k / (ENCODER_SLOTS_PER_SECTOR-1)
            angle = sector*ENCODER_SECTOR_REPEAT_DEG + ENCODER_SECTOR_MARGIN_DEG + t*ENCODER_ACTIVE_SPAN_DEG
            width = ENCODER_SLOT_MAX_WIDTH_MM + t*(ENCODER_SLOT_MIN_WIDTH_MM-ENCODER_SLOT_MAX_WIDTH_MM)
            seq.append((angle,width))
    gaps=[]
    for i in range(len(seq)):
        a,w=seq[i]
        b,v=seq[(i+1)%len(seq)]
        da=((b-a)%360.0)
        gaps.append(2.0*r*math.sin(math.radians(da/2)) - 0.5*(w+v))
    return min(gaps)
ENCODER_MIN_WEB_APPROX_MM = encoder_inner_radius_web_estimate()


# =====================================================================
# INNER STATIONARY LED / FRESNEL-LIKE CARRIER
# =====================================================================

INNER_CARRIER_OD_MM = 56.0
INNER_CARRIER_RADIUS_MM = INNER_CARRIER_OD_MM * 0.5

INNER_CARRIER_WALL_THICKNESS_MM = 2.0
INNER_CARRIER_ID_MM = (
    INNER_CARRIER_OD_MM
    - 2.0 * INNER_CARRIER_WALL_THICKNESS_MM
)
INNER_CARRIER_INNER_RADIUS_MM = INNER_CARRIER_ID_MM * 0.5

INNER_CARRIER_HEIGHT_MM = (
    TOTAL_CYLINDER_HEIGHT_MM
    + ROLLING_LAND_AXIAL_WIDTH_MM
    + 0.80
)

# LED ROW CHANNELS — straight, no Fresnel-style converging tilt.
# Channels measure 1.5 mm axially; 0.5 mm straight row fins produce 2 mm pitch.
LED_CHANNEL_WIDTH_MM = 1.50
ROW_SEPARATOR_AXIAL_WIDTH_MM = 0.50
FRESNEL_FIN_AXIAL_WIDTH_MM = ROW_SEPARATOR_AXIAL_WIDTH_MM  # legacy API alias
ROW_SEPARATOR_RADIAL_HEIGHT_MM = 6.70
FRESNEL_FIN_RADIAL_HEIGHT_MM = ROW_SEPARATOR_RADIAL_HEIGHT_MM  # legacy alias
FRESNEL_FIN_BODY_OVERLAP_MM = 0.0
FRESNEL_FIN_ARC_DEG = 0.0  # full 360-degree Fresnel rings REMOVED
FRESNEL_FIN_HALF_ARC_DEG = 0.0

# A SINGLE STRAIGHT 0.5mm fin at every shared 36-degree boundary.
# Neighboring LED sectors share the SAME physical wall (10 total, not 20).
# The 0°/180° walls isolate the visible and UV hemispheres. Keeping the
# walls on sector boundaries preserves the nominal +/-16° optical sweep
# inside each +/-18° sector (1.6°+ approximate angular margin at fin tip).
SECTOR_BOUNDARY_RIDGE_COUNT = SECTOR_COUNT  # exactly 10 physical fins
SECTOR_BOUNDARY_RIDGE_OFFSET_DEG = 0.0     # also sets alignment datums
SECTOR_BAFFLES_PER_SECTOR = 1
ARC_BOUNDARY_RIDGE_TANGENTIAL_WIDTH_MM = 0.50
ARC_BOUNDARY_RIDGE_RADIAL_HEIGHT_MM = 6.70
ARC_BOUNDARY_RIDGE_BODY_OVERLAP_MM = 0.35
ARC_BOUNDARY_RIDGE_HEIGHT_MM = ACTIVE_WALL_HEIGHT_MM
# A normal LED baffle tip reaches R34.7 (1.3mm clear of the rotating ID).
SECTOR_BAFFLE_ROOT_RADIUS_MM = INNER_CARRIER_RADIUS_MM - ARC_BOUNDARY_RIDGE_BODY_OVERLAP_MM
SECTOR_BAFFLE_TIP_RADIUS_MM = INNER_CARRIER_RADIUS_MM + ARC_BOUNDARY_RIDGE_RADIAL_HEIGHT_MM

# All ten LED sectors are active, with one SHARED 0.5mm wall per boundary.
# Walls exactly at 0 and 180 degrees partition visible and UV hemispheres.
# There are no detached baffle cassettes or printed extra assembly parts.
# Angular convention: viewed looking down +Z, +Y (0..180 deg) is visible,
# and -Y (180..360 deg) is UV. Rotate the complete instrument if needed.
VIS_ACTIVE_SECTOR_INDICES = tuple(range(0, 5))
UV_ACTIVE_SECTOR_INDICES = tuple(range(5, 10))
ACTIVE_OPTICAL_SECTOR_INDICES = VIS_ACTIVE_SECTOR_INDICES + UV_ACTIVE_SECTOR_INDICES
ROW_BAFFLE_CASSETTE_COUNT = 0  # still uninterrupted axial rings
ROW_RING_COUNT = ROW_COUNT + 1  # 49 intermediate + 2 end lips
ROW_RING_RADIAL_INNER_MM = 27.65
ROW_RING_RADIAL_OUTER_MM = 34.70
ROW_BAFFLE_RADIAL_INNER_MM = 27.65
ROW_BAFFLE_RADIAL_OUTER_MM = 34.70
ROW_BAFFLE_SPAN_DEG = 31.0   # leaves edge clearance for straight sector rails
ROW_BAFFLE_SIDE_RAIL_ANGLE_DEG = 15.25
ROW_BAFFLE_SIDE_RAIL_WIDTH_MM = 0.75
ROW_BAFFLE_SIDE_RAIL_R0_MM = 27.65
ROW_BAFFLE_SIDE_RAIL_R1_MM = 34.70
ROW_BAFFLE_CASSETTE_ASSEMBLY_STATUS = 'MESH_JOIN_OVERLAP_NEEDS_SLICER_UNION'

# No lens guide rails. Continuous axial rings intersect the 10 radial sector fins.
# External UV cylindrical or precision relay optics must be designed separately.
LENS_GUIDE_COUNT = 0
LENS_GUIDE_TANGENTIAL_WIDTH_MM = 0.0
LENS_GUIDE_BODY_OVERLAP_MM = 0.0
LENS_GUIDE_OUTER_RADIUS_MM = 35.0  # reference envelope, not printed guide
LENS_GUIDE_HEIGHT_MM = ACTIVE_WALL_HEIGHT_MM

# Legacy stock lens dimension retained for compatibility check only.
# 100.0 mm stock is SHORTER than the 100.5 mm active scan region.
CYL_FRESNEL_LENS_WIDTH_MM = 20.0
CYL_FRESNEL_LENS_THICKNESS_MM = 2.0
CYL_FRESNEL_LENS_STOCK_LENGTH_MM = 100.0

# Active-window fence markers.
#
# The previous 78 mm-tall flared fence ribs are intentionally removed.
# Alignment is now represented by one simple round through-hole at each
# shared 36 degree boundary on the stationary top disk.
ACTIVE_WINDOW_FENCE_HOLE_DIAMETER_MM = COAXIAL_ALIGNMENT_HOLE_DIAMETER_MM
ACTIVE_WINDOW_FENCE_HOLE_RADIUS_MM = (
    ACTIVE_WINDOW_FENCE_HOLE_DIAMETER_MM * 0.5
)
ACTIVE_WINDOW_FENCE_HOLES_PER_SIDE = 1

# The simple alignment hole uses the shared coaxial registration radius
# toward the 36 degree sector boundary in the exposed alignment disk.
ACTIVE_WINDOW_FENCE_HOLE_R_INNER_MM = COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM

# Small Boolean overshoot through both faces of the 2 mm alignment disk.
ACTIVE_WINDOW_FENCE_HOLE_OVERSHOOT_MM = COAXIAL_ALIGNMENT_CUT_OVERSHOOT_MM

INNER_FIN_OUTER_RADIUS_MM = INNER_CARRIER_RADIUS_MM + ROW_SEPARATOR_RADIAL_HEIGHT_MM


# End retaining lips use the material between the first/last LED channel
# and the cylinder ends.
END_LED_LIP_WIDTH_MM = (
    FIRST_ROW_CENTER_Z
    - LED_CHANNEL_WIDTH_MM * 0.5
)

# =====================================================================
# INNER SUPPORT / MARKING FLANGE
# =====================================================================

# A 2 mm internal support disk closes/supports the stationary carrier at
# the open end of the rotating drum.
INNER_SUPPORT_DISK_THICKNESS_MM = 2.0
INNER_SUPPORT_DISK_RADIUS_MM = INNER_CARRIER_RADIUS_MM

# A larger stationary flange sits ABOVE the rotating drum's open rim.
# It provides a visible top annulus for the simple round-hole alignment pattern.
INNER_MARKING_FLANGE_GAP_MM = 0.0
INNER_MARKING_FLANGE_THICKNESS_MM = 2.0

# Preserve a 5 mm radial top-view overhang beyond the new 76 mm drum.
# This keeps the simple round-hole fence/alignment pattern visible from above.
INNER_MARKING_FLANGE_OD_MM = ROLLING_LAND_OUTER_OD_MM
INNER_MARKING_FLANGE_RADIUS_MM = INNER_MARKING_FLANGE_OD_MM * 0.5
ACTIVE_WINDOW_FENCE_HOLE_R_OUTER_MM = COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM

INNER_SUPPORT_HUB_OD_MM = 18.0
INNER_SUPPORT_HUB_RADIUS_MM = INNER_SUPPORT_HUB_OD_MM * 0.5
INNER_SUPPORT_HUB_LENGTH_MM = 10.0

INNER_D_BORE_DIAMETER_MM = 5.20
INNER_D_BORE_RADIUS_MM = INNER_D_BORE_DIAMETER_MM * 0.5
INNER_D_FLAT_TO_ROUND_MM = 4.70
INNER_D_FLAT_X = (
    INNER_D_FLAT_TO_ROUND_MM
    - INNER_D_BORE_RADIUS_MM
)

# =====================================================================
# REGISTRATION / ALIGNMENT MARKS
# =====================================================================

# Registration markings are TRUE THROUGH-CUTS through the 2 mm outer
# base and the 2 mm stationary marking flange.  The extra depth guarantees
# Boolean overshoot on both faces.
MARKING_DEPTH_MM = 2.20
MARKING_TICK_WIDTH_MM = 0.80
MARKING_BOOLEAN_OVERSHOOT_MM = 0.20

# The repeated inner "36 degree" reference must NOT become one continuous
# 360 degree through-slot, because that would detach the flange outer ring.
# Exact +/-18 degree through-ticks still define the true 36 degree boundary.
# The arc body is shortened symmetrically to retain structural bridges.
INNER_36_ARC_SLOT_SPAN_DEG = 30.0

# OUTER base-rim marking radii.
OUTER_MARK_INNER_RADIUS_MM = 33.6
OUTER_MARK_OUTER_RADIUS_MM = 37.4

OUTER_32_ARC_R_INNER_MM = 34.0
OUTER_32_ARC_R_OUTER_MM = 34.7

OUTER_6_ARC_R_INNER_MM = 35.4
OUTER_6_ARC_R_OUTER_MM = 36.1

# INNER support-flange nested arc markings.
#
# Keep these in the exposed annulus OUTSIDE the 66 mm drum wall so they
# remain visible from directly above.  The flange radius is now 38 mm.
INNER_36_ARC_R_INNER_MM = 33.6
INNER_36_ARC_R_OUTER_MM = 34.3

INNER_32_ARC_R_INNER_MM = 34.9
INNER_32_ARC_R_OUTER_MM = 35.6

INNER_6_ARC_R_INNER_MM = 36.2
INNER_6_ARC_R_OUTER_MM = 36.9

# Radial extent used by top-view through-ticks.
INNER_TOP_MARK_OUTER_RADIUS_MM = (
    INNER_MARKING_FLANGE_RADIUS_MM - 0.8
)

# =====================================================================
# VISIBLE + OPTICAL THROUGH-SIGHT REGISTRATION
# =====================================================================

# The alignment hole is intentionally placed in the solid 5.5 degree
# margin between the 32 degree optical arc and 36 degree sector edge:
#
#   optical edge = +16.0 deg
#   horizontal sight line = +14.0 deg
#   sector edge  = +18.0 deg
#
# Thus the sight hole does not cut through the LED arc.
SIGHT_REL_ANGLE_DEG = 14.0

SIGHT_HOLE_DIAMETER_MM = 2.0
SIGHT_HOLE_RADIUS_MM = SIGHT_HOLE_DIAMETER_MM * 0.5

# One circumferential row of alignment holes only. The row is centered
# in the 6 mm non-scanning alignment collar so it cannot touch a Nipkow
# aperture row.
SIGHT_Z_LEVELS_MM = (
    ACTIVE_WALL_HEIGHT_MM + ALIGNMENT_BAND_HEIGHT_MM * 0.5,
)

# Shallow external demarcation dent immediately above the active scan region.
# It remains divided into ten identical 30 degree arc segments, but it does
# NOT cut through the 2 mm drum wall.  This keeps the visual boundary without
# creating a circumferential stress-break line.
DEMARCATION_RING_Z_MM = ACTIVE_WALL_HEIGHT_MM + 0.60
DEMARCATION_RING_AXIAL_WIDTH_MM = 0.60
DEMARCATION_RING_SEGMENT_SPAN_DEG = 30.0
DEMARCATION_DENT_DEPTH_MM = 0.35
DEMARCATION_RING_RADIAL_OVERSHOOT_MM = 0.20

# =====================================================================
# VALIDATION
# =====================================================================

def require(condition, message):
    if not condition:
        raise ValueError(message)


require(
    abs(SECTOR_COUNT * SECTOR_REPEAT_DEG - 360.0) < 1e-8,
    "Sector count/repeat must close exactly to 360 degrees."
)

require(
    len(SIGHT_Z_LEVELS_MM) == 1,
    "Optimized V16 uses exactly one axial sight-hole row."
)

require(
    SIGHT_Z_LEVELS_MM[0] - SIGHT_HOLE_RADIUS_MM > ACTIVE_WALL_HEIGHT_MM,
    "Sight-hole row must remain completely above the active Nipkow region."
)

require(SECTOR_BOUNDARY_RIDGE_COUNT == SECTOR_COUNT == 10 and
        SECTOR_BAFFLES_PER_SECTOR == 1 and
        abs(ARC_BOUNDARY_RIDGE_TANGENTIAL_WIDTH_MM - 0.5) < 1e-10,
        "V17.9 needs ONE shared 0.5mm fin at each of ten sector boundaries.")
require(SECTOR_BAFFLE_ROOT_RADIUS_MM < INNER_CARRIER_RADIUS_MM and
        abs(SECTOR_BAFFLE_TIP_RADIUS_MM - 34.70) < 1e-10 and
        SECTOR_BAFFLE_TIP_RADIUS_MM < OUTER_DRUM_INNER_RADIUS_MM,
        "Radial baffles must join the carrier and clear the rotor.")
# Shared walls are centred ON the 36-degree boundaries rather than
# sitting in pairs 0.9 degrees inside neighboring sectors.
require(SECTOR_BOUNDARY_RIDGE_OFFSET_DEG == 0.0 and
        abs(SECTOR_COUNT * SECTOR_REPEAT_DEG - 360.0) < 1e-10,
        "Shared LED fins must be at 0, 36, 72, ... 324 degrees.")
require(SECTOR_BAFFLE_TIP_RADIUS_MM * math.sin(
            math.radians((SECTOR_REPEAT_DEG - LED_ACTIVE_ARC_DEG) * 0.5))
        > ARC_BOUNDARY_RIDGE_TANGENTIAL_WIDTH_MM * 0.5,
        "The nominal 32deg illumination zone may intersect the sector wall.")


require(
    abs(FRESNEL_FIN_AXIAL_WIDTH_MM - 0.50) < 1e-9,
    "V17 row separators must be 0.5 mm thick."
)

require(
    abs(TOP_REMAINING_MARGIN_MM - 0.50) < 1e-9,
    "V17 must retain exactly 0.5 mm at the top aperture edge."
)

require(
    abs(LAST_APERTURE_EDGE_Z - (ACTIVE_WALL_HEIGHT_MM - END_MARGIN_MM)) < 1e-9,
    "V17 last aperture edge/end margin mismatch."
)

require(
    ROLLING_LAND_COUNT == 2,
    "V17 uses exactly two 10 mm bearing lands."
)

# V17.4 — real THROUGH holes in BOTH Ø80 x 10 mm journals AND both guards.
# Their 38.8 mm centre radius leaves only 0.45 mm material to the R40 OD.
# No cutter intersects the R40 bearing-running surface, but this web is thin;
# physical bearing-fit and strength tests remain mandatory.
require(ROLLING_LAND_ALIGNMENT_HOLE_COUNT == SECTOR_COUNT == 10,
        "Ten aligned through-port datums are required per rotating collar.")
require(ROLLING_LAND_ALIGNMENT_HOLE_DIAMETER_MM == COAXIAL_ALIGNMENT_HOLE_DIAMETER_MM
        and ROLLING_LAND_ALIGNMENT_HOLE_CENTER_RADIUS_MM == COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM,
        "Rotor and fixed flange must use matching aligner XY positions.")
require(ROLLING_LAND_ALIGNMENT_OUTER_WEB_MM >= 0.40,
        "The Ø80 bearing journal needs >=0.4 mm OD web around each port.")
require(ROLLING_LAND_ALIGNMENT_HOLE_CENTER_RADIUS_MM
        - ROLLING_LAND_ALIGNMENT_HOLE_RADIUS_MM
        > OUTER_DRUM_RADIUS_MM,
        "Axial alignment ports must clear the entire outer wall and base in top view.")
require(ROLLING_LAND_ALIGNMENT_HOLE_CENTER_RADIUS_MM
        - ROLLING_LAND_ALIGNMENT_HOLE_RADIUS_MM
        > ROLLING_LAND_INNER_RADIUS_MM,
        "Aligner holes must lie within each bearing-journal annulus.")

require(BEARING_GUARD_COUNT == ROLLING_LAND_COUNT == 2,
        "Provide two inboard bearing shoulder guards.")
require(abs(BEARING_GUARD_AXIAL_WIDTH_MM - 2.0) < 1e-9,
        "Requested guard axial thickness must be 2 mm.")
require(84.0 <= BEARING_GUARD_OUTER_OD_MM <= 84.5,
        "6816 guard OD must suit the bearing inner-race abutment, not its seal.")
require(BEARING_GUARD_OUTER_RADIUS_MM > ROLLING_LAND_OUTER_RADIUS_MM,
        "Guard must protrude radially beyond the 80 mm bearing seat.")
require(BEARING_GUARD_LOWER_Z1_MM < 0.0 and
        BEARING_GUARD_UPPER_Z0_MM > ACTIVE_WALL_HEIGHT_MM,
        "Bearing guards must not shade or touch the active optical wall.")
require(abs(ROLLING_LAND_LOWER_Z1_MM - ROLLING_LAND_LOWER_Z0_MM - 10.) < 1e-9 and
        abs(ROLLING_LAND_UPPER_Z1_MM - ROLLING_LAND_UPPER_Z0_MM - 10.) < 1e-9,
        "Both 6816 bearing journals must remain exactly 10 mm wide.")
require(0.0 < OUTER_HUB_BASE_AXIAL_OVERLAP_MM < OUTER_BASE_THICKNESS_MM,
        "Hub-to-base overlap must be positive and contained in the solid base.")
require(BEARING_GUARD_VIEW_HOLE_COUNT == SECTOR_COUNT,
        "Both guards must provide ten coaxial alignment windows.")
require(BEARING_GUARD_VIEW_HOLE_CENTER_RADIUS_MM - BEARING_GUARD_VIEW_HOLE_RADIUS_MM
        > BEARING_GUARD_INNER_RADIUS_MM + 1.0,
        "Bearing guard view openings must stay inside the shoulder annulus.")
require(BEARING_GUARD_VIEW_TO_BORE_RADIAL_CLEARANCE_MM >= 0.35,
        "Guard view holes must not cut the bearing inner-ring contact OD=80..84.2 region.")
require(GT2_TOOTH_COUNT == 40 and abs(GT2_PITCH_MM - 2.0) < 1e-9,
        "V17.7 retains the 40-tooth 2.0mm-pitch drive.")
require(GT2_ROOT_RADIUS_MM > OUTER_D_BORE_RADIUS_MM + 8.0,
        "GT2 root must leave substantial plastic outside D-shaft socket.")
require(GT2_TIP_RADIUS_MM < OUTER_HUB_RADIUS_MM and
        GT2_CUTTER_OUTER_RADIUS_MM > OUTER_HUB_RADIUS_MM,
        "Cut toothed band from the thicker 28 mm hub without floating geometry.")
require(GT2_TOOTH_FACE_WIDTH_MM >= GT2_BELT_WIDTH_MM,
        "Teeth must span at least the 6 mm timing belt.")
require(GT2_OUTBOARD_FLANGE_Z0_MM > -OUTER_BASE_THICKNESS_MM - OUTER_HUB_LENGTH_MM + 1.0,
        "GT2 outer flange would collide with D-hub outboard end.")
require(GT2_INBOARD_FLANGE_Z1_MM < ROLLING_LAND_LOWER_Z0_MM - 2.0,
        "GT2 inboard flange must remain outside the motor-side bearing.")
require(GT2_TOOTH_Z0_MM < GT2_TOOTH_Z1_MM,
        "Toothed face must have positive axial width.")

require(
    LENS_GUIDE_OUTER_RADIUS_MM < OUTER_DRUM_INNER_RADIUS_MM,
    "Stationary lens guides must remain inside the rotating drum."
)

require(
    abs(
        (SECTOR_REPEAT_DEG - LED_ACTIVE_ARC_DEG) * 0.5
        - 2.0
    ) < 1e-9,
    "V17 optical window must retain 2 degrees margin per side."
)

require(
    abs(
        OUTER_DRUM_INNER_RADIUS_MM
        - LENS_GUIDE_OUTER_RADIUS_MM
        - 1.0
    ) < 1e-9,
    "V17 baffle envelope must retain exactly 1.0 mm radial running clearance."
)

require(
    ACTIVE_WINDOW_FENCE_HOLE_R_OUTER_MM
    < INNER_MARKING_FLANGE_RADIUS_MM,
    "Fence holes must remain inside the top alignment disk."
)

require(
    ACTIVE_WINDOW_FENCE_HOLE_R_OUTER_MM
    + ACTIVE_WINDOW_FENCE_HOLE_RADIUS_MM
    < INNER_MARKING_FLANGE_RADIUS_MM,
    "Top-view fence holes must be fully contained in the alignment disk."
)

require(
    COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM
    + COAXIAL_ALIGNMENT_HOLE_RADIUS_MM
    < INNER_MARKING_FLANGE_RADIUS_MM,
    "Shared sight holes must remain fully inside the 80 mm top alignment disk."
)

_HORIZONTAL_TO_VERTICAL_ANGLE_SEPARATION_DEG = (
    SECTOR_REPEAT_DEG * 0.5 - SIGHT_REL_ANGLE_DEG
)

require(
    _HORIZONTAL_TO_VERTICAL_ANGLE_SEPARATION_DEG >= 4.0,
    "Horizontal and vertical alignment holes are too close angularly."
)

if CYL_FRESNEL_LENS_STOCK_LENGTH_MM < ACTIVE_WALL_HEIGHT_MM:
    print("WARNING: 100 mm legacy lens stock is too short for 100.5 mm active height; external optics required.")


require(
    DEMARCATION_RING_Z_MM - DEMARCATION_RING_AXIAL_WIDTH_MM * 0.5
    > LAST_APERTURE_EDGE_Z,
    "Demarcation ring must stay above the last Nipkow aperture edge."
)

require(
    abs(ENCODER_SECTOR_COUNT * ENCODER_SECTOR_REPEAT_DEG - 360.0) < 1e-8,
    "Encoder sector count/repeat must close to 360 degrees."
)

require(
    abs(TOP_REMAINING_MARGIN_MM - END_MARGIN_MM) < 1e-8,
    "V17 50-row geometry must leave exactly 0.5 mm at top."
)

require(
    abs(
        LED_CHANNEL_WIDTH_MM
        + FRESNEL_FIN_AXIAL_WIDTH_MM
        - ROW_PITCH_MM
    ) < 1e-8,
    "V17 LED channel + row separator must equal 2.0 mm pitch."
)

require(
    abs(END_LED_LIP_WIDTH_MM - 0.50) < 1e-8,
    "Expected 0.5 mm end lip from 1.5 mm LED channels."
)

require(
    INNER_FIN_OUTER_RADIUS_MM < OUTER_DRUM_INNER_RADIUS_MM,
    "Row baffle envelope collides with rotating drum."
)

RADIAL_CLEARANCE_MM = (
    OUTER_DRUM_INNER_RADIUS_MM
    - INNER_FIN_OUTER_RADIUS_MM
)

require(
    OUTER_BASE_THICKNESS_MM >= 4.0,
    "V17.8 drive/encoder disk must be at least 4mm thick. (Legacy arc-mark cutters are inactive.)"
)

require(
    MARKING_DEPTH_MM > INNER_MARKING_FLANGE_THICKNESS_MM,
    "Inner registration markings must fully cut through the flange."
)

require(
    DEMARCATION_RING_SEGMENT_SPAN_DEG < SECTOR_REPEAT_DEG,
    "Demarcation dents must remain segmented within each 36 degree sector."
)

require(
    0.0 < DEMARCATION_DENT_DEPTH_MM < OUTER_WALL_THICKNESS_MM,
    "Demarcation dent depth must stay shallower than the drum wall."
)

require(
    INNER_36_ARC_SLOT_SPAN_DEG < SECTOR_REPEAT_DEG,
    "Inner through-cut sector arcs must leave structural bridges."
)

require(
    INNER_MARKING_FLANGE_RADIUS_MM > OUTER_DRUM_RADIUS_MM,
    "Top alignment disk must project beyond the 76 mm rotating drum."
)

require(
    INNER_TOP_MARK_OUTER_RADIUS_MM < INNER_MARKING_FLANGE_RADIUS_MM,
    "Top-view registration marks must remain inside the alignment disk."
)

require(
    INNER_6_ARC_R_OUTER_MM < INNER_MARKING_FLANGE_RADIUS_MM,
    "Outermost 6 degree arc must remain inside the alignment disk."
)

require(
    ACTIVE_WINDOW_FENCE_HOLE_R_OUTER_MM
    + ACTIVE_WINDOW_FENCE_HOLE_RADIUS_MM
    < INNER_MARKING_FLANGE_RADIUS_MM,
    "Fence through-holes must remain inside the top alignment disk."
)

require(
    ACTIVE_WINDOW_FENCE_HOLE_R_INNER_MM
    - ACTIVE_WINDOW_FENCE_HOLE_RADIUS_MM
    > INNER_CARRIER_RADIUS_MM,
    "Fence through-holes should stay outside the carrier body in top view."
)

# =====================================================================
# ALTERNATE SINGLE-WINDOW LILYGO DEBUG CARRIER (non-touch 1.91in AMOLED)
# =====================================================================
# LILYGO's module is ~60 x 25.5 x 10 mm including connector envelope.
# PCB is ~58.78 x 25.5 mm. These are bounding-box assumptions, not a
# verified STEP-model fixture. Measure actual board + headers before print.
LILYGO_MODULE_AXIAL_MM = 60.0
LILYGO_MODULE_TANGENTIAL_MM = 25.5
LILYGO_MODULE_RADIAL_MM = 10.0
LILYGO_SLOT_AXIAL_EXTRA_MM = 1.5
LILYGO_SLOT_TANGENTIAL_EXTRA_MM = 0.9
LILYGO_SLOT_AZIMUTH_DEG = 18.0  # centre of first nominal 36° sector
LILYGO_BOARD_FRONT_LOCAL_X_MM = 31.9
LILYGO_BOARD_BACK_LOCAL_X_MM = (LILYGO_BOARD_FRONT_LOCAL_X_MM
                                 - LILYGO_MODULE_RADIAL_MM)
LILYGO_BOARD_CENTRE_Z_MM = ACTIVE_WALL_HEIGHT_MM / 2.0
LILYGO_BOARD_BOTTOM_Z_MM = LILYGO_BOARD_CENTRE_Z_MM-LILYGO_MODULE_AXIAL_MM/2
LILYGO_BOARD_TOP_Z_MM = LILYGO_BOARD_CENTRE_Z_MM+LILYGO_MODULE_AXIAL_MM/2
LILYGO_GUIDE_INNER_Y_MM = LILYGO_MODULE_TANGENTIAL_MM/2+0.45
LILYGO_GUIDE_WALL_MM = 1.50
LILYGO_GUIDE_X0_MM = 22.5
LILYGO_GUIDE_X1_MM = 31.3
LILYGO_RETENTION_TAB_X0_MM = 30.2
LILYGO_RETENTION_TAB_X1_MM = 32.25
LILYGO_BOARD_ACTIVE_DISPLAY_AXIAL_MM = 44.22 # visual estimate from prior prototype
LILYGO_BOARD_ACTIVE_DISPLAY_WIDTH_MM = 19.8
LILYGO_CABLE_PORT_RADIUS_MM = 4.0
LILYGO_CABLE_PORT_CENTRE_LOCAL_X_MM = -17.0
LILYGO_CABLE_PORT_CENTRE_LOCAL_Y_MM = 0.0
# The 25.5mm-wide board spans ~43.6deg at its outward front R31.9,
# more than one nominal 36deg sector. Its two 0.5mm walls MUST frame the
# actual slot at +/-30deg relative to the display azimuth, not +/-18deg.
# 60deg between fin axes permits the complete display + guides to remain
# accessible without touching either fin. Exactly TWO walls, not 20.
LILYGO_BAFFLE_COUNT = 2
LILYGO_BAFFLE_TANGENTIAL_WIDTH_MM = 0.50
LILYGO_BAFFLE_HALF_SPAN_DEG = 30.00
LILYGO_BAFFLE_ROOT_RADIUS_MM = SECTOR_BAFFLE_ROOT_RADIUS_MM
LILYGO_BAFFLE_TIP_RADIUS_MM = SECTOR_BAFFLE_TIP_RADIUS_MM

require(ENCODER_SLOTS_PER_SECTOR == 5 and TOTAL_ENCODER_SLOTS == 50,
        'V17.8 needs five slots per sector, total 50')
require(ENCODER_MIN_WEB_APPROX_MM >= 1.20,
        f'Encoder slot bridges too narrow: {ENCODER_MIN_WEB_APPROX_MM:.3f}mm')
require(OUTER_BASE_THICKNESS_MM == 4.0 and
        OUTER_SHELL_BASE_JOIN_OVERLAP_MM >= 1.0,
        'Base thickness/rotor shell overlap must resist drive torsion')
require(HUB_ROOT_GUSSET_PRINT_SLOPE_DEG >= 45.0-1e-6 and
        PRINT_AXIS_TILT_DEG == 0.0,
        'Keep a >=45deg self-supporting gusset in the vertical hub-down print')
require(MOTOR_LOAD_BRIDGE_Z0_MM < ROLLING_LAND_LOWER_Z1_MM and
        MOTOR_LOAD_BRIDGE_Z1_MM < 0.0 and
        MOTOR_LOAD_BRIDGE_Z1_MM > -OUTER_SHELL_BASE_JOIN_OVERLAP_MM and
        MOTOR_LOAD_BRIDGE_R_OUTER_MM < COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM - COAXIAL_ALIGNMENT_HOLE_RADIUS_MM and
        MOTOR_LOAD_BRIDGE_R_INNER_MM < ROLLING_LAND_INNER_RADIUS_MM and
        MOTOR_LOAD_BRIDGE_R_OUTER_MM > ROLLING_LAND_INNER_RADIUS_MM,
        'Bearing load bridge must join the journal, base, guard, shell without blocking aligners')
require(OUTER_HUB_OD_MM == 28.0 and OUTER_HUB_LENGTH_MM == 29.0,
        'Thicker Ø28x29 mm drive stub required')
require(GT2_TOOTH_COUNT == 40 and
        (GT2_ROOT_RADIUS_MM - OUTER_D_BORE_RADIUS_MM) > 9.0,
        '40T pulley must preserve >=9mm radial root wall to D bore')
require(HUB_ROOT_GUSSET_TOP_RADIUS_MM <
        ENCODER_SLOT_CENTER_RADIUS_MM-ENCODER_SLOT_RADIAL_LENGTH_MM/2,
        'Hub root gusset must avoid the radial encoder-slot region.')
require(LILYGO_BOARD_FRONT_LOCAL_X_MM**2 +
        (LILYGO_MODULE_TANGENTIAL_MM/2)**2 <
        (OUTER_DRUM_INNER_RADIUS_MM-1.0)**2,
        'LILYGO board front corners violate >=1mm rotor clearance.')
require(LILYGO_GUIDE_X1_MM**2 +
        (LILYGO_GUIDE_INNER_Y_MM+LILYGO_GUIDE_WALL_MM)**2 <
        (OUTER_DRUM_INNER_RADIUS_MM-1.0)**2,
        'LILYGO guide rails must stay within R35 envelope.')
require(LILYGO_RETENTION_TAB_X1_MM**2 +
        (LILYGO_GUIDE_INNER_Y_MM+0.30)**2 <
        (OUTER_DRUM_INNER_RADIUS_MM-1.0)**2,
        'LILYGO retention tabs require >=1mm rotor running clearance.')
require(LILYGO_BOARD_BOTTOM_Z_MM>5.0 and
        LILYGO_BOARD_TOP_Z_MM<ACTIVE_WALL_HEIGHT_MM-5.0,
        'LILYGO board needs edge clearance from the active region ends.')
# Tangential minimum gap between either debug baffle and wall opening at Rroot.
# The baffle's 0.5mm width is oriented perpendicular to its radius.
_DEBUG_SLOT_TANGENTIAL_HALF_MM = (LILYGO_MODULE_TANGENTIAL_MM +
                                   LILYGO_SLOT_TANGENTIAL_EXTRA_MM) * 0.5
_DEBUG_WALL_NEAREST_Y_MM = (LILYGO_BAFFLE_ROOT_RADIUS_MM *
                            math.sin(math.radians(LILYGO_BAFFLE_HALF_SPAN_DEG))
                            - 0.5*LILYGO_BAFFLE_TANGENTIAL_WIDTH_MM *
                            math.cos(math.radians(LILYGO_BAFFLE_HALF_SPAN_DEG)))
require(LILYGO_BAFFLE_COUNT == 2 and LILYGO_BAFFLE_TANGENTIAL_WIDTH_MM == 0.5,
        'LILYGO has exactly two 0.5mm baffles bordering its single slot.')
require(_DEBUG_WALL_NEAREST_Y_MM > _DEBUG_SLOT_TANGENTIAL_HALF_MM,
        'LILYGO baffle intersects the actual 26.4mm slot wall opening.')
require(LILYGO_BAFFLE_TIP_RADIUS_MM < OUTER_DRUM_INNER_RADIUS_MM,
        'LILYGO baffles would collide with outer drum.')

# V17-specific structural and symmetry checks.
require(ROW_COUNT == 50 and SECTOR_COUNT == 10,
        "V17 must retain 50 rows in 10 mechanical sectors.")
require(abs(ROW_PITCH_MM - 2.0) < 1e-10,
        "V17 row pitch must be 2.0 mm.")
require(abs(APERTURE_DIAMETER_MM - 1.5) < 1e-10,
        "V17 radial bore diameter must be 1.5 mm.")
require(abs(ACTIVE_WALL_HEIGHT_MM - (2*END_MARGIN_MM + APERTURE_DIAMETER_MM + (ROW_COUNT-1)*ROW_PITCH_MM)) < 1e-10,
        "V17 axial hole closure must equal 100.5 mm.")
require(abs(ROW_PITCH_MM - APERTURE_DIAMETER_MM - .5) < 1e-10,
        "V17 axial web between round holes must be 0.5 mm.")
require(abs(LED_CHANNEL_WIDTH_MM - 1.5) < 1e-10,
        "V17 LED channel optical width must equal 1.5 mm.")
require(SECTOR_BOUNDARY_RIDGE_COUNT == SECTOR_COUNT and
        SECTOR_BAFFLES_PER_SECTOR == 1 and
        ARC_BOUNDARY_RIDGE_TANGENTIAL_WIDTH_MM == 0.5,
        "Expect 10 shared integral 0.5mm radial walls on the LED inner.")
require(abs(OUTER_DRUM_INNER_RADIUS_MM - ROW_RING_RADIAL_OUTER_MM - 1.3) < 1e-10,
        "Continuous row-ring tips should retain 1.3 mm rotor clearance.")
require(abs(ROLLING_LAND_AXIAL_WIDTH_MM-10.0)<1e-10 and TOTAL_ENCODER_SLOTS == 50,
        "V17 must retain two 10 mm lands and 60 encoder slots.")
require(SECTOR_BOUNDARY_RIDGE_OFFSET_DEG == 0.0,
        "Shared 36-degree baffles must be at 0, 36, ..., 324 degrees.")
require(abs(SLANT_SWEEP_DEG-32.0)<1e-10,
        "Keep 2-degree clearance from both ends of every 36 degree sector.")
require(VIS_ACTIVE_SECTOR_INDICES == tuple(range(5)) and
        UV_ACTIVE_SECTOR_INDICES == tuple(range(5, 10)),
        "Visible hemisphere must occupy sectors 0..4, UV hemisphere 5..9.")
require(ROW_BAFFLE_CASSETTE_COUNT == 0 and ROW_RING_COUNT == 51 and
        set(ACTIVE_OPTICAL_SECTOR_INDICES) == set(range(SECTOR_COUNT)),
        "One continuous 51-ring assembly remains alongside sector walls.")
require(all((v+5) in UV_ACTIVE_SECTOR_INDICES for v in VIS_ACTIVE_SECTOR_INDICES),
        "Five visible stations must be exactly opposite five UV stations.")
require(SECTOR_BOUNDARY_RIDGE_COUNT == 10 and
        abs(5 * SECTOR_REPEAT_DEG - 180.0) < 1e-10,
        "Five illuminated sectors per hemisphere, ten shared boundary walls.")
require(ROW_BAFFLE_RADIAL_OUTER_MM < OUTER_DRUM_INNER_RADIUS_MM,
        "Row separator tips must clear the rotor.")
require(ROW_BAFFLE_RADIAL_INNER_MM < INNER_CARRIER_RADIUS_MM and
        ROW_BAFFLE_SIDE_RAIL_R0_MM < INNER_CARRIER_RADIUS_MM,
        "Integrated row fins and side rails must overlap the stationary carrier.")
require(ROW_BAFFLE_RADIAL_OUTER_MM <= 35.0,
        "Integrated row fins exceed one millimetre nominal rotor clearance.")
require(COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM - COAXIAL_ALIGNMENT_HOLE_RADIUS_MM
        > OUTER_DRUM_RADIUS_MM,
        "Through-axis datum must be outside outer shell OD radius.")
# The outer rotor always retains 50 bores in EVERY physical sector; the inner
# carrier now also has a matching row-baffle comb in EVERY physical sector.
require(ROW_RING_COUNT == 51 and (ROW_RING_COUNT - 2) == 49,
        "Expected 49 uninterrupted horizontal separators and two lips.")

require(
    abs(OUTER_D_FLAT_X) < OUTER_D_BORE_RADIUS_MM,
    "Outer D-flat invalid."
)

require(
    abs(INNER_D_FLAT_X) < INNER_D_BORE_RADIUS_MM,
    "Inner D-flat invalid."
)

# =====================================================================
# BASIC BLENDER HELPERS
# =====================================================================

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for collection in list(bpy.data.collections):
        if (
            collection.name.startswith("V15_")
            or collection.name.startswith("NIPKOW_")
        ):
            bpy.data.collections.remove(collection)


def deselect_all():
    bpy.ops.object.select_all(action='DESELECT')


def make_active(obj):
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def add_cylinder(
    name,
    radius,
    depth,
    location=(0.0, 0.0, 0.0),
    vertices=128,
):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        end_fill_type='NGON',
        location=location,
    )

    obj = bpy.context.active_object
    obj.name = name
    return obj


def join_objects(objects, active_obj, final_name):
    deselect_all()

    for obj in objects:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = active_obj
    bpy.ops.object.join()

    result = bpy.context.active_object
    result.name = final_name
    return result


def boolean_object(target, cutter, operation, name):
    """
    Apply a single-object Boolean and delete cutter ONLY after success.
    """
    make_active(target)
    bpy.context.view_layer.update()

    modifier = target.modifiers.new(
        name=name,
        type='BOOLEAN',
    )
    modifier.operation = operation
    modifier.solver = BOOLEAN_SOLVER
    modifier.operand_type = 'OBJECT'
    modifier.object = cutter

    try:
        bpy.ops.object.modifier_apply(
            modifier=modifier.name
        )
    except Exception as exc:
        raise RuntimeError(
            f"Boolean failed: {name}; cutter={cutter.name}"
        ) from exc

    bpy.context.view_layer.update()

    if modifier.name in target.modifiers:
        raise RuntimeError(
            f"Boolean modifier did not apply: {name}"
        )

    if cutter.name in bpy.data.objects:
        bpy.data.objects.remove(
            cutter,
            do_unlink=True,
        )


def boolean_collection(target, collection, operation, name):
    """
    V3-style robust collection Boolean.
    """
    make_active(target)
    bpy.context.view_layer.update()

    modifier = target.modifiers.new(
        name=name,
        type='BOOLEAN',
    )
    modifier.operation = operation
    modifier.solver = BOOLEAN_SOLVER
    modifier.operand_type = 'COLLECTION'
    modifier.collection = collection

    try:
        bpy.ops.object.modifier_apply(
            modifier=modifier.name
        )
    except Exception as exc:
        raise RuntimeError(
            f"Collection Boolean failed: {name}; "
            f"cutters={len(collection.objects)}"
        ) from exc

    bpy.context.view_layer.update()

    if modifier.name in target.modifiers:
        raise RuntimeError(
            f"Collection Boolean modifier did not apply: {name}"
        )


def relink_object_only_to_collection(obj, collection):
    if obj.name not in collection.objects:
        collection.objects.link(obj)

    for c in list(obj.users_collection):
        if c != collection:
            c.objects.unlink(obj)


def delete_collection_and_objects(collection):
    for obj in list(collection.objects):
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(
                obj,
                do_unlink=True,
            )

    if collection.name in bpy.data.collections:
        bpy.data.collections.remove(collection)


# =====================================================================
# MESH HELPERS
# =====================================================================

def make_d_prism_cutter(
    name,
    radius,
    flat_x,
    depth,
    z_center,
):
    """
    Closed D-profile prism along Z.
    """
    alpha = math.acos(flat_x / radius)
    arc_steps = 64

    pts = []

    start = alpha
    end = 2.0 * math.pi - alpha

    for i in range(arc_steps + 1):
        t = i / arc_steps
        a = start + t * (end - start)

        pts.append((
            radius * math.cos(a),
            radius * math.sin(a),
        ))

    z0 = z_center - depth * 0.5
    z1 = z_center + depth * 0.5

    n = len(pts)

    verts = (
        [(x, y, z0) for x, y in pts]
        + [(x, y, z1) for x, y in pts]
    )

    faces = []

    faces.append(tuple(reversed(range(n))))
    faces.append(tuple(n + i for i in range(n)))

    for i in range(n):
        j = (i + 1) % n
        faces.append((
            i,
            j,
            n + j,
            n + i,
        ))

    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    bm = bmesh.new()
    bm.from_mesh(mesh)

    bmesh.ops.recalc_face_normals(
        bm,
        faces=list(bm.faces),
    )

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    return obj


def make_annular_sector_prism(
    name,
    r_inner,
    r_outer,
    angle_start_deg,
    angle_end_deg,
    z_bottom,
    z_top,
    segments=20,
):
    """
    Closed annular-sector prism, useful as a shallow engraving cutter.
    """
    require(r_outer > r_inner, "Sector outer radius must exceed inner.")
    require(z_top > z_bottom, "Sector prism z_top must exceed z_bottom.")

    a0 = math.radians(angle_start_deg)
    a1 = math.radians(angle_end_deg)

    verts = []

    # Per angular sample:
    # 0 inner-bottom
    # 1 inner-top
    # 2 outer-bottom
    # 3 outer-top
    for i in range(segments + 1):
        t = i / segments
        a = a0 + t * (a1 - a0)

        ca = math.cos(a)
        sa = math.sin(a)

        verts.extend([
            (r_inner * ca, r_inner * sa, z_bottom),
            (r_inner * ca, r_inner * sa, z_top),
            (r_outer * ca, r_outer * sa, z_bottom),
            (r_outer * ca, r_outer * sa, z_top),
        ])

    faces = []

    for i in range(segments):
        j = i * 4
        k = (i + 1) * 4

        # inner curved face
        faces.append((j + 0, k + 0, k + 1, j + 1))
        # outer curved face
        faces.append((j + 2, j + 3, k + 3, k + 2))
        # bottom
        faces.append((j + 0, j + 2, k + 2, k + 0))
        # top
        faces.append((j + 1, k + 1, k + 3, j + 3))

    # Start cap
    faces.append((0, 1, 3, 2))

    # End cap
    end = segments * 4
    faces.append((end + 0, end + 2, end + 3, end + 1))

    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    bm = bmesh.new()
    bm.from_mesh(mesh)

    bmesh.ops.recalc_face_normals(
        bm,
        faces=list(bm.faces),
    )

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    return obj


def add_xy_segment_box(
    name,
    p0,
    p1,
    tangential_width,
    z_center,
    z_depth,
):
    """Create a vertical rectangular fence along an arbitrary XY segment."""
    x0, y0 = p0
    x1, y1 = p1
    dx = x1 - x0
    dy = y1 - y0
    length = math.hypot(dx, dy)
    require(length > 0.0, "Fence segment must have positive length.")
    angle = math.atan2(dy, dx)

    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=((x0 + x1) * 0.5, (y0 + y1) * 0.5, z_center),
        rotation=(0.0, 0.0, angle),
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.dimensions = (length, tangential_width, z_depth)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def add_active_window_fence_holes_to_collection(
    collection,
    flange_z0,
    flange_z1,
):
    """
    V16 simple alignment: exactly ONE round axial through-hole at each
    shared 36 degree sector boundary.

    These replace the older dotted/compound optical-register structures.

    Count:
      * 10 sector boundaries
      * 1 round hole per boundary
      * 10 holes total

    The cutters intentionally overshoot the top alignment disk in Z so the
    holes are true sight-through holes, not shallow marks.
    """
    count = 0

    z_center = (flange_z0 + flange_z1) * 0.5
    z_depth = (
        (flange_z1 - flange_z0)
        + 2.0 * ACTIVE_WINDOW_FENCE_HOLE_OVERSHOOT_MM
    )

    require(
        z_depth > INNER_MARKING_FLANGE_THICKNESS_MM,
        "Top alignment-hole cutters must fully cross the alignment disk."
    )

    for sector in range(SECTOR_COUNT):
        a_deg = (
            SECTOR_BOUNDARY_RIDGE_OFFSET_DEG
            + sector * SECTOR_REPEAT_DEG
        ) % 360.0
        a = math.radians(a_deg)

        r = ACTIVE_WINDOW_FENCE_HOLE_R_INNER_MM

        x = r * math.cos(a)
        y = r * math.sin(a)

        bpy.ops.mesh.primitive_cylinder_add(
            vertices=48,
            radius=ACTIVE_WINDOW_FENCE_HOLE_RADIUS_MM,
            depth=z_depth,
            end_fill_type='NGON',
            location=(x, y, z_center),
        )

        cutter = bpy.context.active_object
        cutter.name = f"CUT_INNER_TOP_ALIGN_{sector:02d}"

        relink_object_only_to_collection(cutter, collection)
        count += 1

    require(
        count == SECTOR_COUNT,
        "Top alignment-hole count mismatch."
    )

    return count


def create_arc_boundary_ridges():
    """Build exactly ONE 0.5mm wall at each shared 36-degree LED boundary.

    Fin azimuths are 0, 36, 72, 108, 144, 180, 216, 252, 288, 324 deg.
    The sectors on either side SHARE each fin; there is no +/-0.9deg pair.
    The 0deg and 180deg fins partition visible and UV illumination.
    Each fin embeds 0.35mm into the Ø56 carrier and ends at R34.70,
    leaving 1.30mm radial clearance to the rotating drum ID R36.0.
    The ten fins are merged into ONE stationary LED drum mesh object.
    """
    ridges = []
    radial_length = SECTOR_BAFFLE_TIP_RADIUS_MM - SECTOR_BAFFLE_ROOT_RADIUS_MM
    radial_center = 0.5 * (SECTOR_BAFFLE_ROOT_RADIUS_MM +
                           SECTOR_BAFFLE_TIP_RADIUS_MM)
    for boundary in range(SECTOR_COUNT):
        angle_deg = (SECTOR_BOUNDARY_RIDGE_OFFSET_DEG +
                     boundary * SECTOR_REPEAT_DEG) % 360.0
        ridges.append(add_radial_cube_cutter(
            name=f"LED_SHARED_BOUNDARY_{boundary:02d}_0P5",
            angle_deg=angle_deg,
            radial_center=radial_center,
            radial_length=radial_length,
            tangential_width=ARC_BOUNDARY_RIDGE_TANGENTIAL_WIDTH_MM,
            z_center=ACTIVE_WALL_HEIGHT_MM * 0.5,
            z_depth=ACTIVE_WALL_HEIGHT_MM,
        ))
    require(len(ridges) == SECTOR_COUNT == SECTOR_BOUNDARY_RIDGE_COUNT,
            "Exactly ten 0.5mm shared LED sector walls are required.")
    return ridges


def add_radial_cube_cutter(
    name,
    angle_deg,
    radial_center,
    radial_length,
    tangential_width,
    z_center,
    z_depth,
):
    """
    Rectangular cutter whose long XY dimension points radially.
    """
    theta = math.radians(angle_deg)

    x = radial_center * math.cos(theta)
    y = radial_center * math.sin(theta)

    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x, y, z_center),
        rotation=(0.0, 0.0, theta),
    )

    obj = bpy.context.active_object
    obj.name = name

    obj.dimensions = (
        radial_length,
        tangential_width,
        z_depth,
    )

    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True,
    )

    return obj


def add_radial_cylinder_cutter(
    name,
    angle_deg,
    radius_center,
    z,
    cutter_radius,
    cutter_depth,
    vertices=None,
):
    """
    Cylinder with local Z aligned radially.
    """
    if vertices is None:
        vertices = APERTURE_CIRCLE_VERTICES

    theta = math.radians(angle_deg)

    center = Vector((
        radius_center * math.cos(theta),
        radius_center * math.sin(theta),
        z,
    ))

    radial = Vector((
        math.cos(theta),
        math.sin(theta),
        0.0,
    ))

    q = Vector((0.0, 0.0, 1.0)).rotation_difference(radial)

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=cutter_radius,
        depth=cutter_depth,
        end_fill_type='NGON',
        location=center,
        rotation=q.to_euler(),
    )

    obj = bpy.context.active_object
    obj.name = name

    return obj


# =====================================================================
# ANGLE / PUPIL HELPERS
# =====================================================================

def sector_center_angle_deg(sector_index):
    # V17: 0 / 180 degrees are physical separator BOUNDARIES.
    return (sector_index + 0.5) * SECTOR_REPEAT_DEG


def row_relative_angle_deg(row_index):
    """
    Row 0  -> -16 degrees (2 deg inside sector start)
    Row 49 -> +16 degrees (2 deg inside sector end)
    """
    if ROW_COUNT == 1:
        return 0.0

    t = row_index / (ROW_COUNT - 1)

    return (
        -SLANT_SWEEP_DEG * 0.5
        + t * SLANT_SWEEP_DEG
    )


def row_center_z(row_index):
    return FIRST_ROW_CENTER_Z + row_index * ROW_PITCH_MM


# =====================================================================
# OUTER NIPKOW CUTTERS
# =====================================================================

def create_nipkow_aperture_cutter_collection():
    """500 circular, straight-RADIAL tunnels in the rotating wall.

    All cutter axes are normal to the cylindrical shell surface, with ZERO
    tangential or axial tilt.  The 50 positions still form a 32-degree
    stagger inside each 36-degree mechanical sector.
    """
    collection = bpy.data.collections.new("V17_NIPKOW_RADIAL_HOLE_CUTTERS")
    bpy.context.scene.collection.children.link(collection)
    cutter_depth = OUTER_WALL_THICKNESS_MM + 4.0
    require(cutter_depth > OUTER_WALL_THICKNESS_MM,
            "Nipkow cutter must fully span the 2 mm rotating wall.")

    cutter_count = 0
    for sector in range(SECTOR_COUNT):
        for row in range(ROW_COUNT):
            theta_deg = sector_center_angle_deg(sector) + row_relative_angle_deg(row)
            theta = math.radians(theta_deg)
            direction = Vector((math.cos(theta), math.sin(theta), 0.0))
            center = (OUTER_DRUM_RADIUS_MM - OUTER_WALL_THICKNESS_MM * 0.5) * direction
            center.z = row_center_z(row)
            q = Vector((0, 0, 1)).rotation_difference(direction)

            bpy.ops.mesh.primitive_cylinder_add(
                vertices=APERTURE_CIRCLE_VERTICES,
                radius=APERTURE_RADIUS_MM,
                depth=cutter_depth,
                end_fill_type='NGON',
                location=center,
                rotation=q.to_euler(),
            )
            cutter = bpy.context.active_object
            cutter.name = f"CUT_NIP_RADIAL_S{sector:02d}_R{row:02d}"
            relink_object_only_to_collection(cutter, collection)
            cutter_count += 1

    expected = SECTOR_COUNT * ROW_COUNT
    require(cutter_count == expected and len(collection.objects) == expected,
            f"Expected {expected} radial apertures, got {cutter_count}.")
    print(f"  V17 true radial hole cutters: {cutter_count} (0 deg tilt)")
    return collection

# =====================================================================
# OUTER SIGHT-HOLE + DEMARCATION CUTTERS
# =====================================================================

def create_outer_demarcation_ring_collection():
    """
    Ten balanced SHALLOW external arc dents marking the end of the active
    Nipkow region.

    Unlike the older V15/V16 through-slot version, these cutters enter only
    DEMARCATION_DENT_DEPTH_MM into the outside of the 2 mm shell.  The inner
    wall surface remains continuous, eliminating the circumferential
    through-wall stress breakpoint.

    The dent is still segmented 30° within each 36° sector.
    """
    collection = bpy.data.collections.new(
        "V16_OUTER_DEMARCATION_SHALLOW_DENT_CUTTERS"
    )
    bpy.context.scene.collection.children.link(collection)

    # Cut from just outside the drum OD inward by only the requested dent depth.
    r_outer = (
        OUTER_DRUM_RADIUS_MM
        + DEMARCATION_RING_RADIAL_OVERSHOOT_MM
    )
    r_inner = (
        OUTER_DRUM_RADIUS_MM
        - DEMARCATION_DENT_DEPTH_MM
    )

    z0 = (
        DEMARCATION_RING_Z_MM
        - DEMARCATION_RING_AXIAL_WIDTH_MM * 0.5
    )
    z1 = (
        DEMARCATION_RING_Z_MM
        + DEMARCATION_RING_AXIAL_WIDTH_MM * 0.5
    )

    require(
        r_inner > OUTER_DRUM_INNER_RADIUS_MM,
        "Shallow demarcation dent must not reach the inner drum surface."
    )

    for sector in range(SECTOR_COUNT):
        center = sector_center_angle_deg(sector)

        cutter = make_annular_sector_prism(
            name=f"CUT_OUTER_DEMARCATION_DENT_{sector:02d}",
            r_inner=r_inner,
            r_outer=r_outer,
            angle_start_deg=(
                center - DEMARCATION_RING_SEGMENT_SPAN_DEG * 0.5
            ),
            angle_end_deg=(
                center + DEMARCATION_RING_SEGMENT_SPAN_DEG * 0.5
            ),
            z_bottom=z0,
            z_top=z1,
            segments=ARC_SEGMENTS,
        )

        relink_object_only_to_collection(cutter, collection)

    require(
        len(collection.objects) == SECTOR_COUNT,
        "Demarcation shallow-dent cutter count mismatch."
    )

    return collection


# =====================================================================
# THROUGH-CUT REGISTRATION MARKING CUTTERS
# =====================================================================

def add_top_surface_tick_to_collection(
    collection,
    name,
    angle_deg,
    r_inner,
    r_outer,
    surface_z,
    width=MARKING_TICK_WIDTH_MM,
):
    radial_length = r_outer - r_inner
    radial_center = (r_inner + r_outer) * 0.5

    z_depth = (
        MARKING_DEPTH_MM
        + MARKING_BOOLEAN_OVERSHOOT_MM
    )

    z_center = (
        surface_z
        + MARKING_BOOLEAN_OVERSHOOT_MM * 0.5
        - MARKING_DEPTH_MM * 0.5
    )

    cutter = add_radial_cube_cutter(
        name,
        angle_deg,
        radial_center,
        radial_length,
        width,
        z_center,
        z_depth,
    )

    relink_object_only_to_collection(
        cutter,
        collection,
    )


def add_top_surface_arc_to_collection(
    collection,
    name,
    center_angle_deg,
    span_deg,
    r_inner,
    r_outer,
    surface_z,
):
    cutter = make_annular_sector_prism(
        name=name,
        r_inner=r_inner,
        r_outer=r_outer,
        angle_start_deg=center_angle_deg - span_deg * 0.5,
        angle_end_deg=center_angle_deg + span_deg * 0.5,
        z_bottom=surface_z - MARKING_DEPTH_MM,
        z_top=surface_z + MARKING_BOOLEAN_OVERSHOOT_MM,
        segments=ARC_SEGMENTS,
    )

    relink_object_only_to_collection(
        cutter,
        collection,
    )


def create_outer_base_marking_collection():
    """
    Symmetric THROUGH-CUT markings on outer rotating base.

    No unique carved HOME mark is allowed on the rotor.
    Every removed feature repeats with exact 36 degree symmetry.
    """
    collection = bpy.data.collections.new(
        "V15_OUTER_BASE_MARKINGS"
    )
    bpy.context.scene.collection.children.link(collection)

    surface_z = 0.0

    # 32-degree optical arc + 6-degree precision arc repeated in all sectors.
    for sector in range(SECTOR_COUNT):
        c = sector_center_angle_deg(sector)

        add_top_surface_arc_to_collection(
            collection,
            f"CUT_OUTER_32_ARC_{sector:02d}",
            c,
            LED_ACTIVE_ARC_DEG,
            OUTER_32_ARC_R_INNER_MM,
            OUTER_32_ARC_R_OUTER_MM,
            surface_z,
        )

        add_top_surface_arc_to_collection(
            collection,
            f"CUT_OUTER_6_ARC_{sector:02d}",
            c,
            PRECISION_GATE_DEG,
            OUTER_6_ARC_R_INNER_MM,
            OUTER_6_ARC_R_OUTER_MM,
            surface_z,
        )

    # Sector-center ticks.
    for sector in range(SECTOR_COUNT):
        c = sector_center_angle_deg(sector)

        add_top_surface_tick_to_collection(
            collection,
            f"CUT_MARK_CENTER_{sector:02d}",
            c,
            OUTER_MARK_INNER_RADIUS_MM,
            OUTER_MARK_OUTER_RADIUS_MM,
            surface_z,
            width=1.00,
        )

    # 36-degree sector boundaries: one unique boundary every 36 degrees.
    for sector in range(SECTOR_COUNT):
        a = (
            sector_center_angle_deg(sector)
            + SECTOR_REPEAT_DEG * 0.5
        )

        add_top_surface_tick_to_collection(
            collection,
            f"CUT_MARK_36_BOUNDARY_{sector:02d}",
            a,
            33.8,
            OUTER_MARK_OUTER_RADIUS_MM,
            surface_z,
            width=1.00,
        )

    # 32-degree optical boundaries, symmetric +/- 16.0.
    for sector in range(SECTOR_COUNT):
        c = sector_center_angle_deg(sector)

        for side_index, da in enumerate(
            (-LED_ACTIVE_HALF_ARC_DEG, LED_ACTIVE_HALF_ARC_DEG)
        ):
            add_top_surface_tick_to_collection(
                collection,
                f"CUT_MARK_32_{sector:02d}_{side_index}",
                c + da,
                34.0,
                37.0,
                surface_z,
                width=0.80,
            )

    # Precision gate boundaries, symmetric +/- 3.
    for sector in range(SECTOR_COUNT):
        c = sector_center_angle_deg(sector)

        for side_index, da in enumerate(
            (-PRECISION_HALF_GATE_DEG, PRECISION_HALF_GATE_DEG)
        ):
            add_top_surface_tick_to_collection(
                collection,
                f"CUT_MARK_6_{sector:02d}_{side_index}",
                c + da,
                35.2,
                36.8,
                surface_z,
                width=0.70,
            )

    return collection


def create_inner_flange_marking_collection(flange_top_z):
    """
    Create the ten simple top alignment sight holes.

    There is exactly one round through-hole at every shared 36° boundary.
    No dotted traces, arcs, ticks, chevrons, or compound registration glyphs.
    """
    collection = bpy.data.collections.new(
        "V16_INNER_TOP_ALIGNMENT_HOLES"
    )
    bpy.context.scene.collection.children.link(collection)

    flange_z1 = flange_top_z
    flange_z0 = flange_top_z - INNER_MARKING_FLANGE_THICKNESS_MM

    hole_count = add_active_window_fence_holes_to_collection(
        collection,
        flange_z0,
        flange_z1,
    )

    require(
        hole_count == SECTOR_COUNT,
        "Simple top alignment-hole count mismatch."
    )

    return collection


# =====================================================================
# INNER FRESNEL-LIKE SEPARATOR FINS
# =====================================================================

def make_closed_annular_row_ring(name, r_inner, r_outer, z0, z1):
    """One truly circular, closed annular prism (avoids 360° sector endcaps).

    Radial root R27.65 penetrates Ø56 carrier wall by 0.35 mm.
    The 51 rings are intermediate builder objects and join ONE inner drum.
    """
    require(0 < r_inner < r_outer < OUTER_DRUM_INNER_RADIUS_MM,
            'Invalid annular-row radial envelope')
    require(z1 > z0, 'Invalid row-ring thickness')
    n = DRUM_CIRCLE_VERTICES
    vv = []
    for i in range(n):
        a = (2.0*math.pi*i)/n
        c, q = math.cos(a), math.sin(a)
        vv.extend([(r_inner*c,r_inner*q,z0),(r_outer*c,r_outer*q,z0),
                   (r_inner*c,r_inner*q,z1),(r_outer*c,r_outer*q,z1)])
    ff=[]
    for i in range(n):
        j=(i+1)%n
        a,b=i*4,j*4
        ff.extend([(a,a+1,b+1,b), (a+2,b+2,b+3,a+3),
                   (a,b,b+2,a+2), (a+1,a+3,b+3,b+1)])
    mesh=bpy.data.meshes.new(name+'_MESH')
    mesh.from_pydata(vv,[],ff)
    mesh.update()
    bm=bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(mesh); bm.free()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    return ob


def create_continuous_horizontal_row_separators():
    """49 full-circumference 0.5mm rings + 2 end lips.

    These intersect ten SHARED radial 0.5mm sector baffles to form a grid.
    Crosstalk can still pass via the 1.3mm rotor-to-fin radial gap.
    FDM WARNING: 6.7 mm radial overhangs on 0.5 mm rings are very difficult
    to print without supports. Use slicer inspection and test coupon.
    """
    specs=[(0.0, END_LED_LIP_WIDTH_MM, 'BOTTOM')]
    for i in range(ROW_COUNT-1):
        zmid=row_center_z(i)+ROW_PITCH_MM*0.5
        specs.append((zmid-ROW_SEPARATOR_AXIAL_WIDTH_MM*0.5,
                      zmid+ROW_SEPARATOR_AXIAL_WIDTH_MM*0.5,f'ROW_{i:02d}'))
    specs.append((ACTIVE_WALL_HEIGHT_MM-END_LED_LIP_WIDTH_MM,
                  ACTIVE_WALL_HEIGHT_MM,'TOP'))
    assert len(specs)==ROW_RING_COUNT
    return [make_closed_annular_row_ring('ROW_RING_'+tag,
                ROW_RING_RADIAL_INNER_MM,ROW_RING_RADIAL_OUTER_MM,z0,z1)
            for z0,z1,tag in specs]

# =====================================================================
# OUTER HORIZONTAL / RADIAL SIGHT HOLES
# =====================================================================

def create_outer_horizontal_sight_hole_collection():
    """
    One clean circumferential row of ten radial through-holes in the outer
    drum collar, matching the inner-drum horizontal holes exactly.
    """
    collection = bpy.data.collections.new(
        "V16_OUTER_HORIZONTAL_SIGHT_CUTTERS"
    )
    bpy.context.scene.collection.children.link(collection)

    radius_mid = (
        OUTER_DRUM_RADIUS_MM + OUTER_DRUM_INNER_RADIUS_MM
    ) * 0.5

    cutter_depth = OUTER_WALL_THICKNESS_MM + 4.0
    require(
        cutter_depth > OUTER_WALL_THICKNESS_MM,
        "Outer horizontal sight cutter must fully cross the drum wall."
    )

    count = 0

    for sector in range(SECTOR_COUNT):
        a = sector_center_angle_deg(sector) + SIGHT_REL_ANGLE_DEG

        for z in SIGHT_Z_LEVELS_MM:
            cutter = add_radial_cylinder_cutter(
                f"CUT_OUTER_HORIZONTAL_SIGHT_{sector:02d}_{count:02d}",
                a,
                radius_mid,
                z,
                SIGHT_HOLE_RADIUS_MM,
                cutter_depth,
            )
            relink_object_only_to_collection(cutter, collection)
            count += 1

    require(
        count == SECTOR_COUNT * len(SIGHT_Z_LEVELS_MM),
        "Outer horizontal sight-hole count mismatch."
    )

    return collection


# =====================================================================
# INNER SIGHT HOLES
# =====================================================================

def create_inner_sight_hole_collection():
    """One circumferential row of ten holes matching the rotor sectors."""
    collection = bpy.data.collections.new(
        "V16_INNER_SIGHT_THROUGH_CUTTERS"
    )
    bpy.context.scene.collection.children.link(collection)

    radius_mid = (INNER_CARRIER_RADIUS_MM + INNER_CARRIER_INNER_RADIUS_MM) * 0.5
    # Deliberately overshoot both radial wall faces: these are true holes.
    cutter_depth = INNER_CARRIER_WALL_THICKNESS_MM + 4.0
    require(
        cutter_depth > INNER_CARRIER_WALL_THICKNESS_MM,
        "Inner sight-hole cutter must fully cross the carrier wall."
    )
    count = 0

    for sector in range(SECTOR_COUNT):
        a = sector_center_angle_deg(sector) + SIGHT_REL_ANGLE_DEG
        for z in SIGHT_Z_LEVELS_MM:
            cutter = add_radial_cylinder_cutter(
                f"CUT_INNER_SIGHT_{sector:02d}_{count:02d}",
                a, radius_mid, z, SIGHT_HOLE_RADIUS_MM, cutter_depth,
            )
            relink_object_only_to_collection(cutter, collection)
            count += 1

    require(
        count == SECTOR_COUNT * len(SIGHT_Z_LEVELS_MM),
        "Inner sight-hole count mismatch."
    )
    return collection





# =====================================================================
# V16 ROLLING-LAND HELPERS
# =====================================================================

def create_coaxial_alignment_cutters(name, z0, z1):
    """
    Create the ten shared vertical alignment cutters at exactly the same XY
    positions used by the inner top alignment disk.

    These are used on the OUTER rotor after its components are joined so the
    top-view sight path is not blocked by the far rolling land, collar, or any
    other rotating geometry.
    """
    require(z1 > z0, "Coaxial alignment cutter Z span must be positive.")

    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)

    z_center = 0.5 * (z0 + z1)
    z_depth = (z1 - z0) + 2.0 * COAXIAL_ALIGNMENT_CUT_OVERSHOOT_MM

    for sector in range(SECTOR_COUNT):
        a_deg = (
            SECTOR_BOUNDARY_RIDGE_OFFSET_DEG
            + sector * SECTOR_REPEAT_DEG
        ) % 360.0
        a = math.radians(a_deg)

        x = COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM * math.cos(a)
        y = COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM * math.sin(a)

        bpy.ops.mesh.primitive_cylinder_add(
            vertices=48,
            radius=COAXIAL_ALIGNMENT_HOLE_RADIUS_MM,
            depth=z_depth,
            end_fill_type='NGON',
            location=(x, y, z_center),
        )

        cutter = bpy.context.active_object
        cutter.name = f"CUT_COAXIAL_ALIGN_{sector:02d}"
        relink_object_only_to_collection(cutter, collection)

    require(
        len(collection.objects) == COAXIAL_ALIGNMENT_HOLE_COUNT,
        "Coaxial alignment-hole cutter count mismatch."
    )

    return collection



def create_rolling_land(name, z0, z1, alignment_face):
    """One Ø80 × 10 mm bearing journal; ten holes will be drilled AFTER joining.

    Do not use blind pockets: they were invisible from the far end of the
    stationary flange and hid the intended registration pattern. A single
    shared post-join axial cut also clears any overlapping journal/guard
    geometry and can be checked as one straight through-line.
    """
    require(abs((z1-z0)-ROLLING_LAND_AXIAL_WIDTH_MM)<1e-9,
            "Journal axial width must equal 10 mm.")
    require(alignment_face in ('LOWER','UPPER'), "Bad journal side.")
    zc=(z0+z1)*0.5
    land=add_cylinder(name,ROLLING_LAND_OUTER_RADIUS_MM,z1-z0,
                      location=(0.0,0.0,zc),vertices=DRUM_CIRCLE_VERTICES)
    cavity=add_cylinder('CUT_'+name+'_HOLLOW',ROLLING_LAND_INNER_RADIUS_MM,
                        (z1-z0)+1.0, location=(0.0,0.0,zc),
                        vertices=DRUM_CIRCLE_VERTICES)
    boolean_object(land,cavity,'DIFFERENCE','Hollow_'+name)
    return land


def create_bearing_guard(name, z0, z1):
    """Ø84.2 × 2 mm inner-race retention shoulder.

    Datum holes are cut from the WHOLE joined rotor in a single final
    operation so no later journal union can refill or cover them.
    """
    require(abs((z1-z0)-BEARING_GUARD_AXIAL_WIDTH_MM)<1e-9,
            'Bearing-guard width must equal 2 mm.')
    zc=(z0+z1)*0.5
    guard=add_cylinder(name,BEARING_GUARD_OUTER_RADIUS_MM,z1-z0,
                       location=(0.0,0.0,zc),vertices=DRUM_CIRCLE_VERTICES)
    cavity=add_cylinder('CUT_'+name+'_HOLLOW',BEARING_GUARD_INNER_RADIUS_MM,
                        (z1-z0)+1.0, location=(0.0,0.0,zc),
                        vertices=DRUM_CIRCLE_VERTICES)
    boolean_object(guard,cavity,'DIFFERENCE','Hollow_'+name)
    return guard


def gt2_tooth_outer_radius(angle_rad):
    """Approximate rounded 2GT outside profile, repeated every 2 mm pitch.

    Continuous radii: tooth-tip at the centre of each tooth (u=0), groove
    roots halfway between teeth (u=0.5); smooth cosine fillets on flanks.
    This is a *print-fit starting approximation*, not a manufacturer-issued
    conjugate GT2 tooth drawing. Use real-belt backlash/fit calibration.
    """
    phase = (angle_rad * GT2_TOOTH_COUNT / (2.0 * math.pi) + 0.5) % 1.0 - 0.5
    u = abs(phase)
    if u <= 0.13:
        depth_fraction = 0.0
    elif u >= 0.43:
        depth_fraction = 1.0
    else:
        t = (u - 0.13) / 0.30
        depth_fraction = (1.0 - math.cos(math.pi * t)) * 0.5
    return GT2_TIP_RADIUS_MM - GT2_GROOVE_DEPTH_MM * depth_fraction


def make_gt2_tooth_band_cutter(name):
    """Watertight 360° annular cutting shell for a 40T/2 mm pulley.

    Its toothed INNER radius removes the original Ø18 hub surface outside
    the desired profile. The outer cutter radius extends beyond hub surface.
    Cutter is only 6.4 mm high in Z; the two retaining flanges are separate
    annular overlaps, applied AFTER tooth cutting.
    """
    samples = GT2_TOOTH_COUNT * GT2_PROFILE_SAMPLES_PER_TOOTH
    assert samples % GT2_TOOTH_COUNT == 0
    vertices = []
    for i in range(samples):
        a = 2.0 * math.pi * i / samples
        cs, sn = math.cos(a), math.sin(a)
        ri, ro = gt2_tooth_outer_radius(a), GT2_CUTTER_OUTER_RADIUS_MM
        vertices.extend([
            (ri*cs, ri*sn, GT2_TOOTH_Z0_MM),
            (ro*cs, ro*sn, GT2_TOOTH_Z0_MM),
            (ri*cs, ri*sn, GT2_TOOTH_Z1_MM),
            (ro*cs, ro*sn, GT2_TOOTH_Z1_MM),
        ])
    faces=[]
    for i in range(samples):
        j=(i+1)%samples
        a,b=4*i,4*j
        faces.extend([
            (a,b,b+1,a+1),          # lower plane -Z
            (a+2,a+3,b+3,b+2),      # upper plane +Z
            (a,a+2,b+2,b),          # inner cut wall -R
            (a+1,b+1,b+3,a+3),      # outer cut wall +R
        ])
    mesh=bpy.data.meshes.new(name+'_MESH')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm=bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def create_gt2_retaining_flange(name, z0, z1):
    """Integral printable Ø32 x 1 mm belt-retaining annulus around D hub.

    Annular inner radius R12.5 mm overlaps the solid hub (R14 mm),
    and leaves the existing D-shaft bore open after joining.
    """
    require(z1>z0, 'Invalid GT2 flange height')
    zc=(z0+z1)*0.5
    flange=add_cylinder(name, GT2_FLANGE_OUTER_RADIUS_MM, z1-z0,
                        location=(0,0,zc), vertices=DRUM_CIRCLE_VERTICES)
    cavity=add_cylinder('CUT_'+name+'_INSIDE', GT2_FLANGE_INNER_RADIUS_MM,
                        z1-z0+1.0,location=(0,0,zc),vertices=DRUM_CIRCLE_VERTICES)
    boolean_object(flange,cavity,'DIFFERENCE','Hollow_'+name)
    return flange


# =====================================================================
# BUILD OUTER ROTATING DRUM
# =====================================================================

def create_motor_bearing_load_bridge():
    """Annular inner reinforcement between journal, shoulder, base, shell.

    All thickness is inside R37.9; R38.05 begins the nearest alignment
    cutter, preserving the existing Ø1.5 mm sightlines. Created as ONE
    builder mesh and joined with the common rotor; real mesh-union must be
    inspected in Blender/slicer before considering this a safe load path.
    """
    z0,z1=MOTOR_LOAD_BRIDGE_Z0_MM,MOTOR_LOAD_BRIDGE_Z1_MM
    zc=(z0+z1)*0.5
    ring=add_cylinder('MOTOR_JOURNAL_TO_BASE_INNER_REINFORCEMENT',
                      MOTOR_LOAD_BRIDGE_R_OUTER_MM,z1-z0,
                      location=(0.0,0.0,zc),vertices=DRUM_CIRCLE_VERTICES)
    hole=add_cylinder('CUT_MOTOR_LOAD_BRIDGE_CAVITY',
                      MOTOR_LOAD_BRIDGE_R_INNER_MM,z1-z0+1.0,
                      location=(0.0,0.0,zc),vertices=DRUM_CIRCLE_VERTICES)
    boolean_object(ring,hole,'DIFFERENCE','Hollow_motor_bearing_bridge')
    return ring


def create_outer_drum():
    print("")
    print("Building OUTER V17 50-channel rotating drum...")

    # --------------------------------------------------------------
    # 1) 106.5 mm tall hollow shell (100.5 mm active + 6 mm band).
    # --------------------------------------------------------------
    shell = add_cylinder(
        "OUTER_SHELL_SOLID",
        radius=OUTER_DRUM_RADIUS_MM,
        depth=TOTAL_CYLINDER_HEIGHT_MM + OUTER_SHELL_BASE_JOIN_OVERLAP_MM,
        location=(
            0.0,
            0.0,
            (TOTAL_CYLINDER_HEIGHT_MM - OUTER_SHELL_BASE_JOIN_OVERLAP_MM) * 0.5,
        ),
        vertices=DRUM_CIRCLE_VERTICES,
    )

    cavity = add_cylinder(
        "CUT_OUTER_SHELL_CAVITY",
        radius=OUTER_DRUM_INNER_RADIUS_MM,
        depth=TOTAL_CYLINDER_HEIGHT_MM + OUTER_SHELL_BASE_JOIN_OVERLAP_MM + 2.0,
        location=(
            0.0,
            0.0,
            TOTAL_CYLINDER_HEIGHT_MM * 0.5,
        ),
        vertices=DRUM_CIRCLE_VERTICES,
    )

    boolean_object(
        shell,
        cavity,
        'DIFFERENCE',
        "Hollow_outer_shell",
    )

    # --------------------------------------------------------------
    # 2) 2 mm separate expanded closed base.
    # --------------------------------------------------------------
    base = add_cylinder(
        "OUTER_EXPANDED_BASE",
        radius=OUTER_BASE_RADIUS_MM,
        depth=OUTER_BASE_THICKNESS_MM,
        location=(
            0.0,
            0.0,
            -OUTER_BASE_THICKNESS_MM * 0.5,
        ),
        vertices=DRUM_CIRCLE_VERTICES,
    )

    # --------------------------------------------------------------
    # 3) D-shaft hub.
    # --------------------------------------------------------------
    hub = add_cylinder(
        "OUTER_D_SHAFT_HUB",
        radius=OUTER_HUB_RADIUS_MM,
        depth=OUTER_HUB_LENGTH_MM + OUTER_HUB_BASE_AXIAL_OVERLAP_MM,
        location=(
            0.0,
            0.0,
            -OUTER_BASE_THICKNESS_MM
            - OUTER_HUB_LENGTH_MM * 0.5
            + OUTER_HUB_BASE_AXIAL_OVERLAP_MM * 0.5,
        ),
        vertices=128,
    )

    # --------------------------------------------------------------
    # 3b) Integral frustum/gusset spreads hub torque into the thin base.
    # The 40T pulley retains a much thicker root than the old 28T waist.
    # --------------------------------------------------------------
    bpy.ops.mesh.primitive_cone_add(
        vertices=128,
        radius1=OUTER_HUB_RADIUS_MM,
        radius2=HUB_ROOT_GUSSET_TOP_RADIUS_MM,
        depth=HUB_ROOT_GUSSET_HEIGHT_MM,
        location=(0.0,0.0,-OUTER_BASE_THICKNESS_MM
                  -0.5*HUB_ROOT_GUSSET_HEIGHT_MM
                  +HUB_ROOT_GUSSET_BASE_OVERLAP_MM),
    )
    gusset=bpy.context.active_object
    gusset.name='OUTER_D_HUB_ROOT_GUSSET'

    # --------------------------------------------------------------
    # 4) D bore through base, hub AND the gusset.
    # --------------------------------------------------------------
    bore_bottom = (
        -OUTER_BASE_THICKNESS_MM
        - OUTER_HUB_LENGTH_MM
        - 1.0
    )
    bore_top = 1.0

    bore_depth = bore_top - bore_bottom
    bore_center = (bore_top + bore_bottom) * 0.5

    cutter = make_d_prism_cutter(
        "CUT_OUTER_D_BORE_BASE",
        OUTER_D_BORE_RADIUS_MM,
        OUTER_D_FLAT_X,
        bore_depth,
        bore_center,
    )

    boolean_object(
        base,
        cutter,
        'DIFFERENCE',
        "Cut_outer_D_bore_base",
    )

    cutter = make_d_prism_cutter(
        "CUT_OUTER_D_BORE_HUB",
        OUTER_D_BORE_RADIUS_MM,
        OUTER_D_FLAT_X,
        bore_depth,
        bore_center,
    )

    boolean_object(
        hub,
        cutter,
        'DIFFERENCE',
        "Cut_outer_D_bore_hub",
    )

    cutter=make_d_prism_cutter('CUT_OUTER_D_BORE_GUSSET',
                                OUTER_D_BORE_RADIUS_MM,OUTER_D_FLAT_X,
                                bore_depth,bore_center)
    boolean_object(gusset,cutter,'DIFFERENCE','Cut_outer_D_bore_gusset')

    # V17.3: true CIRCUMFERENTIAL TEETH rather than a smooth V-groove.
    # The GT2-style tooth band stays fully outside the adjacent bearing.
    tooth_cutter = make_gt2_tooth_band_cutter(
        'CUT_DRIVE_STUB_40T_2MM_GT2_TOOTH_PROFILE')
    boolean_object(hub, tooth_cutter, 'DIFFERENCE',
                   'Cut_drive_stub_40T_GT2_timing_teeth')
    flange_outer = create_gt2_retaining_flange(
        'GT2_OUTBOARD_FLANGE', GT2_OUTBOARD_FLANGE_Z0_MM, GT2_TOOTH_Z0_MM)
    flange_inner = create_gt2_retaining_flange(
        'GT2_INBOARD_FLANGE', GT2_TOOTH_Z1_MM, GT2_INBOARD_FLANGE_Z1_MM)

    # --------------------------------------------------------------
    # 5) V13 progressive rotational encoder.
    # --------------------------------------------------------------
    print("  Cutting 50 V17.8 progressive optical encoder slots...")

    encoder_index = 0

    for sector in range(ENCODER_SECTOR_COUNT):
        sector_start = (
            sector * ENCODER_SECTOR_REPEAT_DEG
        )

        first_angle = (
            sector_start
            + ENCODER_SECTOR_MARGIN_DEG
        )

        for i in range(ENCODER_SLOTS_PER_SECTOR):
            t = (
                i
                / (ENCODER_SLOTS_PER_SECTOR - 1)
            )

            angle_deg = (
                first_angle
                + i * ENCODER_SLOT_ANGLE_STEP_DEG
            )

            width_mm = (
                ENCODER_SLOT_MAX_WIDTH_MM
                + t * (
                    ENCODER_SLOT_MIN_WIDTH_MM
                    - ENCODER_SLOT_MAX_WIDTH_MM
                )
            )

            cutter = add_radial_cube_cutter(
                f"CUT_ENCODER_{encoder_index:03d}",
                angle_deg,
                ENCODER_SLOT_CENTER_RADIUS_MM,
                ENCODER_SLOT_RADIAL_LENGTH_MM,
                width_mm,
                -OUTER_BASE_THICKNESS_MM * 0.5,
                (
                    OUTER_BASE_THICKNESS_MM
                    + 2.0 * ENCODER_SLOT_Z_OVERSHOOT_MM
                ),
            )

            boolean_object(
                base,
                cutter,
                'DIFFERENCE',
                f"Cut_encoder_{encoder_index:03d}",
            )

            encoder_index += 1

    require(
        encoder_index == TOTAL_ENCODER_SLOTS,
        "Encoder slot count mismatch."
    )

    # --------------------------------------------------------------
    # 6) No decorative/optical registration glyphs in V16.
    # Alignment is intentionally reduced to simple round holes only.
    # --------------------------------------------------------------

    # --------------------------------------------------------------
    # 7) 500 straight radial Nipkow bores.
    # --------------------------------------------------------------
    print("  Creating V17 straight radial Nipkow hole cutters...")

    nipkow_collection = (
        create_nipkow_aperture_cutter_collection()
    )

    print(
        "  Applying one V3-style collection Boolean "
        f"with {len(nipkow_collection.objects)} cutters..."
    )

    boolean_collection(
        shell,
        nipkow_collection,
        'DIFFERENCE',
        "Cut_all_V17_radial_Nipkow_holes",
    )

    delete_collection_and_objects(nipkow_collection)

    # --------------------------------------------------------------
    # 8) Segmented circumferential demarcation DENT.
    #
    # This is now only a 0.35 mm-deep external groove, not a through-wall
    # slit, so the 2 mm shell remains structurally continuous.
    # --------------------------------------------------------------
    print("  Cutting shallow segmented demarcation dent...")
    demarcation_collection = create_outer_demarcation_ring_collection()
    boolean_collection(
        shell, demarcation_collection, 'DIFFERENCE',
        "Cut_outer_demarcation_shallow_dents",
    )
    delete_collection_and_objects(demarcation_collection)

    # --------------------------------------------------------------
    # 9) ONE clean horizontal/radial alignment-hole row.
    #
    # This matches the existing inner-drum horizontal row.
    # It remains separate from the vertical/top coaxial hole system.
    # --------------------------------------------------------------
    print("  Cutting one clean outer horizontal sight-hole row...")

    horizontal_sight_collection = (
        create_outer_horizontal_sight_hole_collection()
    )

    boolean_collection(
        shell,
        horizontal_sight_collection,
        'DIFFERENCE',
        "Cut_outer_horizontal_sight_holes",
    )

    delete_collection_and_objects(horizontal_sight_collection)

    # --------------------------------------------------------------
    # 10) Two 10 mm bearing journals, each with a 2 mm INNER-RACE shoulder.
    # V17.4: ten through-registration holes through BOTH collar+guard pairs,
    # aligned at R38.8 and 0,36,...324 degrees with the stationary flange.
    # The holes are applied to the whole joined rotor later.
    # --------------------------------------------------------------
    print("  Creating 2 x 10 mm bearing seats and two 2 mm shoulders...")
    guard_lower = create_bearing_guard(
        'BEARING_GUARD_MOTOR_SIDE',
        BEARING_GUARD_LOWER_Z0_MM,
        BEARING_GUARD_LOWER_Z1_MM)
    guard_upper = create_bearing_guard(
        'BEARING_GUARD_FAR_SIDE',
        BEARING_GUARD_UPPER_Z0_MM,
        BEARING_GUARD_UPPER_Z1_MM)

    rolling_land_lower = create_rolling_land(
        "ROLLING_LAND_MOTOR_SIDE",
        ROLLING_LAND_LOWER_Z0_MM,
        ROLLING_LAND_LOWER_Z1_MM,
        alignment_face='LOWER',
    )

    rolling_land_upper = create_rolling_land(
        "ROLLING_LAND_FAR_SIDE",
        ROLLING_LAND_UPPER_Z0_MM,
        ROLLING_LAND_UPPER_Z1_MM,
        alignment_face='UPPER',
    )

    # --------------------------------------------------------------
    # V17.8: reinforce the transition journal -> shoulder -> base -> shell.
    # The 2mm shoulder and 10mm journal remain unchanged outside.
    # --------------------------------------------------------------
    motor_load_bridge = create_motor_bearing_load_bridge()

    # --------------------------------------------------------------
    # 11) Join into one outer PRINT object.
    # Structural Boolean UNION is deliberately avoided because earlier
    # versions showed collapse problems. Meshes overlap/touch and modern
    # slicers normally merge them.
    # --------------------------------------------------------------
    outer = join_objects(
        [
            shell,
            base,
            hub,
            gusset,
            flange_outer,
            flange_inner,
            guard_lower,
            rolling_land_lower,
            motor_load_bridge,
            guard_upper,
            rolling_land_upper,
        ],
        shell,
        "OUTER_DRUM_PRINTABLE",
    )

    # --------------------------------------------------------------
    # V17.4 ONE POST-JOIN COAXIAL TRUE THROUGH-HOLE PASS.
    #
    # Ten axial cutters run from BELOW the motor-side journal to ABOVE
    # the far journal. They fully cross BOTH 10 mm bearing seats and BOTH
    # 2 mm shoulders; no late overlapping mesh can refill a through-hole.
    # R=38.8 +/-0.75 mm is outside R=38.0 outer shell/base, but inside
    # R=40.0 journal OD. The residual outer bearing-wall web is 0.45 mm.
    # Caution: this is intentionally thinner than a robust PLA wall.
    # --------------------------------------------------------------
    print('  DRILLING 10 truly open Ø1.5 mm matching axial collar ports...')
    axial_z0 = ROLLING_LAND_LOWER_Z0_MM - 1.0
    axial_z1 = ROLLING_LAND_UPPER_Z1_MM + 1.0
    registration_cutters = create_coaxial_alignment_cutters(
        'V17_4_TRUE_AXIAL_THROUGH_REGISTER_CUTTERS', axial_z0, axial_z1)
    boolean_collection(outer, registration_cutters, 'DIFFERENCE',
                       'V17_4_DRILL_BOTH_BEARING_JOURNALS_AND_GUARDS')
    delete_collection_and_objects(registration_cutters)
    print('  TRUE THROUGH: 10 identical Z-axis lines cross both journals and guards.')
    print('  The Ø80 outer bearing surfaces remain uncut; 0.45 mm web remains.')

    for poly in outer.data.polygons:
        poly.use_smooth = False

    outer.data.validate(verbose=False)
    outer.data.update()

    return outer



# =====================================================================
# V16 STATIONARY LENS-GUIDE HELPERS
# =====================================================================

def create_cylindrical_fresnel_lens_guides():
    """No separate lens guides; sector fins and row rings reach R34.7.

    External UV collection and die-replicating lenses are separate modules,
    not included inside the printed rotor clearance envelope by default.
    """
    return []

# =====================================================================
# BUILD INNER STATIONARY FRESNEL-LIKE LED CARRIER
# =====================================================================

def create_inner_led_carrier():
    print("")
    print("Building INNER V17.9 LED carrier with 10 shared half-mm sector walls...")

    # --------------------------------------------------------------
    # 1) Hollow inner carrier body.
    # --------------------------------------------------------------
    body = add_cylinder(
        "INNER_LED_CARRIER_BODY",
        radius=INNER_CARRIER_RADIUS_MM,
        depth=INNER_CARRIER_HEIGHT_MM,
        location=(
            0.0,
            0.0,
            INNER_CARRIER_HEIGHT_MM * 0.5,
        ),
        vertices=DRUM_CIRCLE_VERTICES,
    )

    cavity = add_cylinder(
        "CUT_INNER_CARRIER_CAVITY",
        radius=INNER_CARRIER_INNER_RADIUS_MM,
        depth=INNER_CARRIER_HEIGHT_MM + 2.0,
        location=(
            0.0,
            0.0,
            INNER_CARRIER_HEIGHT_MM * 0.5,
        ),
        vertices=DRUM_CIRCLE_VERTICES,
    )

    boolean_object(
        body,
        cavity,
        'DIFFERENCE',
        "Hollow_inner_LED_carrier",
    )

    # --------------------------------------------------------------
    # 2) One sight-hole row in the non-scanning alignment collar.
    # --------------------------------------------------------------
    print("  Cutting one inner circumferential sight-hole row...")

    sight_collection = create_inner_sight_hole_collection()

    boolean_collection(
        body,
        sight_collection,
        'DIFFERENCE',
        "Cut_inner_sight_holes",
    )

    delete_collection_and_objects(sight_collection)

    # --------------------------------------------------------------
    # 3) Keep 51 continuous row rings AND add ONE shared straight
    # 0.5mm separator at EACH of the ten 36-degree sector boundaries.
    # --------------------------------------------------------------
    print("  Creating 49 continuous 0.5mm row rings + 2 lips...")
    print("  Creating 10 shared integrated 0.5mm angular sector walls...")
    arc_boundary_ridges=create_arc_boundary_ridges()
    require(len(arc_boundary_ridges)==10, '10 shared LED sector walls are required')
    fins=[]
    lens_guides=[]
    integrated_row_combs=create_continuous_horizontal_row_separators()
    require(len(integrated_row_combs)==ROW_RING_COUNT,
            '51 continuous row rings required for this carrier.')

    # --------------------------------------------------------------
    # 4) Support disk above the full physical carrier body.
    # --------------------------------------------------------------
    support_disk_z0 = INNER_CARRIER_HEIGHT_MM
    support_disk_z1 = (
        support_disk_z0
        + INNER_SUPPORT_DISK_THICKNESS_MM
    )

    support_disk = add_cylinder(
        "INNER_SUPPORT_DISK",
        radius=INNER_SUPPORT_DISK_RADIUS_MM,
        depth=INNER_SUPPORT_DISK_THICKNESS_MM,
        location=(
            0.0,
            0.0,
            (support_disk_z0 + support_disk_z1) * 0.5,
        ),
        vertices=DRUM_CIRCLE_VERTICES,
    )

    # --------------------------------------------------------------
    # 5) Larger stationary top alignment disk/flange.
    # Its 80 mm OD preserves a 2 mm radial overhang beyond the 76 mm
    # rotating drum, keeping the simple round-hole pattern visible from above.
    # --------------------------------------------------------------
    flange_z0 = (
        support_disk_z1
        + INNER_MARKING_FLANGE_GAP_MM
    )
    flange_z1 = (
        flange_z0
        + INNER_MARKING_FLANGE_THICKNESS_MM
    )

    flange = add_cylinder(
        "INNER_MARKING_FLANGE",
        radius=INNER_MARKING_FLANGE_RADIUS_MM,
        depth=INNER_MARKING_FLANGE_THICKNESS_MM,
        location=(
            0.0,
            0.0,
            (flange_z0 + flange_z1) * 0.5,
        ),
        vertices=DRUM_CIRCLE_VERTICES,
    )

    # --------------------------------------------------------------
    # 6) Stationary D-shaped support hub above flange.
    # --------------------------------------------------------------
    hub_z0 = flange_z1
    hub_z1 = hub_z0 + INNER_SUPPORT_HUB_LENGTH_MM

    support_hub = add_cylinder(
        "INNER_D_SUPPORT_HUB",
        radius=INNER_SUPPORT_HUB_RADIUS_MM,
        depth=INNER_SUPPORT_HUB_LENGTH_MM,
        location=(
            0.0,
            0.0,
            (hub_z0 + hub_z1) * 0.5,
        ),
        vertices=128,
    )

    # --------------------------------------------------------------
    # 7) D bore through support disk + flange + support hub.
    # --------------------------------------------------------------
    bore_bottom = (
        support_disk_z0 - 1.0
    )
    bore_top = (
        hub_z1 + 1.0
    )

    bore_depth = bore_top - bore_bottom
    bore_center = (bore_bottom + bore_top) * 0.5

    for target, tag in (
        (support_disk, "DISK"),
        (flange, "FLANGE"),
        (support_hub, "HUB"),
    ):
        cutter = make_d_prism_cutter(
            f"CUT_INNER_D_BORE_{tag}",
            INNER_D_BORE_RADIUS_MM,
            INNER_D_FLAT_X,
            bore_depth,
            bore_center,
        )

        boolean_object(
            target,
            cutter,
            'DIFFERENCE',
            f"Cut_inner_D_bore_{tag}",
        )

    # --------------------------------------------------------------
    # 8) Alignment-hole Boolean intentionally deferred.
    #
    # Do NOT cut the flange here.  The ten simple round alignment holes
    # are cut exactly once after the complete stationary inner assembly
    # has been joined.  This avoids duplicate/overlapping Boolean results.
    # --------------------------------------------------------------
    print("  Deferring top alignment-hole cut until final post-join pass...")

    # --------------------------------------------------------------
    # 9) Join all inner pieces into one separate printable object.
    # --------------------------------------------------------------
    inner_parts = (
        [body]
        + fins
        + lens_guides
        + arc_boundary_ridges
        + integrated_row_combs
        + [
            support_disk,
            flange,
            support_hub,
        ]
    )

    inner = join_objects(
        inner_parts,
        body,
        "INNER_LED_CARRIER_PRINTABLE",
    )

    # --------------------------------------------------------------
    # SINGLE AUTHORITATIVE TRUE-SIGHT PASS
    #
    # Cut the ten top alignment holes exactly once after every inner component has
    # been joined. This guarantees that no overlapping/joined geometry
    # can visually close the holes from the top.
    # --------------------------------------------------------------
    final_top_holes = create_inner_flange_marking_collection(
        flange_top_z=flange_z1
    )

    boolean_collection(
        inner,
        final_top_holes,
        'DIFFERENCE',
        "Final_true_sight_top_alignment_holes",
    )

    delete_collection_and_objects(final_top_holes)

    for poly in inner.data.polygons:
        poly.use_smooth = False

    inner.data.validate(verbose=False)
    inner.data.update()
    # Included in the final single mesh object, not separate STL parts.
    inner['sector_baffle_count'] = SECTOR_BOUNDARY_RIDGE_COUNT
    inner['baffles_per_sector'] = SECTOR_BAFFLES_PER_SECTOR
    inner['baffle_tangential_width_mm'] = ARC_BOUNDARY_RIDGE_TANGENTIAL_WIDTH_MM

    return inner


# V17.7 contains NO external detachable hand crank or print accessories.
# The rotor retains its D shaft drive and integrated toothed pulley.

# =====================================================================
# ALTERNATIVE LILYGO DEBUG INNER DRUM - SINGLE DISPLAY POCKET
# =====================================================================

def debug_slot_box(name, x0, x1, y0, y1, z0, z1):
    """Add a rectangular bracket/cutter in the local radial (+X) frame.

    Rotate ONLY this local part around Z, not the alignment flange or the
    D shaft: matching alignment ports stay at 0,36,... as on the rotor.
    """
    require(x1>x0 and y1>y0 and z1>z0,'Degenerate debug bracket box')
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))
    ob=bpy.context.active_object
    ob.name=name
    ob.dimensions=(x1-x0,y1-y0,z1-z0)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.location=(0.5*(x0+x1),0.5*(y0+y1),0.5*(z0+z1))
    # Rotate the box centre as well as its axes about the global Z axis.
    angle=math.radians(LILYGO_SLOT_AZIMUTH_DEG)
    lx,ly=ob.location.x,ob.location.y
    ob.location.x=lx*math.cos(angle)-ly*math.sin(angle)
    ob.location.y=lx*math.sin(angle)+ly*math.cos(angle)
    ob.rotation_euler.z=angle
    return ob


def create_inner_lilygo_debug_carrier():
    """One printable stationary carrier for one LILYGO 1.91in AMOLED.

    No row fins; two 0.5mm sector-side walls frame the single display.
    Same Z axis, D bore, top flange,
    alignment holes and rotor clearances as ordinary V17 inner carrier.
    An open through-wall pocket accepts ~60 x 25.5 x 10mm LILYGO module.
    Front panel faces radially toward rotating Nipkow apertures.
    
    The board is an unmodeled hardware reference - not a third STL.
    Snap nibs are exploratory and must be test fitted before loading PCB.
    """
    print('Building ALTERNATE LILYGO ONE-SLOT DEBUG inner carrier...')
    body=add_cylinder('DEBUG_INNER_CARRIER_SHELL',INNER_CARRIER_RADIUS_MM,
         INNER_CARRIER_HEIGHT_MM,(0,0,INNER_CARRIER_HEIGHT_MM*0.5),
         vertices=DRUM_CIRCLE_VERTICES)
    cavity=add_cylinder('CUT_DEBUG_INNER_HOLLOW',INNER_CARRIER_INNER_RADIUS_MM,
         INNER_CARRIER_HEIGHT_MM+2,(0,0,INNER_CARRIER_HEIGHT_MM*0.5),
         vertices=DRUM_CIRCLE_VERTICES)
    boolean_object(body,cavity,'DIFFERENCE','DEBUG_HOLLOW')

    # Genuine wall opening for the entire PCB, not 36 slot patterns.
    cutter=debug_slot_box('CUT_DEBUG_SINGLE_BOARD_POCKET',20.0,38.0,
          -0.5*(LILYGO_MODULE_TANGENTIAL_MM+LILYGO_SLOT_TANGENTIAL_EXTRA_MM),
           0.5*(LILYGO_MODULE_TANGENTIAL_MM+LILYGO_SLOT_TANGENTIAL_EXTRA_MM),
           LILYGO_BOARD_BOTTOM_Z_MM-LILYGO_SLOT_AXIAL_EXTRA_MM/2,
           LILYGO_BOARD_TOP_Z_MM+LILYGO_SLOT_AXIAL_EXTRA_MM/2)
    boolean_object(body,cutter,'DIFFERENCE','CUT_ONE_AMOLED_BOARD_OPENING')

    # Preserve existing circumferential sight-hole datum row.
    sideports=create_inner_sight_hole_collection()
    boolean_collection(body,sideports,'DIFFERENCE','DEBUG_CIRCUMFERENTIAL_DATUMS')
    delete_collection_and_objects(sideports)

    # Two integral channel guide rails, seated into the uncut wall edges.
    stops=[]
    edge=LILYGO_GUIDE_INNER_Y_MM
    for sign,tag in [(-1,'MINUS'),(1,'PLUS')]:
        if sign<0: ya,yb=-(edge+LILYGO_GUIDE_WALL_MM),-edge
        else: ya,yb=edge,edge+LILYGO_GUIDE_WALL_MM
        stops.append(debug_slot_box('DEBUG_SIDE_GUIDE_'+tag,
                     LILYGO_GUIDE_X0_MM,LILYGO_GUIDE_X1_MM,ya,yb,
                     LILYGO_BOARD_BOTTOM_Z_MM-1.0,
                     LILYGO_BOARD_TOP_Z_MM+1.0))
        # Two small front retainers on the rail ends, off the active display.
        for ztag,zbase in (('BOTTOM',LILYGO_BOARD_BOTTOM_Z_MM+3.0),
                           ('TOP',LILYGO_BOARD_TOP_Z_MM-3.0)):
            if sign<0: ty0,ty1=-(edge+0.30),-(edge-1.25)
            else: ty0,ty1=edge-1.25,edge+0.30
            stops.append(debug_slot_box('DEBUG_SNAP_TAB_'+tag+'_'+ztag,
                         LILYGO_RETENTION_TAB_X0_MM,
                         LILYGO_RETENTION_TAB_X1_MM,ty0,ty1,
                         zbase-1.5,zbase+1.5))

    # Upper stop (board inserts from the outward radial face).
    stops.append(debug_slot_box('DEBUG_BOARD_TOP_STOP',22.5,30.5,
                -LILYGO_MODULE_TANGENTIAL_MM/2,
                 LILYGO_MODULE_TANGENTIAL_MM/2,
                 LILYGO_BOARD_TOP_Z_MM+0.4,LILYGO_BOARD_TOP_Z_MM+1.6))
    # Two bottom end-stop pads leaving the centre gap for USB-C entry.
    stops.append(debug_slot_box('DEBUG_BOARD_BOTTOM_STOP_L',22.5,30.5,
                -LILYGO_MODULE_TANGENTIAL_MM/2,-8.0,
                 LILYGO_BOARD_BOTTOM_Z_MM-1.6,
                 LILYGO_BOARD_BOTTOM_Z_MM-0.4))
    stops.append(debug_slot_box('DEBUG_BOARD_BOTTOM_STOP_R',22.5,30.5,
                 8.0,LILYGO_MODULE_TANGENTIAL_MM/2,
                 LILYGO_BOARD_BOTTOM_Z_MM-1.6,
                 LILYGO_BOARD_BOTTOM_Z_MM-0.4))

    # Two 0.5mm radial walls outside the actual 26.4mm-wide AMOLED slot.
    # The PCB is wider than a 36deg sector, so use +18deg +/-30deg.
    # They penetrate the carrier shell and join this same final printed drum.
    debug_sector_baffles=[]
    _baffle_r0=LILYGO_BAFFLE_ROOT_RADIUS_MM
    _baffle_r1=LILYGO_BAFFLE_TIP_RADIUS_MM
    for sign,tag in ((-1,'LEFT'),(1,'RIGHT')):
        debug_sector_baffles.append(add_radial_cube_cutter(
            name='DEBUG_SINGLE_SLOT_BAFFLE_'+tag+'_0P5',
            angle_deg=(LILYGO_SLOT_AZIMUTH_DEG +
                       sign*LILYGO_BAFFLE_HALF_SPAN_DEG) % 360.0,
            radial_center=0.5*(_baffle_r0+_baffle_r1),
            radial_length=_baffle_r1-_baffle_r0,
            tangential_width=LILYGO_BAFFLE_TANGENTIAL_WIDTH_MM,
            z_center=ACTIVE_WALL_HEIGHT_MM*0.5,
            z_depth=ACTIVE_WALL_HEIGHT_MM,
        ))
    require(len(debug_sector_baffles)==LILYGO_BAFFLE_COUNT,
            'Debug inner must have exactly two integral angular walls.')

    # Identical interface: same support disk, Ø80 flange, and D-shaped hub.
    support_z0=INNER_CARRIER_HEIGHT_MM
    support_z1=support_z0+INNER_SUPPORT_DISK_THICKNESS_MM
    disk=add_cylinder('DEBUG_INNER_SUPPORT_DISK',INNER_SUPPORT_DISK_RADIUS_MM,
         INNER_SUPPORT_DISK_THICKNESS_MM,
         (0,0,0.5*(support_z0+support_z1)),vertices=DRUM_CIRCLE_VERTICES)
    flange_z0=support_z1+INNER_MARKING_FLANGE_GAP_MM
    flange_z1=flange_z0+INNER_MARKING_FLANGE_THICKNESS_MM
    flange=add_cylinder('DEBUG_INNER_TOP_DATUM_FLANGE',
         INNER_MARKING_FLANGE_RADIUS_MM,INNER_MARKING_FLANGE_THICKNESS_MM,
         (0,0,0.5*(flange_z0+flange_z1)),vertices=DRUM_CIRCLE_VERTICES)
    hub_z0=flange_z1
    hub_z1=hub_z0+INNER_SUPPORT_HUB_LENGTH_MM
    hub=add_cylinder('DEBUG_INNER_D_SUPPORT_HUB',INNER_SUPPORT_HUB_RADIUS_MM,
         INNER_SUPPORT_HUB_LENGTH_MM,(0,0,0.5*(hub_z0+hub_z1)),vertices=128)
    # Exactly the same D bore as the 1206-LED carrier.
    bore_depth=(hub_z1-support_z0)+2.0
    bore_center=0.5*(hub_z1+support_z0)
    for ob,tag in ((disk,'DISK'),(flange,'FLANGE'),(hub,'HUB')):
        dcut=make_d_prism_cutter('CUT_DEBUG_INNER_D_'+tag,
                 INNER_D_BORE_RADIUS_MM,INNER_D_FLAT_X,bore_depth,bore_center)
        boolean_object(ob,dcut,'DIFFERENCE','DEBUG_D_BORE_'+tag)

    # Separate off-axis upper cable/service port for a flexible USB pigtail.
    # A direct straight USB plug across the R36 moving drum is unsafe.
    for ob,tag in ((disk,'DISK'),(flange,'FLANGE')):
        cablecut=add_cylinder('CUT_DEBUG_CABLE_'+tag,
                 LILYGO_CABLE_PORT_RADIUS_MM,
                 INNER_SUPPORT_DISK_THICKNESS_MM+
                 INNER_MARKING_FLANGE_THICKNESS_MM+2.0,
                 (LILYGO_CABLE_PORT_CENTRE_LOCAL_X_MM,
                  LILYGO_CABLE_PORT_CENTRE_LOCAL_Y_MM,
                  0.5*(support_z0+flange_z1)),vertices=48)
        boolean_object(ob,cablecut,'DIFFERENCE','DEBUG_CABLE_PORT_'+tag)

    debug=join_objects([body]+stops+debug_sector_baffles+[disk,flange,hub],body,
                       'INNER_LILYGO_DEBUG_DRUM_PRINTABLE')
    # Matching top registration-hole pass, identical to normal inner.
    aligncut=create_inner_flange_marking_collection(flange_top_z=flange_z1)
    boolean_collection(debug,aligncut,'DIFFERENCE',
                       'DEBUG_TRUE_THROUGH_FLANGE_ALIGNMENT')
    delete_collection_and_objects(aligncut)
    for p in debug.data.polygons: p.use_smooth=False
    debug.data.validate(verbose=False);debug.data.update()
    debug['sector_baffle_count'] = LILYGO_BAFFLE_COUNT
    debug['baffles_per_display_slot'] = LILYGO_BAFFLE_COUNT
    debug['baffle_tangential_width_mm'] = LILYGO_BAFFLE_TANGENTIAL_WIDTH_MM
    print('DEBUG: 1 board pocket, 2 x 0.5mm angular walls, matching D bore and datums.')
    print('DEBUG: body board envelope 60x25.5x10mm, clearance unverified.')
    print('DEBUG: flexible USB cable must route through stationary hollow carrier.')
    return debug

# =====================================================================
# SCENE BUILD
# =====================================================================

clear_scene()

scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.001
scene.unit_settings.length_unit = 'MILLIMETERS'

print("")
print("=" * 88)
print("NIPKOW DRUM LITHOGRAPHY V17.9 — TWO INTERCHANGEABLE INNER DRUMS")
print("50 RADIAL BORES/SECTOR + SHARED 0.5mm BOUNDARIES + LILYGO DEBUG")
print("=" * 88)

print("")
print("MASTER ROW GEOMETRY")
print(f"  Active wall height              : {ACTIVE_WALL_HEIGHT_MM:.3f} mm")
print(f"  Row count                       : {ROW_COUNT}")
print(f"  Row pitch                       : {ROW_PITCH_MM:.3f} mm")
print(f"  Total Nipkow apertures          : {SECTOR_COUNT * ROW_COUNT}")
print(f"  Nipkow scan holes / sector      : {ROW_COUNT}")
print("  Horizontal align holes/sector  : 1 (inner + outer matched)")
print("  Axial rotor registration        : 10 TRUE THROUGH openings through both journals")
print(f"  Round alignment holes / sector  : 1")
print("  Outer alignment systems         : horizontal row + vertical row")
print("  Coaxial alignment               : flange + both guards + both journals, all THROUGH")
print("  Inner alignment Boolean passes : 1 (final post-join only)")
print("  Ø80 bearing journal thru-cuts   : ENABLED (0.45 mm outer web WARNING)")
print(f"  Horizontal sight angle          : +{SIGHT_REL_ANGLE_DEG:.1f} deg")
print("  Vertical/top boundary angle     : 0.0 + 36*k deg")
print(f"  Angular separation              : {_HORIZONTAL_TO_VERTICAL_ANGLE_SEPARATION_DEG:.1f} deg")

print(f"  Rolling land OD                 : {ROLLING_LAND_OUTER_OD_MM:.3f} mm")
print(f"  Rolling land width              : {ROLLING_LAND_AXIAL_WIDTH_MM:.3f} mm")
print(f"  Bearing guard OD                : {BEARING_GUARD_OUTER_OD_MM:.3f} mm")
print(f"  Bearing guard axial width       : {BEARING_GUARD_AXIAL_WIDTH_MM:.3f} mm")
print(f"  Lower bearing seat Z range      : {ROLLING_LAND_LOWER_Z0_MM:.2f} .. {ROLLING_LAND_LOWER_Z1_MM:.2f} mm")
print(f"  Upper bearing seat Z range      : {ROLLING_LAND_UPPER_Z0_MM:.2f} .. {ROLLING_LAND_UPPER_Z1_MM:.2f} mm")
print(f"  GT2 pulley centre Z             : {GT2_CENTER_Z_MM:.3f} mm")
print(f"  GT2 tooth count / pitch         : {GT2_TOOTH_COUNT} / {GT2_PITCH_MM:.3f} mm")
print(f"  GT2 tooth-tip diameter          : {2*GT2_TIP_RADIUS_MM:.3f} mm")
print(f"  GT2 root diameter               : {2*GT2_ROOT_RADIUS_MM:.3f} mm")
print(f"  GT2 toothed face / belt width   : {GT2_TOOTH_FACE_WIDTH_MM:.2f} / {GT2_BELT_WIDTH_MM:.2f} mm")
print(f"  GT2 flange OD                   : {GT2_FLANGE_OUTER_OD_MM:.2f} mm")
print(f"  Guard sight windows             : {BEARING_GUARD_VIEW_HOLE_COUNT} per guard; R38.8, Ø1.5 mm")
print(f"  Strengthened D hub diameter     : {OUTER_HUB_OD_MM:.3f} mm")
print(f"  Extended D-bore stub length     : {OUTER_HUB_LENGTH_MM:.3f} mm")
print(f"  Lens guides (separate)          : none printed")
print("  LED row-ring outer radius       : 34.700 mm")
print("  Row-ring/drum radial gap        : 1.300 mm")
print(f"  Optical margin per sector side  : {(SECTOR_REPEAT_DEG - LED_ACTIVE_ARC_DEG) * 0.5:.3f} deg")
print(f"  Aperture diameter               : {APERTURE_DIAMETER_MM:.3f} mm")
print(f"  First row center                : {FIRST_ROW_CENTER_Z:.3f} mm")
print(f"  Last row center                 : {LAST_ROW_CENTER_Z:.3f} mm")
print(f"  Bottom aperture-edge margin     : {END_MARGIN_MM:.3f} mm")
print(f"  Top aperture-edge margin        : {TOP_REMAINING_MARGIN_MM:.3f} mm")

print("")
print("ANGULAR GEOMETRY")
print(f"  Mechanical sectors              : {SECTOR_COUNT}")
print(f"  Mechanical sector repeat        : {SECTOR_REPEAT_DEG:.3f} deg")
print(f"  LED illumination arc            : {LED_ACTIVE_ARC_DEG:.3f} deg")
print(f"  Precision exposure gate         : {PRECISION_GATE_DEG:.3f} deg")
print(f"  Sight-hole relative angle       : {SIGHT_REL_ANGLE_DEG:.3f} deg")
print(
    f"  Pupil distance beyond drum      : "
    f"{PUPIL_DISTANCE_FROM_OUTER_SURFACE_MM:.3f} mm"
)

print("")
print("OUTER DRUM")
print(f"  OD                              : {OUTER_DRUM_OD_MM:.3f} mm")
print(f"  ID                              : {OUTER_DRUM_ID_MM:.3f} mm")
print(f"  Wall                            : {OUTER_WALL_THICKNESS_MM:.3f} mm")
print(f"  Encoder/drive base thickness    : {OUTER_BASE_THICKNESS_MM:.3f} mm")
print(f"  Encoder minimum web estimate    : {ENCODER_MIN_WEB_APPROX_MM:.3f} mm")
print(f"  Motor bearing load bridge       : R{MOTOR_LOAD_BRIDGE_R_INNER_MM:.2f}..{MOTOR_LOAD_BRIDGE_R_OUTER_MM:.2f}, Z{MOTOR_LOAD_BRIDGE_Z0_MM:.2f}..{MOTOR_LOAD_BRIDGE_Z1_MM:.2f}")
print(f"  Gusset print slope              : {HUB_ROOT_GUSSET_PRINT_SLOPE_DEG:.1f} deg")
print(f"  Preferred print orientation     : {PRINT_BUILD_ORIENTATION}, tilt={PRINT_AXIS_TILT_DEG:.1f} deg")
print(f"  Nipkow apertures                : {SECTOR_COUNT * ROW_COUNT}")
print(f"  Encoder slots                   : {TOTAL_ENCODER_SLOTS}")
print(f"  Legacy outer base arc markings   : INACTIVE (no through-cut)")
print("  50 radial encoder slots only; old decorative arcs not cut from base")

print("")
print("INNER LED CARRIER WITH TWO 0.5mm WALLS PER SECTOR")
print(f"  Carrier OD                      : {INNER_CARRIER_OD_MM:.3f} mm")
print(f"  Carrier ID                      : {INNER_CARRIER_ID_MM:.3f} mm")
print(f"  Top alignment disk OD           : {INNER_MARKING_FLANGE_OD_MM:.3f} mm")
print(
    f"  Alignment disk radial overhang  : "
    f"{INNER_MARKING_FLANGE_RADIUS_MM - OUTER_DRUM_RADIUS_MM:.3f} mm"
)
print(f"  LED channels                    : {ROW_COUNT}")
print(f"  LED channel width               : {LED_CHANNEL_WIDTH_MM:.3f} mm")
print(f"  Internal separator width        : {FRESNEL_FIN_AXIAL_WIDTH_MM:.3f} mm")
print(f"  Full 360-degree row-ring height : {ROW_SEPARATOR_RADIAL_HEIGHT_MM:.3f} mm")
print(f"  Row-baffle envelope OD                      : {2*INNER_FIN_OUTER_RADIUS_MM:.3f} mm")
print(f"  Nominal radial drum clearance   : {RADIAL_CLEARANCE_MM:.3f} mm")
print(f"  Full Fresnel rings             : removed")
print(
    f"  Vertical sector baffles        : "
    f"{SECTOR_BOUNDARY_RIDGE_COUNT} x every {SECTOR_REPEAT_DEG:.3f} deg"
)
print(f"  Sector baffle tangential width : {ARC_BOUNDARY_RIDGE_TANGENTIAL_WIDTH_MM:.2f} mm")
# obsolete decorative fence diagnostic removed
# obsolete decorative fence diagnostic removed
print(
    f"  Fence-hole diameter             : "
    f"{ACTIVE_WINDOW_FENCE_HOLE_DIAMETER_MM:.3f} mm"
)
print(
    f"  Total fence through-holes       : "
    f"{SECTOR_COUNT}"
)
print(
    f"  First sector-boundary ridge     : "
    f"{SECTOR_BOUNDARY_RIDGE_OFFSET_DEG:.3f} deg"
)
print(f"  Bottom/top end lip width        : {END_LED_LIP_WIDTH_MM:.3f} mm")
print(f"  Integrated continuous row rings: {ROW_RING_COUNT}")
print("  49 x 0.5 mm full-circumference axial row dividers; ONE LED DRUM")
print("  10 OPTICAL sector positions : visible 0..4, UV 5..9; one shared wall per boundary")
print("  5 x 36 deg = 180 deg           : each electrical hemisphere fully populated")
print(f"  Total internal horizontal rings: {ROW_RING_COUNT - 2} + 2 end lips")

print("")
print("REGISTRATION")
print(
    "  Outer rotor markings repeat identically every 36 deg; "
    "no unique mass-removing HOME notch."
)
print(
    "  One sight hole per 36 degree sector forms one balanced "
    "circumferential alignment row on both cylinders."
)
print(
    "  A balanced segmented shallow demarcation dent separates the active "
    "Nipkow region from the alignment collar without cutting through the wall."
)
print(
    "  Sight holes can also be used as an optical alignment channel "
    "with a visible/IR LED + photodiode."
)
print("=" * 88)

outer = create_outer_drum()
inner = create_inner_led_carrier()  # 51 rings + 10 shared radial baffles.
# No separate cassettes, crank arm, or grip objects: exactly TWO mesh objects.

# =====================================================================
# FINAL VALIDATION
# =====================================================================

require(
    outer.name in bpy.data.objects,
    "Outer drum object missing after build."
)

require(
    inner.name in bpy.data.objects,
    "Inner carrier object missing after build."
)

require(
    outer != inner,
    "Outer and inner must remain separate objects."
)

require(all(ob.name in bpy.data.objects for ob in (outer, inner)),
        "Rotor and carrier missing after generation.")
# These are two printed objects, not ten extra combs or two crank parts.
mesh_objects = [ob for ob in bpy.data.objects if ob.type == 'MESH']
require(len(mesh_objects) == 2 and set(mesh_objects) == {outer,inner},
        "The selected LED assembly must initially have EXACTLY TWO Blender mesh objects; found: "
        + str([ob.name for ob in mesh_objects]))
# Joined/overlapped meshes need independent manifold and slicer-union checks.
# Ø1.5mm collar holes have 0.45mm outer journal web: physical strength untested.

require(abs(row_center_z(0)-1.25)<1e-9 and
        abs(row_center_z(49)-99.25)<1e-9,
        "First/last hole centers must be Z=1.25 / 99.25 mm.")


require(
    outer.dimensions.x >= OUTER_BASE_OD_MM * 0.95,
    "Outer expanded base missing/collapsed."
)

require(
    inner.dimensions.x >= INNER_MARKING_FLANGE_OD_MM * 0.95,
    "Inner marking flange missing/collapsed."
)

leftover_cutters = [
    obj.name
    for obj in bpy.data.objects
    if obj.name.startswith("CUT_")
]

if leftover_cutters:
    raise RuntimeError(
        "V17 cutter cleanup failed. Leftover CUT_ objects: "
        + ", ".join(leftover_cutters[:20])
    )

# =====================================================================
# V17.4 OPTICAL LINE-OF-SIGHT SELF-TEST — catches hidden collar holes.
# Trace through BOTH final meshes from the fixed flange end to below the
# motor-side bearing. An accidental solid guard/journal/refilled hole will
# block the ray and STOP export instead of silently shipping bad geometry.
# =====================================================================
print('Checking ten unobstructed vertical alignment rays (inner + outer)...')
bpy.context.view_layer.update()
_registration_depsgraph = bpy.context.evaluated_depsgraph_get()
_registration_top_z = (
    INNER_CARRIER_HEIGHT_MM + INNER_SUPPORT_DISK_THICKNESS_MM
    + INNER_MARKING_FLANGE_GAP_MM + INNER_MARKING_FLANGE_THICKNESS_MM
    + INNER_SUPPORT_HUB_LENGTH_MM + 2.0
)
_registration_bottom_z = ROLLING_LAND_LOWER_Z0_MM - 2.0
_registration_length = _registration_top_z - _registration_bottom_z
require(_registration_length > 100.0, 'Alignment test ray span invalid.')
for _datum_i in range(SECTOR_COUNT):
    _datum_angle = math.radians(
        SECTOR_BOUNDARY_RIDGE_OFFSET_DEG + _datum_i * SECTOR_REPEAT_DEG)
    _datum_x = COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM * math.cos(_datum_angle)
    _datum_y = COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM * math.sin(_datum_angle)
    _hit, _pos, _normal, _face, _ob, _matrix = bpy.context.scene.ray_cast(
        _registration_depsgraph,
        Vector((_datum_x, _datum_y, _registration_top_z)),
        Vector((0.0, 0.0, -1.0)),
        distance=_registration_length,
    )
    if _hit:
        raise RuntimeError(
            f'VISIBLE ALIGNMENT HOLE BLOCKED at sector {_datum_i}, '
            f'angle {math.degrees(_datum_angle):.1f} deg; '
            f'first solid hit={_ob.name} z={_pos.z:.3f} mm. '
            'Check Boolean cutters before generating STLs.'
        )
print('PASS: all 10 matching straight-through registration sightlines are open.')

print("")
print("=" * 88)
print("V17.9 LED ASSEMBLY / 50 ENCODER + 4MM BASE: PASS (PRINTABILITY UNVERIFIED)")
print("=" * 88)
print(f"Outer object                     : {outer.name}")
print(f"Inner object                     : {inner.name}")
print("Normal LED inner: 49 row separators + 2 lips + 10 shared sector walls.")
print("")
print("ROW ALIGNMENT:")
print(f"  outer row pitch                : {ROW_PITCH_MM:.3f} mm")
print(f"  inner LED channel pitch        : {ROW_PITCH_MM:.3f} mm")
print(f"  row/channel count              : {ROW_COUNT}/{ROW_COUNT}")
print("")
print("ANGULAR REFERENCES:")
print(f"  sector                         : 36.0 deg")
print(f"  LED illumination               : {LED_ACTIVE_ARC_DEG:.1f} deg")
print(f"  precision gate                 : 6.0 deg")
print(f"  sight registration line        : +{SIGHT_REL_ANGLE_DEG:.1f} deg")
print("")
print("IMPORTANT:")
print(
    "  The 32 deg illumination arc and 6 deg precision gate are "
    "independent parameters."
)
print(
    "  Start optical testing with the narrow precision gate and "
    "expand only after measured spot/focus verification."
)
print("=" * 88)

# =====================================================================
# SEPARATE STL EXPORT
# =====================================================================

if AUTO_EXPORT_STL:
    try:
        deselect_all()
        outer.select_set(True)
        bpy.context.view_layer.objects.active = outer

        outer_path = bpy.path.abspath(
            "//" + OUTER_STL_FILENAME
        )

        bpy.ops.wm.stl_export(
            filepath=outer_path,
            export_selected_objects=True,
        )

        print("Outer STL exported:", outer_path)

    except Exception as exc:
        raise RuntimeError("Outer STL automatic export failed") from exc

    try:
        deselect_all()
        inner.select_set(True)
        bpy.context.view_layer.objects.active = inner

        inner_path = bpy.path.abspath(
            "//" + INNER_STL_FILENAME
        )

        bpy.ops.wm.stl_export(
            filepath=inner_path,
            export_selected_objects=True,
        )

        print("Inner STL exported:", inner_path)

    except Exception as exc:
        raise RuntimeError("Inner LED STL automatic export failed") from exc

    print('V17.9 also exports the alternative 2-wall LILYGO inner drum.')

# Select both final objects for inspection.
deselect_all()
outer.select_set(True)
inner.select_set(True)
bpy.context.view_layer.objects.active = outer

print("")
print("V17.9 — TWO ASSEMBLY PARTS: OUTER + ONE SELECTED INNER")
print("Inspect 10 THROUGH datums, two guards, 40T tooth printability, and row rings before slicing.")


# =====================================================================
# V17.9: EXPORT THE ALTERNATE TWO-WALL LILYGO INNER; KEEP TWO PARTS
# =====================================================================
debug_inner=create_inner_lilygo_debug_carrier()
require(debug_inner.name in bpy.data.objects,
        'The alternative one-slot LILYGO inner drum is missing')
require(len([ob for ob in bpy.data.objects if ob.type=='MESH'])==3,
        'Only rotor + two alternative inner variants may exist temporarily')
if AUTO_EXPORT_STL:
    try:
        deselect_all()
        debug_inner.select_set(True)
        bpy.context.view_layer.objects.active=debug_inner
        p=bpy.path.abspath('//'+DEBUG_STL_FILENAME)
        bpy.ops.wm.stl_export(filepath=p,export_selected_objects=True)
        print('Alternative LILYGO STL exported:',p)
    except Exception as exc:
        raise RuntimeError('Alternative LILYGO STL export failed') from exc

# Final scene contains EXACTLY two mesh bodies: rotor + selected inner.
# Unselected alternative remains available as a separately exported STL.
if SCENE_INNER_VARIANT=='LILYGO':
    bpy.data.objects.remove(inner,do_unlink=True)
    inner=debug_inner
else:
    bpy.data.objects.remove(debug_inner,do_unlink=True)
require(len([ob for ob in bpy.data.objects if ob.type=='MESH'])==2,
        'The final scene MUST contain exactly two printable drum meshes')
require(inner.get('sector_baffle_count') ==
        (SECTOR_BOUNDARY_RIDGE_COUNT if SCENE_INNER_VARIANT == 'LED' else
         LILYGO_BAFFLE_COUNT),
        'Chosen inner variant lost its sector baffle manifest')
require(outer.name in bpy.data.objects and inner.name in bpy.data.objects,
        'Selected rotor/inner variant missing after alternative export')

# Verify the alternate flange/rotor line of sight, where applicable.
print('Testing ten visible registration rays in FINAL selected assembly...')
bpy.context.view_layer.update()
_deps=bpy.context.evaluated_depsgraph_get()
for _i in range(SECTOR_COUNT):
    _aa=math.radians(_i*SECTOR_REPEAT_DEG)
    _ox=COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM*math.cos(_aa)
    _oy=COAXIAL_ALIGNMENT_HOLE_CENTER_RADIUS_MM*math.sin(_aa)
    _hit,_loc,_norm,_face,_obj,_mat=bpy.context.scene.ray_cast(
        _deps,Vector((_ox,_oy,_registration_top_z)),
        Vector((0.0,0.0,-1.0)),distance=_registration_length)
    require(not _hit, f'Final assembly registration sightline {_i} blocked by '
            +(_obj.name if _obj else '<unknown>'))

deselect_all(); outer.select_set(True);inner.select_set(True)
bpy.context.view_layer.objects.active=inner
print('V17.8 COMPLETE: 3 distinct STL exports (if enabled); 2 final mesh objects.')
print('Chosen final inner scene variant:',SCENE_INNER_VARIANT)
print('DO NOT install both inner drums at the same time.')

# Check that all requested STL exports actually exist and are nonempty.
if AUTO_EXPORT_STL:
    import os
    for _f in (OUTER_STL_FILENAME,INNER_STL_FILENAME,DEBUG_STL_FILENAME):
        _out=bpy.path.abspath('//'+_f)
        require(os.path.isfile(_out) and os.path.getsize(_out)>1024,
                f'Missing or empty STL export: {_out}')
