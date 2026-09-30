import unreal,os,runpy
script_dir=unreal.Paths.project_dir()+'SourceAssets/Landscape/Scripts/'
runpy.run_path(script_dir+'finalize_landscape.py')
runpy.run_path(script_dir+'verify_landscape.py')
