# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


#Scriptname & version: Cardboy0's Shrinkwrap-Project supporter - V.1.0  (I often forget to actually update this number so don't trust it)
#Author: Cardboy0 (https://twitter.com/cardboy0)
#Made for Blender 2.83



############SETTINGS#############

VG_displace_name = "VG_belly"   #The modifiers need to know which specific vertices you want to be affected by looking at the vertex group with the same name to the left. Change it to another name if you want.


#################################
###########DESCRIPTION###########

#For a more detailed description or guide on how to use, visit the (NSFW) online manual: https://docs.google.com/document/d/1rpJIQqvXcGL9UN-JYzqRKVHk8xaMxgCKM0UYLyqDW_A/edit

#You can download the newest version of this scipt at https://github.com/Cardboy0/Shrinkwrap-Project-supporter , and older versions at https://github.com/Cardboy0/Shrinkwrap-Project-supporter/tree/old-versions .

#This is a script that will help people who want to use the "project" property of a Shrinkwrap modifier to make an Object poke out of the skin of another object, along a specified axis. Basically like those old pin-art toys: https://en.wikipedia.org/wiki/Pin_Art . It doesn't bake anything, it just adds some required modifiers, objects and drivers to make your life easier. This allows viewing your changes in realtime. It's still in development as - while it does do its job - the result, especially if you want to use it for belly bulge fetish pornography, can look hideous.


#################################
########QUICK-START GUIDE########
#1. Get a human model into your scene and add a new plane.
#2. Give your human model a new vertex group, call it "VG_belly" and assign all vertices of the belly to it.
#3. Select both new objects (humanoid has to be the active object), and run this script.
#4. A new model will have been added to your scene with the same name as the original with the addition "projectable". It differs from the original since it has some new modifiers and other stuff.
#5. 3 of the new modifiers will be marked as red since they lack a target object in their settings, a shrinkwrap mod and two vertex weight proximity mods.
#6. For all three mods choose the same target object which is supposed to make the belly deform and move it in front of the belly.
#7. The plane can be used to change the direction of the shrinkwrap projection. If you want to, you can parent it to three vertices of the original belly so it will always have the belly axis.


#################################
#############CHANGELOG###########
# 1.0
#       - Script now also adds additional modifiers for smoothing, although they are disabled by default.
#       - The created object now has some custom properties that can be dealed with by simply selecting the object, pressing n (in viewport) and going to the "properties" field in "item". They are as follows:
#               + fix bulge         #increase this value if the created bulge has noise
#               + show shrinkwrap   #toggles visibility of all added bulging modifiers
#               + show smooth       #toggles visibility of all added smoothing modifiers
#               + smooth tune max   #changes values of the vertex group that the smooth modifiers uses. Explaining is hard, instead just set the VG as active, go into weight paint mode and see what happens when u mess with this value.
#               + smooth tune min   #same as above
#
# 0.9  
#       - Original







############################################################################################################################################################################
############################################################################################################################################################################
import bpy

C = bpy.context
D = bpy.data
O = bpy.ops

abbr = "SPS." #abbreviation to use for added mods and other stuff
Smoothtype = 1

#lets you select a list of objects (need to input the actual classes instead of their names), and also optionally choose the object you want to be active. By default it sets the first item in the list as active. The optional active object doesn't have to be in the list to be set as active, but then it still won't be selected.
#will deselect all other objects
#example: select_objects([Suzanne,Cube,Suzanne.001],Suzanne.004)
def select_objects(object_list, active_object = None):
    O.object.select_all(action='DESELECT')
    if object_list == [] and active_object == None:
        return "no objects to select"
    for i in object_list:
        i.select_set(True)
    if active_object == None:
        C.view_layer.objects.active = object_list[0]
    else:
        C.view_layer.objects.active = active_object


