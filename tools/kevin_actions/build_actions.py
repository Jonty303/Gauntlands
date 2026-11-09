"""Build the local animation catalogue from licensed native Blender sources.
Run Blender --background --factory-startup --python this_file -- SOURCE [PACK].
Outputs remain gitignored; source downloads are read-only.
"""
import bpy, json, sys, zipfile, re, hashlib, math
from pathlib import Path
from mathutils import Matrix, Vector
from io_scene_fbx import parse_fbx
ROOT=Path(__file__).resolve().parents[2]
ARGS=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
SOURCE=Path(ARGS[0]) if ARGS else ROOT.parent/'Human'
ONLY=ARGS[1] if len(ARGS)>1 else None
CACHE=ROOT/'.local/kevin'; OUT=ROOT/'prototype/assets/kevin_local/actions'
OUT.mkdir(parents=True,exist_ok=True);CACHE.mkdir(parents=True,exist_ok=True)
PACKS={
 'basic':('HumanBasicMotionsFREE_BlenderFiles.zip','HumanM_BasicMotionsFREE_2.4.blend'),
 'melee':('HumanMeleeAnimationsFREE_BlenderFiles.zip','HumanM_MeleeAnimationsFREE_2.0.2.blend'),
 'archer':('HumanArcherAnimationsFREE_BlenderFiles.zip','HumanM_ArcherAnimationsFREE_2.0.blend'),
 'magic':('HumanSpellcastingAnimationsFREE_BlenderFiles.zip','HumanM_SpellcastingAnimationsFREE_2.0.blend'),
 'crafting':('HumanCraftingAnimationsFREE_BlenderFiles.zip','HumanM_CraftingAnimationsFREE_2.2.1.blend')}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def walk_time(el):
 if el.id==b'LocalTime':return el.props
 for child in el.elems:
  value=walk_time(child)
  if value is not None:return value
metadata={}
for f in SOURCE.glob('Animations/Male/**/*.fbx'):
 tree,_=parse_fbx.parse(str(f));ticks=walk_time(tree)
 if ticks:metadata[f.stem]={'fbx':str(f.relative_to(SOURCE)),'duration':(ticks[1]-ticks[0])/46186158000}

def equipment(name):
 if name.startswith('Bow'):return ['Bow','BowString','Arrow'] if 'Shot' in name else ['Bow','BowString']
 if 'Sheathe' in name or 'sheathe' in name:return ['SwordL' if name.endswith('_L') else 'SwordR']
 if 'Polearm' in name:return ['Polearm']
 if '2H' in name and not 'Magic' in name:return ['Greatsword']
 if name=='Attack1H01_L':return ['SwordL']
 if name=='Attack1H01_R':return ['SwordR']
 if name in ['AttackShield01','CombatIdle1H01','CombatDamage01']:return ['SwordR','Shield']
 if name.startswith('Farming'):return ['Plow']
 if name.startswith('Fishing'):return ['FishingPole']
 if name.startswith('Hammering'):return ['HammerL' if '_L' in name else 'HammerR']
 if name.startswith('Mining'):return ['PickaxeL' if '_L' in name else 'PickaxeR']
 return []
def looping(name):
 return name.startswith(('Walk','Run','Sprint','StrafeRun','Talk','Gathering','Mining')) or name.endswith(' - Loop') or ('Idle' in name and '-' not in name) or name.endswith(' - Hold') or (name.startswith('Magic') and name.endswith(' - Load'))
def group(name):
 if name.startswith(('Walk','Run','Sprint','StrafeRun')):return 'Movement'
 if 'Idle' in name and not name.startswith(('Combat','Casting','Bow')):return 'Idle'
 if name.startswith(('Bow','Sheathe','Unsheathe')):return 'Archery / equipment'
 if name.startswith(('Magic','Casting')):return 'Spellcasting'
 if name.startswith(('Attack','Combat','Death')):return 'Combat'
 if name.startswith(('Farming','Fishing','Hammer','Mining','Gather')):return 'Crafting'
 return 'General'
def material(obj,colour):
 mat=bpy.data.materials.new(obj.name+' preview');mat.diffuse_color=(*colour,1);mat.use_nodes=True
 node=mat.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=mat.diffuse_color;node.inputs['Roughness'].default_value=.72
 obj.data.materials.clear();obj.data.materials.append(mat)
 for poly in obj.data.polygons:poly.material_index=0

def assign(rig,action):
 rig.animation_data_create();rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0]
def frame(scene,f):
 scene.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
def verts(obj):
 dg=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(dg);me=ev.to_mesh();result=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();return result

