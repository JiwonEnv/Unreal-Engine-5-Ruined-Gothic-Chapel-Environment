import unreal, os, json
root = os.path.join(unreal.Paths.project_dir(), 'SourceAssets/Blockout')
p = os.path.join(root,'Meshes/SM_BO_Probe.obj')
with open(p,'w') as f:
    f.write('o Probe\n')
    for x,y,z in [(0,0,0),(100,0,0),(100,200,0),(0,200,0),(0,0,300),(100,0,300),(100,200,300),(0,200,300)]:
        f.write('v %s %s %s\n' % (x,y,z))
    for face in [(1,4,3,2),(5,6,7,8),(1,2,6,5),(2,3,7,6),(3,4,8,7),(4,1,5,8)]:
        f.write('f '+' '.join(map(str,face))+'\n')
t = unreal.AssetImportTask()
t.filename=p
t.destination_path='/Game/GothicChapel/Blockout/Meshes'
t.automated=True
t.save=True
t.replace_existing=True
opts=unreal.FbxImportUI()
opts.import_mesh=True
opts.import_materials=False
opts.import_textures=False
opts.import_as_skeletal=False
opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
opts.static_mesh_import_data.set_editor_property('combine_meshes',True)
opts.static_mesh_import_data.set_editor_property('convert_scene',False)
t.options=opts
t.factory=unreal.FbxFactory()
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
report={'imported':list(t.imported_object_paths)}
if t.imported_object_paths:
    m=unreal.load_asset(t.imported_object_paths[0]); b=m.get_bounding_box()
    report['bounds']=str(b)
report['merge_available']=hasattr(unreal,'EditorScriptingMergeStaticMeshActorsOptions')
with open(os.path.join(root,'probe.json'),'w') as f:json.dump(report,f,indent=2)
unreal.log('BLOCKOUT_PROBE_COMPLETE')
