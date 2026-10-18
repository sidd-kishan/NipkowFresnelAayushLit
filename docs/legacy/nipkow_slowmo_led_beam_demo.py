# ======================================================================
# SLOW-MOTION HELICAL-SLIT NIPKOW DEMO
# ----------------------------------------------------------------------
# Updated for easier viewing:
#   • Much slower animation
#   • Higher viewport FPS
#   • LED flash lasts multiple frames
#   • Visible pulsed ray/beam from helix crossing to screen pixel
#   • Corrected geometry:
#       - horizontal outer drum
#       - stationary 25 mm inner core
#       - straight axial LED strip
#       - LEDs standing radially upright
#       - thin cylindrical arc reflector/window
#
# Workflow:
#   1. Blender -> Scripting
#   2. Paste this entire file
#   3. Run Script
#   4. Press Play
#
# Tip:
#   Hide OUTER_DRUM in the Outliner to inspect the inside.
# ======================================================================

import bpy
import math
from mathutils import Vector

# ======================================================================
# 1. USER PARAMETERS
# ======================================================================

# ---------------- Mechanical geometry ----------------
INNER_CORE_DIAMETER_MM = 25.0
OUTER_DRUM_DIAMETER_MM = 45.0
DRUM_LENGTH_MM         = 100.0

# Outer helical slit
SLIT_WIDTH_MM          = 0.30
HELIX_TURNS            = 1.00
HELIX_SAMPLES          = 700

# ---------------- Axial LED strip ----------------
LED_COUNT              = 16
LED_SIZE_X_MM          = 1.60   # along X
LED_SIZE_Y_MM          = 1.60   # along Y
LED_SIZE_Z_MM          = 1.20   # along Z (visual radial height)
LED_STRIP_MARGIN_MM    = 6.0

# ---------------- Arc window / reflector ----------------
ARC_WINDOW_DEG         = 36.0
ARC_INNER_RADIUS_MM    = 15.0
ARC_THICKNESS_MM       = 0.55
ARC_AXIAL_MARGIN_MM    = 4.0

# ---------------- Raster ----------------
RASTER_X               = 24               # columns
RASTER_Y               = LED_COUNT        # rows
PIXEL_PITCH_X_MM       = 2.20
PIXEL_PITCH_Y_MM       = 3.10
PIXEL_FILL             = 0.82

# ---------------- Slow-motion timing ----------------
FPS                    = 60
FRAMES_PER_STEP        = 8      # slower -> easier to observe
LED_PULSE_DURATION     = 4      # number of frames LED stays visibly on
BEAM_PULSE_DURATION    = 4      # number of frames beam is visible

START_FRAME            = 1
TARGET_RPM             = 2000.0

# For VIEWPORT visualization only:
# one visible revolution per image column
VISIBLE_REVOLUTIONS    = float(RASTER_X)

# Projection screen
SCREEN_Z_MM            = -86.0
SCREEN_Y_OFFSET_MM     = 0.0

# ======================================================================
# 2. UNIT CONVERSION
# ======================================================================

MM = 0.001

INNER_CORE_DIAMETER = INNER_CORE_DIAMETER_MM * MM
OUTER_DRUM_DIAMETER = OUTER_DRUM_DIAMETER_MM * MM
DRUM_LENGTH         = DRUM_LENGTH_MM * MM

CORE_RADIUS = INNER_CORE_DIAMETER * 0.5
DRUM_RADIUS = OUTER_DRUM_DIAMETER * 0.5

SLIT_WIDTH = SLIT_WIDTH_MM * MM

LED_X = LED_SIZE_X_MM * MM
LED_Y = LED_SIZE_Y_MM * MM
LED_Z = LED_SIZE_Z_MM * MM

ARC_INNER_RADIUS = ARC_INNER_RADIUS_MM * MM
ARC_THICKNESS    = ARC_THICKNESS_MM * MM
ARC_OUTER_RADIUS = ARC_INNER_RADIUS + ARC_THICKNESS

PIXEL_PITCH_X = PIXEL_PITCH_X_MM * MM
PIXEL_PITCH_Y = PIXEL_PITCH_Y_MM * MM

SCREEN_Z      = SCREEN_Z_MM * MM
SCREEN_Y_OFF  = SCREEN_Y_OFFSET_MM * MM

TOTAL_STEPS = RASTER_X * RASTER_Y
END_FRAME = START_FRAME + TOTAL_STEPS * FRAMES_PER_STEP + 30