def add_rigid(obj,clean,bone,local,name):
 # Convert the original prop vertices to rig rest space, then skin rigidly.
 obj.data=obj.data.copy();obj.data.transform(clean.data.bones[bone].matrix_local@local)
 obj.parent=clean;obj.parent_type='OBJECT';obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4)
 obj.name=name
 for m in list(obj.modifiers):obj.modifiers.remove(m)
 obj.vertex_groups.clear();g=obj.vertex_groups.new(name=bone);g.add(list(range(len(obj.data.vertices))),1,'REPLACE')
 m=obj.modifiers.new('Preview skin','ARMATURE');m.object=clean
 material(obj,(.32,.20,.09) if any(w in name for w in ['Bow','Plow','Fishing']) else (.52,.55,.59))
 return obj

def make_action(clean,name,samples):
 action=bpy.data.actions.new(name);action.use_fake_user=True
 slot=action.slots.new(id_type='OBJECT',name=clean.name)
 strip=action.layers.new('Baked').strips.new(type='KEYFRAME');bag=strip.channelbag(slot,ensure=True)
 for p in clean.pose.bones:
  channels=[[],[],[]];previous=None
  for matrices in samples:
   kwargs={'parent_matrix':matrices[p.parent.name],'parent_matrix_local':p.parent.bone.matrix_local} if p.parent else {}
   local=p.bone.convert_local_to_pose(matrices[p.name],p.bone.matrix_local,invert=True,**kwargs)
   loc,rot,scale=local.decompose()
   if previous is not None and rot.dot(previous)<0:rot.negate()
   previous=rot.copy()
   for values,value in zip(channels,[loc,rot,scale]):values.append(tuple(value))
  p.rotation_mode='QUATERNION'
  for path,values in zip(['location','rotation_quaternion','scale'],channels):
   for axis in range(len(values[0])):
    fc=bag.fcurves.new(data_path='pose.bones["'+p.name+'"].'+path,index=axis)
    fc.keyframe_points.add(len(values));fc.keyframe_points.foreach_set('co',[v for i,row in enumerate(values) for v in [i+1,row[axis]]])
    for k in fc.keyframe_points:k.interpolation='LINEAR'
 return action

