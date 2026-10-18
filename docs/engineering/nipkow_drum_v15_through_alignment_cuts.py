# =====================================================================
# NIPKOW DRUM LITHOGRAPHY V15
# DUAL-STEERING + OPTICAL/MECHANICAL REGISTRATION
#
# TWO SEPARATE PRINTABLE OBJECTS:
#
#   1) OUTER_DRUM_PRINTABLE
#      - rotating Nipkow drum
#      - 66 mm OD, 78 mm active wall height
#      - 2 mm wall
#      - separate 2 mm closed encoder/base disk
#      - 10 sectors x 36 degrees
#      - 30 aperture rows per sector = 300 Nipkow apertures
#      - 1.6 mm apertures, 2.6 mm row pitch
#      - EXACT 0.5 mm material margin at both axial ends
#      - apertures are 3D-aimed toward a sector-local common pupil
#      - V13 progressive encoder slots retained
#      - 0.6 mm-deep NON-THROUGH registration engraving
#      - 25 degree illumination-window markings
#      - 6 degree precision-exposure markings
#      - one circumferential row of through sight holes for optical registration
#
#   2) INNER_LED_CARRIER_PRINTABLE
#      - stationary Fresnel-like LED carrier
#      - 56 mm OD, 78 mm active height
#      - localized 25 degree LED arc only
#      - 30 LED channels, each 1.7 mm wide
#      - channels centered on EXACTLY the same 2.6 mm row centers
#      - 29 internal separator fins, 0.9 mm wide, 2 mm radial height
#      - top fins slope downward; bottom fins slope upward
#      - two narrow end retaining lips
#      - 10-fold optical sight holes, one matching hole per 36 degree sector
#      - separate support disk, marked flange and D-shaped support hub
#
# IMPORTANT OPTICAL INTERPRETATION
# --------------------------------
# The "Fresnel-like" structure is NOT a refractive Fresnel lens.
# The fins provide source/baffle aiming and the angled apertures provide
# directional filtering. The final 25 mm projection lens still performs
# the optical imaging.
#
# COORDINATE SYSTEM
# -----------------
# Z = common cylinder axis
# XY = circular cross-section
#
# Outer active wall: Z = 0 .. 78 mm
# Outer base:        Z = -2 .. 0 mm
#
# Optical-axis reference for the stationary carrier is +X / 0 degrees.
#
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

OUTER_STL_FILENAME = "nipkow_v15_outer_drum.stl"
INNER_STL_FILENAME = "nipkow_v15_inner_fresnel_led_carrier.stl"

# =====================================================================
# MASTER GEOMETRY
# =====================================================================

# 30 rows * 2.6 mm pitch = 78.0 mm.
# With 1.6 mm apertures and row centers at 1.3 + n*2.6:
# first aperture begins at 0.5 mm
# last aperture ends at 77.5 mm
# leaving EXACTLY 0.5 mm at both ends.
ACTIVE_WALL_HEIGHT_MM = 78.0

# Dedicated non-scanning alignment collar above the 78 mm active region.
ALIGNMENT_BAND_HEIGHT_MM = 6.0

TOTAL_CYLINDER_HEIGHT_MM = (
    ACTIVE_WALL_HEIGHT_MM
    + ALIGNMENT_BAND_HEIGHT_MM
)

ROW_COUNT = 30
ROW_PITCH_MM = 2.60

APERTURE_DIAMETER_MM = 1.60
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
SLANT_SWEEP_DEG = 36.0

# Broad LED illumination region.
LED_ACTIVE_ARC_DEG = 25.0
LED_ACTIVE_HALF_ARC_DEG = LED_ACTIVE_ARC_DEG * 0.5

# Narrow region intended initially for precision exposure/calibration.
PRECISION_GATE_DEG = 6.0
PRECISION_HALF_GATE_DEG = PRECISION_GATE_DEG * 0.5

# Common-pupil model.
#
# The pupil is modeled 120 mm radially beyond the OUTER drum surface.
# Every aperture in a sector aims toward a virtual pupil located on that
# sector's radial centerline. When that sector rotates to the real lens
# axis, the tunnel geometry has the intended orientation.
#
# Change this value after the real lens working geometry is measured.
PUPIL_DISTANCE_FROM_OUTER_SURFACE_MM = 120.0

# Safety guard against accidentally making extreme diagonal tunnels.
MAX_ALLOWED_TUNNEL_TILT_DEG = 30.0

# =====================================================================
# OUTER ROTATING DRUM
# =====================================================================

OUTER_DRUM_OD_MM = 66.0
OUTER_DRUM_RADIUS_MM = OUTER_DRUM_OD_MM * 0.5

OUTER_WALL_THICKNESS_MM = 2.0
OUTER_DRUM_ID_MM = (
    OUTER_DRUM_OD_MM
    - 2.0 * OUTER_WALL_THICKNESS_MM
)
OUTER_DRUM_INNER_RADIUS_MM = OUTER_DRUM_ID_MM * 0.5

# Separate closed base below the full 78 mm active wall.
OUTER_BASE_THICKNESS_MM = 2.0

# Expanded motor/encoder disk.
OUTER_BASE_OD_MM = 76.0
OUTER_BASE_RADIUS_MM = OUTER_BASE_OD_MM * 0.5

# Motor D-shaft hub.
OUTER_HUB_OD_MM = 18.0
OUTER_HUB_RADIUS_MM = OUTER_HUB_OD_MM * 0.5
OUTER_HUB_LENGTH_MM = 10.0

OUTER_D_BORE_DIAMETER_MM = 5.20
OUTER_D_BORE_RADIUS_MM = OUTER_D_BORE_DIAMETER_MM * 0.5
OUTER_D_FLAT_TO_ROUND_MM = 4.70
OUTER_D_FLAT_X = (
    OUTER_D_FLAT_TO_ROUND_MM
    - OUTER_D_BORE_RADIUS_MM
)