# ======================================================================
# 3. SCENE CLEANUP
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
# 4. MATERIAL HELPERS
# ======================================================================

def find_input(node, names):
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
        s = find_input(bsdf, ["Base Color"])
        if s:
            s.default_value = base_rgba

        s = find_input(bsdf, ["Metallic"])
        if s:
            s.default_value = metallic

        s = find_input(bsdf, ["Roughness"])
        if s:
            s.default_value = roughness

        if emission_rgb is not None:
            s = find_input(bsdf, ["Emission Color", "Emission"])
            if s:
                s.default_value = (
                    emission_rgb[0],
                    emission_rgb[1],
                    emission_rgb[2],
                    1.0
                )

            s = find_input(bsdf, ["Emission Strength"])
            if s:
                s.default_value = emission_strength

    mat.diffuse_color = base_rgba
    return mat


MAT_DRUM = make_material(
    "MAT_DRUM",
    (0.035, 0.045, 0.060, 1.0),
    metallic=0.35,
    roughness=0.28
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

MAT_BEARING = make_material(
    "MAT_BEARING",
    (0.32, 0.34, 0.38, 1.0),
    metallic=0.88,
    roughness=0.18
)

MAT_LED_OFF = make_material(
    "MAT_LED_OFF",
    (0.08, 0.20, 0.08, 1.0),
    roughness=0.35
)

MAT_LED_ON = make_material(
    "MAT_LED_ON",
    (0.05, 0.75, 0.12, 1.0),
    roughness=0.22,
    emission_rgb=(0.02, 1.0, 0.08),
    emission_strength=8.0
)

MAT_HELIX = make_material(
    "MAT_HELIX",
    (0.20, 0.55, 1.0, 1.0),
    roughness=0.20,
    emission_rgb=(0.05, 0.35, 1.0),
    emission_strength=4.5
)

MAT_ARC = make_material(
    "MAT_ARC",
    (0.55, 0.58, 0.62, 1.0),
    metallic=0.88,
    roughness=0.16
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
    emission_strength=6.5
)

MAT_CURSOR = make_material(
    "MAT_CURSOR",
    (1.0, 0.26, 0.02, 1.0),
    roughness=0.18,
    emission_rgb=(1.0, 0.05, 0.01),
    emission_strength=7.0
)

MAT_BEAM = make_material(
    "MAT_BEAM",
    (1.0, 0.70, 0.10, 1.0),
    roughness=0.10,
    emission_rgb=(1.0, 0.75, 0.10),
    emission_strength=10.0
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
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        obj.data.materials.append(material)
    return obj

def add_cylinder(name, radius, depth, location, material=None,
                 rotation=(0.0, 0.0, 0.0), vertices=96, open_ended=False):
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
    verts = []
    faces = []

    a0 = math.radians(center_deg - span_deg * 0.5)
    a1 = math.radians(center_deg + span_deg * 0.5)

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

        faces.append((b0 + 0, b1 + 0, b1 + 1, b0 + 1))  # inner
        faces.append((b0 + 2, b0 + 3, b1 + 3, b1 + 2))  # outer
        faces.append((b0 + 0, b0 + 2, b1 + 2, b1 + 0))  # x_min side
        faces.append((b0 + 1, b1 + 1, b1 + 3, b0 + 3))  # x_max side

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

def add_text(name, body, location, size=0.004, material=None, rotation=(0.0, 0.0, 0.0)):
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

def set_beam_between(obj, p1, p2, radius=0.00022):
    p1 = Vector(p1)
    p2 = Vector(p2)
    d = p2 - p1
    length = d.length

    obj.location = (p1 + p2) * 0.5
    obj.scale = (1.0, 1.0, max(length * 0.5, 0.00001))
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = d.to_track_quat('Z', 'Y')

# ======================================================================
# 6. ROTOR / OUTER DRUM / HELIX
# ======================================================================

rotor = bpy.data.objects.new("ROTOR_MASTER", None)
scene.collection.objects.link(rotor)
rotor.empty_display_type = 'PLAIN_AXES'
rotor.empty_display_size = 0.025
rotor.rotation_mode = 'XYZ'

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

helix_points = []
for i in range(HELIX_SAMPLES):
    u = i / float(HELIX_SAMPLES - 1)
    x = -DRUM_LENGTH * 0.49 + u * DRUM_LENGTH * 0.98
    theta = -math.pi * 0.5 + HELIX_TURNS * 2.0 * math.pi * u
    r = DRUM_RADIUS + 0.00018
    y = r * math.cos(theta)
    z = r * math.sin(theta)
    helix_points.append((x, y, z))

helix = make_poly_curve(
    "CONTINUOUS_HELICAL_SLIT",
    helix_points,
    max(0.000025, SLIT_WIDTH * 0.5),
    MAT_HELIX
)
helix.parent = rotor

# ======================================================================
# 7. STATIONARY CORE / SHAFT / SUPPORTS
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
    MAT_BEARING,
    rotation=(0.0, math.pi / 2.0, 0.0),
    vertices=64
)

for sx in (-1.0, 1.0):
    x = sx * DRUM_LENGTH * 0.58

    add_cylinder(
        "BEARING",
        0.0105,
        0.0070,
        (x, 0.0, 0.0),
        MAT_BEARING,
        rotation=(0.0, math.pi / 2.0, 0.0),
        vertices=96
    )

    add_cube(
        "SUPPORT_BLOCK",
        (x, 0.0, -0.028),
        (0.008, 0.056, 0.058),
        MAT_FRAME
    )

# ======================================================================
# 8. STRAIGHT AXIAL LED STRIP
# ======================================================================

strip_length = DRUM_LENGTH - 2.0 * LED_STRIP_MARGIN_MM * MM

if LED_COUNT == 1:
    led_x_positions = [0.0]
else:
    led_x_positions = [
        -strip_length * 0.5 + i * strip_length / (LED_COUNT - 1)
        for i in range(LED_COUNT)
    ]

led_center_z = -(CORE_RADIUS + LED_Z * 0.5)

led_off_objects = []
led_on_objects = []

for i, x in enumerate(led_x_positions):
    led_off = add_cube(
        f"LED_OFF_{i:02d}",
        (x, 0.0, led_center_z),
        (LED_X, LED_Y, LED_Z),
        MAT_LED_OFF
    )
    led_off_objects.append(led_off)

    led_on = add_cube(
        f"LED_ON_{i:02d}",
        (x, 0.0, led_center_z),
        (LED_X * 1.08, LED_Y * 1.08, LED_Z * 1.10),
        MAT_LED_ON
    )
    led_on.hide_viewport = True
    led_on.hide_render = True
    led_on.keyframe_insert(data_path="hide_viewport", frame=START_FRAME)
    led_on.keyframe_insert(data_path="hide_render", frame=START_FRAME)
    led_on_objects.append(led_on)

led_carrier = add_cube(
    "LED_AXIAL_CARRIER",
    (0.0, 0.0, -(CORE_RADIUS + LED_Z + 0.00025)),
    (strip_length + 0.004, LED_Y * 1.35, 0.00045),
    MAT_FRAME
)

# ======================================================================
# 9. THIN ARC WINDOW / REFLECTOR
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
    segments=72,
    material=MAT_ARC
)

