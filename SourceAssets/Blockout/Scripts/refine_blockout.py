import unreal,os,json
root=os.path.join(unreal.Paths.project_dir(),'SourceAssets/Blockout')
ea=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors=ea.get_all_level_actors()
for a in actors:
    if isinstance(a,unreal.StaticMeshActor) and a.get_actor_label().startswith('BO_') and 'BO_RotationVerified' not in [str(t) for t in a.tags]:
        r=a.get_actor_rotation()
        a.set_actor_rotation(unreal.Rotator(pitch=r.roll,yaw=r.pitch,roll=r.yaw),False)
        a.tags=list(a.tags)+['BO_RotationVerified']
    if a.get_actor_label() in ['Cube','Cube2']:
        # Persistent component visibility also survives editor reopening.
        a.static_mesh_component.set_visibility(False)
        a.static_mesh_component.set_hidden_in_game(True)
        a.set_actor_enable_collision(False)
    if a.get_actor_label()=='BO_Camera_West_Interior':
        a.set_actor_location(unreal.Vector(130,-25,190),False,False)
        a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(a.get_actor_location(),unreal.Vector(1120,0,310)),False)
    if a.get_actor_label()=='BO_Camera_Exterior_Overview':
        a.set_actor_location(unreal.Vector(-900,-1600,1120),False,False)
        a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(a.get_actor_location(),unreal.Vector(550,0,350)),False)
sm=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
done=set()
for a in actors:
    if not isinstance(a,unreal.StaticMeshActor) or not a.get_actor_label().startswith('BO_'):continue
    m=a.static_mesh_component.static_mesh
    if '/Blockout/Meshes/' not in m.get_path_name() or m.get_path_name() in done:continue
    done.add(m.get_path_name())
    settings=sm.get_lod_build_settings(m,0)
    settings.set_editor_property('use_mikk_t_space',False)
    settings.set_editor_property('recompute_normals',True)
    settings.set_editor_property('recompute_tangents',True)
    sm.set_lod_build_settings(m,0,settings)
    unreal.EditorAssetLibrary.save_loaded_asset(m)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
exec(compile(open(os.path.join(root,'Scripts/verify_blockout.py'),encoding='utf-8-sig').read(),'verify_blockout.py','exec'))
unreal.log('BLOCKOUT_REFINE_COMPLETE')