# =====================================================================
# V13-STYLE ROTATIONAL ENCODER
# =====================================================================

ENCODER_SECTOR_COUNT = 10
ENCODER_SECTOR_REPEAT_DEG = 36.0
ENCODER_SLOTS_PER_SECTOR = 8
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

INNER_CARRIER_HEIGHT_MM = TOTAL_CYLINDER_HEIGHT_MM

# LED CHANNELS:
# LED strip sits BETWEEN separator fins.
# 1.7 mm channel + 0.9 mm separator = 2.6 mm pitch.
LED_CHANNEL_WIDTH_MM = 1.70
FRESNEL_FIN_AXIAL_WIDTH_MM = (
    ROW_PITCH_MM - LED_CHANNEL_WIDTH_MM
)  # 0.90 mm

FRESNEL_FIN_RADIAL_HEIGHT_MM = 2.00

# Fresnel separator fins now continue around the FULL 360 degree cylinder.
# The 25 degree LED optical sector is physically demarcated by two
# continuous vertical boundary ribs at +/-12.5 degrees.
FRESNEL_FIN_ARC_DEG = 360.0
FRESNEL_FIN_HALF_ARC_DEG = 180.0

# Slight overlap into body so slicers robustly merge the fin mesh.
FRESNEL_FIN_BODY_OVERLAP_MM = 0.20

# Vertical sector-boundary ribs.
#
# These are intentionally placed OUTSIDE the central 25 degree optical
# window. They sit on the boundaries between the ten 36 degree sectors:
#
#   18, 54, 90, ... 342 degrees
#
# This leaves almost the full 36 degree sector available for LED strips.
SECTOR_BOUNDARY_RIDGE_COUNT = SECTOR_COUNT
SECTOR_BOUNDARY_RIDGE_OFFSET_DEG = SECTOR_REPEAT_DEG * 0.5

ARC_BOUNDARY_RIDGE_TANGENTIAL_WIDTH_MM = 0.50
ARC_BOUNDARY_RIDGE_RADIAL_HEIGHT_MM = 2.00
ARC_BOUNDARY_RIDGE_BODY_OVERLAP_MM = 0.20
ARC_BOUNDARY_RIDGE_HEIGHT_MM = ACTIVE_WALL_HEIGHT_MM

# Outward-flared fences for the nominal 25 degree active optical window.
# Each fence begins at +/-12.5 degrees on the carrier surface and runs
# outward toward the shared +/-18 degree boundary ridge of that sector.
ACTIVE_WINDOW_FENCE_WIDTH_MM = 0.50
ACTIVE_WINDOW_FENCE_BODY_OVERLAP_MM = 0.20
ACTIVE_WINDOW_FENCE_TIP_OVERLAP_MM = 0.10
ACTIVE_WINDOW_FENCE_HEIGHT_MM = ACTIVE_WALL_HEIGHT_MM

INNER_FIN_OUTER_RADIUS_MM = (
    INNER_CARRIER_RADIUS_MM
    + FRESNEL_FIN_RADIAL_HEIGHT_MM
)

# Approximate radial distance from the inner carrier surface to the same
# pupil used by the outer drum.
INNER_TO_PUPIL_RADIAL_MM = (
    PUPIL_DISTANCE_FROM_OUTER_SURFACE_MM
    + OUTER_DRUM_RADIUS_MM
    - INNER_CARRIER_RADIUS_MM
)

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
# It gives a visible area for 36/25/6 degree registration marks.
INNER_MARKING_FLANGE_GAP_MM = 0.0
INNER_MARKING_FLANGE_THICKNESS_MM = 2.0
INNER_MARKING_FLANGE_OD_MM = 70.0
INNER_MARKING_FLANGE_RADIUS_MM = INNER_MARKING_FLANGE_OD_MM * 0.5

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

OUTER_25_ARC_R_INNER_MM = 34.0
OUTER_25_ARC_R_OUTER_MM = 34.7

OUTER_6_ARC_R_INNER_MM = 35.4
OUTER_6_ARC_R_OUTER_MM = 36.1

# INNER support-flange nested arc markings.
INNER_36_ARC_R_INNER_MM = 30.0
INNER_36_ARC_R_OUTER_MM = 30.7

INNER_25_ARC_R_INNER_MM = 31.2
INNER_25_ARC_R_OUTER_MM = 31.9

INNER_6_ARC_R_INNER_MM = 32.4
INNER_6_ARC_R_OUTER_MM = 33.1

# =====================================================================
# VISIBLE + OPTICAL THROUGH-SIGHT REGISTRATION
# =====================================================================

# The alignment hole is intentionally placed in the solid 5.5 degree
# margin between the 25 degree optical arc and 36 degree sector edge:
#
#   optical edge = +12.5 deg
#   sight line   = +16.5 deg
#   sector edge  = +18.0 deg
#
# Thus the sight hole does not cut through the LED arc.
SIGHT_REL_ANGLE_DEG = 16.5

SIGHT_HOLE_DIAMETER_MM = 2.0
SIGHT_HOLE_RADIUS_MM = SIGHT_HOLE_DIAMETER_MM * 0.5

# One circumferential row of alignment holes only. The row is centered
# in the 6 mm non-scanning alignment collar so it cannot touch a Nipkow
# aperture row.
SIGHT_Z_LEVELS_MM = (
    ACTIVE_WALL_HEIGHT_MM + ALIGNMENT_BAND_HEIGHT_MM * 0.5,
)