# ======================================================================
# 10. MARKERS
# ======================================================================

active_led_marker = add_cube(
    "ACTIVE_LED_MARKER",
    (led_x_positions[0], 0.0, led_center_z - 0.00005),
    (LED_X * 1.28, LED_Y * 1.28, LED_Z * 1.15),
    MAT_CURSOR
)

arc_mid_r = 0.5 * (ARC_INNER_RADIUS + ARC_OUTER_RADIUS)
arc_center_angle = math.radians(-90.0)
cross_y = arc_mid_r * math.cos(arc_center_angle)
cross_z = arc_mid_r * math.sin(arc_center_angle)

helix_cross_marker = add_cube(
    "HELIX_CROSS_MARKER",
    (led_x_positions[0], cross_y, cross_z),
    (0.0010, 0.0010, 0.0010),
    MAT_CURSOR
)

# ======================================================================
# 11. SCREEN + GRID
# ======================================================================

screen_w = RASTER_X * PIXEL_PITCH_X
screen_h = RASTER_Y * PIXEL_PITCH_Y

screen = add_cube(
    "PROJECTION_SCREEN",
    (0.0, SCREEN_Y_OFF, SCREEN_Z - 0.0007),
    (screen_w + 0.008, screen_h + 0.008, 0.0010),
    MAT_SCREEN
)