#adds a simple driver to the desired property. Class_source is the desired object (Object, Modifier, Shapekey, whatever), and property_source is the name of the actual property, for instant "show_viewport". Obj_target is the object whose property should be taken as a reference for the driver, and data_path_target is the data_path to its property. To get the data_path of a property, use CLASS.path_from_id("propertyname")
#driversimpleadd(property_source = "show_viewport", class_source = i, Obj_target = Obj_new, data_path_target = Mod_shrinkwrap.path_from_id("show_viewport"))
def driversimpleadd (property_source, class_source, Obj_target, data_path_target):
    driver = class_source.driver_add(property_source).driver
    var = driver.variables.new()
    var.type = "SINGLE_PROP"
    var.targets[0].id = Obj_target
    var.targets[0].data_path = data_path_target
    driver.expression = var.name
    return driver


#creates a new vertex groups for the desired object, with all vertices having been assigned with the same weight.
def createVGhomoweight(object, weight, name = None):
    if name == None:
        name = "all weights = " + str(weight)
    VG_return = object.vertex_groups.new(name = name)
    v_indices = []
    for i in object.data.vertices:
        v_indices += [i.index]
    VG_return.add(v_indices, weight, "ADD") 
    return VG_return
#########################################################################
#########################################################################
#########################################################################    
print("Start******************************************")

O.object.mode_set_with_submode(mode='EDIT',  mesh_select_mode = {"VERT"} ) #me must make sure that only vertex selection is possible in edit mode, otherwise problems can appear
O.object.mode_set(mode='OBJECT')


#assigning the 2 selected objects to variables.
for i in C.selected_objects:
    if i == C.view_layer.objects.active:
        Obj_orig = i
    else:
        Obj_axis  = i


select_objects([Obj_orig])
O.object.duplicate()
Obj_new       = C.object
Obj_new.name  = Obj_orig.name + " projectable"


L_addedmods = [] #list of all added mods so we can unextend them later for comfort


Mod_hook = Obj_new.modifiers.new(abbr+"Hook", "HOOK")
L_addedmods += [Mod_hook]
O.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0))
Obj_empstatic = C.object
Obj_empstatic.name = abbr + "hook object"
Obj_empstatic.hide_set(True)
select_objects([Obj_new])
for i in range(len(Obj_new.modifiers)):
    O.object.modifier_move_up(modifier = Mod_hook.name)
Mod_hook.object = Obj_empstatic
O.object.mode_set_with_submode(mode='EDIT')
O.mesh.select_all(action='SELECT')
O.object.hook_assign(modifier = Mod_hook.name)
O.object.mode_set(mode='OBJECT')


Const_rot = Obj_new.constraints.new("COPY_ROTATION")        #this combination of hook mod and constraint allows use to change the rotation of the object without rotating the actual mesh
Const_rot.name = abbr+Const_rot.name
Const_rot.target = Obj_axis


VG_allmax = createVGhomoweight(Obj_new, 1, abbr+"vwm mod")

Mod_VWmix = Obj_new.modifiers.new(abbr+"Vertex Weight Mix", 'VERTEX_WEIGHT_MIX')
L_addedmods += [Mod_VWmix]
Mod_VWmix.vertex_group_a = VG_displace_name
Mod_VWmix.vertex_group_b = VG_allmax.name


Mod_displace = Obj_new.modifiers.new(abbr+"Displace for shrinkwrap", "DISPLACE")
L_addedmods += [Mod_displace]
Mod_displace.direction = "Z"
Mod_displace.vertex_group = VG_displace_name
Mod_displace.strength = 10


Mod_shrinkwrap = Obj_new.modifiers.new(abbr+"Shrinkwrap", "SHRINKWRAP")
L_addedmods += [Mod_shrinkwrap]
Mod_shrinkwrap.wrap_method = 'PROJECT'
Mod_shrinkwrap.use_positive_direction = False
Mod_shrinkwrap.use_negative_direction = True
Mod_shrinkwrap.use_project_z = True
Mod_shrinkwrap.project_limit = Mod_displace.strength * Mod_displace.mid_level
Mod_shrinkwrap.vertex_group = VG_displace_name
#dont add a CO yet, the user has to do that


