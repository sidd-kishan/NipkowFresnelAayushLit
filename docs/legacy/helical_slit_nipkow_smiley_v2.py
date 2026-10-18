# ======================================================================
# HELICAL-SLIT NIPKOW DRUM + SMILEY RASTER SIMULATION
# Monolithic Blender Python script
#
# Workflow:
#   1) Blender -> Scripting -> New
#   2) Paste/run this whole file
#   3) Press PLAY
#
# Compatibility:
#   - NEVER accesses Action.fcurves.
#   - Uses keyframe_insert() only.
#   - Sets keyframe interpolation BEFORE key creation.
#   - Avoids renderer enum names that changed across Blender versions.
# ======================================================================

import bpy
import math
from mathutils import Vector

# ======================================================================
# 1. USER PARAMETERS
# ======================================================================

# Mechanical dimensions
INNER_CORE_DIAMETER_MM = 25.0
OUTER_DRUM_DIAMETER_MM = 45.0
DRUM_LENGTH_MM          = 100.0

# Helical slit
SLIT_WIDTH_MM          = 0.30
HELIX_TURNS_ALONG_DRUM = 1.0
HELIX_SAMPLES          = 700

# Internal LED arc / arc-window
LED_PACKAGE_MM        = 1.60      # 1616 LED package
LED_COUNT             = 16
LED_ARC_WINDOW_DEG    = 100.0     # tune this for larger LEDs
LED_ARC_RADIUS_MM     = 16.0
LED_BODY_THICKNESS_MM = 0.80

# Raster
RASTER_X = 24
RASTER_Y = LED_COUNT

PIXEL_PITCH_X_MM = 2.00
# Keep the final picture approximately square.
PIXEL_PITCH_Y_MM = PIXEL_PITCH_X_MM * (RASTER_X / RASTER_Y)
PIXEL_FILL       = 0.82

# Animation
FPS                  = 30
FRAMES_PER_PIXEL     = 1
START_FRAME          = 1
TARGET_RPM           = 2000.0
TRUE_2000_RPM_VISUAL = False

# In slowed mode, one visible drum revolution scans one raster row.
VISIBLE_REVOLUTIONS = float(RASTER_Y)

# Projection plane
SCREEN_Z_MM        = -85.0
SCREEN_Y_OFFSET_MM = 0.0

# ======================================================================
# 2. UNIT CONVERSION / DERIVED VALUES
# ======================================================================

MM = 0.001

INNER_CORE_DIAMETER = INNER_CORE_DIAMETER_MM * MM
OUTER_DRUM_DIAMETER = OUTER_DRUM_DIAMETER_MM * MM
DRUM_LENGTH          = DRUM_LENGTH_MM * MM
SLIT_WIDTH           = SLIT_WIDTH_MM * MM
LED_PACKAGE          = LED_PACKAGE_MM * MM
LED_ARC_RADIUS       = LED_ARC_RADIUS_MM * MM
LED_BODY_THICKNESS   = LED_BODY_THICKNESS_MM * MM
PIXEL_PITCH_X        = PIXEL_PITCH_X_MM * MM
PIXEL_PITCH_Y        = PIXEL_PITCH_Y_MM * MM
SCREEN_Z             = SCREEN_Z_MM * MM
SCREEN_Y_OFFSET      = SCREEN_Y_OFFSET_MM * MM

DRUM_RADIUS = OUTER_DRUM_DIAMETER * 0.5
CORE_RADIUS = INNER_CORE_DIAMETER * 0.5

TOTAL_PIXELS = RASTER_X * RASTER_Y
END_FRAME = START_FRAME + TOTAL_PIXELS * FRAMES_PER_PIXEL + 12

duration_seconds = max(1.0 / FPS, (END_FRAME - START_FRAME) / FPS)

if TRUE_2000_RPM_VISUAL:
    rotor_revolutions = (TARGET_RPM / 60.0) * duration_seconds
