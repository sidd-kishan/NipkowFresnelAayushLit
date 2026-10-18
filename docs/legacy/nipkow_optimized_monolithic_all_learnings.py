# ======================================================================
# OPTIMIZED MONOLITHIC BLENDER SCRIPT
# Helical-slit Nipkow drum with corrected internal geometry
# ======================================================================
#
# WHAT THIS SCRIPT MODELS
# -----------------------
# 1) Outer rotating drum lying horizontally (axis = world X)
# 2) Continuous helical slit on the outer drum
# 3) Stationary inner core, diameter = 25 mm
# 4) One straight LED strip running along the drum length (world X)
# 5) LEDs standing radially upright on the lower side of the inner core
# 6) A thin cylindrical arc window / reflector above the LED line
# 7) LED blinking synchronized to the helix crossing the strip
# 8) A smiley image rasterizing onto a floor projection screen
#
# WORKFLOW
# --------
# 1. Open Blender
# 2. Go to Scripting
# 3. Paste this ENTIRE file into a new text block
# 4. Run Script
# 5. Press PLAY
#
# NOTES
# -----
# - This is a didactic simulation, not a full optical physics solver.
# - To make the scan visible, the rotor is slowed for viewport playback.
#   The target physical speed is still recorded as 2000 RPM.
# - No Action.fcurves access is used anywhere.
# - If you want to inspect the internals, hide: OUTER_DRUM
#
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

# Outer drum helix
SLIT_WIDTH_MM          = 0.30
HELIX_TURNS            = 1.00
HELIX_SAMPLES          = 700

# ---------------- Axial LED strip ----------------
LED_COUNT              = 16
LED_SIZE_X_MM          = 1.60   # along X (axial)
LED_SIZE_Y_MM          = 1.60   # along Y (tangential width)
LED_SIZE_Z_MM          = 1.20   # along Z (radial height), a little exaggerated
LED_STRIP_MARGIN_MM    = 6.0    # empty margin at both ends of the strip

# ---------------- Arc window / reflector ----------------
ARC_WINDOW_DEG         = 36.0   # angular width of curved reflector/window
ARC_INNER_RADIUS_MM    = 15.0
ARC_THICKNESS_MM       = 0.55
ARC_AXIAL_MARGIN_MM    = 4.0

# ---------------- Raster / display ----------------
# Model:
#   - Each revolution scans one image COLUMN
#   - Within that revolution, the helix sweeps along X and crosses LEDs in order
#   - Each LED corresponds to one image ROW
RASTER_X               = 24                # columns
RASTER_Y               = LED_COUNT         # rows = number of LEDs

PIXEL_PITCH_X_MM       = 2.20
PIXEL_PITCH_Y_MM       = 3.10
PIXEL_FILL             = 0.82

# ---------------- Animation ----------------
FPS                    = 30
FRAMES_PER_STEP        = 1
START_FRAME            = 1
TARGET_RPM             = 2000.0

# For visualization:
# one visible revolution per image column
VISIBLE_REVOLUTIONS    = float(RASTER_X)

# ---------------- Projection screen ----------------
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
END_FRAME = START_FRAME + TOTAL_STEPS * FRAMES_PER_STEP + 20

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
    emission_strength=7.0
)