Mod_vwp = Obj_new.modifiers.new(abbr+"Vertex Weight Proximity", "VERTEX_WEIGHT_PROXIMITY")
L_addedmods += [Mod_vwp]
Mod_vwp.vertex_group = VG_displace_name
Mod_vwp.proximity_mode = 'GEOMETRY'
Mod_vwp.proximity_geometry = {'VERTEX', 'EDGE', 'FACE'}
Mod_vwp.min_dist = 0
Mod_vwp.max_dist = 0.001
#no CO either, as it has to be the same chosen by the user. Adding a driver for that doesn't seem to be possible.


Mod_displacereverse = Obj_new.modifiers.new(abbr+"Displace reverse", "DISPLACE")
L_addedmods += [Mod_displacereverse]
Mod_displacereverse.direction = "Z"
Mod_displacereverse.vertex_group = VG_displace_name
Mod_displacereverse.strength = -10



#adding mods for easier smoothing
L_addedmods_smooth = []
if Smoothtype == 1:
    VG_smooth_vwp  = createVGhomoweight(Obj_new, 1, abbr+"Vertex Weight Proximity for smooth")
    
    Obj_new.vertex_groups.active = Obj_new.vertex_groups[VG_displace_name]
    bpy.ops.object.vertex_group_copy()
    VG_smooth_mask = Obj_new.vertex_groups[-1]
    VG_smooth_mask.name  = abbr + VG_displace_name + "_copy"
    
    Mod_vwm_smooth = Obj_new.modifiers.new(abbr+"Vertex Weight Mix for smooth", "VERTEX_WEIGHT_MIX")
    L_addedmods_smooth += [Mod_vwm_smooth]
    Mod_vwm_smooth.vertex_group_a = VG_smooth_vwp.name
    Mod_vwm_smooth.vertex_group_b = VG_smooth_vwp.name
    Mod_vwm_smooth.mix_mode = "SUB"
    
    Mod_vwp_smooth = Obj_new.modifiers.new(abbr+"Vertex Weight Proximity for smooth", "VERTEX_WEIGHT_PROXIMITY")
    L_addedmods_smooth += [Mod_vwp_smooth]
    Mod_vwp_smooth.vertex_group = VG_smooth_vwp.name
    Mod_vwp_smooth.proximity_mode = 'GEOMETRY'
    Mod_vwp_smooth.proximity_geometry = {'VERTEX', 'EDGE', 'FACE'}
    Mod_vwp_smooth.min_dist = 0.1
    Mod_vwp_smooth.max_dist = 0.08
    Mod_vwp_smooth.mask_vertex_group = VG_smooth_mask.name
    
    Mod_smooth = Obj_new.modifiers.new(abbr+"Smooth", 'SMOOTH')
    L_addedmods_smooth += [Mod_smooth]
    Mod_smooth.vertex_group = VG_smooth_vwp.name
    Mod_smooth.iterations = 10
    


#creating custom properties for Obj_new so that the user can easily change things like viewport visibility of all added mods at once.
#I got this stuff with the custom properties from this post by user batFINGER: https://blender.stackexchange.com/questions/143975/how-to-edit-a-custom-property-in-a-python-script    
if not Obj_new.get('_RNA_UI'):
    Obj_new['_RNA_UI'] = {}

#The names for the custom properties we create. Not optimal, maybe later reference them with Obj_new['_RNA_UI'][name] instead as actual objects.
cp_main_show      = abbr + "show shrinkwrap"
cp_smooth_show    = abbr + "show smooth"
cp_main_fix       = abbr + "fix bulge"
cp_smooth_mintune = abbr + "smooth tune max"  #IMPORTANT: description says "max" instead of "min" because this value should be higher than the other one. It's still for the VWP "Lowest" value
cp_smooth_maxtune = abbr + "smooth tune min"  #same thing 

