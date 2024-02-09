from dataclasses import dataclass

MAX_FLOAT_PRECISION = 16

@dataclass
class Vert:
    i: int      = 0
    vx: float   = 0.0
    vy: float   = 0.0
    vz: float   = 0.0
    nx: float   = 0.0
    ny: float   = 0.0
    nz: float   = 0.0
    u: float    = 0.0
    v: float    = 0.0
    r: float    = 0.0
    g: float    = 0.0
    b: float    = 0.0
    
    def __str__(self):
        return "v {} {} {} {} {} {} {} {} {} {} {} {}\n".format(
            self.i, 
            round(self.vx, MAX_FLOAT_PRECISION),
            round(self.vy, MAX_FLOAT_PRECISION),
            round(self.vz, MAX_FLOAT_PRECISION),
            round(self.nx, MAX_FLOAT_PRECISION),
            round(self.ny, MAX_FLOAT_PRECISION),
            round(self.nz, MAX_FLOAT_PRECISION),
            round(self.u, MAX_FLOAT_PRECISION),
            round(self.v, MAX_FLOAT_PRECISION),
            round(self.r, MAX_FLOAT_PRECISION),
            round(self.g, MAX_FLOAT_PRECISION),
            round(self.b, MAX_FLOAT_PRECISION)
        )
    
@dataclass
class Joint:
    name: str
    parent: int = -1
    vx: float   = 0.0
    vy: float   = 0.0
    vz: float   = 0.0 
    rx: float   = 0.0
    ry: float   = 0.0
    rz: float   = 0.0

    def __str__(self):
        return "j {} {} {} {} {} {} {} {}\n".format(
            self.name,
            self.parent,
            round(self.vx, MAX_FLOAT_PRECISION),
            round(self.vy, MAX_FLOAT_PRECISION),
            round(self.vz, MAX_FLOAT_PRECISION),
            round(self.rx, MAX_FLOAT_PRECISION),
            round(self.ry, MAX_FLOAT_PRECISION),
            round(self.rz, MAX_FLOAT_PRECISION) 
        )

@dataclass 
class Tri:
    i: int
    v1: int = 0
    v2: int = 0
    v3: int = 0

    def __str__(self):
        return "t {} {} {} {}\n".format(
            self.i,
            self.v1,
            self.v2,
            self.v3 
        )
    
@dataclass 
class Weight:
    i: int 
    j: int 
    w: float 
    x: float 
    y: float 
    z: float 

    def __str__(self):
        return "w {} {} {} {} {} {}\n".format(
            self.i,
            self.j,
            round(self.w, MAX_FLOAT_PRECISION),
            round(self.x, MAX_FLOAT_PRECISION),
            round(self.y, MAX_FLOAT_PRECISION),
            round(self.z, MAX_FLOAT_PRECISION) 
        )



#### ANIM FORMAT
@dataclass 
class AnimJoint:
    joint: Joint   # to reference name and parent index 
    flags: int 
    start_index: int  # not sure if I need this for my purposes

    def __str__(self):
        return "h "

@dataclass
class Frame:
    i: int 
    tx: float 
    ty: float 
    tz: float 
    rx: float 
    ry: float 
    rz: float 

    def __str__(self):
        return "f "
    
@dataclass
class Clip:
    joints: [Joint]
    frameRate: int 