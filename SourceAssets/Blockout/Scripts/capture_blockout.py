import unreal,os
root=os.path.join(unreal.Paths.project_dir(),'SourceAssets/Blockout')
exec(compile(open(os.path.join(root,'Scripts/verify_blockout.py'),encoding='utf-8-sig').read(),'verify_blockout.py','exec'))
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_set_game_view(True)
cam=next(a for a in actors if a.get_actor_label()=='BO_Camera_West_Interior')
unreal.AutomationLibrary.take_high_res_screenshot(1600,1000,os.path.join(root,'Blockout_Interior.png'),camera=cam,delay=1.0)