# Stable priority removes duplicate clips, not distinct actions.
seen=set();catalog=[];reports={}
for pack,(archive,blend) in PACKS.items():
 with zipfile.ZipFile(SOURCE/'Animations'/archive) as z:(CACHE/blend).write_bytes(z.read(blend))
 bpy.ops.wm.open_mainfile(filepath=str(CACHE/blend),load_ui=False,use_scripts=False)
 source_actions=[]
 for a in sorted(bpy.data.actions,key=lambda a:a.name):
  if not a.name.startswith('HumanM@') or a.name not in metadata or '[RM]' in a.name:continue
  name=a.name.split('@',1)[1]
  if name in seen:continue
  seen.add(name);source_actions.append(a)
  d=metadata[a.name]['duration'];entry={'id':re.sub(r'[^a-zA-Z0-9]+','_',name).strip('_'),'name':name,'category':group(name),'pack':pack,'source_action':a.name,'source_fbx':metadata[a.name]['fbx'],'duration':d,'loop':looping(name),'hold':name in ['Death01','Fall01'],'props':equipment(name),'asset':'res://assets/kevin_local/actions/'+pack+'.glb'}
  catalog.append(entry)
 if ONLY and pack!=ONLY:continue
 rig=bpy.data.objects['Rig'];mesh=bpy.data.objects['HumanM_BodyMesh'];scene=bpy.context.scene
 entries=[e for e in catalog if e['pack']==pack];by_name={e['source_action']:e for e in entries}
 # Remove stale NLA influence; evaluate each source action end/start before baking.
 for track in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(track)
 clean=rig.copy();clean.data=rig.data.copy();scene.collection.objects.link(clean);clean.name='DummyRig';clean.animation_data_clear()
 for p in clean.pose.bones:
  for c in list(p.constraints):p.constraints.remove(c)
 bpy.ops.object.select_all(action='DESELECT');clean.select_set(True);bpy.context.view_layer.objects.active=clean
 bpy.ops.object.mode_set(mode='EDIT')
 for b in list(clean.data.edit_bones):
  if not b.name.startswith('B-'):clean.data.edit_bones.remove(b)
 bpy.ops.object.mode_set(mode='OBJECT')
 if pack=='archer':
  bpy.ops.object.select_all(action='DESELECT');clean.select_set(True);bpy.context.view_layer.objects.active=clean;bpy.ops.object.mode_set(mode='EDIT')
  for side in ['L','R']:
   old=clean.data.edit_bones['B-handProp.'+side];new=clean.data.edit_bones.new('PropSword'+side);new.head=old.head;new.tail=old.tail;new.matrix=old.matrix;new.parent=clean.data.edit_bones['B-root']
  bpy.ops.object.mode_set(mode='OBJECT')
 props=[];bow=None;bow_mesh=None;bow_rest={};bow_mount=Matrix.Rotation(-math.pi/2,4,'X')
 if pack=='melee':
  assign(rig,source_actions[0]);frame(scene,1)
  for old,name,side in [('Sword_R','SwordR','R'),('Sword_L','SwordL','L'),('Shield','Shield','L'),('WeaponGS','Greatsword','R'),('WeaponPolearm','Polearm','R')]:
   obj=bpy.data.objects[old];bone='B-handProp.'+side;local=rig.pose.bones[bone].matrix.inverted()@obj.matrix_world
   props.append(add_rigid(obj,clean,bone,local,name))
 if pack in ['crafting','archer']:
  wanted=[('Human_Hammer','HammerL','L'),('Human_Hammer','HammerR','R'),('Human_Pickaxe','PickaxeL','L'),('Human_Pickaxe','PickaxeR','R'),('Human_Plow','Plow','R'),('Human_FishingPole','FishingPole','R')] if pack=='crafting' else [('Human_Sword','SwordL','L'),('Human_Sword','SwordR','R')]
  for file,name,side in wanted:
   f=(SOURCE/'Models/Weapons'/str(file+'.fbx')) if pack=='archer' else next(SOURCE.glob('Models/Tools/'+file+'.fbx'));before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(f),use_anim=False)
   obj=next(o for o in set(bpy.data.objects)-before if o.type=='MESH')
   props.append(add_rigid(obj,clean,('PropSword'+side) if pack=='archer' else ('B-handProp.'+side),Matrix.Scale(.01,4),name))
 if pack=='archer':
  with zipfile.ZipFile(SOURCE/'Animations'/archive) as z:(CACHE/'HumanArcherAnimations_BowAndProps.blend').write_bytes(z.read('HumanArcherAnimations_BowAndProps.blend'))
  with bpy.data.libraries.load(str(CACHE/'HumanArcherAnimations_BowAndProps.blend'),link=False) as (src,dst):dst.objects=['Human_Bow','Human_BowMesh','Human_Arrow']
  for obj in dst.objects:scene.collection.objects.link(obj)
  bow=bpy.data.objects['Human_Bow'];bow_mesh=bpy.data.objects['Human_BowMesh'];arrow=bpy.data.objects['Human_Arrow']
  bow_rest={b.name:b.matrix_local.copy() for b in bow.data.bones}
  mount=clean.data.bones['B-handProp.L'].matrix_local@bow_mount
  bpy.ops.object.select_all(action='DESELECT');clean.select_set(True);bpy.context.view_layer.objects.active=clean;bpy.ops.object.mode_set(mode='EDIT')
  for b in bow.data.bones:
   new=clean.data.edit_bones.new('Bow_'+b.name);new.head=mount@b.head_local;new.tail=mount@b.tail_local;new.matrix=mount@b.matrix_local
   new.parent=clean.data.edit_bones['Bow_'+b.parent.name] if b.parent else clean.data.edit_bones['B-handProp.L']
  bpy.ops.object.mode_set(mode='OBJECT')
  bow_mesh.data=bow_mesh.data.copy();bow_mesh.data.transform(mount@bow.matrix_world.inverted()@bow_mesh.matrix_world)
  bow_mesh.parent=clean;bow_mesh.matrix_parent_inverse=Matrix.Identity(4);bow_mesh.matrix_basis=Matrix.Identity(4);bow_mesh.name='Bow'
  for g in bow_mesh.vertex_groups:g.name='Bow_'+g.name
  for mod in bow_mesh.modifiers:
   if mod.type=='ARMATURE':mod.object=clean
  material(bow_mesh,(.32,.20,.09));props.append(bow_mesh)
  # Two crossed ribbons retain visible string thickness in every review camera.
  vertices=[];faces=[];weights=[]
  for tip in ['B-bowTip01','B-bowTip02']:
   endpoints=[bow_rest[tip].translation,bow_rest['B-nockPoint'].translation]
   for axis in [Vector((0,.0015,0)),Vector((.0015,0,0))]:
    start=len(vertices)
    for end,bone in zip(endpoints,[tip,'B-nockPoint']):
     for sign in [-1,1]:vertices.append(tuple(mount@(end+axis*sign)));weights.append('Bow_'+bone)
    faces.append((start,start+1,start+3,start+2))
  data=bpy.data.meshes.new('Visible bow string');data.from_pydata(vertices,[],faces);data.update()
  string=bpy.data.objects.new('BowString',data);scene.collection.objects.link(string);string.parent=clean
  for bone in set(weights):
   g=string.vertex_groups.new(name=bone);g.add([i for i,b in enumerate(weights) if b==bone],1,'REPLACE')
  mod=string.modifiers.new('Bow deformation','ARMATURE');mod.object=clean;material(string,(.8,.72,.55));props.append(string)
  # Arrow local +Z points down the shaft; the authored prop bone points along +Y.
  props.append(add_rigid(arrow,clean,'B-handProp.R',Matrix.Rotation(-math.pi/2,4,'X'),'Arrow'))
 baked=[];checks=[];bow_sequences={}
 for a in source_actions:
  entry=by_name[a.name];count=round(entry['duration']*60)+1;last=1+entry['duration']*30
  assign(rig,a);frame(scene,last);frame(scene,1)
  samples=[];surfaces={};floors=[]
  for i in range(count):
   frame(scene,1+i*.5)
   matrices={p.name:p.matrix.copy() for p in rig.pose.bones if p.name.startswith('B-')}
   surface=verts(mesh)
   floors.append(max(0,.0005-min(v.z for v in surface)))
   if i in [0,(count-1)//2,count-1]:surfaces[i]=surface
   if bow:
    mount=matrices['B-handProp.L']@bow_mount
    nock=mount.inverted()@matrices['B-handProp.R'].translation
    draw=max(0,min(.22,(-nock.x-.327)*.3)) if entry['name'].startswith('BowShot') else 0
    if entry['name'].endswith('Release'):draw*=max(0,1-(i/60)/.10)
    for name,rest in bow_rest.items():
     mat=rest.copy()
     if 'Limb01' in name or 'Tip01' in name:mat=Matrix.Rotation(-draw,4,'Y')@mat
     if 'Limb02' in name or 'Tip02' in name:mat=Matrix.Rotation(draw,4,'Y')@mat
     if 'nockPoint' in name and entry['name'].startswith('BowShot'):
      release=entry['name'].endswith('Release')
      amount=max(0,1-(i/60)/.10) if release else 1
      mat.translation=rest.translation.lerp(nock,amount)
     matrices['Bow_'+name]=mount@mat
   samples.append(matrices)
  if pack=='archer':
   for i,matrices in enumerate(samples):
    fraction=i/(count-1)
    for side in ['L','R']:
     hand=matrices['B-handProp.'+side]
     transform=hand.copy()
     if 'sheathe' in entry['name'].lower() and entry['name'].endswith('_'+side):
      # Viewer-only grip-to-back transfer; not an inventory/equip system.
      y=Vector((.35 if side=='L' else -.35,0,-.94)).normalized();z=Vector((0,1,0));x=y.cross(z).normalized()
      back=Matrix((x,y,z)).transposed().to_4x4();back.translation=Vector((-.18 if side=='L' else .18,.17,1.60))
      back=matrices['B-chest']@rig.data.bones['B-chest'].matrix_local.inverted()@back
      amount=max(0,min(1,(fraction-.35)/.25));amount=amount*amount*(3-2*amount)
      if entry['name'].startswith('Unsheathe'):amount=1-amount
      transform=hand.lerp(back,amount)
     matrices['PropSword'+side]=transform
  baked_action=make_action(clean,entry['id'],samples);baked.append(baked_action);assign(clean,baked_action)
  # Validate source skin against the baked skeleton at start/mid/end.
  old_parent=mesh.parent;world=mesh.matrix_world.copy();mesh.parent=clean;mesh.matrix_world=world
  arm=next(m for m in mesh.modifiers if m.type=='ARMATURE');arm.object=clean
  maxerr=0;minimum=100
  for i,source_vertices in surfaces.items():
   frame(scene,i+1);vs=verts(mesh);maxerr=max(maxerr,max((x-y).length for x,y in zip(vs,source_vertices)));minimum=min(minimum,min(v.z for v in vs))
  arm.object=rig;mesh.parent=old_parent;mesh.matrix_world=world
  assert maxerr<.003,(entry['name'],maxerr)
  entry['ground_offset']=max(0,-minimum)+.0005
  entry['floor_samples']=floors
  if pack=='archer' and entry['name'].startswith('BowShot'):bow_sequences[entry['id']]=(samples,floors)
  checks.append({'id':entry['id'],'frames':count,'source_bake_error_m':maxerr,'sampled_min_y':minimum})
  print('BAKED',pack,entry['id'],count,maxerr,flush=True)
 if pack=='archer':
  load,lf=bow_sequences['BowShot01_Load'];hold,hf=bow_sequences['BowShot01_Hold'];release,rf=bow_sequences['BowShot01_Release']
  combined=load[:-1]+hold[:18]+release;floor_profile=lf[:-1]+hf[:18]+rf
  entry={'id':'BowShotComplete','name':'BowShot - Complete','category':'Archery / equipment','pack':pack,'source_action':'Load + 0.3 s Hold + Release','source_fbx':'Composite of the three supplied BowShot01 clips','duration':(len(combined)-1)/60,'loop':False,'hold':False,'props':['Bow','BowString','Arrow'],'asset':'res://assets/kevin_local/actions/archer.glb','ground_offset':max(floor_profile),'floor_samples':floor_profile,'arrow_release_time':(len(load)-1+18)/60}
  entry['join_error_m']=max((load[-1][n].translation-hold[0][n].translation).length for n in load[-1])
  entries.append(entry);baked.append(make_action(clean,entry['id'],combined));checks.append({'id':entry['id'],'frames':len(combined),'composite':True,'join_error_m':entry['join_error_m']})
 world=mesh.matrix_world.copy();mesh.parent=clean;mesh.matrix_world=world
 for m in mesh.modifiers:
  if m.type=='ARMATURE':m.object=clean
 mesh.name='KevinMaleDummy';material(mesh,(.55,.65,.7));mesh.data.validate(clean_customdata=False)
 keep=[mesh,clean]+props
 for obj in list(bpy.data.objects):
  if obj not in keep:bpy.data.objects.remove(obj,do_unlink=True)
 for a in list(bpy.data.actions):
  if a not in baked:bpy.data.actions.remove(a)
 scene.render.fps=60;scene.frame_start=1;scene.frame_end=max(round(e['duration']*60)+1 for e in entries)
 assign(clean,baked[0]);frame(scene,1)
 bpy.ops.object.select_all(action='DESELECT')
 for obj in keep:obj.select_set(True)
 bpy.context.view_layer.objects.active=clean
 output=OUT/(pack+'.glb')
 bpy.ops.export_scene.gltf(filepath=str(output),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_frame_range=False,export_frame_step=1,export_anim_slide_to_zero=True,export_skins=True,export_influence_nb=8,export_morph=False,export_yup=True,export_apply=True)
 template=(ROOT/'tools/kevin_walk/dummy_walk.glb.import').read_text(encoding='utf-8')
 resource='res://assets/kevin_local/actions/'+pack+'.glb'
 cache_name=pack+'.glb-'+hashlib.md5(resource.encode()).hexdigest()+'.scn'
 template=re.sub(r'uid=.*\n','',template)
 template=template.replace('dummy_walk.glb-5ca5823b6938f52f766905cd3f3ba7c7.scn',cache_name).replace('res://assets/kevin_local/dummy_walk.glb',resource).replace('animation/remove_immutable_tracks=true','animation/remove_immutable_tracks=false').replace('nodes/use_name_suffixes=true','nodes/use_name_suffixes=false')
 imp=Path(str(output)+'.import')
 if not imp.exists():imp.write_text(template,encoding='utf-8')
 reports[pack]={'source_archive':archive,'source_sha256':sha(SOURCE/'Animations'/archive),'blend':blend,'blender':bpy.app.version_string,'output_sha256':sha(output),'bytes':output.stat().st_size,'bones':len(clean.data.bones),'props':[o.name for o in props],'checks':checks}
 (ROOT/'tools/kevin_actions'/('build_'+pack+'.json')).write_text(json.dumps(reports[pack],indent=2)+'\n',encoding='utf-8')
 (OUT/(pack+'.json')).write_text(json.dumps(entries,indent=2)+'\n',encoding='utf-8')
# Merge independent pack builds without losing measured offsets.
merged=[]
for pack in PACKS:
 path=OUT/(pack+'.json')
 if path.exists():merged+=json.loads(path.read_text(encoding='utf-8'))
merged.sort(key=lambda e:({'Combat':0,'Archery / equipment':1,'Spellcasting':2,'Idle':3,'General':4,'Movement':5,'Crafting':6}[e['category']],e['name']))
(ROOT/'prototype/action_catalogue.json').write_text(json.dumps(merged,indent=2)+'\n',encoding='utf-8')
print('CATALOGUE',len(merged),flush=True)
