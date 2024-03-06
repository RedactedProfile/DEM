# DEM Model Format

<table>
  <tr>
    <td>WARNING!! As of this writing, this is all a heavy work in progress and nothing is ready to be used yet.</td>
  </tr>
</table>

This generic 3D model format is a flat 2D structure inspired in-part by Wavefront OBJ, but the information found within is inspired by MD5, and supports Skeletal animation.  
This format is intended to be easily machine parsable without any additional tools, parsers, or libraries. The data within is purposely laid out in such a way to make the most sense when reading in line-by-line.  Special consideration has been placed to also make reading char-by-char inside each line as easy as possible with no weird tricks or special characters. But if you are the type to read in whole lines at once, the format has you covered by making each line single-space delimited.  I want to value your time as a developer, you're a busy person, as are we all. 

DEM (pronounded `Dehm`) stands for "Despair Engine Model", it is intended for use in that game. You can use it and this blender exporter for your own purposes. If you do plan to use it, please credit me. 

**Author's note:**  
Look, text based model formats aren't known as the most efficient types and often involve a lot of conversion, tokenization, deserialization, etc. 
I've gone to great lengths to make this as sparse, terse, and meaningfully powerful as possible, while keeping the data found within specifically laid out as efficiently as possible and focused on real time rendering. 

And while it's not exactly pretty to look at with the naked eye, it's structure does make it easy to understand what's what and should be easy enough to modify by hand, or even create by hand from scratch. 



#### MDL FORMAT
`model {str}`  
Denotes the start of the model file, and provides the machine name of the model by which it should be referenced in code and editors  
`joints {int}`  
The number of joints for this model  
`meshes {int}`  
The number of meshes for this model  
`sequences {int}`  
Provides the numbers of animation sequences for this model  
`mesh {str}`  
Denotes the start of Model::Mesh Mode and gives the mesh a name   
`mat {str}`  
Defines the text based name of the intended material to use for this model   
`verts {int}`  
Denotes the start of Model::Mesh::Vertex Mode, and provides the number of verticies in this mesh   
`v {int:VertIndex} {float:PointX} {float:PointY} {float:PointZ} {float:NormalX} {float:NormalY} {float:NormalZ} {float:TexU} {float:TexV} {float:ColorR} {float:ColorG} {float:ColorB}`  
Defines a single Vertex with Position Coordinates, Normals, Texture Coordinates, and Vertex Color  
`tris {int}`  
Denotes the start of Model::Mesh::Triangle Mode, and provides the number of triangles in this mesh   
`t {int:PolyIndex} {int:VertIndex} {int:VertIndex} {int:VertIndex}`    
Defines a single triangle, the only primitive DEM supports:  
`weights {int}`   
Denotes the start of Model::Mesh::Skin Mode, and provides the number of weights defined   
`w {int:WeightIndex} {int:JointIndex} {float:InfluenceFactor} {float:PointX} {float:PointY} {float:PointZ}`  
Defines an influence weight 

