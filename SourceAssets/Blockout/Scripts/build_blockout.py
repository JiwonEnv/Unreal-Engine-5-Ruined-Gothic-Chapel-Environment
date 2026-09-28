"""Notion specification 12-1..15, UE 5.6 editor Python. Units: centimetres.
Run from Unreal console: py ".../build_blockout.py"
Only creates BO_ actors; previous user actors are retained in a hidden archive.
"""
import unreal, math, os, json, random, traceback

ROOT = os.path.join(unreal.Paths.project_dir(), 'SourceAssets/Blockout')
DEST = '/Game/GothicChapel/Blockout'
BASE = 20.0
TAG = 'GothicChapel_Notion_Blockout'
EA = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
AS = unreal.AssetToolsHelpers.get_asset_tools()
created = []
meshes = {}
materials = {}

class Geo:
    def __init__(self): self.v, self.f = [], []
    def face(self, pts):
        n = len(self.v); self.v.extend(pts)
        for i in range(1,len(pts)-1): self.f.append((n,n+i,n+i+1))
    def prism(self, poly, depth=60, y=0):
        # Polygon in the x/z plane; closed, independently triangulated strips.
        front=[(x,y,z) for x,z in poly]; back=[(x,y+depth,z) for x,z in poly]
        self.face(front[::-1]); self.face(back)
        for i in range(len(poly)):
            j=(i+1)%len(poly); self.face([front[i],front[j],back[j],back[i]])
    def box(self, lo, hi):
        x,y,z=lo; X,Y,Z=hi
        self.prism([(x,z),(X,z),(X,Z),(x,Z)],Y-y,y)
    def beam(self, a, b, width=20, depth=None):
        depth=width if depth is None else depth
        a=unreal.Vector(*a); b=unreal.Vector(*b); d=b-a
        length=d.length(); d=d/length
        ref=unreal.Vector(0,0,1) if abs(d.z)<.95 else unreal.Vector(0,1,0)
        u=d.cross(ref); u=u/u.length()*width/2
        v=d.cross(u); v=v/v.length()*depth/2
        verts=[a-u-v,a+u-v,a+u+v,a-u+v,b-u-v,b+u-v,b+u+v,b-u+v]
        vv=[(p.x,p.y,p.z) for p in verts]
        for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:self.face([vv[i] for i in ids])
    def shell_quad(self, points, thick=12):
        self.face(points); self.face([(x,y,z+thick) for x,y,z in points][::-1])
        for i in range(len(points)):
            j=(i+1)%len(points); a=points[i]; b=points[j]
            self.face([a,b,(b[0],b[1],b[2]+thick),(a[0],a[1],a[2]+thick)])
    def save(self,name):
        path=os.path.join(ROOT,'Meshes',name+'.obj')
        with open(path,'w') as f:
            f.write('o '+name+'\n')
            # UE OBJ importer mirrors Y. Precompensate to preserve authored axes.
            for x,y,z in self.v:f.write('v %.5f %.5f %.5f\n'%(x,-y,z))
            for a,b,c in self.f:f.write('f %d %d %d\n'%(c+1,b+1,a+1))
        return path

def pointed(x,half,rise):
    # Two circular arcs, meeting at a point. x measured from opening centre.
    c=max(half*.35,(rise*rise-half*half)/(2*half))
    radius=half+c
    return rise*math.sqrt(max(0,radius*radius-(abs(x)+c)**2))/math.sqrt(radius*radius-c*c)

def interp(points,x):
    for (a,h),(b,k) in zip(points,points[1:]):
        if a<=x<=b:return h+(k-h)*(x-a)/(b-a)
    return points[0][1] if x<points[0][0] else points[-1][1]

def wall(width=400, opening=100, sill=160, height=280, rise=80, profile=None):
    g=Geo(); centre=width/2; l=centre-opening/2; r=centre+opening/2
    top=lambda x:interp(profile,x) if profile else 550
    cuts=sorted(set([0,l,r,width]+[l+opening*i/24 for i in range(25)]+([p[0] for p in profile] if profile else [])))
    for a,b in zip(cuts,cuts[1:]):
        if a<0 or b>width:continue
        if a>=l-.001 and b<=r+.001:
            if sill>0:g.prism([(a,0),(b,0),(b,min(sill,top(b))),(a,min(sill,top(a)))])
            ha=sill+height-rise+pointed(a-centre,opening/2,rise)
            hb=sill+height-rise+pointed(b-centre,opening/2,rise)
            ta,tb=top(a),top(b)
            if ta>ha and tb>hb:g.prism([(a,ha),(b,hb),(b,tb),(a,ta)])
        else:g.prism([(a,0),(b,0),(b,top(b)),(a,top(a))])
    return g

