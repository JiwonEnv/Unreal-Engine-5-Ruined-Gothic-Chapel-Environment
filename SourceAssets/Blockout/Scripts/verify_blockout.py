import unreal,json,os
root=os.path.join(unreal.Paths.project_dir(),'SourceAssets/Blockout')
ea=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
rows=[]
def vec(v):return [round(v.x,3),round(v.y,3),round(v.z,3)]
for a in ea.get_all_level_actors():
    p,h=a.get_actor_bounds(False)
    row={'label':a.get_actor_label(),'location':vec(a.get_actor_location()),'rotation':str(a.get_actor_rotation()),'bounds_centre':vec(p),'bounds_half':vec(h),'hidden_editor':a.is_temporarily_hidden_in_editor()}
    if isinstance(a,unreal.StaticMeshActor):
        m=a.static_mesh_component.static_mesh
        row['mesh_bounds']=str(m.get_bounding_box()) if m else None
    rows.append(row)
hits=[]
for section,start,end,ys in [('doorway',-90,110,[-45,0,45]),('aisle',110,820,[-65,0,65])]:
  for y in ys:
    hit=unreal.SystemLibrary.capsule_trace_single(world,unreal.Vector(start,y,116),unreal.Vector(end,y,116),25,88,unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,False,[],unreal.DrawDebugTrace.NONE,True)
    if hit is None:
        hits.append({'section':section,'y':y,'blocking_hit':False})
    else:
        values=hit.to_tuple()
        hits.append({'section':section,'y':y,'blocking_hit':bool(values[0]),'distance':values[3],'actor':values[9].get_actor_label() if values[9] else None})
with open(os.path.join(root,'verification.json'),'w') as f:json.dump({'actors':rows,'aisle_capsule_sweeps':hits},f,indent=2)
cam=next(a for a in ea.get_all_level_actors() if a.get_actor_label()=='BO_Camera_West_Interior')
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(cam.get_actor_location(),cam.get_actor_rotation())
unreal.log('BLOCKOUT_VERIFY_COMPLETE')