#### ANIM FORMAT
The DEM Animation format follows a purposly similar structure as the core model format, there are no surprises here or special tricks. 
All animations by default are packed into the DEM model format. However, you may opt to export out a DEMA animation file (pronounced: `dehma`) per sequence, which is useful for shared animation libraries.  (The exporter plans to support this, it's not yet available)

`sequence {str}`  
Denotes the start of Model::Anim::Sequence Mode, and provides the machine name by which it should be referenced in code and editors  
`rate {int}`  
The framerate   
`components {int}`  
The number of animated components (default: 9 (translation, rotation, scale))  
`joints {int}`  
Denotes the start of Model::Anim::Sequence::Joints Mode, and provides the number of joints to be animated in this sequence  
`j {str:Name} {int:ParentJointIndex} {int:Flags} {int:StartComponentIndex}`  
Defines an animated joint  
Note: StartComponentIndex will default to 9  
`bounds {int}`  
Denotes the start of Model::Anim::Sequence::Bounds Mode, and provides the number of bounds in this sequence  
`b {float} {float} {float} {float} {float} {float}`  
Defines min and max points defining the bounding box for each frame, used for collision detection and view culling  
`events {int}`  
Denotes the start of Model::Anim::Sequence::FrameEvents Mode, and provides the number of events in this sequence    
`e {int:EventIndex} {int:FrameIndex} {str:Name}`  
Defines a frame event by machine name to be triggered on a specified frame. It'll be up to your game code to determine what to do with this.  
`frames {int}`    
Denotes the start of Model::Anim::Sequence::Frame Mode, and provides the number of frames this sequence has   
`f {int:FrameIndex} {int:JointIndex} {float:TranslateX} {float:TranslateY} {float:TranslateZ} {float:RotateX} {float:RotateY} {float:RoateZ} {float:ScaleX} {float:ScaleY} {float:ScaleZ}`  
Defines a single frame's singlular joint animated components. There will be an "f" line for every joint in the frame  



# Examples

## Static Model: Blender Cube
```
DEM 10
model box
meshes 1
mesh Cube
mat cube
verts 8
v 0 -1.0 -1.0 -1.0 -0.5773503184318542 -0.5773503184318542 -0.5773503184318542 0.125 0.75 1.0 1.0 1.0
v 1 -1.0 -1.0 1.0 -0.5773503184318542 -0.5773503184318542 0.5773503184318542 0.875 0.75 1.0 1.0 1.0
v 2 -1.0 1.0 -1.0 -0.5773503184318542 0.5773503184318542 -0.5773503184318542 0.125 0.5 1.0 1.0 1.0
v 3 -1.0 1.0 1.0 -0.5773503184318542 0.5773503184318542 0.5773503184318542 0.875 0.5 1.0 1.0 1.0
v 4 1.0 -1.0 -1.0 0.5773503184318542 -0.5773503184318542 -0.5773503184318542 0.375 0.75 1.0 1.0 1.0
v 5 1.0 -1.0 1.0 0.5773503184318542 -0.5773503184318542 0.5773503184318542 0.625 0.75 1.0 1.0 1.0
v 6 1.0 1.0 -1.0 0.5773503184318542 0.5773503184318542 -0.5773503184318542 0.375 0.5 1.0 1.0 1.0
v 7 1.0 1.0 1.0 0.5773503184318542 0.5773503184318542 0.5773503184318542 0.625 0.5 1.0 1.0 1.0
tris 12
t 0 1 2 0
t 1 3 6 2
t 2 7 4 6
t 3 5 0 4
t 4 6 0 2
t 5 3 5 7
t 6 1 3 2
t 7 3 7 6
t 8 7 5 4
t 9 5 1 0
t 10 6 4 0
t 11 3 1 5
```

## Static Model: Multiple Boxes
```
coming soon
```

## Animated Model: Waving Rectangle 
```
coming soon
```


## Blender Exporter Plugin FAQ

This is the original reference implementation of the DEM/DEMA format exporter. If there are others out there that are extending the format, I cannot provide support to those.  

### How does the "material" part work?

The material name that will be put in the file and assigned to the mesh is based off the Material name applied to the mesh in Blender. 


### Are there any limitations for the format?
- Vert count: no
- Mesh count: no
- Joint count: no 
- Sequence count: no 
- TexCoords: yes(1)
- VertColors: yes(2)
- Joint Weights: possibly(3)
- Materials: yes(4)

(1) A single vertex can only have one UV coordinate to it.   
(2) A single vertex can only have one color value to it.  
(3) This part is still a work in progress and may change if I desire to make a hard choice about something.   
(4) There can only be one material per mesh  

### Do I need animation?

No, if no joints or sequences are present in the scene, the information will not be in the exported file. 

### How do I do the animation?
1. In the timeline, make your animation like normal, animating just the joints you're interested in
2. When you've reached the end of your sequence, in the Dope Sheet, scrub to the beginning of your sequence and place a marker (M) and rename it (F2) with the name you wish to call the sequence. 
3. (optional) bake the timeline for the most reliable results. How interpolation works is up to the engine. 

Markers are required for the exporter to pay attention to animation sequences

### How to author multiple animation sequences

1. Do animation like normal
2. Split animations up with named markers at the start of each desired sequence.

**Pro Tip:** Always keep a "Resting Frame" handy to copy and paste at the start of each new sequence. though ultimately it's up to you. 
