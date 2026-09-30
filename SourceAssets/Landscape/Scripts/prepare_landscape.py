"""Prepare hill heightmap and landscape material in the currently open UE 5.6 level.
Height import is performed using Landscape Sculpt > Heightmap > Import from File.
"""
import unreal, os, json, math, struct, shutil, datetime
ROOT=os.path.join(unreal.Paths.project_dir(),'SourceAssets/Landscape')
EA=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors=EA.get_all_level_actors()
lands=[a for a in actors if isinstance(a,unreal.Landscape)]
assert len(lands)==1, 'Expected one landscape'
land=lands[0]
# Preserve the current in-memory level, including user edits, before modifying it.
assert unreal.EditorLevelLibrary.save_current_level()
backup=os.path.join(unreal.Paths.project_saved_dir(),'LandscapeBackups',datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
os.makedirs(backup,exist_ok=True)
shutil.copy2(os.path.join(unreal.Paths.project_content_dir(),'GothicChapel/Levels/Main/GothicChapel_Main.umap'),backup)
N=505; step=50.; ox=600-(N-1)*step/2; oy=-(N-1)*step/2

def smooth(a,b,v):
 t=max(0.,min(1.,(v-a)/(b-a))); return t*t*(3-2*t)
def height(x,y):
 # Broad asymmetric ridge, falling away from the chapel clearing.
 dx=x-600
 radius=math.sqrt((dx/4700)**2+(y/3300)**2)
 hill=-1850+1820*math.exp(-radius**1.65)
 undulation=(90*math.sin(x/1900+y/2400)+65*math.sin(x/900-y/1350)+24*math.sin(x/340+y/490))*smooth(.15,1.1,radius)
 z=hill+undulation
 # Flat foundation and shoulder leave the 6x12m structure fully above ground.
 d=max(abs(dx)-850,abs(y)-700)
 blend=smooth(0,1500,d)
 z=-12*(1-blend)+z*blend
 # Gentle west approach: 2.8m tread, softer shoulders, merges with hill.
 cy=300*math.sin(min(0,x)/1800)*smooth(-200,-2200,x) if False else 300*math.sin(min(0,x)/1800)*smooth(200,2200,-x)
 pathz=-12-1150*smooth(0,9000,-x)
 path=smooth(420,150,abs(y-cy))*(1-smooth(0,300,x))* (1-smooth(8500,10000,-x))
 return z*(1-path)+pathz*path
vals=[]
for j in range(N):
 for i in range(N):vals.append(max(0,min(65535,round(32768+height(ox+i*step,oy+j*step)*128/100))))
with open(os.path.join(ROOT,'Chapel_Hill_505.r16'),'wb') as f:f.write(struct.pack('<%dH'%len(vals),*vals))
land.set_actor_scale3d(unreal.Vector(step,step,100))
land.set_actor_location(unreal.Vector(ox,oy,0),False,False)
land.set_actor_label('Landscape_Chapel_Hill')
lib=unreal.MaterialEditingLibrary
path='/Game/GothicChapel/Environment/Landscape/Materials'
name='M_Landscape_ChapelHill'
assert not unreal.EditorAssetLibrary.does_asset_exist(path+'/'+name), 'Material exists; inspect before rebuilding'
m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,path,unreal.Material,unreal.MaterialFactoryNew())
pos=lib.create_material_expression(m,unreal.MaterialExpressionWorldPosition,-700,0)
custom=lib.create_material_expression(m,unreal.MaterialExpressionCustom,-400,0)
custom.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT3)
inp=unreal.CustomInput(); inp.set_editor_property('input_name','P'); custom.set_editor_property('inputs',[inp])
custom.set_editor_property('description','Muted meadow, limestone soil and wet west approach')
custom.set_editor_property('code',r'''
float2 p=P.xy;
float n=sin(p.x*.009+sin(p.y*.006))*sin(p.y*.011)+.45*sin(p.x*.034+p.y*.025);
float micro=sin(p.x*.45)*sin(p.y*.37)*.5+.5;
float macro=sin(p.x*.0008+p.y*.0006)*sin(p.y*.0011);
float3 meadow=lerp(float3(.065,.082,.040),float3(.16,.17,.085),saturate(.5+n*.22+macro*.18));
float3 earth=lerp(float3(.12,.105,.078),float3(.25,.23,.18),micro*.45+.2);
float3 stone=float3(.29,.28,.235)*(0.8+micro*.3);
float3 wn=normalize(cross(ddy(P),ddx(P)));
float slope=1-abs(wn.z);
float rock=smoothstep(.10,.30,slope)*.65;
float cx=min(0,p.x);
float cy=300*sin(cx/1800)*smoothstep(200,2200,-cx);
float track=(1-smoothstep(125,240,abs(p.y-cy)+n*13))*(1-smoothstep(-50,150,p.x))*(1-smoothstep(8500,10000,-p.x));
float foundation=(1-smoothstep(680,980,abs(p.x-600)))*(1-smoothstep(470,770,abs(p.y)));
float soil=max(track,foundation*.8);
return lerp(lerp(meadow,stone,rock),earth,soil)*(0.93+micro*.14);
''')
lib.connect_material_expressions(pos,'',custom,'P');lib.connect_material_property(custom,'',unreal.MaterialProperty.MP_BASE_COLOR)
r=lib.create_material_expression(m,unreal.MaterialExpressionConstant,-400,280);r.set_editor_property('r',.68);lib.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
metal=lib.create_material_expression(m,unreal.MaterialExpressionConstant,-400,400);metal.set_editor_property('r',0);lib.connect_material_property(metal,'',unreal.MaterialProperty.MP_METALLIC)
lib.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m)
land.set_editor_property('landscape_material',m)
# User's blockout was temporarily hidden in editor: show for terrain integration review.
for a in actors:
 if a.get_actor_label().startswith('BO_'): a.set_is_temporarily_hidden_in_editor(False)
unreal.EditorLevelLibrary.set_level_viewport_camera_info(unreal.Vector(-3700,-4200,2500),unreal.Rotator(pitch=-23,yaw=47,roll=0))
with open(os.path.join(ROOT,'build_report.json'),'w') as f:json.dump({'backup':backup,'resolution':N,'xy_scale_cm':step,'origin':[ox,oy,0],'height_range_cm':[min((v-32768)*100/128 for v in vals),max((v-32768)*100/128 for v in vals)],'material':path+'/'+name,'heightmap_import':'pending'},f,indent=2)
unreal.log('LANDSCAPE_PREPARED: import Chapel_Hill_505.r16')