def arch_trim(width, sill, height, rise, thickness=12, depth=12, broken=False):
    g=Geo(); h=width/2; spring=sill+height-rise
    for side in [-1,1]:
        g.box((side*h-(thickness if side<0 else 0),-6,sill),(side*h+(thickness if side>0 else 0),depth,spring))
    for i in range(24):
        if broken and 13<=i<=22:continue
        x=-h+width*i/24; X=-h+width*(i+1)/24
        z=spring+pointed(x,h,rise); Z=spring+pointed(X,h,rise)
        g.prism([(x,z),(X,Z),(X,Z+thickness),(x,z+thickness)],depth+6,-6)
    return g

def material(name,color):
    path=DEST+'/Materials/'+name
    m=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else AS.create_asset(name,DEST+'/Materials',unreal.Material,unreal.MaterialFactoryNew())
    m.set_editor_property('two_sided',True)
    lib=unreal.MaterialEditingLibrary
    lib.delete_all_material_expressions(m)
    c=lib.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-400,0)
    c.set_editor_property('constant',unreal.LinearColor(*color,1))
    lib.connect_material_property(c,'',unreal.MaterialProperty.MP_BASE_COLOR)
    r=lib.create_material_expression(m,unreal.MaterialExpressionConstant,-400,160)
    r.set_editor_property('r',.82);lib.connect_material_property(r,'',unreal.MaterialProperty.MP_ROUGHNESS)
    lib.recompile_material(m);unreal.EditorAssetLibrary.save_loaded_asset(m)
    return m

def import_geo(name,g):
    task=unreal.AssetImportTask();task.filename=g.save(name);task.destination_path=DEST+'/Meshes'
    task.automated=True;task.save=False;task.replace_existing=True
    opts=unreal.FbxImportUI();opts.import_mesh=True;opts.import_materials=False;opts.import_textures=False;opts.import_as_skeletal=False
    opts.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    opts.static_mesh_import_data.set_editor_property('combine_meshes',True)
    opts.static_mesh_import_data.set_editor_property('convert_scene',False)
    opts.static_mesh_import_data.set_editor_property('auto_generate_collision',False)
    opts.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs',False)
    task.options=opts;task.factory=unreal.FbxFactory()
    AS.import_asset_tasks([task])
    if not task.imported_object_paths:raise RuntimeError('Import failed: '+name)
    m=unreal.load_asset(task.imported_object_paths[0])
    body=m.get_editor_property('body_setup')
    body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    unreal.EditorAssetLibrary.save_loaded_asset(m)
    meshes[name]=m;return m

def actor(name,mesh,pos=(0,0,0),mat='Stone',folder='Structure',yaw=0,scale=(1,1,1),rot=None):
    a=EA.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(pos[0],pos[1],pos[2]+BASE),rot or unreal.Rotator(pitch=0,yaw=yaw,roll=0))
    a.set_actor_label('BO_'+name);a.set_folder_path('Blockout/'+folder)
    a.set_editor_property('tags',[TAG])
    c=a.static_mesh_component;c.set_static_mesh(mesh);c.set_material(0,materials[mat]);c.set_collision_profile_name('BlockAll')
    a.set_actor_scale3d(unreal.Vector(*scale));created.append(a);return a

def box(name,pos,size,mat='Stone',folder='Structure',yaw=0,rot=None):
    return actor(name,cube,pos,mat,folder,yaw,tuple(v/100 for v in size),rot)

def geoactor(name,g,pos=(0,0,0),mat='Stone',folder='Structure',yaw=0):
    return actor(name,import_geo('SM_BO_'+name,g),pos,mat,folder,yaw)