else:
    rotor_revolutions = VISIBLE_REVOLUTIONS

led_arc_rad = math.radians(LED_ARC_WINDOW_DEG)
led_arc_length = LED_ARC_RADIUS * led_arc_rad

if LED_COUNT > 1:
    led_center_pitch = led_arc_length / (LED_COUNT - 1)
else:
    led_center_pitch = led_arc_length

led_clearance = led_center_pitch - LED_PACKAGE

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

# Remove only unused datablocks so repeated runs stay clean.
for datablocks in (bpy.data.curves, bpy.data.meshes, bpy.data.materials):
    for datablock in list(datablocks):
        if datablock.users == 0:
            try:
                datablocks.remove(datablock)
            except Exception:
                pass

scene = bpy.context.scene
scene.frame_start = START_FRAME
scene.frame_end = END_FRAME
scene.render.fps = FPS
scene.frame_set(START_FRAME)
scene.world.color = (0.008, 0.010, 0.014)

# ======================================================================
# 4. MATERIAL HELPERS
# ======================================================================

def socket_by_names(node, names):
    for name in names:
        if name in node.inputs:
            return node.inputs[name]
    return None


def make_material(name, base_rgba, metallic=0.0, roughness=0.45,
                  emission_rgb=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    bsdf = nodes.get('Principled BSDF')

    if bsdf is not None:
        s = socket_by_names(bsdf, ['Base Color'])
        if s:
            s.default_value = base_rgba

        s = socket_by_names(bsdf, ['Metallic'])
        if s:
            s.default_value = metallic

        s = socket_by_names(bsdf, ['Roughness'])
        if s:
            s.default_value = roughness

        if emission_rgb is not None and emission_strength > 0.0:
            s = socket_by_names(bsdf, ['Emission Color', 'Emission'])
            if s:
                s.default_value = (
                    emission_rgb[0],
                    emission_rgb[1],
                    emission_rgb[2],
                    1.0
                )

            s = socket_by_names(bsdf, ['Emission Strength'])
            if s:
                s.default_value = emission_strength

    mat.diffuse_color = base_rgba
    return mat


MAT_DRUM = make_material(
    'MAT_DRUM', (0.035, 0.045, 0.060, 1.0), metallic=0.35, roughness=0.30
)
MAT_CORE = make_material(
    'MAT_CORE', (0.10, 0.11, 0.13, 1.0), metallic=0.20, roughness=0.42
)
MAT_FRAME = make_material(
    'MAT_FRAME', (0.12, 0.13, 0.15, 1.0), metallic=0.65, roughness=0.30
)
MAT_BEARING = make_material(
    'MAT_BEARING', (0.30, 0.32, 0.35, 1.0), metallic=0.90, roughness=0.20
)
MAT_LED_OFF = make_material(
    'MAT_LED_OFF', (0.10, 0.16, 0.08, 1.0), roughness=0.30
)
MAT_LED_ON = make_material(
    'MAT_LED_ON', (0.04, 0.70, 0.12, 1.0), roughness=0.25,
    emission_rgb=(0.02, 1.0, 0.08), emission_strength=7.0
)
MAT_SLIT = make_material(
    'MAT_SLIT', (0.20, 0.60, 1.0, 1.0), roughness=0.18,
    emission_rgb=(0.05, 0.35, 1.0), emission_strength=4.5
)
MAT_ARC = make_material(
    'MAT_ARC', (0.9, 0.30, 0.05, 1.0), roughness=0.25,
    emission_rgb=(1.0, 0.12, 0.01), emission_strength=2.5
)
MAT_SCREEN = make_material(
    'MAT_SCREEN', (0.025, 0.028, 0.032, 1.0), roughness=0.85
)
MAT_GRID = make_material(
    'MAT_GRID', (0.055, 0.060, 0.070, 1.0), roughness=0.75
)
MAT_PIXEL = make_material(
    'MAT_PIXEL', (0.03, 0.85, 0.13, 1.0), roughness=0.20,
    emission_rgb=(0.01, 1.0, 0.07), emission_strength=6.0
)
MAT_CURSOR = make_material(
    'MAT_CURSOR', (1.0, 0.25, 0.03, 1.0), roughness=0.20,
    emission_rgb=(1.0, 0.05, 0.01), emission_strength=7.0
)
MAT_TEXT = make_material(
    'MAT_TEXT', (0.65, 0.72, 0.82, 1.0), roughness=0.55
)

# ======================================================================
# 5. GEOMETRY HELPERS
# ======================================================================

def add_cube(name, location, dimensions, material, rotation=(0.0, 0.0, 0.0)):
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


def add_cylinder(name, radius, depth, location, material,
                 rotation=(0.0, 0.0, 0.0), vertices=96, open_ended=False):
    kwargs = dict(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation
    )
    if open_ended:
        kwargs['end_fill_type'] = 'NOTHING'

    bpy.ops.mesh.primitive_cylinder_add(**kwargs)
    obj = bpy.context.object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj


def make_poly_curve(name, points, bevel_depth, material, cyclic=False):
    curve_data = bpy.data.curves.new(name=name + '_CURVE', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 1
    curve_data.bevel_depth = bevel_depth
    curve_data.bevel_resolution = 2

    spline = curve_data.splines.new('POLY')
    spline.points.add(len(points) - 1)

    for i, p in enumerate(points):
        spline.points[i].co = (p[0], p[1], p[2], 1.0)

    spline.use_cyclic_u = cyclic

    obj = bpy.data.objects.new(name, curve_data)
    scene.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def add_text(name, body, location, size=0.004, material=None):
    curve = bpy.data.curves.new(name=name + '_FONT', type='FONT')
    curve.body = body
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.size = size
    curve.extrude = 0.00004

    obj = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(obj)
    obj.location = location

    if material:
        curve.materials.append(material)

    return obj


def point_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# ======================================================================
# 6. ROTOR MASTER
# ======================================================================

# Important: the rotor Empty has its axis directly on world X.
# The cylinder geometry is rotated underneath it. This avoids mixed-axis
# Euler problems and lets the whole drum + slit rotate cleanly around X.
rotor = bpy.data.objects.new('ROTOR_MASTER', None)
scene.collection.objects.link(rotor)
rotor.empty_display_type = 'PLAIN_AXES'
rotor.empty_display_size = 0.030
rotor.rotation_mode = 'XYZ'

# ======================================================================
# 7. OUTER DRUM
# ======================================================================

drum_body = add_cylinder(
    'OUTER_DRUM',
    DRUM_RADIUS,
    DRUM_LENGTH,
    (0.0, 0.0, 0.0),
    MAT_DRUM,
    rotation=(0.0, math.pi / 2.0, 0.0),
    vertices=160,
    open_ended=True
)
drum_body.parent = rotor

# Thin end rings for visual structure.
for sx in (-1.0, 1.0):
    x = sx * DRUM_LENGTH * 0.5
    ring = add_cylinder(
        'DRUM_END_RING',
        DRUM_RADIUS * 1.01,
        0.0020,
        (x, 0.0, 0.0),
        MAT_FRAME,
        rotation=(0.0, math.pi / 2.0, 0.0),
        vertices=128,
        open_ended=False
    )
    ring.parent = rotor

# ======================================================================
# 8. CONTINUOUS HELICAL SLIT
# ======================================================================

helix_points = []

for i in range(HELIX_SAMPLES):
    u = i / float(HELIX_SAMPLES - 1)

    x = -DRUM_LENGTH * 0.49 + u * DRUM_LENGTH * 0.98
    theta = -math.pi * 0.5 + HELIX_TURNS_ALONG_DRUM * 2.0 * math.pi * u

    r = DRUM_RADIUS + 0.00018
    y = r * math.cos(theta)
    z = r * math.sin(theta)

    helix_points.append((x, y, z))

helix = make_poly_curve(
    'CONTINUOUS_HELICAL_SLIT',
    helix_points,
    max(0.000025, SLIT_WIDTH * 0.50),
    MAT_SLIT,
    cyclic=False
)
helix.parent = rotor

# ======================================================================
# 9. STATIONARY 25 mm INNER CORE / SHAFT / BEARINGS
# ======================================================================

core = add_cylinder(
    'STATIONARY_25MM_CORE',
    CORE_RADIUS,
    DRUM_LENGTH * 0.90,
    (0.0, 0.0, 0.0),
    MAT_CORE,
    rotation=(0.0, math.pi / 2.0, 0.0),
    vertices=128,
    open_ended=False
)

shaft = add_cylinder(
    'STATIONARY_SHAFT',
    0.0030,
    DRUM_LENGTH * 1.35,
    (0.0, 0.0, 0.0),
    MAT_BEARING,
    rotation=(0.0, math.pi / 2.0, 0.0),
    vertices=64,
    open_ended=False
)

for sx in (-1.0, 1.0):
    x = sx * DRUM_LENGTH * 0.57
    add_cylinder(
        'BEARING_OUTER',
        0.0105,
        0.0070,
        (x, 0.0, 0.0),
        MAT_BEARING,
        rotation=(0.0, math.pi / 2.0, 0.0),
        vertices=96,
        open_ended=False
    )

# ======================================================================
# 10. STATIONARY LED ARC / ARC WINDOW
# ======================================================================

arc_center_deg = 270.0
arc_start_deg = arc_center_deg - LED_ARC_WINDOW_DEG * 0.5

arc_points = []
ARC_SAMPLES = 160

for i in range(ARC_SAMPLES):
    u = i / float(ARC_SAMPLES - 1)
    a = math.radians(arc_start_deg + u * LED_ARC_WINDOW_DEG)

    y = LED_ARC_RADIUS * math.cos(a)
    z = LED_ARC_RADIUS * math.sin(a)
    arc_points.append((0.0, y, z))

make_poly_curve(
    'LED_ARC_WINDOW',
    arc_points,
    0.00018,
    MAT_ARC,
    cyclic=False
)

led_positions = []

for i in range(LED_COUNT):
    u = 0.5 if LED_COUNT == 1 else i / float(LED_COUNT - 1)
    angle_deg = arc_start_deg + u * LED_ARC_WINDOW_DEG
    a = math.radians(angle_deg)

    y = LED_ARC_RADIUS * math.cos(a)
    z = LED_ARC_RADIUS * math.sin(a)

    add_cube(
        f'LED_{i:02d}',
        (0.0, y, z),
        (0.0012, LED_PACKAGE, LED_BODY_THICKNESS),
        MAT_LED_OFF,
        rotation=(a, 0.0, 0.0)
    )

    led_positions.append(Vector((0.0, y, z)))

active_led = add_cube(
    'ACTIVE_LED_MARKER',
    led_positions[0],
    (
        0.0016,
        LED_PACKAGE * 1.15,
        max(LED_BODY_THICKNESS * 1.25, 0.0010)
    ),
    MAT_LED_ON
)

# ======================================================================
# 11. FLOOR SCREEN / RASTER GRID
# ======================================================================

screen_w = RASTER_X * PIXEL_PITCH_X
screen_h = RASTER_Y * PIXEL_PITCH_Y

add_cube(
    'PROJECTION_SCREEN',
    (0.0, SCREEN_Y_OFFSET, SCREEN_Z - 0.0007),
    (screen_w + 0.008, screen_h + 0.008, 0.0010),
    MAT_SCREEN
)

for row in range(RASTER_Y):
    for col in range(RASTER_X):
        x = (col - (RASTER_X - 1) * 0.5) * PIXEL_PITCH_X
        y = SCREEN_Y_OFFSET + (row - (RASTER_Y - 1) * 0.5) * PIXEL_PITCH_Y

        add_cube(
            f'GRID_{row:02d}_{col:02d}',
            (x, y, SCREEN_Z),
            (
                PIXEL_PITCH_X * PIXEL_FILL,
                PIXEL_PITCH_Y * PIXEL_FILL,
                0.00045
            ),
            MAT_GRID
        )

# ======================================================================
# 12. PROCEDURAL SMILEY MASK
# ======================================================================

def smiley_mask(col, row):
    u = ((col + 0.5) / RASTER_X) * 2.0 - 1.0
    v = ((row + 0.5) / RASTER_Y) * 2.0 - 1.0

    r = math.sqrt(u*u + v*v)

    # Face outline
    if 0.76 < r < 0.88:
        return True

    # Eyes
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

    # Smile
    smile_center_y = 0.02
    sr = math.sqrt(u*u + (v - smile_center_y) ** 2)

    if (
        -0.62 < u < 0.62 and
        -0.58 < v < -0.02 and
        0.48 < sr < 0.60
    ):
        return True

    # Smile corners
    if (
        0.50 < abs(u) < 0.64 and
        -0.28 < v < -0.02
    ):
        return True

    return False

# ======================================================================
# 13. BRIGHT SMILEY PIXELS
# ======================================================================

bright_pixels = {}
tiny_scale = (0.001, 0.001, 0.001)

for row in range(RASTER_Y):
    for col in range(RASTER_X):
        if not smiley_mask(col, row):
            continue

        x = (col - (RASTER_X - 1) * 0.5) * PIXEL_PITCH_X
        y = SCREEN_Y_OFFSET + (row - (RASTER_Y - 1) * 0.5) * PIXEL_PITCH_Y

        pix = add_cube(
            f'SMILE_{row:02d}_{col:02d}',
            (x, y, SCREEN_Z + 0.00065),
            (
                PIXEL_PITCH_X * PIXEL_FILL,
                PIXEL_PITCH_Y * PIXEL_FILL,
                0.00070
            ),
            MAT_PIXEL
        )
        pix.scale = tiny_scale
        bright_pixels[(row, col)] = pix

# ======================================================================
# 14. ACTIVE SCAN CURSOR
# ======================================================================

cursor = add_cube(
    'ACTIVE_SCAN_CURSOR',
    (0.0, 0.0, SCREEN_Z + 0.0018),
    (
        PIXEL_PITCH_X * 0.42,
        PIXEL_PITCH_Y * 0.42,
        0.0012
    ),
    MAT_CURSOR
)

# ======================================================================
# 15. ANIMATION -- NEW API-SAFE METHOD
# ======================================================================

# Blender 4.4+ Actions are layered and Action.fcurves is no longer a safe
# direct API. This script never accesses it.
#
# Instead, we set Blender's default interpolation mode BEFORE creating each
# group of keyframes. Subsequent keys on that curve inherit the interpolation
# from the previous key.

prefs_edit = bpy.context.preferences.edit
old_interp = prefs_edit.keyframe_new_interpolation_type

# ---------- Raster / LED switching = constant steps ----------
prefs_edit.keyframe_new_interpolation_type = 'CONSTANT'

for pix in bright_pixels.values():
    pix.scale = tiny_scale
    pix.keyframe_insert(data_path='scale', frame=START_FRAME)

cursor.location = (
    -(RASTER_X - 1) * 0.5 * PIXEL_PITCH_X,
    SCREEN_Y_OFFSET - (RASTER_Y - 1) * 0.5 * PIXEL_PITCH_Y,
    SCREEN_Z + 0.0018
)
cursor.keyframe_insert(data_path='location', frame=START_FRAME)

active_led.location = led_positions[0]
active_led.keyframe_insert(data_path='location', frame=START_FRAME)

for row in range(RASTER_Y):
    row_start_index = row * RASTER_X
    row_start_frame = START_FRAME + row_start_index * FRAMES_PER_PIXEL

    # Select next LED / image row.
    active_led.location = led_positions[row]
    active_led.keyframe_insert(data_path='location', frame=row_start_frame)

    for col in range(RASTER_X):
        index = row * RASTER_X + col
        frame = START_FRAME + index * FRAMES_PER_PIXEL

        x = (col - (RASTER_X - 1) * 0.5) * PIXEL_PITCH_X
        y = SCREEN_Y_OFFSET + (row - (RASTER_Y - 1) * 0.5) * PIXEL_PITCH_Y

        cursor.location = (x, y, SCREEN_Z + 0.0018)
        cursor.keyframe_insert(data_path='location', frame=frame)

        pix = bright_pixels.get((row, col))
        if pix is not None:
            pix.scale = (1.0, 1.0, 1.0)
            pix.keyframe_insert(data_path='scale', frame=frame)

cursor.keyframe_insert(data_path='location', frame=END_FRAME)
active_led.keyframe_insert(data_path='location', frame=END_FRAME)

# ---------- Rotor = linear rotation ----------
prefs_edit.keyframe_new_interpolation_type = 'LINEAR'

rotor.rotation_euler = (0.0, 0.0, 0.0)
rotor.keyframe_insert(
    data_path='rotation_euler',
    index=0,
    frame=START_FRAME
)

rotor.rotation_euler.x = rotor_revolutions * 2.0 * math.pi
rotor.keyframe_insert(
    data_path='rotation_euler',
    index=0,
    frame=END_FRAME
)

# Restore user's interpolation preference.
prefs_edit.keyframe_new_interpolation_type = old_interp

# ======================================================================
# 16. MOTOR / DRIVE PULLEY VISUAL
# ======================================================================

add_cylinder(
    'MOTOR',
    0.010,
    0.030,
    (DRUM_LENGTH * 0.68, 0.035, 0.008),
    MAT_FRAME,
    rotation=(0.0, math.pi / 2.0, 0.0),
    vertices=64,
    open_ended=False
)

drive_pulley = add_cylinder(
    'ROTOR_DRIVE_PULLEY',
    DRUM_RADIUS * 0.72,
    0.004,
    (DRUM_LENGTH * 0.53, 0.0, 0.0),
    MAT_FRAME,
    rotation=(0.0, math.pi / 2.0, 0.0),
    vertices=96,
    open_ended=False
)
drive_pulley.parent = rotor

# ======================================================================
# 17. LABELS
# ======================================================================

title_y = SCREEN_Y_OFFSET - screen_h * 0.67

add_text(
    'TITLE_TEXT',
    'HELICAL-SLIT NIPKOW RASTER',
    (0.0, title_y, SCREEN_Z + 0.0012),
    size=0.0044,
    material=MAT_TEXT
)

mode_text = (
    f'TARGET {TARGET_RPM:.0f} RPM | ' +
    ('TRUE-RPM VIEW' if TRUE_2000_RPM_VISUAL else 'SLOWED VIEW')
)

add_text(
    'RPM_TEXT',
    mode_text,
    (0.0, title_y - 0.008, SCREEN_Z + 0.0012),
    size=0.0026,
    material=MAT_TEXT
)

arc_text = (
    f'LED ARC {LED_ARC_WINDOW_DEG:.0f} deg | '
    f'{LED_COUNT} LEDs | {LED_PACKAGE_MM:.1f} mm package'
)

add_text(
    'ARC_TEXT',
    arc_text,
    (0.0, title_y - 0.014, SCREEN_Z + 0.0012),
    size=0.0023,
    material=MAT_TEXT
)

# ======================================================================
# 18. CAMERA
# ======================================================================

bpy.ops.object.camera_add(location=(0.165, -0.195, 0.135))
camera = bpy.context.object
camera.name = 'SIM_CAMERA'
camera.data.lens = 52
point_at(camera, (0.0, -0.002, -0.035))
scene.camera = camera

# ======================================================================
# 19. LIGHTS
# ======================================================================

bpy.ops.object.light_add(type='AREA', location=(0.050, -0.070, 0.150))
key_light = bpy.context.object
key_light.name = 'KEY_LIGHT'
key_light.data.energy = 850
key_light.data.shape = 'DISK'
key_light.data.size = 0.16
point_at(key_light, (0.0, 0.0, -0.015))

bpy.ops.object.light_add(type='AREA', location=(-0.110, 0.080, 0.070))
fill_light = bpy.context.object
fill_light.name = 'FILL_LIGHT'
fill_light.data.energy = 500
fill_light.data.size = 0.12
point_at(fill_light, (0.0, 0.0, -0.020))

# ======================================================================
# 20. METADATA
# ======================================================================

scene['simulation_type'] = 'continuous helical slit Nipkow raster'
scene['inner_core_diameter_mm'] = INNER_CORE_DIAMETER_MM
scene['outer_drum_diameter_mm'] = OUTER_DRUM_DIAMETER_MM
scene['drum_length_mm'] = DRUM_LENGTH_MM
scene['slit_width_mm'] = SLIT_WIDTH_MM
scene['led_package_mm'] = LED_PACKAGE_MM
scene['led_count'] = LED_COUNT
scene['led_arc_window_deg'] = LED_ARC_WINDOW_DEG
scene['target_rpm'] = TARGET_RPM
scene['raster_x'] = RASTER_X
scene['raster_y'] = RASTER_Y

# ======================================================================
# 21. START FRAME / VIEWPORT
# ======================================================================

scene.frame_set(START_FRAME)

try:
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.type = 'MATERIAL'
except Exception:
    pass

# ======================================================================
# 22. REPORT
# ======================================================================

print('')
print('==============================================================')
print(' HELICAL-SLIT NIPKOW SIMULATION READY')
print('==============================================================')
print(f'Blender version          : {bpy.app.version_string}')
print(f'Stationary core diameter : {INNER_CORE_DIAMETER_MM:.2f} mm')
print(f'Outer drum diameter      : {OUTER_DRUM_DIAMETER_MM:.2f} mm')
print(f'Outer drum length        : {DRUM_LENGTH_MM:.2f} mm')
print(f'Helical slit width       : {SLIT_WIDTH_MM:.3f} mm')
print(f'Helix turns along drum   : {HELIX_TURNS_ALONG_DRUM:.2f}')
print('')
print(f'LED package              : {LED_PACKAGE_MM:.2f} mm')
print(f'LED count                : {LED_COUNT}')
print(f'LED arc window           : {LED_ARC_WINDOW_DEG:.2f} degrees')
print(f'LED arc radius           : {LED_ARC_RADIUS_MM:.2f} mm')
print(f'LED arc length           : {led_arc_length/MM:.2f} mm')
print(f'LED center pitch         : {led_center_pitch/MM:.2f} mm')
print(f'Package clearance        : {led_clearance/MM:.2f} mm')

if led_clearance < 0.0:
    print('WARNING: LED packages overlap at this arc width.')
    required_arc_rad = (
        (LED_COUNT - 1) * LED_PACKAGE / LED_ARC_RADIUS
        if LED_COUNT > 1 else 0.0
    )
    required_arc_deg = math.degrees(required_arc_rad)
    print(
        'Minimum arc just to fit packages (zero gap): '
        f'{required_arc_deg:.2f} degrees'
    )
else:
    print('LED packages fit within the selected arc window.')

print('')
print(f'Raster                   : {RASTER_X} x {RASTER_Y}')
print(f'Timeline                  : {START_FRAME} .. {END_FRAME}')
print(f'Target physical RPM       : {TARGET_RPM:.0f}')
print(f'Viewport rotor revolutions: {rotor_revolutions:.2f}')
print('')
print('NO Action.fcurves ACCESS IS USED.')
print('Run Script completed. Press PLAY.')
print('==============================================================')