for row in range(RASTER_Y):
    for col in range(RASTER_X):
        x = (col - (RASTER_X - 1) * 0.5) * PIXEL_PITCH_X
        y = SCREEN_Y_OFF + ((row - (RASTER_Y - 1) * 0.5) * PIXEL_PITCH_Y)
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
# 12. SMILEY MASK
# ======================================================================

def smiley_mask(col, row):
    u = ((col + 0.5) / RASTER_X) * 2.0 - 1.0
    v = ((row + 0.5) / RASTER_Y) * 2.0 - 1.0

    r = math.sqrt(u*u + v*v)
    if 0.76 < r < 0.88:
        return True

    eye_y = 0.27
    eye_rx = 0.09
    eye_ry = 0.13

    left_eye = (((u + 0.30) / eye_rx) ** 2 + ((v - eye_y) / eye_ry) ** 2) <= 1.0
    right_eye = (((u - 0.30) / eye_rx) ** 2 + ((v - eye_y) / eye_ry) ** 2) <= 1.0

    if left_eye or right_eye:
        return True

    smile_r = math.sqrt(u*u + (v - 0.02) ** 2)
    if (-0.62 < u < 0.62) and (-0.58 < v < -0.02) and (0.48 < smile_r < 0.60):
        return True

    return False

# ======================================================================
# 13. PROJECTED PIXELS
# ======================================================================

projected_pixels = {}

for row in range(RASTER_Y):
    for col in range(RASTER_X):
        if not smiley_mask(col, row):
            continue

        x = (col - (RASTER_X - 1) * 0.5) * PIXEL_PITCH_X
        y = SCREEN_Y_OFF + ((row - (RASTER_Y - 1) * 0.5) * PIXEL_PITCH_Y)

        pix = add_cube(
            f"PIXEL_ON_{row:02d}_{col:02d}",
            (x, y, SCREEN_Z + 0.00065),
            (
                PIXEL_PITCH_X * PIXEL_FILL,
                PIXEL_PITCH_Y * PIXEL_FILL,
                0.00070
            ),
            MAT_PIXEL
        )

        pix.hide_viewport = True
        pix.hide_render = True
        pix.keyframe_insert(data_path="hide_viewport", frame=START_FRAME)
        pix.keyframe_insert(data_path="hide_render", frame=START_FRAME)

        projected_pixels[(row, col)] = pix

# ======================================================================
# 14. SCREEN CURSOR
# ======================================================================

