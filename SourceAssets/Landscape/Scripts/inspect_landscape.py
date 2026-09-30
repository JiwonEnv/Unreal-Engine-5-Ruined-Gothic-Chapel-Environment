import unreal,json,os
root=unreal.Paths.project_dir()+'SourceAssets/Landscape/'
a=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
d={'actors':[], 'landscape_api':[n for n in dir(unreal.Landscape) if any(k in n for k in ['height','layer','import','export','component'])]}
for x in a:
 p=x.get_actor_location(); s=x.get_actor_scale3d()
 r={'label':x.get_actor_label(),'class':x.get_class().get_name(),'location':[p.x,p.y,p.z],'scale':[s.x,s.y,s.z]}
 if isinstance(x,unreal.LandscapeProxy):
  r['bounds']=str(x.get_actor_bounds(False)); r['properties']={}
  for k in ['landscape_material','component_size_quads','subsection_size_quads','num_subsections','landscape_components','can_have_layers_content']:
   try:r['properties'][k]=str(x.get_editor_property(k))
   except Exception as e:r['properties'][k]=str(e)
 d['actors'].append(r)
with open(root+'scene_before.json','w') as f:json.dump(d,f,indent=2)