# Through-cut demarcation ring immediately above the active scan region.
# It is divided into ten identical 30 degree arc slots rather than one
# uninterrupted 360 degree cut.  The remaining 6 degrees per 36 degree
# sector form structural bridges, preserving the collar as part of the drum.
DEMARCATION_RING_Z_MM = ACTIVE_WALL_HEIGHT_MM + 0.60
DEMARCATION_RING_AXIAL_WIDTH_MM = 0.60
DEMARCATION_RING_SEGMENT_SPAN_DEG = 30.0
DEMARCATION_RING_RADIAL_OVERSHOOT_MM = 0.30

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
    "Optimized V15 uses exactly one axial sight-hole row."
)

require(
    SIGHT_Z_LEVELS_MM[0] - SIGHT_HOLE_RADIUS_MM > ACTIVE_WALL_HEIGHT_MM,
    "Sight-hole row must remain completely above the active Nipkow region."
)

require(
    abs(ARC_BOUNDARY_RIDGE_TANGENTIAL_WIDTH_MM - 0.50) < 1e-9,
    "Sector-boundary vertical ridges must be 0.5 mm wide."
)

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
    "78 mm / 30-row geometry must leave exactly 0.5 mm at the top."
)

require(
    abs(
        LED_CHANNEL_WIDTH_MM
        + FRESNEL_FIN_AXIAL_WIDTH_MM
        - ROW_PITCH_MM
    ) < 1e-8,
    "LED channel + separator fin must equal 2.6 mm pitch."
)

require(
    abs(END_LED_LIP_WIDTH_MM - 0.45) < 1e-8,
    "Expected 0.45 mm end retaining lip from 1.7 mm LED channels."
)

require(
    INNER_FIN_OUTER_RADIUS_MM < OUTER_DRUM_INNER_RADIUS_MM,
    "Inner Fresnel fin tips collide with rotating drum."
)

RADIAL_CLEARANCE_MM = (
    OUTER_DRUM_INNER_RADIUS_MM
    - INNER_FIN_OUTER_RADIUS_MM
)

require(
    MARKING_DEPTH_MM > OUTER_BASE_THICKNESS_MM,
    "Outer registration markings must fully cut through the base."
)

require(
    MARKING_DEPTH_MM > INNER_MARKING_FLANGE_THICKNESS_MM,
    "Inner registration markings must fully cut through the flange."
)

require(
    DEMARCATION_RING_SEGMENT_SPAN_DEG < SECTOR_REPEAT_DEG,
    "Through demarcation arcs must leave a structural bridge in every sector."
)

require(
    INNER_36_ARC_SLOT_SPAN_DEG < SECTOR_REPEAT_DEG,
    "Inner through-cut sector arcs must leave structural bridges."
)

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


def make_slanted_annular_fin(
    name,
    r_inner,
    r_outer,
    angle_start_deg,
    angle_end_deg,
    z_center_inner,
    z_center_outer,
    axial_width,
    segments=20,
):
    """
    Fresnel-like separator fin.

    The inner edge is centered at z_center_inner.
    The outer edge is centered at z_center_outer.

    Thus upper fins can lean downward and lower fins can lean upward while
    the LED channel centers remain locked to the Nipkow row pitch.
    """
    require(r_outer > r_inner, "Fin outer radius must exceed inner.")
    require(axial_width > 0.0, "Fin width must be positive.")

    a0 = math.radians(angle_start_deg)
    a1 = math.radians(angle_end_deg)

    zi0 = z_center_inner - axial_width * 0.5
    zi1 = z_center_inner + axial_width * 0.5

    zo0 = z_center_outer - axial_width * 0.5
    zo1 = z_center_outer + axial_width * 0.5

    verts = []

    for i in range(segments + 1):
        t = i / segments
        a = a0 + t * (a1 - a0)

        ca = math.cos(a)
        sa = math.sin(a)

        verts.extend([
            (r_inner * ca, r_inner * sa, zi0),
            (r_inner * ca, r_inner * sa, zi1),
            (r_outer * ca, r_outer * sa, zo0),
            (r_outer * ca, r_outer * sa, zo1),
        ])

    faces = []

    for i in range(segments):
        j = i * 4
        k = (i + 1) * 4

        faces.append((j + 0, k + 0, k + 1, j + 1))
        faces.append((j + 2, j + 3, k + 3, k + 2))
        faces.append((j + 0, j + 2, k + 2, k + 0))
        faces.append((j + 1, k + 1, k + 3, j + 3))

    faces.append((0, 1, 3, 2))

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


def make_slanted_full_ring(
    name,
    r_inner,
    r_outer,
    z_center_inner,
    z_center_outer,
    axial_width,
    segments=96,
):
    """
    Closed 360-degree slanted annular ring.

    Unlike make_slanted_annular_fin(), this has NO angular end caps and
    closes cleanly around 360 degrees. The inner and outer ring edges may
    have different Z centers, producing the Fresnel-like axial tilt.
    """
    require(r_outer > r_inner, "Ring outer radius must exceed inner.")
    require(axial_width > 0.0, "Ring width must be positive.")
    require(segments >= 12, "Full ring needs at least 12 segments.")

    zi0 = z_center_inner - axial_width * 0.5
    zi1 = z_center_inner + axial_width * 0.5

    zo0 = z_center_outer - axial_width * 0.5
    zo1 = z_center_outer + axial_width * 0.5

    verts = []

    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        ca = math.cos(a)
        sa = math.sin(a)

        verts.extend([
            (r_inner * ca, r_inner * sa, zi0),
            (r_inner * ca, r_inner * sa, zi1),
            (r_outer * ca, r_outer * sa, zo0),
            (r_outer * ca, r_outer * sa, zo1),
        ])

    faces = []

    for i in range(segments):
        ni = (i + 1) % segments

        j = i * 4
        k = ni * 4

        # inner cylindrical face
        faces.append((j + 0, k + 0, k + 1, j + 1))
        # outer cylindrical face
        faces.append((j + 2, j + 3, k + 3, k + 2))
        # lower slanted annular face
        faces.append((j + 0, j + 2, k + 2, k + 0))
        # upper slanted annular face
        faces.append((j + 1, k + 1, k + 3, j + 3))

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


