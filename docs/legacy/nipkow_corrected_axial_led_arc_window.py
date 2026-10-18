# ======================================================================
# CORRECTED HELICAL-SLIT NIPKOW DRUM SIMULATION
# ======================================================================
# Corrected geometry:
#   • Drum axis is HORIZONTAL along world X.
#   • The stationary 25 mm inner core is coaxial with the outer drum.
#   • LEDs are NOT arranged around the circumference.
#   • LEDs form one STRAIGHT AXIAL LINE along the drum length.
#   • Each LED stands RADIAL / VERTICAL at the bottom of the core.
#   • A separate THIN CURVED ARC WINDOW / REFLECTOR runs along the same
#     axial length above the LED line.
#   • The outer drum carries one continuous helical slit.
#   • A simple smiley raster animation is pre-keyed.
#
# Workflow:
#   1. Open Blender -> Scripting
#   2. Paste this whole file into a new text block
#   3. Run Script
#   4. Press PLAY
#
# No external packages or add-ons are required.
# No Action.fcurves access is used.
# ======================================================================

import bpy
import math
from mathutils import Vector

# ======================================================================
# 1. USER PARAMETERS
# ======================================================================

# Mechanical geometry
INNER_CORE_DIAMETER_MM = 25.0
OUTER_DRUM_DIAMETER_MM = 45.0
DRUM_LENGTH_MM          = 100.0

# Outer helical slit
SLIT_WIDTH_MM           = 0.30
HELIX_TURNS             = 1.0
HELIX_SAMPLES           = 600

# Axial LED strip
LED_COUNT               = 16
LED_PACKAGE_X_MM        = 1.60   # size along drum axis
LED_PACKAGE_Y_MM        = 1.60   # tangential width
LED_VISUAL_HEIGHT_MM    = 1.20   # radial height; slightly exaggerated for visibility
LED_STRIP_MARGIN_MM     = 6.0

# Thin curved arc window / reflector
ARC_WINDOW_DEG          = 36.0   # angular width around the lower part of core
ARC_INNER_RADIUS_MM     = 15.0   # radial position from axis
ARC_THICKNESS_MM        = 0.55
ARC_AXIAL_MARGIN_MM     = 4.0

# Raster display
RASTER_X                = 24
RASTER_Y                = LED_COUNT
PIXEL_PITCH_X_MM        = 2.00
PIXEL_PITCH_Y_MM        = 3.00
PIXEL_FILL              = 0.82

# Animation
FPS                     = 30
FRAMES_PER_PIXEL        = 1
START_FRAME             = 1
TARGET_RPM              = 2000.0

# For a visible Blender demo, one raster row = one visible drum revolution.
VISIBLE_REVOLUTIONS     = float(RASTER_Y)

# Projection screen
SCREEN_Z_MM             = -86.0
SCREEN_Y_OFFSET_MM      = 0.0

# ======================================================================
# 2. UNITS
# ======================================================================

MM = 0.001

INNER_CORE_DIAMETER = INNER_CORE_DIAMETER_MM * MM
OUTER_DRUM_DIAMETER = OUTER_DRUM_DIAMETER_MM * MM
DRUM_LENGTH          = DRUM_LENGTH_MM * MM

CORE_RADIUS = INNER_CORE_DIAMETER * 0.5
DRUM_RADIUS = OUTER_DRUM_DIAMETER * 0.5

SLIT_WIDTH = SLIT_WIDTH_MM * MM

LED_X = LED_PACKAGE_X_MM * MM
LED_Y = LED_PACKAGE_Y_MM * MM
LED_H = LED_VISUAL_HEIGHT_MM * MM

ARC_INNER_RADIUS = ARC_INNER_RADIUS_MM * MM
ARC_THICKNESS    = ARC_THICKNESS_MM * MM
ARC_OUTER_RADIUS = ARC_INNER_RADIUS + ARC_THICKNESS

PIXEL_PITCH_X = PIXEL_PITCH_X_MM * MM
PIXEL_PITCH_Y = PIXEL_PITCH_Y_MM * MM
SCREEN_Z      = SCREEN_Z_MM * MM
SCREEN_Y_OFFSET = SCREEN_Y_OFFSET_MM * MM

