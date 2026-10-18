# ======================================================================
# NIPKOW DRUM — SLOW-MOTION VISIBLE OUTER-SLIT FLASH
# ======================================================================
# Corrected + synchronized model:
#   • Horizontal drum axis = world X
#   • Stationary 25 mm inner core
#   • Straight axial LED line
#   • LEDs stand radially upright
#   • Thin cylindrical arc reflector/window
#   • Continuous helical slit
#   • LED timing is derived from the ACTUAL helix phase at each LED X
#   • Bright OUTER_SLIT_FLASH appears on the drum surface
#   • INTERNAL_RAY: LED -> slit crossing
#   • EXTERNAL_RAY: slit crossing -> projected pixel
#   • Smiley builds progressively
#
# Run Script, then press PLAY.
#
# Useful Outliner objects:
#   OUTER_DRUM
#   CONTINUOUS_HELICAL_SLIT
#   THIN_ARC_WINDOW_REFLECTOR
#   OUTER_SLIT_FLASH
#   INTERNAL_RAY
#   EXTERNAL_RAY
#
# No Action.fcurves access is used.
# ======================================================================

import bpy
import math
from mathutils import Vector

# ----------------------------------------------------------------------
# 1. PARAMETERS
# ----------------------------------------------------------------------

INNER_CORE_DIAMETER_MM = 25.0
OUTER_DRUM_DIAMETER_MM = 45.0
DRUM_LENGTH_MM = 100.0

SLIT_WIDTH_MM = 0.30
HELIX_TURNS = 1.0
HELIX_SAMPLES = 800

LED_COUNT = 16
LED_SIZE_X_MM = 1.60
LED_SIZE_Y_MM = 1.60
LED_SIZE_Z_MM = 1.20
LED_STRIP_MARGIN_MM = 6.0

ARC_WINDOW_DEG = 36.0
ARC_INNER_RADIUS_MM = 15.0
ARC_THICKNESS_MM = 0.55
ARC_AXIAL_MARGIN_MM = 4.0

RASTER_X = 24
RASTER_Y = LED_COUNT
PIXEL_PITCH_X_MM = 2.20
PIXEL_PITCH_Y_MM = 3.10
PIXEL_FILL = 0.82

# Slow-motion playback:
FPS = 60
FRAMES_PER_REV = 192          # 3.2 seconds per visible revolution at 60 FPS
LED_FLASH_FRAMES = 12         # 0.2 seconds
RAY_FLASH_FRAMES = 12
START_FRAME = 1

TARGET_RPM = 2000.0           # physical target, metadata only in slow-mo mode

SCREEN_Z_MM = -88.0
SCREEN_Y_OFFSET_MM = 0.0

# ----------------------------------------------------------------------
# 2. UNITS
# ----------------------------------------------------------------------

MM = 0.001

INNER_CORE_DIAMETER = INNER_CORE_DIAMETER_MM * MM
OUTER_DRUM_DIAMETER = OUTER_DRUM_DIAMETER_MM * MM
DRUM_LENGTH = DRUM_LENGTH_MM * MM

CORE_RADIUS = INNER_CORE_DIAMETER * 0.5
DRUM_RADIUS = OUTER_DRUM_DIAMETER * 0.5

SLIT_WIDTH = SLIT_WIDTH_MM * MM

LED_X = LED_SIZE_X_MM * MM
LED_Y = LED_SIZE_Y_MM * MM
LED_Z = LED_SIZE_Z_MM * MM

ARC_INNER_RADIUS = ARC_INNER_RADIUS_MM * MM
ARC_OUTER_RADIUS = ARC_INNER_RADIUS + ARC_THICKNESS_MM * MM

PIXEL_PITCH_X = PIXEL_PITCH_X_MM * MM
PIXEL_PITCH_Y = PIXEL_PITCH_Y_MM * MM

SCREEN_Z = SCREEN_Z_MM * MM
SCREEN_Y_OFF = SCREEN_Y_OFFSET_MM * MM

TOTAL_REVOLUTIONS = RASTER_X
END_FRAME = START_FRAME + TOTAL_REVOLUTIONS * FRAMES_PER_REV + 30