def build():
    global cube
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world.get_name()!='GothicChapel_Main':raise RuntimeError('Open GothicChapel_Main before running')
    if any(TAG in [str(t) for t in a.tags] for a in EA.get_all_level_actors()):raise RuntimeError('Blockout already exists; edit it rather than duplicating')
    cube=unreal.load_asset('/Engine/BasicShapes/Cube')
    for key,color in {'Stone':(.48,.46,.42),'Trim':(.64,.61,.54),'Floor':(.30,.31,.30),'Roof':(.12,.16,.19),'Wood':(.21,.16,.11),'Hero':(.64,.53,.36),'Glass':(.12,.25,.31),'Cloth':(.27,.29,.24),'Scale':(.19,.38,.42)}.items():
        materials[key]=material('M_BO_'+key,color)
    # Preserve existing prototype actors in a hidden archive, no deletion.
    for a in EA.get_all_level_actors():
        if a.get_actor_label() in ['Cube','Cube2','Cube2_Pivot']:
            a.set_folder_path('Archive/PreBlockout_20260928');a.set_is_temporarily_hidden_in_editor(True);a.set_actor_hidden_in_game(True);a.set_actor_enable_collision(False)
    # West is X=0; east is X=1200. Interior Y=-300..300.
    for i in range(3):box('Floor_Bay%d_400x600'%(i+1),(200+400*i,0,-10),(400,600,20),'Floor','01_Floors')
    for s in [-1,1]:box('Foundation_'+str(s),(600,s*330,-10),(1320,60,20),'Stone','01_Floors')
    box('Foundation_West',(-30,0,-10),(60,600,20),'Stone','01_Floors')
    box('Foundation_East',(1230,0,-10),(60,600,20),'Stone','01_Floors')
    wall_full=import_geo('SM_BO_Wall_Lancet_400x60x550',wall())
    wall_mid=import_geo('SM_BO_Wall_Lancet_Broken',wall(profile=[(0,550),(260,550),(270,505),(295,520),(320,440),(345,465),(370,375),(400,390)]))
    west_n=import_geo('SM_BO_Wall_Ruin_North',wall(profile=[(0,250),(70,285),(100,225),(160,250),(180,180),(240,190),(260,285),(310,270),(340,410),(400,455)]))
    west_s=import_geo('SM_BO_Wall_Ruin_South',wall(profile=[(0,180),(70,220),(120,110),(200,130),(240,230),(280,210),(330,340),(360,300),(400,390)]))
    lancet=import_geo('SM_BO_Lancet_Trim',arch_trim(100,160,280,80))
    for side,y in [('North',300),('South',-360)]:
        actor(side+'_Bay1_Ruined',west_n if side=='North' else west_s,(0,y,0),folder='02_Walls/West_Ruined')
        actor(side+'_Bay2_Partial',wall_mid if side=='South' else wall_full,(400,y,0),folder='02_Walls/Middle_Partial')
        actor(side+'_Bay3_Intact',wall_full,(800,y,0),folder='02_Walls/East_Intact')
        for i in [1,2]:actor(side+'_Lancet_'+str(i+1),lancet,(i*400+200,y if side=='North' else y+60,0),'Trim','03_Openings')
    # Solid end gables with genuine through openings.
    east=wall(720,240,220,400,140,[(0,550),(360,850),(720,550)])
    geoactor('East_Gable_HeroOpening',east,(1260,-360,0),folder='02_Walls/East_Intact',yaw=90)
    west=wall(720,160,0,320,100,[(0,360),(90,410),(145,600),(195,620),(230,570),(255,420),(285,340),(345,325),(380,270),(420,245),(470,290),(520,220),(580,260),(640,310),(720,320)])
    geoactor('West_Gable_Collapsed',west,(0,-360,0),folder='02_Walls/West_Ruined',yaw=90)
    geoactor('West_Portal_BrokenArch',arch_trim(160,0,320,100,20,16,True),(0,0,0),'Trim','03_Openings',90)
    geoactor('East_Hero_Arch',arch_trim(240,220,400,140,18,15),(1200,0,0),'Trim','04_Hero',90)
    # Three lancets inside the single 2.4 x 4 m Hero opening; minimal tracery.
    tracery=Geo()
    for q in [-80,0,80]:
        g=arch_trim(66,220,310 if q==0 else 275,65,7,12)
        tracery.v.extend([(x+q,y,z) for x,y,z in g.v]);offset=len(tracery.v)-len(g.v);tracery.f.extend([tuple(v+offset for v in f) for f in g.f])
    geoactor('East_ThreeLight_Tracery',tracery,(1220,0,0),'Trim','04_Hero',90)
    for i,y in enumerate([-80,0,80]):
        box('Hero_Glass_Placeholder_'+str(i),(1240,y,340),(5,60,240),'Glass','04_Hero')
    # Attached piers, transverse arches, and external buttresses share X axes.
    butt=Geo();butt.box((-40,0,0),(40,100,210));butt.box((-35,0,210),(35,72,375));butt.box((-30,0,375),(30,45,480))
    butt.shell_quad([(-30,0,500),(30,0,500),(30,45,480),(-30,45,480)],5)
    butt_mesh=import_geo('SM_BO_Buttress_80x100x500',butt)
    rib=Geo()
    for i in range(40):
        y=-300+600*i/40;Y=-300+600*(i+1)/40
        rib.beam((0,y,420+pointed(y,300,300)),(0,Y,420+pointed(Y,300,300)),20,14)
    ribmesh=import_geo('SM_BO_Transverse_Rib_600',rib)
    for j,x in enumerate([0,400,800,1200]):
        for side,s in [('North',1),('South',-1)]:
            height=420 if x>=400 else (250 if s==1 else 180)
            box('Pier_'+side+'_'+str(x),(x,s*282.5,height/2),(60,35,height),'Trim','05_Structure/Piers')
            box('Pier_Base_'+side+'_'+str(x),(x,s*278,15),(76,44,30),'Trim','05_Structure/Piers')
            if x>=400:box('Capital_'+side+'_'+str(x),(x,s*275,409),(75,50,22),'Trim','05_Structure/Piers')
            if x>=400:actor('Buttress_'+side+'_'+str(x),butt_mesh,(x,s*360,0),'Stone','05_Structure/Buttresses',0 if s==1 else 180)
            else:box('Buttress_Remnant_'+side,(x,s*405,125),(80,90,250),'Stone','05_Structure/Buttresses')
        if x>=800:actor('Transverse_Arch_'+str(x),ribmesh,(x,0,0),'Trim','06_Vaults/Ribs')
    broken=Geo()
    for side in [-1,1]:
        for i in range(8 if side==1 else 5):
            y=side*(300-i*15);Y=side*(300-(i+1)*15)
            broken.beam((0,y,420+pointed(y,300,300)),(0,Y,420+pointed(Y,300,300)),20,14)
    geoactor('Broken_Transverse_400',broken,(400,0,0),'Trim','06_Vaults/Ribs')
    # Four webs and diagonal ribs for each preserved bay; west roof is absent.
    for bay,x0 in [(2,400),(3,800)]:
        dg=Geo()
        corners=[(-200,-300),(200,-300),(200,300),(-200,300)]
        for k,(cx,cy) in enumerate(corners):
            start=0 if bay==3 else (9 if k==0 else 0)
            end=20 if bay==3 else (20 if k in [1,2] else 14)
            for i in range(start,end):
                t=i/20;T=(i+1)/20
                # from spring at corner to shared central boss
                r=1-t;R=1-T
                dg.beam((200+cx*r,cy*r,720-300*r*r),(200+cx*R,cy*R,720-300*R*R),20,14)
        geoactor('Bay%d_DiagonalRibs'%bay,dg,(x0,0,0),'Trim','06_Vaults/Ribs')
        for sector in range(4):
            if bay==2 and sector in [0,3]:continue
            a=corners[sector];b=corners[(sector+1)%4];web=Geo()
            def pt(r,t):
                ex=a[0]+(b[0]-a[0])*t;ey=a[1]+(b[1]-a[1])*t
                edge=420+(130 if abs(a[1]-b[1])<1 else 300)*(1-(2*t-1)**2)
                return (200+ex*r,ey*r,720-(720-edge)*r*r+9)
            for i in range(10):
                for j in range(14):
                    if bay==2 and i>6 and j<4:continue
                    r=i/10;R=(i+1)/10;t=j/14;T=(j+1)/14
                    if i==0:web.shell_quad([pt(r,t),pt(R,t),pt(R,T)],10)
                    else:web.shell_quad([pt(r,t),pt(R,t),pt(R,T),pt(r,T)],10)
            geoactor('Bay%d_Web_%d'%(bay,sector),web,(x0,0,0),'Stone','06_Vaults/Webs')
        actor('Bay%d_Boss'%bay,unreal.load_asset('/Engine/BasicShapes/Sphere'),(x0+200,0,714),'Trim','06_Vaults/Ribs',scale=(.35,.35,.18))
    # Roof volumes: ridge 850, eaves 550. Broken middle; missing west bay.
    for bay,x0 in [(2,400),(3,800)]:
        for s in [-1,1]:
            g=Geo();start=0 if bay==3 else (120 if s==1 else 240)
            g.shell_quad([(start,0,850),(400,0,850),(400,s*375,550),(max(0,start-60),s*375,550)],12)
            geoactor('Bay%d_Roof_%s'%(bay,'N' if s==1 else 'S'),g,(x0,0,0),'Roof','07_Roof/Slate')
    for x in [800,1200]:
        g=Geo()
        for s in [-1,1]:g.beam((0,s*340,565),(0,0,832),18,20)
        g.beam((0,-235,650),(0,235,650),16,18)
        g.beam((0,0,650),(0,0,825),16,18)
        geoactor('Timber_Truss_'+str(x),g,(x,0,0),'Wood','07_Roof/Timber')
    g=Geo();g.beam((550,-330,562),(620,-100,750),18,18);g.beam((460,300,564),(560,220,648),18,18)
    geoactor('Broken_Truss_Middle',g,mat='Wood',folder='07_Roof/Timber')
    # Altar centred on the Hero opening, exact 305 cm tabletop width.
    box('Altar_Step_Lower',(1020,0,10),(300,420,20),'Trim','04_Hero/Altar')
    box('Altar_Step_Upper',(1060,0,30),(220,370,20),'Trim','04_Hero/Altar')
    box('Altar_Plinth',(1090,0,49),(110,315,18),'Hero','04_Hero/Altar')
    box('Altar_Body',(1090,0,93),(85,275,70),'Hero','04_Hero/Altar')
    box('Altar_Tabletop_305cm',(1085,0,139),(115,305,22),'Trim','04_Hero/Altar')
    for y in [-137,137]:box('Altar_Pilaster_'+str(y),(1041,y,94),(18,22,72),'Trim','04_Hero/Altar')
    # Subtle blind arcades on front face, only blockout relief.
    for y in [-84,0,84]:geoactor('Altar_BlindArcade_'+str(y),arch_trim(62,61,63,24,6,4),(1044,y,0),'Trim','04_Hero/Altar',90)
    # Bellcote ruin stays connected to the remaining tall west gable.
    box('Bellcote_Left_Remnant',(-30,-198,640),(60,40,90),'Stone','04_Hero/WestSilhouette')
    box('Bellcote_Right_Broken',(-30,-130,607),(60,30,36),'Stone','04_Hero/WestSilhouette')
    # Sparse furniture leaves a 180 cm central aisle.
    for idx,(x,y,yaw,broken) in enumerate([(570,-195,-4,False),(720,194,6,True),(855,-190,3,False)]):
        g=Geo();g.box((-22,-85,39),(22,85,48));g.box((14,-85,48),(22,85,88 if not broken else 62))
        for yy in [-65,65]:g.box((-18,yy-7,0),(18,yy+7,39))
        geoactor('Bench_'+str(idx+1),g,(x,y,0),'Wood','08_Props/Benches',yaw)
    box('Supply_Crate',(815,255,28),(65,60,56),'Wood','08_Props/Refuge',8)
    actor('Refuge_Bundle',unreal.load_asset('/Engine/BasicShapes/Sphere'),(755,258,22),'Cloth','08_Props/Refuge',scale=(.7,.46,.4))
    box('Folded_Cloth',(1070,-102,154),(65,90,6),'Cloth','08_Props/Refuge',-6)
    for y in [-155,155]:
        box('Candle_Base_'+str(y),(1090,y,47),(25,25,14),'Wood','08_Props/Candles')
        box('Candle_Stem_'+str(y),(1090,y,81),(7,7,60),'Wood','08_Props/Candles')
    # West-biased debris, with clear entry and no scattering over altar.
    rng=random.Random(927)
    rubble=Geo()
    # irregular tetrahedral stone prototype; authored once and instanced
    vv=[(-.5,-.5,-.35),(.5,-.4,-.5),(.42,.5,-.3),(-.45,.4,-.4),(-.3,-.35,.4),(.38,-.3,.5),(.3,.4,.3),(-.4,.3,.35)]
    for face in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:rubble.face([tuple(c*100 for c in vv[i]) for i in face])
    rm=import_geo('SM_BO_Rubble_Stone',rubble)
    for i in range(58):
        x=rng.uniform(-170,470) if i<49 else rng.uniform(470,750)
        y=rng.choice([-1,1])*rng.uniform(130,390)
        w=rng.uniform(22,60);d=rng.uniform(20,52);h=rng.uniform(14,38)
        actor('Rubble_%02d'%i,rm,(x,y,h/2),'Stone','09_Debris/Stone',scale=(w/100,d/100,h/100),rot=unreal.Rotator(pitch=rng.uniform(-20,20),yaw=rng.uniform(0,180),roll=rng.uniform(-15,15)))
    for i in range(8):
        box('Fallen_Timber_'+str(i),(rng.uniform(-100,470),rng.choice([-1,1])*rng.uniform(170,295),20),(rng.uniform(90,230),15,18),'Wood','09_Debris/Timber',rng.uniform(-65,65))
    for i in range(14):
        box('Slate_Debris_'+str(i),(rng.uniform(50,530),rng.choice([-1,1])*rng.uniform(150,290),7),(rng.uniform(22,45),rng.uniform(18,35),5),'Roof','09_Debris/Slate',rng.uniform(0,180))
    # 180 cm mannequin, to the side of the west entry.
    scale=Geo();scale.box((-12,-19,75),(12,19,145));scale.box((-11,-18,0),(11,-4,75));scale.box((-11,4,0),(11,18,75))
    scale.box((-10,-13,150),(10,13,180));scale.box((-9,-30,88),(9,-20,140));scale.box((-9,20,88),(9,30,140))
    geoactor('Scale_Reference_180cm',scale,(-100,145,0),'Scale','10_Review')
    # Keep the existing environment, relocate spawn into the clear western aisle.
    for a in EA.get_all_level_actors():
        if a.get_class().get_name()=='PlayerStart':
            a.set_actor_location(unreal.Vector(115,0,BASE+100),False,False);a.set_actor_rotation(unreal.Rotator(0,0,0),False)
    for name,pos,target in [('West_Interior',(-230,0,210),(1060,0,270)),('Exterior_Overview',(-1050,-1450,1080),(550,0,320)),('Altar_Detail',(675,-100,185),(1090,0,170))]:
        p=unreal.Vector(*pos);t=unreal.Vector(*target)
        cam=EA.spawn_actor_from_class(unreal.CameraActor,p,unreal.MathLibrary.find_look_at_rotation(p,t));cam.set_actor_label('BO_Camera_'+name);cam.set_folder_path('Blockout/10_Review/Cameras');cam.tags=[TAG]
        cam.camera_component.set_editor_property('field_of_view',65.0);created.append(cam)
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(-1050,-1450,1080),unreal.MathLibrary.find_look_at_rotation(unreal.Vector(-1050,-1450,1080),unreal.Vector(550,0,320)))
    EA.clear_actor_selection_set()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    report={'status':'complete','actors_created':len(created),'meshes_created':len(meshes),'map':world.get_name(),'interior_cm':[1200,600],'wall_thickness_cm':60,'bay_axes_x':[0,400,800,1200],'spring_cm':420,'vault_cm':720,'roof_cm':850,'altar_tabletop_cm':305,'clear_aisle_cm':180,'source_pages':15,'actors':[a.get_actor_label() for a in created]}
    with open(os.path.join(ROOT,'build_report.json'),'w') as f:json.dump(report,f,indent=2)
    unreal.log('BLOCKOUT_BUILD_COMPLETE '+str(len(created))+' actors')

try:build()
except Exception:
    with open(os.path.join(ROOT,'build_error.txt'),'w') as f:f.write(traceback.format_exc())
    unreal.log_error(traceback.format_exc())
    raise