def create_active_window_fences():
    """
    Two outward-flared vertical fences per 36 degree sector.

    At the inner carrier surface they begin at the nominal 25 degree
    window edges (+/-12.5 deg). At the fin-tip radius they flare outward
    to the shared 36 degree sector boundaries (+/-18 deg).
    """
    fences = []
    r0 = INNER_CARRIER_RADIUS_MM - ACTIVE_WINDOW_FENCE_BODY_OVERLAP_MM
    r1 = INNER_FIN_OUTER_RADIUS_MM + ACTIVE_WINDOW_FENCE_TIP_OVERLAP_MM

    for sector in range(SECTOR_COUNT):
        c = sector_center_angle_deg(sector)
        for side_index, sign in enumerate((-1.0, +1.0)):
            a0 = math.radians(c + sign * LED_ACTIVE_HALF_ARC_DEG)
            a1 = math.radians(c + sign * (SECTOR_REPEAT_DEG * 0.5))
            p0 = (r0 * math.cos(a0), r0 * math.sin(a0))
            p1 = (r1 * math.cos(a1), r1 * math.sin(a1))

            fence = add_xy_segment_box(
                name=f"ACTIVE_WINDOW_FENCE_{sector:02d}_{side_index:01d}",
                p0=p0,
                p1=p1,
                tangential_width=ACTIVE_WINDOW_FENCE_WIDTH_MM,
                z_center=ACTIVE_WINDOW_FENCE_HEIGHT_MM * 0.5,
                z_depth=ACTIVE_WINDOW_FENCE_HEIGHT_MM,
            )
            fences.append(fence)

    require(len(fences) == SECTOR_COUNT * 2, "Expected two active-window fences per sector.")
    return fences


def create_arc_boundary_ridges():
    """
    Create 10 shared 0.5 mm axial ribs at the 36 degree sector boundaries.

    Boundary angles:
        18, 54, 90, ... 342 degrees

    The end ridge of one sector is the start ridge of the next, so there
    are 10 physical ridges, not 20 overlapping ridges.
    """
    ridges = []

    radial_length = (
        ARC_BOUNDARY_RIDGE_RADIAL_HEIGHT_MM
        + ARC_BOUNDARY_RIDGE_BODY_OVERLAP_MM
    )

    radial_center = (
        INNER_CARRIER_RADIUS_MM
        - ARC_BOUNDARY_RIDGE_BODY_OVERLAP_MM
        + radial_length * 0.5
    )

    for index in range(SECTOR_BOUNDARY_RIDGE_COUNT):
        angle_deg = (
            SECTOR_BOUNDARY_RIDGE_OFFSET_DEG
            + index * SECTOR_REPEAT_DEG
        ) % 360.0

        ridge = add_radial_cube_cutter(
            name=f"SECTOR_BOUNDARY_RIDGE_{index:02d}",
            angle_deg=angle_deg,
            radial_center=radial_center,
            radial_length=radial_length,
            tangential_width=ARC_BOUNDARY_RIDGE_TANGENTIAL_WIDTH_MM,
            z_center=ARC_BOUNDARY_RIDGE_HEIGHT_MM * 0.5,
            z_depth=ARC_BOUNDARY_RIDGE_HEIGHT_MM,
        )

        ridges.append(ridge)

    require(
        len(ridges) == SECTOR_BOUNDARY_RIDGE_COUNT,
        "Sector-boundary ridge count mismatch."
    )

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
    return sector_index * SECTOR_REPEAT_DEG