HELIX_X_MIN = -DRUM_LENGTH * 0.49
HELIX_X_MAX = +DRUM_LENGTH * 0.49
HELIX_X_SPAN = HELIX_X_MAX - HELIX_X_MIN

# ----------------------------------------------------------------------
# 3. CLEAN SCENE
# ----------------------------------------------------------------------

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
scene.world.color = (0.006, 0.008, 0.012)

# ----------------------------------------------------------------------
# 4. MATERIALS
# ----------------------------------------------------------------------

def find_input(node, names):
    for n in names:
        if n in node.inputs:
            return node.inputs[n]
    return None

def mat(name, base, metallic=0.0, roughness=0.45,
        emission=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")

    if bsdf:
        s = find_input(bsdf, ["Base Color"])
        if s:
            s.default_value = base

        s = find_input(bsdf, ["Metallic"])
        if s:
            s.default_value = metallic

        s = find_input(bsdf, ["Roughness"])
        if s:
            s.default_value = roughness

        if emission is not None:
            s = find_input(bsdf, ["Emission Color", "Emission"])
            if s:
                s.default_value = (*emission, 1.0)

            s = find_input(bsdf, ["Emission Strength"])
            if s:
                s.default_value = strength

    m.diffuse_color = base
    return m


MAT_DRUM = mat("MAT_DRUM", (0.025, 0.035, 0.055, 1), 0.35, 0.28)
MAT_CORE = mat("MAT_CORE", (0.10, 0.11, 0.13, 1), 0.18, 0.42)
MAT_FRAME = mat("MAT_FRAME", (0.14, 0.15, 0.17, 1), 0.65, 0.28)
MAT_BEARING = mat("MAT_BEARING", (0.32, 0.34, 0.38, 1), 0.88, 0.18)

MAT_LED_OFF = mat("MAT_LED_OFF", (0.04, 0.14, 0.05, 1), 0.0, 0.35)
MAT_LED_ON = mat(
    "MAT_LED_ON", (0.04, 0.80, 0.10, 1), 0.0, 0.18,
    emission=(0.01, 1.0, 0.05), strength=12.0
)

MAT_HELIX = mat(
    "MAT_HELIX", (0.12, 0.45, 1.0, 1), 0.0, 0.18,
    emission=(0.03, 0.30, 1.0), strength=5.0
)

MAT_ARC = mat("MAT_ARC", (0.58, 0.60, 0.64, 1), 0.9, 0.14)

MAT_FLASH = mat(
    "MAT_FLASH", (1.0, 0.95, 0.20, 1), 0.0, 0.06,
    emission=(1.0, 0.65, 0.02), strength=18.0
)

MAT_INTERNAL_RAY = mat(
    "MAT_INTERNAL_RAY", (0.3, 1.0, 0.35, 1), 0.0, 0.08,
    emission=(0.10, 1.0, 0.15), strength=10.0
)

MAT_EXTERNAL_RAY = mat(
    "MAT_EXTERNAL_RAY", (1.0, 0.65, 0.08, 1), 0.0, 0.08,
    emission=(1.0, 0.45, 0.02), strength=10.0
)

MAT_SCREEN = mat("MAT_SCREEN", (0.018, 0.022, 0.028, 1), 0.0, 0.9)
MAT_GRID = mat("MAT_GRID", (0.045, 0.050, 0.060, 1), 0.0, 0.8)

MAT_PIXEL = mat(
    "MAT_PIXEL", (0.03, 0.9, 0.12, 1), 0.0, 0.18,
    emission=(0.01, 1.0, 0.05), strength=7.0
)

MAT_CURSOR = mat(
    "MAT_CURSOR", (1.0, 0.20, 0.02, 1), 0.0, 0.15,
    emission=(1.0, 0.03, 0.01), strength=8.0
)

MAT_TEXT = mat("MAT_TEXT", (0.70, 0.78, 0.90, 1), 0.0, 0.5)

# ----------------------------------------------------------------------
# 5. HELPERS
# ----------------------------------------------------------------------

def add_cube(name, location, dimensions, material=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:
        o.data.materials.append(material)
    return o

def add_cylinder(name, radius, depth, location, material=None,
                 rotation=(0,0,0), vertices=96, open_ended=False):
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
    o = bpy.context.object
    o.name = name
    if material:
        o.data.materials.append(material)
    return o

def add_sphere(name, radius, location, material=None):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=16,
        radius=radius,
        location=location
    )
    o = bpy.context.object
    o.name = name
    if material:
        o.data.materials.append(material)
    return o

def make_curve(name, points, bevel, material):
    cd = bpy.data.curves.new(name + "_CURVE", type='CURVE')
    cd.dimensions = '3D'
    cd.bevel_depth = bevel
    cd.bevel_resolution = 2

    sp = cd.splines.new('POLY')
    sp.points.add(len(points)-1)
    for i,p in enumerate(points):
        sp.points[i].co = (p[0],p[1],p[2],1)

    o = bpy.data.objects.new(name, cd)
    scene.collection.objects.link(o)
    o.data.materials.append(material)
    return o

def make_arc_shell(name, x0, x1, ri, ro, center_deg, span_deg, segments, material):
    verts = []
    faces = []

    a0 = math.radians(center_deg - span_deg*0.5)
    a1 = math.radians(center_deg + span_deg*0.5)

    for i in range(segments+1):
        u = i/segments
        a = a0 + (a1-a0)*u

        yi, zi = ri*math.cos(a), ri*math.sin(a)
        yo, zo = ro*math.cos(a), ro*math.sin(a)

        verts += [
            (x0,yi,zi),(x1,yi,zi),
            (x0,yo,zo),(x1,yo,zo)
        ]

    for i in range(segments):
        b0 = i*4
        b1 = (i+1)*4

        faces += [
            (b0+0,b1+0,b1+1,b0+1),
            (b0+2,b0+3,b1+3,b1+2),
            (b0+0,b0+2,b1+2,b1+0),
            (b0+1,b1+1,b1+3,b0+3),
        ]

    faces += [
        (0,1,3,2),
        (segments*4,segments*4+2,segments*4+3,segments*4+1)
    ]

    me = bpy.data.meshes.new(name+"_MESH")
    me.from_pydata(verts,[],faces)
    me.update()

    o = bpy.data.objects.new(name,me)
    scene.collection.objects.link(o)
    o.data.materials.append(material)
    return o

def add_text(name, text, location, size=0.003):
    cd = bpy.data.curves.new(name+"_FONT", type='FONT')
    cd.body = text
    cd.align_x = 'CENTER'
    cd.align_y = 'CENTER'
    cd.size = size
    cd.extrude = 0.00003
    o = bpy.data.objects.new(name,cd)
    scene.collection.objects.link(o)
    o.location = location
    cd.materials.append(MAT_TEXT)
    return o

def point_at(obj,target):
    d = Vector(target)-obj.location
    obj.rotation_euler = d.to_track_quat('-Z','Y').to_euler()

def set_cylinder_between(obj,p1,p2,radius):
    p1 = Vector(p1)
    p2 = Vector(p2)
    d = p2-p1
    L = max(d.length, 1e-6)

    obj.location = (p1+p2)*0.5
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = d.to_track_quat('Z','Y')

    # Object is a unit-depth cylinder; scale Z gives half the required length
    obj.scale = (radius, radius, L*0.5)

def key_hide(obj, frame, hidden):
    obj.hide_viewport = hidden
    obj.hide_render = hidden
    obj.keyframe_insert(data_path="hide_viewport", frame=frame)
    obj.keyframe_insert(data_path="hide_render", frame=frame)

# ----------------------------------------------------------------------
# 6. ROTOR + OUTER DRUM
# ----------------------------------------------------------------------

rotor = bpy.data.objects.new("ROTOR_MASTER",None)
scene.collection.objects.link(rotor)
rotor.rotation_mode='XYZ'

drum = add_cylinder(
    "OUTER_DRUM",
    DRUM_RADIUS,
    DRUM_LENGTH,
    (0,0,0),
    MAT_DRUM,
    rotation=(0,math.pi/2,0),
    vertices=192,
    open_ended=True
)
drum.parent=rotor

for s in (-1,1):
    ring = add_cylinder(
        "DRUM_END_RING",
        DRUM_RADIUS*1.01,
        0.0022,
        (s*DRUM_LENGTH*0.5,0,0),
        MAT_FRAME,
        rotation=(0,math.pi/2,0),
        vertices=128
    )
    ring.parent=rotor

# Helix local geometry on rotor
helix_pts=[]
for i in range(HELIX_SAMPLES):
    u=i/(HELIX_SAMPLES-1)
    x=HELIX_X_MIN + u*HELIX_X_SPAN
    theta=-math.pi/2 + HELIX_TURNS*2*math.pi*u
    r=DRUM_RADIUS+0.00018
    helix_pts.append((x,r*math.cos(theta),r*math.sin(theta)))

helix = make_curve(
    "CONTINUOUS_HELICAL_SLIT",
    helix_pts,
    max(0.00003,SLIT_WIDTH*0.5),
    MAT_HELIX
)
helix.parent=rotor

# ----------------------------------------------------------------------
# 7. STATIONARY CORE / SHAFT
# ----------------------------------------------------------------------

core = add_cylinder(
    "STATIONARY_25MM_CORE",
    CORE_RADIUS,
    DRUM_LENGTH*0.92,
    (0,0,0),
    MAT_CORE,
    rotation=(0,math.pi/2,0),
    vertices=144
)

shaft = add_cylinder(
    "STATIONARY_SHAFT",
    0.003,
    DRUM_LENGTH*1.30,
    (0,0,0),
    MAT_BEARING,
    rotation=(0,math.pi/2,0),
    vertices=64
)

for s in (-1,1):
    x=s*DRUM_LENGTH*0.58
    add_cylinder(
        "BEARING",
        0.0105,
        0.007,
        (x,0,0),
        MAT_BEARING,
        rotation=(0,math.pi/2,0),
        vertices=96
    )

# ----------------------------------------------------------------------
# 8. STRAIGHT AXIAL LED LINE
# ----------------------------------------------------------------------

strip_length=DRUM_LENGTH-2*LED_STRIP_MARGIN_MM*MM

if LED_COUNT==1:
    led_x_positions=[0]
else:
    led_x_positions=[
        -strip_length*0.5+i*strip_length/(LED_COUNT-1)
        for i in range(LED_COUNT)
    ]

led_center_z=-(CORE_RADIUS+LED_Z*0.5)

led_glows=[]

for i,x in enumerate(led_x_positions):
    add_cube(
        f"LED_OFF_{i:02d}",
        (x,0,led_center_z),
        (LED_X,LED_Y,LED_Z),
        MAT_LED_OFF
    )

    g=add_cube(
        f"LED_FLASH_{i:02d}",
        (x,0,led_center_z),
        (LED_X*1.20,LED_Y*1.20,LED_Z*1.22),
        MAT_LED_ON
    )
    key_hide(g,START_FRAME,True)
    led_glows.append(g)

add_cube(
    "LED_AXIAL_CARRIER",
    (0,0,-(CORE_RADIUS+LED_Z+0.00025)),
    (strip_length+0.004,LED_Y*1.4,0.00045),
    MAT_FRAME
)

# ----------------------------------------------------------------------
# 9. ARC WINDOW / REFLECTOR
# ----------------------------------------------------------------------

arc_x0=-strip_length*0.5-ARC_AXIAL_MARGIN_MM*MM
arc_x1=+strip_length*0.5+ARC_AXIAL_MARGIN_MM*MM

arc_window=make_arc_shell(
    "THIN_ARC_WINDOW_REFLECTOR",
    arc_x0,arc_x1,
    ARC_INNER_RADIUS,ARC_OUTER_RADIUS,
    -90.0,ARC_WINDOW_DEG,80,MAT_ARC
)

# ----------------------------------------------------------------------
# 10. SCREEN + SMILEY
# ----------------------------------------------------------------------

screen_w=RASTER_X*PIXEL_PITCH_X
screen_h=RASTER_Y*PIXEL_PITCH_Y

add_cube(
    "PROJECTION_SCREEN",
    (0,SCREEN_Y_OFF,SCREEN_Z-0.0007),
    (screen_w+0.008,screen_h+0.008,0.001),
    MAT_SCREEN
)

for r in range(RASTER_Y):
    for c in range(RASTER_X):
        px=(c-(RASTER_X-1)*0.5)*PIXEL_PITCH_X
        py=SCREEN_Y_OFF+(r-(RASTER_Y-1)*0.5)*PIXEL_PITCH_Y
        add_cube(
            f"GRID_{r:02d}_{c:02d}",
            (px,py,SCREEN_Z),
            (PIXEL_PITCH_X*PIXEL_FILL,PIXEL_PITCH_Y*PIXEL_FILL,0.00035),
            MAT_GRID
        )

def smiley(c,r):
    u=((c+0.5)/RASTER_X)*2-1
    v=((r+0.5)/RASTER_Y)*2-1
    q=math.sqrt(u*u+v*v)

    if 0.76<q<0.88:
        return True

    e1=(((u+0.30)/0.09)**2+((v-0.27)/0.13)**2)<=1
    e2=(((u-0.30)/0.09)**2+((v-0.27)/0.13)**2)<=1
    if e1 or e2:
        return True

    sr=math.sqrt(u*u+(v-0.02)**2)
    return (-0.62<u<0.62 and -0.58<v<-0.02 and 0.48<sr<0.60)

pixels={}
for r in range(RASTER_Y):
    for c in range(RASTER_X):
        if not smiley(c,r):
            continue

        px=(c-(RASTER_X-1)*0.5)*PIXEL_PITCH_X
        py=SCREEN_Y_OFF+(r-(RASTER_Y-1)*0.5)*PIXEL_PITCH_Y

        p=add_cube(
            f"PIXEL_{r:02d}_{c:02d}",
            (px,py,SCREEN_Z+0.0006),
            (PIXEL_PITCH_X*PIXEL_FILL,PIXEL_PITCH_Y*PIXEL_FILL,0.00065),
            MAT_PIXEL
        )
        key_hide(p,START_FRAME,True)
        pixels[(r,c)]=p

# ----------------------------------------------------------------------
# 11. FLASH OBJECTS
# ----------------------------------------------------------------------

# Physical optical crossing is at the center of the lower arc: theta = -90°
# The marker is slightly OUTSIDE the drum so the glow is clearly visible.
FLASH_RADIUS=0.0017
FLASH_SURFACE_R=DRUM_RADIUS+0.0012

outer_flash=add_sphere(
    "OUTER_SLIT_FLASH",
    FLASH_RADIUS,
    (led_x_positions[0],0,-FLASH_SURFACE_R),
    MAT_FLASH
)
key_hide(outer_flash,START_FRAME,True)

# Always-visible small crossing guide
cross_guide=add_sphere(
    "OUTER_CROSS_GUIDE",
    0.00055,
    (led_x_positions[0],0,-FLASH_SURFACE_R),
    MAT_CURSOR
)

# Beam cylinders are created with depth=2, radius=1 then scaled/oriented.
internal_ray=add_cylinder(
    "INTERNAL_RAY",
    1.0,
    2.0,
    (0,0,0),
    MAT_INTERNAL_RAY,
    vertices=16
)
internal_ray.rotation_mode='QUATERNION'
key_hide(internal_ray,START_FRAME,True)

external_ray=add_cylinder(
    "EXTERNAL_RAY",
    1.0,
    2.0,
    (0,0,0),
    MAT_EXTERNAL_RAY,
    vertices=16
)
external_ray.rotation_mode='QUATERNION'
key_hide(external_ray,START_FRAME,True)

screen_cursor=add_cube(
    "SCREEN_CURSOR",
    (0,0,SCREEN_Z+0.0016),
    (PIXEL_PITCH_X*0.38,PIXEL_PITCH_Y*0.38,0.001),
    MAT_CURSOR
)

# ----------------------------------------------------------------------
# 12. TRUE HELIX-CROSSING TIMING
# ----------------------------------------------------------------------

# Helix local angle at axial position x:
# theta0(x) = -90° + 2*pi*HELIX_TURNS*u
#
# The lower optical window is centered at target angle = -90°.
# Crossing condition:
# theta0 + rotor_angle = target  (mod 2*pi)
#
# Therefore:
# rotor_phase_for_cross = (target - theta0) mod 2*pi
#
# This determines the precise slow-motion frame of each LED crossing.

target_angle=-math.pi/2

cross_fraction=[]

for x in led_x_positions:
    u=(x-HELIX_X_MIN)/HELIX_X_SPAN
    theta0=-math.pi/2 + HELIX_TURNS*2*math.pi*u
    phase=(target_angle-theta0)%(2*math.pi)
    frac=phase/(2*math.pi)
    cross_fraction.append(frac)

# ----------------------------------------------------------------------
# 13. ROTOR ANIMATION — EXACTLY ONE REVOLUTION PER COLUMN
# ----------------------------------------------------------------------

for frame in range(START_FRAME,END_FRAME+1):
    rev=(frame-START_FRAME)/float(FRAMES_PER_REV)
    rotor.rotation_euler.x=rev*2*math.pi
    rotor.keyframe_insert(
        data_path="rotation_euler",
        index=0,
        frame=frame
    )

# ----------------------------------------------------------------------
# 14. FLASH / RAY / PIXEL ANIMATION
# ----------------------------------------------------------------------

for col in range(RASTER_X):
    rev_start=START_FRAME+col*FRAMES_PER_REV

    for row in range(RASTER_Y):
        frac=cross_fraction[row]
        frame=rev_start+int(round(frac*FRAMES_PER_REV))

        x=led_x_positions[row]

        # Projected pixel position
        px=(col-(RASTER_X-1)*0.5)*PIXEL_PITCH_X
        py=SCREEN_Y_OFF+(row-(RASTER_Y-1)*0.5)*PIXEL_PITCH_Y

        # Actual world crossing point on lower drum surface
        slit_point=(x,0,-FLASH_SURFACE_R)

        # LED center
        led_point=(x,0,led_center_z)

        # Move always-visible guide
        cross_guide.location=slit_point
        cross_guide.keyframe_insert(data_path="location",frame=frame)

        # Move screen cursor
        screen_cursor.location=(px,py,SCREEN_Z+0.0016)
        screen_cursor.keyframe_insert(data_path="location",frame=frame)

        # Only light when requested image pixel is ON
        if smiley(col,row):
            led=led_glows[row]

            # LED flash
            if frame>START_FRAME:
                key_hide(led,frame-1,True)
            key_hide(led,frame,False)
            key_hide(led,frame+LED_FLASH_FRAMES,True)

            # Outer drum flash
            outer_flash.location=slit_point
            outer_flash.keyframe_insert(data_path="location",frame=frame)
            if frame>START_FRAME:
                key_hide(outer_flash,frame-1,True)
            key_hide(outer_flash,frame,False)
            key_hide(outer_flash,frame+LED_FLASH_FRAMES,True)

            # Internal ray: LED -> slit
            set_cylinder_between(
                internal_ray,
                led_point,
                slit_point,
                radius=0.00020
            )
            internal_ray.keyframe_insert(data_path="location",frame=frame)
            internal_ray.keyframe_insert(data_path="rotation_quaternion",frame=frame)
            internal_ray.keyframe_insert(data_path="scale",frame=frame)

            if frame>START_FRAME:
                key_hide(internal_ray,frame-1,True)
            key_hide(internal_ray,frame,False)
            key_hide(internal_ray,frame+RAY_FLASH_FRAMES,True)

            # External ray: slit -> screen pixel
            screen_point=(px,py,SCREEN_Z+0.0010)

            set_cylinder_between(
                external_ray,
                slit_point,
                screen_point,
                radius=0.00024
            )
            external_ray.keyframe_insert(data_path="location",frame=frame)
            external_ray.keyframe_insert(data_path="rotation_quaternion",frame=frame)
            external_ray.keyframe_insert(data_path="scale",frame=frame)

            if frame>START_FRAME:
                key_hide(external_ray,frame-1,True)
            key_hide(external_ray,frame,False)
            key_hide(external_ray,frame+RAY_FLASH_FRAMES,True)

            # Reveal projected pixel permanently
            p=pixels[(row,col)]
            if frame>START_FRAME:
                key_hide(p,frame-1,True)
            key_hide(p,frame,False)

# ----------------------------------------------------------------------
# 15. LABELS
# ----------------------------------------------------------------------

title_y=SCREEN_Y_OFF-screen_h*0.74

add_text(
    "TITLE",
    "SLOW-MOTION HELIX CROSSING + OUTER DRUM FLASH",
    (0,title_y,SCREEN_Z+0.0012),
    0.0038
)

add_text(
    "INFO",
    f"{FPS} FPS | {FRAMES_PER_REV} frames/rev | {LED_FLASH_FRAMES} frame flash | target physical {TARGET_RPM:.0f} RPM",
    (0,title_y-0.007,SCREEN_Z+0.0012),
    0.0023
)

# ----------------------------------------------------------------------
# 16. CAMERA — LOWER SIDE ANGLE
# ----------------------------------------------------------------------
# The previous camera looked from above and the bottom flash was hidden
# by the drum. This camera is intentionally positioned at a lower side angle
# so OUTER_SLIT_FLASH on the lower cylinder is visible.

bpy.ops.object.camera_add(
    location=(0.160,-0.190,-0.020)
)
camera=bpy.context.object
camera.name="SIM_CAMERA"
camera.data.lens=48
point_at(camera,(0,0,-0.045))
scene.camera=camera

# ----------------------------------------------------------------------
# 17. LIGHTS
# ----------------------------------------------------------------------

bpy.ops.object.light_add(type='AREA',location=(0.05,-0.08,0.13))
key=bpy.context.object
key.data.energy=850
key.data.size=0.16
point_at(key,(0,0,-0.02))

bpy.ops.object.light_add(type='AREA',location=(-0.10,0.07,0.04))
fill=bpy.context.object
fill.data.energy=450
fill.data.size=0.12
point_at(fill,(0,0,-0.03))

# ----------------------------------------------------------------------
# 18. METADATA / VIEWPORT
# ----------------------------------------------------------------------

scene["target_rpm"]=TARGET_RPM
scene["slowmo_fps"]=FPS
scene["frames_per_revolution"]=FRAMES_PER_REV
scene["led_flash_frames"]=LED_FLASH_FRAMES
scene["model"]="actual helix phase synchronized LED crossing"

scene.frame_set(START_FRAME)

try:
    for a in bpy.context.screen.areas:
        if a.type=='VIEW_3D':
            a.spaces.active.shading.type='MATERIAL'
except Exception:
    pass

# ----------------------------------------------------------------------
# 19. REPORT
# ----------------------------------------------------------------------

print("")
print("============================================================")
print(" VISIBLE OUTER-SLIT FLASH DEMO READY")
print("============================================================")
print(f"Blender                  : {bpy.app.version_string}")
print(f"FPS                      : {FPS}")
print(f"Frames/revolution        : {FRAMES_PER_REV}")
print(f"Seconds/revolution       : {FRAMES_PER_REV/FPS:.2f}")
print(f"LED/flash duration       : {LED_FLASH_FRAMES/FPS:.2f} s")
print(f"Target physical RPM      : {TARGET_RPM:.0f}")
print("")
print("Timing is now derived from the actual helical phase at each LED X.")
print("Camera is moved low so the bottom drum flash is visible.")
print("")
print("Watch these objects:")
print("  OUTER_SLIT_FLASH")
print("  INTERNAL_RAY")
print("  EXTERNAL_RAY")
print("  LED_FLASH_00 ... LED_FLASH_15")
print("")
print("Press PLAY.")
print("============================================================")