TOTAL_PIXELS = RASTER_X * RASTER_Y
END_FRAME = START_FRAME + TOTAL_PIXELS * FRAMES_PER_PIXEL + 12

# ======================================================================
# 3. CLEAN SCENE
# ======================================================================

try:
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
except Exception:
    pass

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.frame_start = START_FRAME
scene.frame_end = END_FRAME
scene.render.fps = FPS
scene.frame_set(START_FRAME)
scene.world.color = (0.008, 0.010, 0.014)

# ======================================================================
# 4. MATERIALS
# ======================================================================

def get_socket(node, names):
    for n in names:
        if n in node.inputs:
            return node.inputs[n]
    return None

def make_material(name, base_rgba, metallic=0.0, roughness=0.45,
                  emission_rgb=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True

    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        s = get_socket(bsdf, ["Base Color"])
        if s:
            s.default_value = base_rgba

        s = get_socket(bsdf, ["Metallic"])
        if s:
            s.default_value = metallic

        s = get_socket(bsdf, ["Roughness"])
        if s:
            s.default_value = roughness

        if emission_rgb is not None:
            s = get_socket(bsdf, ["Emission Color", "Emission"])
            if s:
                s.default_value = (
                    emission_rgb[0],
                    emission_rgb[1],
                    emission_rgb[2],
                    1.0
                )
            s = get_socket(bsdf, ["Emission Strength"])
            if s:
                s.default_value = emission_strength

    mat.diffuse_color = base_rgba
    return mat


MAT_DRUM = make_material(
    "MAT_DRUM",
    (0.035, 0.045, 0.060, 1.0),
    metallic=0.35,
    roughness=0.30
)

MAT_CORE = make_material(
    "MAT_CORE",
    (0.11, 0.12, 0.14, 1.0),
    metallic=0.20,
    roughness=0.42
)

MAT_FRAME = make_material(
    "MAT_FRAME",
    (0.15, 0.16, 0.18, 1.0),
    metallic=0.65,
    roughness=0.28
)

MAT_LED = make_material(
    "MAT_LED",
    (0.04, 0.65, 0.12, 1.0),
    roughness=0.25,
    emission_rgb=(0.02, 1.0, 0.08),
    emission_strength=5.0
)

MAT_ACTIVE_LED = make_material(
    "MAT_ACTIVE_LED",
    (1.0, 0.20, 0.03, 1.0),
    roughness=0.20,
    emission_rgb=(1.0, 0.05, 0.01),
    emission_strength=7.0
)

MAT_ARC = make_material(
    "MAT_ARC_REFLECTOR",
    (0.55, 0.58, 0.62, 1.0),
    metallic=0.85,
    roughness=0.16
)

MAT_SLIT = make_material(
    "MAT_HELIX",
    (0.20, 0.55, 1.0, 1.0),
    roughness=0.20,
    emission_rgb=(0.05, 0.35, 1.0),
    emission_strength=4.0
)

MAT_SCREEN = make_material(
    "MAT_SCREEN",
    (0.025, 0.028, 0.032, 1.0),
    roughness=0.88
)

MAT_GRID = make_material(
    "MAT_GRID",
    (0.060, 0.065, 0.075, 1.0),
    roughness=0.80
)

MAT_PIXEL = make_material(
    "MAT_PIXEL",
    (0.03, 0.85, 0.13, 1.0),
    roughness=0.18,
    emission_rgb=(0.01, 1.0, 0.07),
    emission_strength=6.0
)

MAT_CURSOR = make_material(
    "MAT_CURSOR",
    (1.0, 0.26, 0.02, 1.0),
    roughness=0.18,
    emission_rgb=(1.0, 0.05, 0.01),
    emission_strength=7.0
)

MAT_TEXT = make_material(
    "MAT_TEXT",
    (0.70, 0.76, 0.86, 1.0),
    roughness=0.50
)

# ======================================================================
# 5. GEOMETRY HELPERS
# ======================================================================

def add_cube(name, location, dimensions, material=None, rotation=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=location,
        rotation=rotation
    )
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )
    if material:
        obj.data.materials.append(material)
    return obj