MAT_HELIX = make_material(
    "MAT_HELIX",
    (0.20, 0.55, 1.0, 1.0),
    roughness=0.20,
    emission_rgb=(0.05, 0.35, 1.0),
    emission_strength=4.0
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
# 5. BASIC HELPERS
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
    """
    Thin cylindrical arc shell coaxial with world X.
    Used for the arc reflector/window.
    """
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

        # x_min/inner, x_max/inner, x_min/outer, x_max/outer
        verts.extend([
            (x_min, yi, zi),
            (x_max, yi, zi),
            (x_min, yo, zo),
            (x_max, yo, zo),
        ])

    for i in range(segments):
        b0 = i * 4
        b1 = (i + 1) * 4

        # inner surface
        faces.append((b0 + 0, b1 + 0, b1 + 1, b0 + 1))
        # outer surface
        faces.append((b0 + 2, b0 + 3, b1 + 3, b1 + 2))
        # x_min side
        faces.append((b0 + 0, b0 + 2, b1 + 2, b1 + 0))
        # x_max side
        faces.append((b0 + 1, b1 + 1, b1 + 3, b0 + 3))

    # side faces at angular boundaries
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

# ======================================================================
# 6. MAIN ROTOR EMPTY
# ======================================================================

rotor = bpy.data.objects.new("ROTOR_MASTER", None)
scene.collection.objects.link(rotor)
rotor.empty_display_type = 'PLAIN_AXES'
rotor.empty_display_size = 0.025
rotor.rotation_mode = 'XYZ'

# ======================================================================
# 7. OUTER ROTATING DRUM
# ======================================================================

# Blender cylinder is along local Z, so rotate 90° around Y to align to X.
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

# ======================================================================
# 8. CONTINUOUS HELICAL SLIT
# ======================================================================

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
# 9. STATIONARY CORE / SHAFT / BEARINGS
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
# 10. CORRECT AXIAL LED STRIP
# ======================================================================
#
# LEDs:
#   - arranged in one straight line along X
#   - centered at Y = 0
#   - placed below the core (negative Z)
#   - standing upright radially (their local height is along Z)
#
# If you take a single cross-section at one X location, you only see one LED.
# Along the full side view, you see the whole strip of many LEDs.
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

# Base LED bodies
led_off_objects = []

# Glow overlays for blinking (same geometry, hidden until pulse)
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

# LED carrier / small PCB strip
led_carrier = add_cube(
    "LED_AXIAL_CARRIER",
    (0.0, 0.0, -(CORE_RADIUS + LED_Z + 0.00025)),
    (strip_length + 0.004, LED_Y * 1.35, 0.00045),
    MAT_FRAME
)

# ======================================================================
# 11. THIN ARC WINDOW / REFLECTOR
# ======================================================================
#
# Curved around the lower side of the core, but extending axially along X.
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
# 12. ACTIVE CROSSING MARKERS
# ======================================================================
#
# These are purely to make the timing visible:
#   - ACTIVE_LED_MARKER sits over the LED currently being crossed
#   - HELIX_CROSS_MARKER sits on the arc window at that same X position
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
# 13. SCREEN + GRID
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
# 14. SMILEY MASK
# ======================================================================

def smiley_mask(col, row):
    # Normalize to approximately square image coordinates.
    u = ((col + 0.5) / RASTER_X) * 2.0 - 1.0
    v = ((row + 0.5) / RASTER_Y) * 2.0 - 1.0

    r = math.sqrt(u*u + v*v)

    # Face ring
    if 0.76 < r < 0.88:
        return True

    # Eyes
    eye_y = 0.27
    eye_rx = 0.09
    eye_ry = 0.13

    left_eye = (((u + 0.30) / eye_rx) ** 2 + ((v - eye_y) / eye_ry) ** 2) <= 1.0
    right_eye = (((u - 0.30) / eye_rx) ** 2 + ((v - eye_y) / eye_ry) ** 2) <= 1.0

    if left_eye or right_eye:
        return True

    # Smile
    smile_r = math.sqrt(u*u + (v - 0.02) ** 2)
    if (-0.62 < u < 0.62) and (-0.58 < v < -0.02) and (0.48 < smile_r < 0.60):
        return True

    return False

# ======================================================================
# 15. PROGRESSIVE PROJECTION PIXELS
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
# 16. SCREEN CURSOR
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
# 17. ANIMATION LOGIC
# ======================================================================
#
# MODEL USED HERE:
#   - One full revolution = one image column
#   - During that revolution, helix sweeps along X and crosses LEDs 0..N-1
#   - At each crossing, the corresponding LED may blink
#   - If that image pixel is ON, the projected pixel appears on the screen
#
# This captures the intended timing relationship:
#     helix crossing -> LED pulse -> projected pixel
# ======================================================================

for col in range(RASTER_X):
    for row in range(RASTER_Y):
        step_index = col * RASTER_Y + row
        frame = START_FRAME + step_index * FRAMES_PER_STEP

        led_x = led_x_positions[row]

        # Marker over active LED
        active_led_marker.location = (led_x, 0.0, led_center_z - 0.00005)
        active_led_marker.keyframe_insert(data_path="location", frame=frame)

        # Marker where helix meets the reflector/window region
        helix_cross_marker.location = (led_x, cross_y, cross_z)
        helix_cross_marker.keyframe_insert(data_path="location", frame=frame)

        # Cursor on projection screen
        px = (col - (RASTER_X - 1) * 0.5) * PIXEL_PITCH_X
        py = SCREEN_Y_OFF + ((row - (RASTER_Y - 1) * 0.5) * PIXEL_PITCH_Y)
        screen_cursor.location = (px, py, SCREEN_Z + 0.0018)
        screen_cursor.keyframe_insert(data_path="location", frame=frame)

        # LED blink when helix crosses this LED
        led_pulse = led_on_objects[row]

        if frame > START_FRAME:
            led_pulse.hide_viewport = True
            led_pulse.hide_render = True
            led_pulse.keyframe_insert(data_path="hide_viewport", frame=frame - 1)
            led_pulse.keyframe_insert(data_path="hide_render", frame=frame - 1)

        pixel_is_on = smiley_mask(col, row)

        if pixel_is_on:
            # Blink ON at crossing
            led_pulse.hide_viewport = False
            led_pulse.hide_render = False
            led_pulse.keyframe_insert(data_path="hide_viewport", frame=frame)
            led_pulse.keyframe_insert(data_path="hide_render", frame=frame)

            # Turn OFF one frame later so it looks like a pulse
            led_pulse.hide_viewport = True
            led_pulse.hide_render = True
            led_pulse.keyframe_insert(data_path="hide_viewport", frame=frame + 1)
            led_pulse.keyframe_insert(data_path="hide_render", frame=frame + 1)

            # Reveal projected screen pixel permanently
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

        else:
            # Keep LED hidden for OFF pixels
            led_pulse.hide_viewport = True
            led_pulse.hide_render = True
            led_pulse.keyframe_insert(data_path="hide_viewport", frame=frame)
            led_pulse.keyframe_insert(data_path="hide_render", frame=frame)

# Hold markers to the end
active_led_marker.keyframe_insert(data_path="location", frame=END_FRAME)
helix_cross_marker.keyframe_insert(data_path="location", frame=END_FRAME)
screen_cursor.keyframe_insert(data_path="location", frame=END_FRAME)

# Rotor rotation: key every frame to avoid relying on interpolation editing
anim_frames = max(1, END_FRAME - START_FRAME)

for frame in range(START_FRAME, END_FRAME + 1):
    u = (frame - START_FRAME) / float(anim_frames)
    rotor.rotation_euler.x = VISIBLE_REVOLUTIONS * 2.0 * math.pi * u
    rotor.keyframe_insert(data_path="rotation_euler", index=0, frame=frame)

# ======================================================================
# 18. MOTOR / DRIVE VISUAL
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
# 19. LABELS
# ======================================================================

title_y = SCREEN_Y_OFF - screen_h * 0.67

add_text(
    "TITLE",
    "OPTIMIZED HELICAL-SLIT NIPKOW DEMO",
    (0.0, title_y, SCREEN_Z + 0.0012),
    size=0.0042,
    material=MAT_TEXT
)

add_text(
    "GEOM_LABEL",
    "LEDs: straight axial line, standing radially | arc window: thin cylindrical arc",
    (0.0, title_y - 0.0075, SCREEN_Z + 0.0012),
    size=0.0024,
    material=MAT_TEXT
)

add_text(
    "SCAN_LABEL",
    "Each revolution scans one image column; LEDs pulse when helix crosses them",
    (0.0, title_y - 0.0135, SCREEN_Z + 0.0012),
    size=0.0023,
    material=MAT_TEXT
)

add_text(
    "RPM_LABEL",
    f"Target physical speed = {TARGET_RPM:.0f} RPM | viewport revolutions = {VISIBLE_REVOLUTIONS:.0f}",
    (0.0, title_y - 0.0190, SCREEN_Z + 0.0012),
    size=0.0022,
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
point_at(camera, (0.0, 0.0, -0.030))
scene.camera = camera

# ======================================================================
# 21. LIGHTING
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
# 22. SCENE METADATA
# ======================================================================

scene["design"] = "optimized axial LED + arc window + helix-crossing pulse model"
scene["inner_core_diameter_mm"] = INNER_CORE_DIAMETER_MM
scene["outer_drum_diameter_mm"] = OUTER_DRUM_DIAMETER_MM
scene["drum_length_mm"] = DRUM_LENGTH_MM
scene["led_count"] = LED_COUNT
scene["led_size_mm"] = f"{LED_SIZE_X_MM} x {LED_SIZE_Y_MM} x {LED_SIZE_Z_MM}"
scene["arc_window_deg"] = ARC_WINDOW_DEG
scene["slit_width_mm"] = SLIT_WIDTH_MM
scene["target_rpm"] = TARGET_RPM
scene["raster_x"] = RASTER_X
scene["raster_y"] = RASTER_Y

# ======================================================================
# 23. VIEWPORT SETUP
# ======================================================================

scene.frame_set(START_FRAME)

try:
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'MATERIAL'
except Exception:
    pass

# ======================================================================
# 24. CONSOLE REPORT
# ======================================================================

led_pitch = strip_length / (LED_COUNT - 1) if LED_COUNT > 1 else strip_length
arc_mid_r = 0.5 * (ARC_INNER_RADIUS + ARC_OUTER_RADIUS)
arc_length = arc_mid_r * math.radians(ARC_WINDOW_DEG)

print("")
print("==============================================================")
print(" OPTIMIZED NIPKOW SIMULATION READY")
print("==============================================================")
print(f"Blender version              : {bpy.app.version_string}")
print(f"Inner stationary core        : {INNER_CORE_DIAMETER_MM:.2f} mm diameter")
print(f"Outer drum                   : {OUTER_DRUM_DIAMETER_MM:.2f} mm diameter")
print(f"Drum length                  : {DRUM_LENGTH_MM:.2f} mm")
print("")
print("LED STRIP")
print("  arrangement                : straight axial line")
print("  orientation                : standing radially upright")
print(f"  count                      : {LED_COUNT}")
print(f"  package                    : {LED_SIZE_X_MM:.2f} x {LED_SIZE_Y_MM:.2f} x {LED_SIZE_Z_MM:.2f} mm")
print(f"  axial pitch                : {led_pitch / MM:.2f} mm")
print("")
print("ARC WINDOW / REFLECTOR")
print("  geometry                   : thin cylindrical arc shell")
print(f"  angular width              : {ARC_WINDOW_DEG:.2f} deg")
print(f"  inner radius               : {ARC_INNER_RADIUS_MM:.2f} mm")
print(f"  thickness                  : {ARC_THICKNESS_MM:.2f} mm")
print(f"  arc length (midline)       : {arc_length / MM:.2f} mm")
print("")
print("SCAN MODEL")
print("  one revolution -> one image column")
print("  one LED         -> one image row")
print("  LED pulse       -> when helix crosses LED position")
print("")
print(f"Raster                       : {RASTER_X} x {RASTER_Y}")
print(f"Target physical speed        : {TARGET_RPM:.0f} RPM")
print(f"Visible viewport revolutions : {VISIBLE_REVOLUTIONS:.0f}")
print(f"Timeline                     : {START_FRAME} .. {END_FRAME}")
print("")
print("Tip: hide OUTER_DRUM in the Outliner to inspect internals.")
print("Press PLAY.")
print("==============================================================")