screen_cursor = add_cube(
    "ACTIVE_SCREEN_CURSOR",
    (
        -(RASTER_X - 1) * 0.5 * PIXEL_PITCH_X,
        SCREEN_Y_OFF - (RASTER_Y - 1) * 0.5 * PIXEL_PITCH_Y,
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
# 15. VISIBLE BEAM
# ======================================================================

beam = add_cylinder(
    "VISIBLE_OPTICAL_BEAM",
    0.00022,
    0.010,
    (0.0, 0.0, 0.0),
    MAT_BEAM,
    rotation=(0.0, 0.0, 0.0),
    vertices=18
)
beam.rotation_mode = 'QUATERNION'
beam.hide_viewport = True
beam.hide_render = True
beam.keyframe_insert(data_path="hide_viewport", frame=START_FRAME)
beam.keyframe_insert(data_path="hide_render", frame=START_FRAME)

# ======================================================================
# 16. ANIMATION LOGIC
# ======================================================================
#
# Model:
#   one visible revolution -> one image column
#   one LED                -> one image row
#   when helix reaches that LED's X position, LED pulses
#   beam flashes from arc crossing to screen sample
#   if smiley pixel is ON, projected pixel is revealed
# ======================================================================

for col in range(RASTER_X):
    for row in range(RASTER_Y):
        step_index = col * RASTER_Y + row
        frame = START_FRAME + step_index * FRAMES_PER_STEP

        led_x = led_x_positions[row]

        # active LED marker
        active_led_marker.location = (led_x, 0.0, led_center_z - 0.00005)
        active_led_marker.keyframe_insert(data_path="location", frame=frame)

        # helix crossing marker
        helix_cross_marker.location = (led_x, cross_y, cross_z)
        helix_cross_marker.keyframe_insert(data_path="location", frame=frame)

        # screen cursor
        px = (col - (RASTER_X - 1) * 0.5) * PIXEL_PITCH_X
        py = SCREEN_Y_OFF + ((row - (RASTER_Y - 1) * 0.5) * PIXEL_PITCH_Y)
        screen_cursor.location = (px, py, SCREEN_Z + 0.0018)
        screen_cursor.keyframe_insert(data_path="location", frame=frame)

        pixel_is_on = smiley_mask(col, row)
        led_pulse = led_on_objects[row]

        # LED pulse
        if frame > START_FRAME:
            led_pulse.hide_viewport = True
            led_pulse.hide_render = True
            led_pulse.keyframe_insert(data_path="hide_viewport", frame=frame - 1)
            led_pulse.keyframe_insert(data_path="hide_render", frame=frame - 1)

        if pixel_is_on:
            led_pulse.hide_viewport = False
            led_pulse.hide_render = False
            led_pulse.keyframe_insert(data_path="hide_viewport", frame=frame)
            led_pulse.keyframe_insert(data_path="hide_render", frame=frame)

            led_pulse.hide_viewport = True
            led_pulse.hide_render = True
            led_pulse.keyframe_insert(data_path="hide_viewport", frame=frame + LED_PULSE_DURATION)
            led_pulse.keyframe_insert(data_path="hide_render", frame=frame + LED_PULSE_DURATION)

            # reveal projected pixel
            pix = projected_pixels[(row, col)]

            if frame > START_FRAME:
                pix.hide_viewport = True
                pix.hide_render = True
                pix.keyframe_insert(data_path="hide_viewport", frame=frame - 1)
                pix.keyframe_insert(data_path="hide_render", frame=frame - 1)

            pix.hide_viewport = False
            pix.hide_render = False
            pix.keyframe_insert(data_path="hide_viewport", frame=frame)
            pix.keyframe_insert(data_path="hide_render", frame=frame)

            # beam pulse only when LED is actually on
            start_point = (led_x, cross_y, cross_z)
            end_point = (px, py, SCREEN_Z + 0.0010)

            if frame > START_FRAME:
                beam.hide_viewport = True
                beam.hide_render = True
                beam.keyframe_insert(data_path="hide_viewport", frame=frame - 1)
                beam.keyframe_insert(data_path="hide_render", frame=frame - 1)

            set_beam_between(beam, start_point, end_point, radius=0.00022)
            beam.keyframe_insert(data_path="location", frame=frame)
            beam.keyframe_insert(data_path="rotation_quaternion", frame=frame)
            beam.keyframe_insert(data_path="scale", frame=frame)

            beam.hide_viewport = False
            beam.hide_render = False
            beam.keyframe_insert(data_path="hide_viewport", frame=frame)
            beam.keyframe_insert(data_path="hide_render", frame=frame)

            beam.hide_viewport = True
            beam.hide_render = True
            beam.keyframe_insert(data_path="hide_viewport", frame=frame + BEAM_PULSE_DURATION)
            beam.keyframe_insert(data_path="hide_render", frame=frame + BEAM_PULSE_DURATION)

        else:
            # keep LED hidden
            led_pulse.hide_viewport = True
            led_pulse.hide_render = True
            led_pulse.keyframe_insert(data_path="hide_viewport", frame=frame)
            led_pulse.keyframe_insert(data_path="hide_render", frame=frame)

# Hold markers
active_led_marker.keyframe_insert(data_path="location", frame=END_FRAME)
helix_cross_marker.keyframe_insert(data_path="location", frame=END_FRAME)
screen_cursor.keyframe_insert(data_path="location", frame=END_FRAME)

# Rotor rotation: key every frame so playback is smooth and version-safe
anim_frames = max(1, END_FRAME - START_FRAME)

for frame in range(START_FRAME, END_FRAME + 1):
    u = (frame - START_FRAME) / float(anim_frames)
    rotor.rotation_euler.x = VISIBLE_REVOLUTIONS * 2.0 * math.pi * u
    rotor.keyframe_insert(data_path="rotation_euler", index=0, frame=frame)

# ======================================================================
# 17. MOTOR / DRIVE VISUAL
# ======================================================================

motor = add_cylinder(
    "MOTOR",
    0.010,
    0.030,
    (DRUM_LENGTH * 0.68, 0.035, 0.008),
    MAT_FRAME,
    rotation=(0.0, math.pi / 2.0, 0.0),
    vertices=64
)

rotor_pulley = add_cylinder(
    "ROTOR_DRIVE_PULLEY",
    DRUM_RADIUS * 0.72,
    0.004,
    (DRUM_LENGTH * 0.53, 0.0, 0.0),
    MAT_FRAME,
    rotation=(0.0, math.pi / 2.0, 0.0),
    vertices=96
)
rotor_pulley.parent = rotor

# ======================================================================
# 18. LABELS
# ======================================================================

screen_h = RASTER_Y * PIXEL_PITCH_Y
title_y = SCREEN_Y_OFF - screen_h * 0.72

add_text(
    "TITLE",
    "SLOW-MOTION HELICAL-SLIT NIPKOW DEMO",
    (0.0, title_y, SCREEN_Z + 0.0012),
    size=0.0040,
    material=MAT_TEXT
)

add_text(
    "LABEL_1",
    "LEDs blink when the helix crosses; beam flashes toward the floor screen",
    (0.0, title_y - 0.007, SCREEN_Z + 0.0012),
    size=0.0025,
    material=MAT_TEXT
)

add_text(
    "LABEL_2",
    f"Viewport: {FPS} FPS | {FRAMES_PER_STEP} frames per scan step | target physical speed = {TARGET_RPM:.0f} RPM",
    (0.0, title_y - 0.013, SCREEN_Z + 0.0012),
    size=0.0023,
    material=MAT_TEXT
)

# ======================================================================
# 19. CAMERA
# ======================================================================

bpy.ops.object.camera_add(
    location=(0.170, -0.205, 0.145)
)
camera = bpy.context.object
camera.name = "SIM_CAMERA"
camera.data.lens = 50
point_at(camera, (0.0, 0.0, -0.028))
scene.camera = camera

# ======================================================================
# 20. LIGHTS
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
# 21. METADATA
# ======================================================================

scene["design"] = "slow motion axial LED helix crossing demo"
scene["inner_core_diameter_mm"] = INNER_CORE_DIAMETER_MM
scene["outer_drum_diameter_mm"] = OUTER_DRUM_DIAMETER_MM
scene["drum_length_mm"] = DRUM_LENGTH_MM
scene["led_count"] = LED_COUNT
scene["arc_window_deg"] = ARC_WINDOW_DEG
scene["slit_width_mm"] = SLIT_WIDTH_MM
scene["target_rpm"] = TARGET_RPM
scene["fps"] = FPS
scene["frames_per_step"] = FRAMES_PER_STEP

# ======================================================================
# 22. VIEWPORT SETUP
# ======================================================================

scene.frame_set(START_FRAME)

try:
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'MATERIAL'
except Exception:
    pass

# ======================================================================
# 23. REPORT
# ======================================================================

led_pitch = strip_length / (LED_COUNT - 1) if LED_COUNT > 1 else strip_length
arc_mid_r = 0.5 * (ARC_INNER_RADIUS + ARC_OUTER_RADIUS)
arc_length = arc_mid_r * math.radians(ARC_WINDOW_DEG)

print("")
print("==============================================================")
print(" SLOW-MOTION NIPKOW DEMO READY")
print("==============================================================")
print(f"Blender version              : {bpy.app.version_string}")
print(f"Viewport FPS                 : {FPS}")
print(f"Frames per scan step         : {FRAMES_PER_STEP}")
print(f"LED pulse duration           : {LED_PULSE_DURATION} frames")
print(f"Beam pulse duration          : {BEAM_PULSE_DURATION} frames")
print("")
print("LED STRIP")
print("  arrangement                : straight axial line")
print("  orientation                : standing radially upright")
print(f"  count                      : {LED_COUNT}")
print(f"  axial pitch                : {led_pitch / MM:.2f} mm")
print("")
print("ARC WINDOW / REFLECTOR")
print(f"  angular width              : {ARC_WINDOW_DEG:.2f} deg")
print(f"  arc length (midline)       : {arc_length / MM:.2f} mm")
print("")
print("TIMING MODEL")
print("  one visible revolution     : one image column")
print("  one LED                    : one image row")
print("  when helix crosses an LED  : LED pulse + beam flash")
print("")
print(f"Raster                       : {RASTER_X} x {RASTER_Y}")
print(f"Timeline                     : {START_FRAME} .. {END_FRAME}")
print(f"Target physical speed        : {TARGET_RPM:.0f} RPM")
print("")
print("Tip: hide OUTER_DRUM to inspect internals.")
print("Press PLAY.")
print("==============================================================")