def add_cylinder(name, radius, depth, location, material=None,
                 rotation=(0.0, 0.0, 0.0), vertices=96,
                 open_ended=False):
    kwargs = dict(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation
    )
    if open_ended:
        kwargs["end_fill_type"] = 'NOTHING'

    bpy.ops.mesh.primitive_cylinder_add(**kwargs)
    obj = bpy.context.object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj


def make_poly_curve(name, points, bevel_depth, material):
    curve_data = bpy.data.curves.new(name + "_CURVE", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 1
    curve_data.bevel_depth = bevel_depth
    curve_data.bevel_resolution = 2

    spline = curve_data.splines.new('POLY')
    spline.points.add(len(points) - 1)

    for i, p in enumerate(points):
        spline.points[i].co = (p[0], p[1], p[2], 1.0)

    obj = bpy.data.objects.new(name, curve_data)
    scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def make_arc_shell(name, x_min, x_max, r_inner, r_outer,
                   center_deg, span_deg, segments, material):
    """
    Makes a thin cylindrical ARC SHELL around world-X axis.
    Cross-section is in YZ plane.

    The shell has:
      - inner curved surface
      - outer curved surface
      - two angular side faces
      - two axial end faces
    """
    verts = []
    faces = []

    a0 = math.radians(center_deg - span_deg * 0.5)
    a1 = math.radians(center_deg + span_deg * 0.5)

    # For each angular step we store 4 vertices:
    #   0 = x_min, inner radius
    #   1 = x_max, inner radius
    #   2 = x_min, outer radius
    #   3 = x_max, outer radius
    for i in range(segments + 1):
        u = i / float(segments)
        a = a0 + (a1 - a0) * u

        yi = r_inner * math.cos(a)
        zi = r_inner * math.sin(a)

        yo = r_outer * math.cos(a)
        zo = r_outer * math.sin(a)

        verts.extend([
            (x_min, yi, zi),
            (x_max, yi, zi),
            (x_min, yo, zo),
            (x_max, yo, zo),
        ])

    for i in range(segments):
        b0 = i * 4
        b1 = (i + 1) * 4

        # inner curved surface
        faces.append((b0 + 0, b1 + 0, b1 + 1, b0 + 1))

        # outer curved surface
        faces.append((b0 + 2, b0 + 3, b1 + 3, b1 + 2))

        # x_min edge surface
        faces.append((b0 + 0, b0 + 2, b1 + 2, b1 + 0))

        # x_max edge surface
        faces.append((b0 + 1, b1 + 1, b1 + 3, b0 + 3))

    # angular side faces
    s0 = 0
    s1 = segments * 4

    faces.append((s0 + 0, s0 + 1, s0 + 3, s0 + 2))
    faces.append((s1 + 0, s1 + 2, s1 + 3, s1 + 1))

    mesh = bpy.data.meshes.new(name + "_MESH")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.data.materials.append(material)

    return obj


def add_text(name, body, location, size=0.004, material=None,
             rotation=(0.0, 0.0, 0.0)):
    curve = bpy.data.curves.new(name + "_FONT", type='FONT')
    curve.body = body
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = size
    curve.extrude = 0.00004

    obj = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation

    if material:
        curve.materials.append(material)

    return obj


def point_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# ======================================================================
# 6. MASTER ROTOR
# ======================================================================

rotor = bpy.data.objects.new("ROTOR_MASTER", None)
scene.collection.objects.link(rotor)
rotor.empty_display_type = 'PLAIN_AXES'
rotor.empty_display_size = 0.025
rotor.rotation_mode = 'XYZ'

# ======================================================================
# 7. OUTER DRUM
# ======================================================================

# Blender cylinder is along local Z; rotate it so axis becomes world X.
drum = add_cylinder(
    "OUTER_DRUM",
    DRUM_RADIUS,
    DRUM_LENGTH,
    (0.0, 0.0, 0.0),
    MAT_DRUM,
    rotation=(0.0, math.pi / 2.0, 0.0),
    vertices=160,
    open_ended=True
)
drum.parent = rotor

# end rings
for sx in (-1.0, 1.0):
    ring = add_cylinder(
        "DRUM_END_RING",
        DRUM_RADIUS * 1.01,
        0.0022,
        (sx * DRUM_LENGTH * 0.5, 0.0, 0.0),
        MAT_FRAME,
        rotation=(0.0, math.pi / 2.0, 0.0),
        vertices=128
    )
    ring.parent = rotor

# ======================================================================
# 8. CONTINUOUS HELICAL SLIT
# ======================================================================

helix_pts = []

for i in range(HELIX_SAMPLES):
    u = i / float(HELIX_SAMPLES - 1)

    x = -DRUM_LENGTH * 0.49 + u * DRUM_LENGTH * 0.98

    theta = (
        -math.pi * 0.5
        + HELIX_TURNS * 2.0 * math.pi * u
    )

    r = DRUM_RADIUS + 0.00018

    y = r * math.cos(theta)
    z = r * math.sin(theta)

    helix_pts.append((x, y, z))

helix = make_poly_curve(
    "CONTINUOUS_HELICAL_SLIT",
    helix_pts,
    max(0.000025, SLIT_WIDTH * 0.5),
    MAT_SLIT
)
helix.parent = rotor

# ======================================================================
# 9. STATIONARY 25 MM CORE + SHAFT
# ======================================================================

core = add_cylinder(
    "STATIONARY_25MM_CORE",
    CORE_RADIUS,
    DRUM_LENGTH * 0.92,
    (0.0, 0.0, 0.0),
    MAT_CORE,
    rotation=(0.0, math.pi / 2.0, 0.0),
    vertices=128
)

shaft = add_cylinder(
    "STATIONARY_SHAFT",
    0.0030,
    DRUM_LENGTH * 1.30,
    (0.0, 0.0, 0.0),
    MAT_FRAME,
    rotation=(0.0, math.pi / 2.0, 0.0),
    vertices=64
)

# ======================================================================
# 10. CORRECT AXIAL LED STRIP
# ======================================================================
#
# IMPORTANT GEOMETRY:
#
# Drum axis = X
#
# LEDs lie in a STRAIGHT LINE along X.
# Each LED stands RADIAL / VERTICAL at the lower side of the core.
#
# Side view:
#
#       | | | | | | | |   LEDs upright
#       | | | | | | | |
#     -------------------  inner core tangent region
#
# Cross-section through one X position:
#
#          arc reflector
#            ______
#          /        \
#              |
#              | LED
#            (CORE)
#
# ======================================================================

strip_length = DRUM_LENGTH - 2.0 * LED_STRIP_MARGIN_MM * MM

if LED_COUNT == 1:
    led_x_positions = [0.0]
else:
    led_x_positions = [
        -strip_length * 0.5 + i * strip_length / (LED_COUNT - 1)
        for i in range(LED_COUNT)
    ]

# LEDs are placed at bottom of core: Y=0, negative Z.
# "Vertical / radial" means their height points outward along -Z.
led_center_z = -(CORE_RADIUS + LED_H * 0.5)

led_objects = []

for i, x in enumerate(led_x_positions):
    led = add_cube(
        f"LED_{i:02d}",
        (x, 0.0, led_center_z),
        (LED_X, LED_Y, LED_H),
        MAT_LED
    )
    led_objects.append(led)

# Thin PCB/strip carrier underneath the LED row.
carrier = add_cube(
    "LED_AXIAL_CARRIER",
    (0.0, 0.0, -(CORE_RADIUS + LED_H + 0.00025)),
    (strip_length + 0.004, LED_Y * 1.35, 0.00045),
    MAT_FRAME
)

# ======================================================================
# 11. CORRECT THIN ARC WINDOW / REFLECTOR
# ======================================================================
#
# This is a cylindrical arc segment coaxial with the drum.
# It runs along X over the whole LED row.
#
# Arc is centered at -90 degrees, i.e. directly below the core.
# ======================================================================

arc_x_min = -strip_length * 0.5 - ARC_AXIAL_MARGIN_MM * MM
arc_x_max = +strip_length * 0.5 + ARC_AXIAL_MARGIN_MM * MM

arc_window = make_arc_shell(
    "THIN_ARC_WINDOW_REFLECTOR",
    arc_x_min,
    arc_x_max,
    ARC_INNER_RADIUS,
    ARC_OUTER_RADIUS,
    center_deg=-90.0,
    span_deg=ARC_WINDOW_DEG,
    segments=64,
    material=MAT_ARC
)

# ======================================================================
# 12. OPTIONAL ACTIVE LED MARKER
# ======================================================================
#
# Marker sits over whichever axial LED is currently being used for that row.
# This makes the strip-to-raster mapping obvious during playback.
# ======================================================================

active_led = add_cube(
    "ACTIVE_LED_MARKER",
    (
        led_x_positions[0],
        0.0,
        led_center_z - 0.00005
    ),
    (
        LED_X * 1.25,
        LED_Y * 1.25,
        LED_H * 1.10
    ),
    MAT_ACTIVE_LED
)

# ======================================================================
# 13. SCREEN + GRID
# ======================================================================

screen_w = RASTER_X * PIXEL_PITCH_X
screen_h = RASTER_Y * PIXEL_PITCH_Y

screen = add_cube(
    "PROJECTION_SCREEN",
    (0.0, SCREEN_Y_OFFSET, SCREEN_Z - 0.0007),
    (screen_w + 0.008, screen_h + 0.008, 0.0010),
    MAT_SCREEN
)

for row in range(RASTER_Y):
    for col in range(RASTER_X):
        x = (col - (RASTER_X - 1) * 0.5) * PIXEL_PITCH_X
        y = SCREEN_Y_OFFSET + (
            (row - (RASTER_Y - 1) * 0.5) * PIXEL_PITCH_Y
        )

        add_cube(
            f"GRID_{row:02d}_{col:02d}",
            (x, y, SCREEN_Z),
            (
                PIXEL_PITCH_X * PIXEL_FILL,
                PIXEL_PITCH_Y * PIXEL_FILL,
                0.00040
            ),
            MAT_GRID
        )

# ======================================================================
# 14. PROCEDURAL SMILEY
# ======================================================================

def smiley_mask(col, row):
    u = ((col + 0.5) / RASTER_X) * 2.0 - 1.0
    v = ((row + 0.5) / RASTER_Y) * 2.0 - 1.0

    r = math.sqrt(u*u + v*v)

    # face outline
    if 0.76 < r < 0.88:
        return True

    # eyes
    eye_y = 0.27
    eye_rx = 0.09
    eye_ry = 0.13

    left_eye = (
        ((u + 0.30) / eye_rx) ** 2 +
        ((v - eye_y) / eye_ry) ** 2
    ) <= 1.0

    right_eye = (
        ((u - 0.30) / eye_rx) ** 2 +
        ((v - eye_y) / eye_ry) ** 2
    ) <= 1.0

    if left_eye or right_eye:
        return True

    # smile
    smile_r = math.sqrt(u*u + (v - 0.02) ** 2)

    if (
        -0.62 < u < 0.62
        and -0.58 < v < -0.02
        and 0.48 < smile_r < 0.60
    ):
        return True

    return False

# ======================================================================
# 15. CREATE SMILEY PIXELS
# ======================================================================

smiley_pixels = {}

for row in range(RASTER_Y):
    for col in range(RASTER_X):
        if not smiley_mask(col, row):
            continue

        x = (col - (RASTER_X - 1) * 0.5) * PIXEL_PITCH_X
        y = SCREEN_Y_OFFSET + (
            (row - (RASTER_Y - 1) * 0.5) * PIXEL_PITCH_Y
        )

        pix = add_cube(
            f"SMILE_{row:02d}_{col:02d}",
            (x, y, SCREEN_Z + 0.00065),
            (
                PIXEL_PITCH_X * PIXEL_FILL,
                PIXEL_PITCH_Y * PIXEL_FILL,
                0.00070
            ),
            MAT_PIXEL
        )

        # Use boolean visibility animation instead of F-curve editing.
        pix.hide_viewport = True
        pix.hide_render = True

        pix.keyframe_insert(
            data_path="hide_viewport",
            frame=START_FRAME
        )
        pix.keyframe_insert(
            data_path="hide_render",
            frame=START_FRAME
        )

        smiley_pixels[(row, col)] = pix

# ======================================================================
# 16. ACTIVE SCAN CURSOR
# ======================================================================

cursor = add_cube(
    "ACTIVE_SCAN_CURSOR",
    (
        -(RASTER_X - 1) * 0.5 * PIXEL_PITCH_X,
        SCREEN_Y_OFFSET - (RASTER_Y - 1) * 0.5 * PIXEL_PITCH_Y,
        SCREEN_Z + 0.0018
    ),
    (
        PIXEL_PITCH_X * 0.42,
        PIXEL_PITCH_Y * 0.42,
        0.0011
    ),
    MAT_CURSOR
)

# ======================================================================
# 17. ANIMATION -- NO Action.fcurves
# ======================================================================

for row in range(RASTER_Y):

    # Axial LED position corresponding to this raster row.
    active_led.location = (
        led_x_positions[row],
        0.0,
        led_center_z - 0.00005
    )

    row_start_frame = START_FRAME + row * RASTER_X * FRAMES_PER_PIXEL

    active_led.keyframe_insert(
        data_path="location",
        frame=row_start_frame
    )

    for col in range(RASTER_X):
        index = row * RASTER_X + col
        frame = START_FRAME + index * FRAMES_PER_PIXEL

        x = (col - (RASTER_X - 1) * 0.5) * PIXEL_PITCH_X
        y = SCREEN_Y_OFFSET + (
            (row - (RASTER_Y - 1) * 0.5) * PIXEL_PITCH_Y
        )

        cursor.location = (x, y, SCREEN_Z + 0.0018)
        cursor.keyframe_insert(
            data_path="location",
            frame=frame
        )

        pix = smiley_pixels.get((row, col))
        if pix is not None:
            # Boolean animation is effectively step-like and avoids
            # accessing Action.fcurves.
            if frame > START_FRAME:
                pix.hide_viewport = True
                pix.hide_render = True
                pix.keyframe_insert(
                    data_path="hide_viewport",
                    frame=frame - 1
                )
                pix.keyframe_insert(
                    data_path="hide_render",
                    frame=frame - 1
                )

            pix.hide_viewport = False
            pix.hide_render = False
            pix.keyframe_insert(
                data_path="hide_viewport",
                frame=frame
            )
            pix.keyframe_insert(
                data_path="hide_render",
                frame=frame
            )

# Rotor rotation:
# key every frame so we do not need to alter interpolation data.
anim_frames = max(1, END_FRAME - START_FRAME)

for frame in range(START_FRAME, END_FRAME + 1):
    u = (frame - START_FRAME) / float(anim_frames)

    rotor.rotation_euler.x = (
        VISIBLE_REVOLUTIONS * 2.0 * math.pi * u
    )

    rotor.keyframe_insert(
        data_path="rotation_euler",
        index=0,
        frame=frame
    )

# ======================================================================
# 18. FRAME / BEARINGS
# ======================================================================

for sx in (-1.0, 1.0):
    x = sx * DRUM_LENGTH * 0.58

    add_cylinder(
        "BEARING",
        0.0105,
        0.0070,
        (x, 0.0, 0.0),
        MAT_FRAME,
        rotation=(0.0, math.pi / 2.0, 0.0),
        vertices=96
    )

    add_cube(
        "SUPPORT",
        (x, 0.0, -0.028),
        (0.008, 0.056, 0.058),
        MAT_FRAME
    )

# ======================================================================
# 19. LABELS
# ======================================================================

add_text(
    "TITLE",
    "CORRECTED AXIAL LED + ARC WINDOW",
    (0.0, -0.074, SCREEN_Z + 0.0012),
    size=0.0042,
    material=MAT_TEXT
)

add_text(
    "LED_LABEL",
    "LEDs: straight along X, standing radially",
    (0.0, -0.081, SCREEN_Z + 0.0012),
    size=0.0026,
    material=MAT_TEXT
)

add_text(
    "ARC_LABEL",
    f"Arc window: {ARC_WINDOW_DEG:.1f} deg",
    (0.0, -0.087, SCREEN_Z + 0.0012),
    size=0.0024,
    material=MAT_TEXT
)

# ======================================================================
# 20. CAMERA
# ======================================================================

bpy.ops.object.camera_add(
    location=(0.165, -0.195, 0.135)
)

camera = bpy.context.object
camera.name = "SIM_CAMERA"
camera.data.lens = 50
point_at(camera, (0.0, 0.0, -0.032))
scene.camera = camera

# ======================================================================
# 21. LIGHTS
# ======================================================================

bpy.ops.object.light_add(
    type='AREA',
    location=(0.06, -0.08, 0.15)
)
key = bpy.context.object
key.name = "KEY_LIGHT"
key.data.energy = 900
key.data.shape = 'DISK'
key.data.size = 0.16
point_at(key, (0.0, 0.0, -0.015))

bpy.ops.object.light_add(
    type='AREA',
    location=(-0.10, 0.08, 0.08)
)
fill = bpy.context.object
fill.name = "FILL_LIGHT"
fill.data.energy = 500
fill.data.size = 0.12
point_at(fill, (0.0, 0.0, -0.020))

# ======================================================================
# 22. METADATA + START FRAME
# ======================================================================

scene["design"] = "axial upright LED strip + thin arc window"
scene["inner_core_diameter_mm"] = INNER_CORE_DIAMETER_MM
scene["outer_drum_diameter_mm"] = OUTER_DRUM_DIAMETER_MM
scene["drum_length_mm"] = DRUM_LENGTH_MM
scene["led_count"] = LED_COUNT
scene["arc_window_deg"] = ARC_WINDOW_DEG
scene["slit_width_mm"] = SLIT_WIDTH_MM
scene["target_rpm"] = TARGET_RPM

scene.frame_set(START_FRAME)

# Try to set material preview in all 3D viewports.
try:
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'MATERIAL'
except Exception:
    pass

# ======================================================================
# 23. REPORT
# ======================================================================

led_pitch = (
    strip_length / (LED_COUNT - 1)
    if LED_COUNT > 1 else strip_length
)

arc_mid_r = (ARC_INNER_RADIUS + ARC_OUTER_RADIUS) * 0.5
arc_cross_section_length = arc_mid_r * math.radians(ARC_WINDOW_DEG)

print("")
print("==============================================================")
print(" CORRECTED NIPKOW SIMULATION READY")
print("==============================================================")
print(f"Blender version            : {bpy.app.version_string}")
print(f"Core diameter              : {INNER_CORE_DIAMETER_MM:.2f} mm")
print(f"Outer drum diameter        : {OUTER_DRUM_DIAMETER_MM:.2f} mm")
print(f"Drum length                : {DRUM_LENGTH_MM:.2f} mm")
print("")
print("LED GEOMETRY")
print("  arrangement              : straight axial line")
print("  axis                     : world X")
print("  orientation              : radial / vertical")
print(f"  count                    : {LED_COUNT}")
print(f"  axial pitch              : {led_pitch / MM:.2f} mm")
print(f"  package                  : {LED_PACKAGE_X_MM:.2f} x {LED_PACKAGE_Y_MM:.2f} mm")
print("")
print("ARC WINDOW / REFLECTOR")
print("  type                     : cylindrical arc shell")
print("  axis                     : world X")
print(f"  angular width            : {ARC_WINDOW_DEG:.2f} deg")
print(f"  inner radius             : {ARC_INNER_RADIUS_MM:.2f} mm")
print(f"  radial thickness         : {ARC_THICKNESS_MM:.2f} mm")
print(f"  cross-section arc length : {arc_cross_section_length / MM:.2f} mm")
print("")
print("OUTER ROTOR")
print(f"  helical slit width       : {SLIT_WIDTH_MM:.3f} mm")
print(f"  visible revolutions      : {VISIBLE_REVOLUTIONS:.1f}")
print(f"  target physical RPM      : {TARGET_RPM:.0f}")
print("")
print("To inspect internals, hide OUTER_DRUM in the Outliner.")
print("Press PLAY to run the raster animation.")
print("==============================================================")
