import unreal,json,os
root=unreal.Paths.project_dir()+'SourceAssets/Landscape/'
ea=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);actors=ea.get_all_level_actors()
land=next(a for a in actors if isinstance(a,unreal.Landscape));land.set_actor_location(unreal.Vector(-12000,-12600,12),False,False)
# Foundation underside Z=0, quantized clearing now Z=0.28125 cm.
cam=next(a for a in actors if a.get_actor_label()=='LS_Camera_Hill_Overview')
cam.set_actor_location(unreal.Vector(-2700,-2700,950),False,False);cam.set_actor_rotation(unreal.Rotator(pitch=-10,yaw=40,roll=0),False)
report=json.load(open(root+'build_report.json'));report['origin']=[-12000,-12600,12];json.dump(report,open(root+'build_report.json','w'),indent=2)
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(cam.get_actor_location(),cam.get_actor_rotation())
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