#for i in [cp_main_show, cp_smooth_show, cp_main_fix, cp_smooth_mintune, cp_smooth_maxtune]:
#    i = i.replace("'", "\"")

Obj_new[cp_main_show]      = True
Obj_new[cp_smooth_show]    = False
Obj_new[cp_main_fix]       = Mod_vwp.max_dist
Obj_new[cp_smooth_mintune] = Mod_vwp_smooth.min_dist
Obj_new[cp_smooth_maxtune] = Mod_vwp_smooth.max_dist

#the properties of custom properties can actually behave kinda weird, just so you know (or remember)
for i in [cp_main_show, cp_smooth_show]:
    Obj_new['_RNA_UI'][i] = {"description":i,
                      "default": True,
                      "min":0,
                      "max":1,
                      "soft_min":0,
                      "soft_max":1,
                      "is_overridable_library":0,
                      }
                      
Obj_new['_RNA_UI'][cp_main_fix] = {"description": cp_main_fix,      #weirdness example: in this case it's actually required to use floats instead of ints
                  "default": Mod_vwp.max_dist,
                  "min":0.0,
                  "max":10.0,                               
                  "soft_min":0.0,
                  "soft_max":1.0,
                  "is_overridable_library":0,
                  }
#UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUGH the data_path_target between the brackets NEEDS to have "" instead of '' , but str() changes "" to ''
#fixed with {} and .format

cp_main_show      = '["{}"]'.format(cp_main_show)
cp_smooth_show    = '["{}"]'.format(cp_smooth_show)
cp_main_fix       = '["{}"]'.format(cp_main_fix)
cp_smooth_mintune = '["{}"]'.format(cp_smooth_mintune)
cp_smooth_maxtune = '["{}"]'.format(cp_smooth_maxtune)



#adding the drivers that reference the new custom properties.
for e in ["show_viewport", "show_in_editmode", "show_render"]:                  
    for i in L_addedmods:
        i.show_expanded = False
        driversimpleadd(property_source = e, class_source = i, Obj_target = Obj_new, data_path_target = cp_main_show)
    for i in L_addedmods_smooth:         
        i.show_expanded = False
        driversimpleadd(property_source = e, class_source = i, Obj_target = Obj_new, data_path_target = cp_smooth_show)
driv_main_constraint = driversimpleadd(property_source = "mute", class_source = Const_rot, Obj_target = Obj_new, data_path_target = cp_main_show)
driv_main_constraint.expression = "(var - True)**2"  #apparentely you can add True + True and get the number 2, meaning True == 1. We need to switch True and False because here it's "mute" instead of "show_viewport".

driv_main_displace        = driversimpleadd(property_source = "strength", class_source = Mod_displace,        Obj_target = Obj_new, data_path_target = Mod_shrinkwrap.path_from_id("project_limit"))
driv_main_displacereverse = driversimpleadd(property_source = "strength", class_source = Mod_displacereverse, Obj_target = Obj_new, data_path_target = Mod_shrinkwrap.path_from_id("project_limit"))
driv_main_displace.expression        += "* 2"
driv_main_displacereverse.expression += "* -2"

driv_main_fix             = driversimpleadd(property_source = "max_dist", class_source = Mod_vwp,             Obj_target = Obj_new, data_path_target = cp_main_fix)
driv_smooth_mintune       = driversimpleadd(property_source = "min_dist", class_source = Mod_vwp_smooth,      Obj_target = Obj_new, data_path_target = cp_smooth_mintune)
driv_smooth_maxtune       = driversimpleadd(property_source = "max_dist", class_source = Mod_vwp_smooth,      Obj_target = Obj_new, data_path_target = cp_smooth_maxtune)



Obj_orig.hide_set(True)

print("****************************************************\nFinished")