def row_relative_angle_deg(row_index):
    """
    Row 0  -> -18 degrees
    Row 29 -> +18 degrees
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


def local_pupil_position_for_sector(sector_index):
    """
    Sector-local virtual pupil.

    Each of the ten sectors receives an identical rotated copy of the
    optical geometry. This preserves rotor symmetry.
    """
    a = math.radians(
        sector_center_angle_deg(sector_index)
    )

    pupil_r = (
        OUTER_DRUM_RADIUS_MM
        + PUPIL_DISTANCE_FROM_OUTER_SURFACE_MM
    )

    return Vector((
        pupil_r * math.cos(a),
        pupil_r * math.sin(a),
        ACTIVE_CENTER_Z,
    ))


# =====================================================================
# OUTER NIPKOW CUTTERS
# =====================================================================

def create_nipkow_aperture_cutter_collection():
    """
    300 independent closed cylinders in one V3-style collection.

    The desired outer-surface aperture center remains on the exact
    mechanical scan lattice. Only the tunnel AXIS is changed to point
    toward the sector-local common pupil.
    """
    collection = bpy.data.collections.new(
        "V15_NIPKOW_APERTURE_CUTTERS"
    )
    bpy.context.scene.collection.children.link(collection)

    # Deliberately overshoot both radial wall faces: these are true holes.
    cutter_depth = OUTER_WALL_THICKNESS_MM + 4.0
    require(
        cutter_depth > OUTER_WALL_THICKNESS_MM,
        "Outer sight-hole cutter must fully cross the drum wall."
    )

    cutter_count = 0
    max_tilt_deg = 0.0

    for sector in range(SECTOR_COUNT):
        sector_center_deg = sector_center_angle_deg(sector)
        pupil = local_pupil_position_for_sector(sector)

        for row in range(ROW_COUNT):
            theta_deg = (
                sector_center_deg
                + row_relative_angle_deg(row)
            )
            theta = math.radians(theta_deg)

            z = row_center_z(row)

            # Desired aperture center ON THE OUTER DRUM SURFACE.
            p_outer = Vector((
                OUTER_DRUM_RADIUS_MM * math.cos(theta),
                OUTER_DRUM_RADIUS_MM * math.sin(theta),
                z,
            ))

            # Aim from this exact surface point toward the local pupil.
            direction = pupil - p_outer
            direction.normalize()

            local_radial = Vector((
                math.cos(theta),
                math.sin(theta),
                0.0,
            ))

            dot = max(
                -1.0,
                min(1.0, direction.dot(local_radial))
            )

            tilt_deg = math.degrees(math.acos(dot))
            max_tilt_deg = max(max_tilt_deg, tilt_deg)

            # Place cutter center slightly inward along its own axis.
            # This keeps the axis passing through the intended outer
            # aperture location while ensuring generous wall intersection.
            cutter_center = (
                p_outer
                - direction * (OUTER_WALL_THICKNESS_MM * 0.5)
            )

            q = Vector((0.0, 0.0, 1.0)).rotation_difference(
                direction
            )

            bpy.ops.mesh.primitive_cylinder_add(
                vertices=APERTURE_CIRCLE_VERTICES,
                radius=APERTURE_RADIUS_MM,
                depth=cutter_depth,
                end_fill_type='NGON',
                location=cutter_center,
                rotation=q.to_euler(),
            )

            cutter = bpy.context.active_object
            cutter.name = (
                f"CUT_NIP_S{sector:02d}_R{row:02d}"
            )

            relink_object_only_to_collection(
                cutter,
                collection,
            )

            cutter_count += 1

    expected = SECTOR_COUNT * ROW_COUNT

    require(
        cutter_count == expected,
        f"Expected {expected} Nipkow cutters, got {cutter_count}."
    )

    require(
        len(collection.objects) == expected,
        "Nipkow cutter collection count mismatch."
    )

    require(
        max_tilt_deg <= MAX_ALLOWED_TUNNEL_TILT_DEG,
        (
            f"Maximum tunnel tilt {max_tilt_deg:.2f} deg exceeds "
            f"allowed {MAX_ALLOWED_TUNNEL_TILT_DEG:.2f} deg."
        )
    )

    print(
        f"  Maximum 3D Nipkow tunnel tilt: "
        f"{max_tilt_deg:.3f} degrees"
    )

    bpy.context.view_layer.update()

    return collection


# =====================================================================
# OUTER SIGHT-HOLE + DEMARCATION CUTTERS
# =====================================================================

def create_outer_sight_hole_collection():
    collection = bpy.data.collections.new(
        "V15_OUTER_SIGHT_THROUGH_CUTTERS"
    )
    bpy.context.scene.collection.children.link(collection)

    radius_mid = (
        OUTER_DRUM_RADIUS_MM
        + OUTER_DRUM_INNER_RADIUS_MM
    ) * 0.5

    cutter_depth = (
        OUTER_WALL_THICKNESS_MM
        + 4.0
    )

    count = 0

    for sector in range(SECTOR_COUNT):
        a = (
            sector_center_angle_deg(sector)
            + SIGHT_REL_ANGLE_DEG
        )

        for z in SIGHT_Z_LEVELS_MM:
            cutter = add_radial_cylinder_cutter(
                f"CUT_OUTER_SIGHT_{sector:02d}_{count:02d}",
                a,
                radius_mid,
                z,
                SIGHT_HOLE_RADIUS_MM,
                cutter_depth,
            )

            relink_object_only_to_collection(
                cutter,
                collection,
            )

            count += 1

    require(
        count == SECTOR_COUNT * len(SIGHT_Z_LEVELS_MM),
        "Outer sight-hole count mismatch."
    )

    return collection




def create_outer_demarcation_ring_collection():
    """
    Ten balanced THROUGH-CUT arc slots marking the end of the active Nipkow
    region.  A continuous 360 degree through-slot would sever the 6 mm
    alignment collar from the drum, so each 36 degree sector retains a
    symmetric 6 degree structural bridge.
    """
    collection = bpy.data.collections.new(
        "V15_OUTER_DEMARCATION_THROUGH_CUTTERS"
    )
    bpy.context.scene.collection.children.link(collection)

    r_inner = (
        OUTER_DRUM_INNER_RADIUS_MM
        - DEMARCATION_RING_RADIAL_OVERSHOOT_MM
    )
    r_outer = (
        OUTER_DRUM_RADIUS_MM
        + DEMARCATION_RING_RADIAL_OVERSHOOT_MM
    )

    z0 = DEMARCATION_RING_Z_MM - DEMARCATION_RING_AXIAL_WIDTH_MM * 0.5
    z1 = DEMARCATION_RING_Z_MM + DEMARCATION_RING_AXIAL_WIDTH_MM * 0.5

    for sector in range(SECTOR_COUNT):
        center = sector_center_angle_deg(sector)
        cutter = make_annular_sector_prism(
            name=f"CUT_OUTER_DEMARCATION_{sector:02d}",
            r_inner=r_inner,
            r_outer=r_outer,
            angle_start_deg=center - DEMARCATION_RING_SEGMENT_SPAN_DEG * 0.5,
            angle_end_deg=center + DEMARCATION_RING_SEGMENT_SPAN_DEG * 0.5,
            z_bottom=z0,
            z_top=z1,
            segments=ARC_SEGMENTS,
        )
        relink_object_only_to_collection(cutter, collection)

    require(
        len(collection.objects) == SECTOR_COUNT,
        "Demarcation through-cut count mismatch."
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

    # 25-degree optical arc + 6-degree precision arc repeated in all sectors.
    for sector in range(SECTOR_COUNT):
        c = sector_center_angle_deg(sector)

        add_top_surface_arc_to_collection(
            collection,
            f"CUT_OUTER_25_ARC_{sector:02d}",
            c,
            LED_ACTIVE_ARC_DEG,
            OUTER_25_ARC_R_INNER_MM,
            OUTER_25_ARC_R_OUTER_MM,
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

    # 25-degree optical boundaries, symmetric +/- 12.5.
    for sector in range(SECTOR_COUNT):
        c = sector_center_angle_deg(sector)

        for side_index, da in enumerate(
            (-LED_ACTIVE_HALF_ARC_DEG, LED_ACTIVE_HALF_ARC_DEG)
        ):
            add_top_surface_tick_to_collection(
                collection,
                f"CUT_MARK_25_{sector:02d}_{side_index}",
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
    Stationary flange shows nested 36 / 25 / 6 degree arcs.

    The complete 36 / 25 / 6 degree reference is repeated in all ten
    36 degree sectors so the stationary carrier matches the rotor pattern.
    """
    collection = bpy.data.collections.new(
        "V15_INNER_FLANGE_MARKINGS"
    )
    bpy.context.scene.collection.children.link(collection)

    for sector in range(SECTOR_COUNT):
        center = sector_center_angle_deg(sector)
        add_top_surface_arc_to_collection(
            collection,
            f"CUT_INNER_36_ARC_{int(center):03d}",
            center,
            INNER_36_ARC_SLOT_SPAN_DEG,
            INNER_36_ARC_R_INNER_MM,
            INNER_36_ARC_R_OUTER_MM,
            flange_top_z,
        )

        add_top_surface_arc_to_collection(
            collection,
            f"CUT_INNER_25_ARC_{int(center):03d}",
            center,
            25.0,
            INNER_25_ARC_R_INNER_MM,
            INNER_25_ARC_R_OUTER_MM,
            flange_top_z,
        )

        add_top_surface_arc_to_collection(
            collection,
            f"CUT_INNER_6_ARC_{int(center):03d}",
            center,
            6.0,
            INNER_6_ARC_R_INNER_MM,
            INNER_6_ARC_R_OUTER_MM,
            flange_top_z,
        )

        # Center line.
        add_top_surface_tick_to_collection(
            collection,
            f"CUT_INNER_CENTER_{int(center):03d}",
            center,
            29.4,
            34.3,
            flange_top_z,
            width=1.00,
        )

        # +/-18, +/-12.5, +/-3 around this optical reference.
        for tag, half_span, width, r0, r1 in (
            ("36", 18.0, 1.00, 29.5, 34.2),
            ("25", 12.5, 0.80, 30.7, 34.0),
            ("06", 3.0, 0.70, 32.0, 33.8),
        ):
            for side_index, da in enumerate((-half_span, half_span)):
                add_top_surface_tick_to_collection(
                    collection,
                    (
                        f"CUT_INNER_{tag}_EDGE_"
                        f"{int(center):03d}_{side_index}"
                    ),
                    center + da,
                    r0,
                    r1,
                    flange_top_z,
                    width=width,
                )

        # Sight-line tick in the structural margin.
        add_top_surface_tick_to_collection(
            collection,
            f"CUT_INNER_SIGHT_MARK_{int(center):03d}",
            center + SIGHT_REL_ANGLE_DEG,
            30.0,
            34.2,
            flange_top_z,
            width=0.80,
        )

    return collection


