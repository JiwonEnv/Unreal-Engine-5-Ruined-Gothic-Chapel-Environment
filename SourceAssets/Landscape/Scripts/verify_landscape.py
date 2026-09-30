import unreal,json,os,math,struct
root=unreal.Paths.project_dir()+'SourceAssets/Landscape/'
ea=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=ea.get_all_level_actors()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
land=next(a for a in actors if isinstance(a,unreal.Landscape))
ignore=[a for a in actors if a!=land]
raw=open(root+'Chapel_Hill_505.r16','rb').read();v=struct.unpack('<%dH'%(len(raw)//2),raw)
checks=[]
for x,y in [(600,0),(-1000,0),(-3000,-250),(-6000,50),(600,3000),(600,-6000),(9000,0)]:
 h=unreal.SystemLibrary.line_trace_single(world,unreal.Vector(x,y,1500),unreal.Vector(x,y,-4000),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,ignore,unreal.DrawDebugTrace.NONE,True)
 data=h.to_tuple() if h else None
 # HitResult: blocking, penetrating, time, distance, location, impact point, normal, impact normal...
 z=data[4].z if data and data[0] else None
 i=round((x+12000)/50);j=round((y+12600)/50);expected=(v[j*505+i]-32768)/1.28+land.get_actor_location().z
 checks.append({'x':x,'y':y,'actual_z':z,'expected_z':expected,'pass':z is not None and abs(z-expected)<3})
paths=[]
for section,start,end,ys in [('doorway',-90,110,[-45,0,45]),('aisle',110,820,[-65,0,65])]:
 for y in ys:
  hit=unreal.SystemLibrary.capsule_trace_single(world,unreal.Vector(start,y,116),unreal.Vector(end,y,116),25,88,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE,True)
  a=hit.to_tuple() if hit else None
  paths.append({'section':section,'y':y,'blocked':bool(a and a[0])})
slopes=[]
for x in range(-8500,-50,50):
 y=round((300*math.sin(x/1800))/50)*50
 i=round((x+12000)/50);j=round((y+12600)/50)
 slopes.append(math.degrees(math.atan(abs(v[j*505+i+1]-v[j*505+i])/1.28/50)))
report={'height_checks':checks,'interior_capsule_sweeps':paths,'max_approach_longitudinal_slope_degrees':max(slopes),'bounds':str(land.get_actor_bounds(False)),'edit_layers_preserved':land.get_editor_property('can_have_layers_content'),'material':str(land.get_editor_property('landscape_material'))}
with open(root+'verification.json','w') as f:json.dump(report,f,indent=2)
assert all(c['pass'] for c in checks),'Landscape height import mismatch'
assert not any(c['blocked'] for c in paths),'Interior collision regression'
# Save only current level; original material assets remain untouched.
assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
b=json.load(open(root+'build_report.json'));b.update(heightmap_import='verified',height_range_cm=[(min(v)-32768)/1.28,(max(v)-32768)/1.28]);json.dump(b,open(root+'build_report.json','w'),indent=2)
cam=next((a for a in actors if a.get_actor_label()=='LS_Camera_Hill_Overview'),None)
if cam is None:cam=ea.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(-2700,-3100,1700))
cam.set_actor_label('LS_Camera_Hill_Overview');cam.set_folder_path('Landscape/Review');cam.set_actor_rotation(unreal.Rotator(pitch=-10,yaw=40,roll=0),False)
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(cam.get_actor_location(),cam.get_actor_rotation())
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_game_view(True)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,root+'Landscape_Overview.png',camera=cam,delay=1)
unreal.log('LANDSCAPE_VERIFIED_AND_SAVED')

