import unreal, json, os
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
data = []
for a in actors:
    p = a.get_actor_location()
    s = a.get_actor_scale3d()
    data.append({'label':a.get_actor_label(), 'class':a.get_class().get_name(), 'location':[p.x,p.y,p.z], 'scale':[s.x,s.y,s.z], 'folder':str(a.get_folder_path())})
with open(os.path.join(unreal.Paths.project_dir(),'SourceAssets/Blockout/scene_before.json'),'w') as f: json.dump(data,f,indent=2)
unreal.log('BLOCKOUT_INSPECT_COMPLETE')