# =====================================================================
# INNER FRESNEL-LIKE SEPARATOR FINS
# =====================================================================

def fresnel_outer_center_z(z_inner_center):
    """
    Axial convergence toward ACTIVE_CENTER_Z.

    Because alpha = atan((zc-z)/L), then:
        tan(alpha) = (zc-z)/L

    Across the 2 mm radial fin height the outer edge shifts:
        dz = h * (zc-z)/L

    Thus top fins lean down and bottom fins lean up.
    """
    return (
        z_inner_center
        + FRESNEL_FIN_RADIAL_HEIGHT_MM
        * (
            (ACTIVE_CENTER_Z - z_inner_center)
            / INNER_TO_PUPIL_RADIAL_MM
        )
    )


def create_fresnel_separator_fins():
    """
    Returns a list of fin objects.

    30 LED channels are centered exactly at the aperture row centers.
    Therefore 29 full-width separator fins lie halfway between rows.

    Two narrow end lips retain the first/last LED strips.
    """
    fins = []

    r_inner = (
        INNER_CARRIER_RADIUS_MM
        - FRESNEL_FIN_BODY_OVERLAP_MM
    )
    r_outer = INNER_FIN_OUTER_RADIUS_MM

    # Fresnel separator geometry is now a complete 360-degree ring.

    # Bottom retaining lip.
    bottom_z = END_LED_LIP_WIDTH_MM * 0.5
    bottom_outer_z = fresnel_outer_center_z(bottom_z)

    fins.append(
        make_slanted_full_ring(
            "FRESNEL_END_LIP_BOTTOM",
            r_inner,
            r_outer,
            bottom_z,
            bottom_outer_z,
            END_LED_LIP_WIDTH_MM,
            segments=max(DRUM_CIRCLE_VERTICES // 2, 48),
        )
    )

    # 29 internal separator fins between 30 LED channels.
    for i in range(ROW_COUNT - 1):
        z0 = row_center_z(i)
        z1 = row_center_z(i + 1)

        fin_center = (z0 + z1) * 0.5
        outer_center = fresnel_outer_center_z(fin_center)

        fin = make_slanted_full_ring(
            f"FRESNEL_SEPARATOR_{i:02d}",
            r_inner,
            r_outer,
            fin_center,
            outer_center,
            FRESNEL_FIN_AXIAL_WIDTH_MM,
            segments=max(DRUM_CIRCLE_VERTICES // 2, 48),
        )

        fins.append(fin)

    # Top retaining lip.
    top_lip_start = (
        LAST_ROW_CENTER_Z
        + LED_CHANNEL_WIDTH_MM * 0.5
    )

    top_width = ACTIVE_WALL_HEIGHT_MM - top_lip_start
    top_z = top_lip_start + top_width * 0.5
    top_outer_z = fresnel_outer_center_z(top_z)

    fins.append(
        make_slanted_full_ring(
            "FRESNEL_END_LIP_TOP",
            r_inner,
            r_outer,
            top_z,
            top_outer_z,
            top_width,
            segments=max(DRUM_CIRCLE_VERTICES // 2, 48),
        )
    )

    expected = (ROW_COUNT - 1) + 2

    require(
        len(fins) == expected,
        f"Expected {expected} Fresnel fins/lips, got {len(fins)}."
    )

    return fins


# =====================================================================
# INNER SIGHT HOLES
# =====================================================================

def create_inner_sight_hole_collection():
    """One circumferential row of ten holes matching the rotor sectors."""
    collection = bpy.data.collections.new(
        "V15_INNER_SIGHT_THROUGH_CUTTERS"
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
# BUILD OUTER ROTATING DRUM
# =====================================================================

def create_outer_drum():
    print("")
    print("Building OUTER V15 rotating drum...")

    # --------------------------------------------------------------
    # 1) 78 mm tall hollow shell.
    # --------------------------------------------------------------
    shell = add_cylinder(
        "OUTER_SHELL_SOLID",
        radius=OUTER_DRUM_RADIUS_MM,
        depth=TOTAL_CYLINDER_HEIGHT_MM,
        location=(
            0.0,
            0.0,
            TOTAL_CYLINDER_HEIGHT_MM * 0.5,
        ),
        vertices=DRUM_CIRCLE_VERTICES,
    )

    cavity = add_cylinder(
        "CUT_OUTER_SHELL_CAVITY",
        radius=OUTER_DRUM_INNER_RADIUS_MM,
        depth=TOTAL_CYLINDER_HEIGHT_MM + 2.0,
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
        depth=OUTER_HUB_LENGTH_MM,
        location=(
            0.0,
            0.0,
            -OUTER_BASE_THICKNESS_MM
            - OUTER_HUB_LENGTH_MM * 0.5,
        ),
        vertices=128,
    )

    # --------------------------------------------------------------
    # 4) D bore through base + hub.
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

    # --------------------------------------------------------------
    # 5) V13 progressive rotational encoder.
    # --------------------------------------------------------------
    print("  Cutting 80 V13-style encoder slots...")

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
    # 6) Symmetric THROUGH-CUT base registration markings.
    # --------------------------------------------------------------
    print("  Cutting symmetric registration markings fully through base...")

    mark_collection = create_outer_base_marking_collection()

    boolean_collection(
        base,
        mark_collection,
        'DIFFERENCE',
        "Carve_outer_registration_marks",
    )

    delete_collection_and_objects(mark_collection)

    # --------------------------------------------------------------
    # 7) 300 dual-steering Nipkow tunnels.
    # --------------------------------------------------------------
    print("  Creating 300 dual-steering Nipkow aperture cutters...")

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
        "Cut_all_V15_Nipkow_tunnels",
    )

    delete_collection_and_objects(nipkow_collection)

    # --------------------------------------------------------------
    # 8) Segmented circumferential demarcation ring.  Every segment is
    #    a TRUE THROUGH-CUT and is applied AFTER the Nipkow Boolean.
    #    Ten equal bridges prevent the collar from being severed.
    # --------------------------------------------------------------
    print("  Cutting balanced through-slot demarcation ring...")
    demarcation_collection = create_outer_demarcation_ring_collection()
    boolean_collection(
        shell, demarcation_collection, 'DIFFERENCE',
        "Cut_outer_demarcation_through_slots",
    )
    delete_collection_and_objects(demarcation_collection)

    # --------------------------------------------------------------
    # 9) One balanced circumferential row of optical alignment holes.
    # --------------------------------------------------------------
    print("  Cutting one circumferential row of sight holes...")
    sight_collection = create_outer_sight_hole_collection()
    boolean_collection(
        shell, sight_collection, 'DIFFERENCE',
        "Cut_outer_sight_holes",
    )
    delete_collection_and_objects(sight_collection)

    # --------------------------------------------------------------
    # 10) Join into one outer PRINT object.
    # Structural Boolean UNION is deliberately avoided because earlier
    # versions showed collapse problems. Meshes overlap/touch and modern
    # slicers normally merge them.
    # --------------------------------------------------------------
    outer = join_objects(
        [shell, base, hub],
        shell,
        "OUTER_DRUM_PRINTABLE",
    )

    for poly in outer.data.polygons:
        poly.use_smooth = False

    outer.data.validate(verbose=False)
    outer.data.update()

    return outer


# =====================================================================
# BUILD INNER STATIONARY FRESNEL-LIKE LED CARRIER
# =====================================================================

def create_inner_led_carrier():
    print("")
    print("Building INNER V15 Fresnel-like LED carrier...")

    # --------------------------------------------------------------
    # 1) 78 mm hollow inner carrier body.
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
    # 3) Fresnel-like separator fins.
    #
    # NOTE:
    # There are 30 LED channels but only 29 full internal separators.
    # The channels are the 1.7 mm gaps and are CENTERED exactly on the
    # same 30 row centers as the outer Nipkow apertures.
    # --------------------------------------------------------------
    print(
        "  Creating 30 aligned LED channels "
        "with slanted separator fins..."
    )

    fins = create_fresnel_separator_fins()

    # Two outward-flared side fences per 36 degree sector. Each begins at
    # the nominal +/-12.5 degree active-window edge and reaches the shared
    # +/-18 degree sector boundary at the fin-tip radius.
    active_window_fences = create_active_window_fences()

    # Ten shared 0.5 mm axial ridges mark the 36 degree boundaries.
    arc_boundary_ridges = create_arc_boundary_ridges()

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
    # 5) Larger stationary marking flange at Z = 80..82.
    # This lies above the rotating drum rim and does not need to pass
    # through the 62 mm drum ID.
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
    # 8) THROUGH-CUT nested 36 / 25 / 6 degree optical registration marks
    # on stationary flange.
    # --------------------------------------------------------------
    print("  Cutting stationary 36/25/6 optical markings fully through flange...")

    mark_collection = create_inner_flange_marking_collection(
        flange_top_z=flange_z1
    )

    boolean_collection(
        flange,
        mark_collection,
        'DIFFERENCE',
        "Carve_inner_registration_marks",
    )

    delete_collection_and_objects(mark_collection)

    # --------------------------------------------------------------
    # 9) Join all inner pieces into one separate printable object.
    # --------------------------------------------------------------
    inner_parts = (
        [body]
        + fins
        + active_window_fences
        + arc_boundary_ridges
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

    for poly in inner.data.polygons:
        poly.use_smooth = False

    inner.data.validate(verbose=False)
    inner.data.update()

    return inner


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
print("NIPKOW DRUM LITHOGRAPHY V15")
print("DUAL STEERING + OPTICAL REGISTRATION + SYMMETRIC MARKINGS")
print("=" * 88)

print("")
print("MASTER ROW GEOMETRY")
print(f"  Active wall height              : {ACTIVE_WALL_HEIGHT_MM:.3f} mm")
print(f"  Row count                       : {ROW_COUNT}")
print(f"  Row pitch                       : {ROW_PITCH_MM:.3f} mm")
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
print(f"  Separate base                   : {OUTER_BASE_THICKNESS_MM:.3f} mm")
print(f"  Nipkow apertures                : {SECTOR_COUNT * ROW_COUNT}")
print(f"  Encoder slots                   : {TOTAL_ENCODER_SLOTS}")
print(f"  Registration marking cut depth  : {MARKING_DEPTH_MM:.3f} mm THROUGH")
print(
    f"  Wall/base left under 0.6 mark   : "
    f"{OUTER_BASE_THICKNESS_MM - MARKING_DEPTH_MM:.3f} mm"
)

print("")
print("INNER FRESNEL-LIKE CARRIER")
print(f"  Carrier OD                      : {INNER_CARRIER_OD_MM:.3f} mm")
print(f"  Carrier ID                      : {INNER_CARRIER_ID_MM:.3f} mm")
print(f"  LED channels                    : {ROW_COUNT}")
print(f"  LED channel width               : {LED_CHANNEL_WIDTH_MM:.3f} mm")
print(f"  Internal separator width        : {FRESNEL_FIN_AXIAL_WIDTH_MM:.3f} mm")
print(f"  Fin radial height               : {FRESNEL_FIN_RADIAL_HEIGHT_MM:.3f} mm")
print(f"  Fin-tip OD                      : {2*INNER_FIN_OUTER_RADIUS_MM:.3f} mm")
print(f"  Nominal radial drum clearance   : {RADIAL_CLEARANCE_MM:.3f} mm")
print(f"  Fresnel ridge circumference     : {FRESNEL_FIN_ARC_DEG:.3f} deg")
print(
    f"  Vertical sector ridges          : "
    f"{SECTOR_BOUNDARY_RIDGE_COUNT} x every {SECTOR_REPEAT_DEG:.3f} deg"
)
print(
    f"  Sector-boundary ridge width     : "
    f"{ARC_BOUNDARY_RIDGE_TANGENTIAL_WIDTH_MM:.3f} mm"
)
print(f"  Outward active-window fences    : {SECTOR_COUNT * 2}")
print(
    f"  First sector-boundary ridge     : "
    f"{SECTOR_BOUNDARY_RIDGE_OFFSET_DEG:.3f} deg"
)
print(f"  Bottom/top end lip width        : {END_LED_LIP_WIDTH_MM:.3f} mm")

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
    "  A balanced segmented through-cut demarcation ring separates the active "
    "Nipkow region from the alignment collar."
)
print(
    "  Sight holes can also be used as an optical alignment channel "
    "with a visible/IR LED + photodiode."
)
print("=" * 88)

outer = create_outer_drum()
inner = create_inner_led_carrier()

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
        "V15 cutter cleanup failed. Leftover CUT_ objects: "
        + ", ".join(leftover_cutters[:20])
    )

print("")
print("=" * 88)
print("V15 SELF VALIDATION: PASS")
print("=" * 88)
print(f"Outer object                     : {outer.name}")
print(f"Inner object                     : {inner.name}")
print("Outer/inner remain separate for independent printing.")
print("")
print("ROW ALIGNMENT:")
print(f"  outer row pitch                : {ROW_PITCH_MM:.3f} mm")
print(f"  inner LED channel pitch        : {ROW_PITCH_MM:.3f} mm")
print(f"  row/channel count              : {ROW_COUNT}/{ROW_COUNT}")
print("")
print("ANGULAR REFERENCES:")
print(f"  sector                         : 36.0 deg")
print(f"  LED illumination               : 25.0 deg")
print(f"  precision gate                 : 6.0 deg")
print(f"  sight registration line        : +{SIGHT_REL_ANGLE_DEG:.1f} deg")
print("")
print("IMPORTANT:")
print(
    "  The 25 deg illumination arc and 6 deg precision gate are "
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
        print(
            "Outer STL automatic export failed:",
            repr(exc)
        )

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
        print(
            "Inner STL automatic export failed:",
            repr(exc)
        )

# Select both final objects for inspection.
deselect_all()
outer.select_set(True)
inner.select_set(True)
bpy.context.view_layer.objects.active = outer

print("")
print("V15 COMPLETE")
print("Inspect single-row sight alignment, demarcation ring, sector fences and fins before slicing.")
