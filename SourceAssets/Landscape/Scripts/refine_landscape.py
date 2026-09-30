import unreal,os,json,math,struct
root=unreal.Paths.project_dir()+'SourceAssets/Landscape/'
def smooth(a,b,v):
 t=max(0.,min(1.,(v-a)/(b-a)));return t*t*(3-2*t)
def base(x,y):
 dx=x-600;rad=math.sqrt((dx/5200)**2+(y/3900)**2)
 z=-1800+1788*math.exp(-rad**1.85)
 z+=(75*math.sin(x/1900+y/2400)+55*math.sin(x/900-y/1350)+15*math.sin(x/340+y/490))*smooth(.15,1.1,rad)
 d=math.sqrt((dx/1100)**2+(y/850)**2)
 b=smooth(1,2.5,d)
 return -12*(1-b)+z*b
def height(x,y):
 cy=300*math.sin(min(0,x)/1800)*smooth(200,2200,-x)
 path=(1-smooth(150,700,abs(y-cy)))*(1-smooth(-100,100,x))*(1-smooth(8500,10000,-x))
 return base(x,y)*(1-path)+base(x,cy)*path
vals=[round(32768+height(-12000+i*50,-12600+j*50)*1.28) for j in range(505) for i in range(505)]
with open(root+'Chapel_Hill_505.r16','wb') as f:f.write(struct.pack('<%dH'%len(vals),*vals))
m=unreal.load_asset('/Game/GothicChapel/Environment/Landscape/Materials/M_Landscape_ChapelHill')
lib=unreal.MaterialEditingLibrary
lib.delete_all_material_expressions(m)
pos=lib.create_material_expression(m,unreal.MaterialExpressionWorldPosition,-700,0)
head=r'''
struct TerrainNoise {
 float hash(float2 v){return frac(sin(dot(v,float2(127.1,311.7)))*43758.5453);}
 float noise(float2 v){float2 i=floor(v),f=frac(v);f=f*f*(3-2*f);return lerp(lerp(hash(i),hash(i+float2(1,0)),f.x),lerp(hash(i+float2(0,1)),hash(i+1),f.x),f.y);}
 float fbm(float2 p){return noise(p)*.55+noise(p*2.03+17)*.28+noise(p*4.13-9)*.17;}
}; TerrainNoise T;
float2 p=P.xy;
float n=T.fbm(p*.012);
float detail=T.fbm(p*.12);
float macro=T.fbm(p*.0007);
float cy=300*sin(min(0,p.x)/1800)*smoothstep(200,2200,-p.x);
float track=(1-smoothstep(110,240,abs(p.y-cy)+(n-.5)*85))*(1-smoothstep(-50,150,p.x))*(1-smoothstep(8500,10000,-p.x));
float foundation=(1-smoothstep(680,980,abs(p.x-600)))*(1-smoothstep(470,770,abs(p.y)));
float soil=max(track,foundation*.85);
'''
def custom(name,code,output,y):
 c=lib.create_material_expression(m,unreal.MaterialExpressionCustom,-380,y)
 c.set_editor_property('output_type',output);c.set_editor_property('description',name)
 i=unreal.CustomInput();i.set_editor_property('input_name','P');c.set_editor_property('inputs',[i]);c.set_editor_property('code',head+code)
 lib.connect_material_expressions(pos,'',c,'P');return c
c=custom('Meadow / weathered soil / exposed limestone',r'''
float3 meadow=lerp(float3(.055,.071,.038),float3(.15,.16,.083),saturate(n*.75+macro*.25));
float3 earth=lerp(float3(.105,.091,.070),float3(.245,.220,.170),n*.75+detail*.25);
float3 normal=normalize(cross(ddy(P),ddx(P)));
float rock=smoothstep(.08,.27,1-abs(normal.z))*.65;
float3 stone=lerp(float3(.17,.17,.145),float3(.32,.30,.25),detail);
return lerp(lerp(meadow,stone,rock),earth,soil)*(.88+detail*.24);
''',unreal.CustomMaterialOutputType.CMOT_FLOAT3,0)
lib.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
r=custom('Damp ground roughness', 'return lerp(.87,.38,soil*(.55+.45*n));',unreal.CustomMaterialOutputType.CMOT_FLOAT1,280)
lib.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
n=custom('Fine ground normal', 'float e=1.5; float h=T.fbm(p*.08); float hx=T.fbm((p+float2(e,0))*.08); float hy=T.fbm((p+float2(0,e))*.08); return normalize(float3((h-hx)*.55,(h-hy)*.55,1));',unreal.CustomMaterialOutputType.CMOT_FLOAT3,500)
lib.connect_material_property(n,'',unreal.MaterialProperty.MP_NORMAL)
lib.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m)
# Frame the actual west approach; explicit keywords avoid Rotator positional ordering.
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(-2700,-3100,1700),unreal.Rotator(pitch=-20,yaw=44,roll=0))
unreal.log('LANDSCAPE_REFINED: reimport heightmap')
