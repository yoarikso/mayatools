## Maya Display Color + Visibility Override extension
## Shown at: https://www.youtube.com/watch?v=NoUiMNqP2R0
## Johannes Pagwiwoko
## http://yoarikso.tumblr.com



import maya.cmds as cmds
import maya.OpenMaya as om

class DisplayColorOverride(object):
    '''
    drawing overrides logic
    '''
    MAX_OVERRIDE_COLORS = 32
    
    @classmethod
    def override_color(cls, color_index):
        # check color index
        if (color_index >= cls.MAX_OVERRIDE_COLORS or color_index < 0):
            om.MGlobal.displayError("Color index out of range: 0 <= x <= 32")
            return False
            
        # get shapes and override color
        shapes = cls.shape_nodes()
        if not shapes:
            om.MGlobal.displayError("No shapes nodes selected")
            return False
        
        for shape in shapes:
            cmds.setAttr("{0}.overrideEnabled".format(shape), True)
            cmds.setAttr("{0}.overrideColor".format(shape), color_index)
            
        # deselect
        cmds.select(clear=True)
        return True
        
    @classmethod
    def turn_visibility_on(cls):
        shapes = cls.shape_nodes()
        if not shapes:
            om.MGlobal.displayError("No shapes nodes selected")
            return False
        
        for shape in shapes:
            cmds.setAttr("{0}.visibility".format(shape), True)
            
    @classmethod
    def turn_visibility_off(cls):
        shapes = cls.shape_nodes()
        if not shapes:
            om.MGlobal.displayError("No shapes nodes selected")
            return False
        
        for shape in shapes:
            cmds.setAttr("{0}.visibility".format(shape), False)
    
    @classmethod
    def use_defaults(cls):
        # back to normal, ie. unoverridable
        shapes = cls.shape_nodes()
        if not shapes:
            om.MGlobal.displayError("No shapes nodes selected")
            return False
            
        for shape in shapes:
            cmds.setAttr("{0}.overrideEnabled".format(shape), False)
            cmds.setAttr("{0}.overrideVisibility".format(shape), True)
    
    @classmethod
    def shape_nodes(cls):
        selection = cmds.ls(selection=True)
        if not selection:
            return None
            
        shapes = []
        for node in selection:
            shapes.extend(cmds.listRelatives(node, shapes=True))
            
        return shapes   
        
    
class DisplayColorOverrideUI(object):
    '''
    GUI part
    '''
    WINDOW_NAME = "tdnDrawingOverrideColorPallette"
    COLOR_PALETTE_CELL_WIDTH = 20
    FORM_OFFSET = 2
    
    color_palette = None
    vis_checkbox = None
    
    @classmethod
    def display(cls):
        # delete if a window exists
        cls.delete()
        
        # create window
        main_window = cmds.window(cls.WINDOW_NAME, title="Drawing Color Override", rtf=True, sizeable=False)
        main_layout = cmds.formLayout(parent=main_window)
        
        # window specs
        rows = 4
        columns = DisplayColorOverride.MAX_OVERRIDE_COLORS / rows
        width = columns * cls.COLOR_PALETTE_CELL_WIDTH
        height = rows * cls.COLOR_PALETTE_CELL_WIDTH
        
        # make color pallete, default = transparent = 0, topDown -> use left top as 0 counting to 32
        cls.color_palette = cmds.palettePort(dimensions=(columns, rows),
                                             transparent=0, 
                                             width=width,
                                             height=height,
                                             topDown=True,
                                             colorEditable=False,
                                             parent=main_layout)
        
        # build color palette with the 32 color
        for index in range(1, DisplayColorOverride.MAX_OVERRIDE_COLORS):
            color_component = cmds.colorIndex(index, q=True)
            cmds.palettePort(cls.color_palette,
                             edit=True,
                             rgbValue=(index, color_component[0], color_component[1], color_component[2]))
        
        # make the 0th - the transparent default
        cmds.palettePort(cls.color_palette,
                         edit=True,
                         rgbValue=(0, 0.6, 0.6, 0.6))
        
        # Now, Create the override and default button
        override_button = cmds.button(label="Override", 
                                      command="DisplayColorOverrideUI.override()",
                                      parent=main_layout)
        
        default_button = cmds.button(label="Default", 
                                      command="DisplayColorOverrideUI.default()",
                                      parent=main_layout)
        
        # Create checkbox
        vis_checkbox = cmds.checkBox(label="Visible", 
                                     onCommand="DisplayColorOverrideUI.turn_visibility_on()",
                                     offCommand="DisplayColorOverrideUI.turn_visibility_off()",
                                     parent=main_layout,
                                     value=True)
                         
        # Layout the Color Palette, offset margin
        cmds.formLayout(main_layout, edit=True,
                        attachForm=(cls.color_palette, "top", cls.FORM_OFFSET))
        cmds.formLayout(main_layout, edit=True,
                        attachForm=(cls.color_palette, "right", cls.FORM_OFFSET))
        cmds.formLayout(main_layout, edit=True,
                        attachForm=(cls.color_palette, "left", cls.FORM_OFFSET))
        
        # Layout the override button, attach top to the palette, left to the form, right to the middle
        cmds.formLayout(main_layout, edit=True,
                        attachControl=(override_button, "top", cls.FORM_OFFSET, cls.color_palette))
        cmds.formLayout(main_layout, edit=True,
                        attachForm=(override_button, "left", cls.FORM_OFFSET))
        cmds.formLayout(main_layout, edit=True,
                        attachPosition=(override_button, "right", 0, 50))
        
        # Layout the default button
        cmds.formLayout(main_layout, edit=True,
                        attachOppositeControl=(default_button, "top", 0, override_button))
        cmds.formLayout(main_layout, edit=True,
                        attachControl=(default_button, "left", 0, override_button))
        cmds.formLayout(main_layout, edit=True,
                        attachForm=(default_button, "right", cls.FORM_OFFSET))
        
        # Layout the checkbox
        cmds.formLayout(main_layout, edit=True,
                        attachControl=(vis_checkbox, "top", cls.FORM_OFFSET, override_button))
        cmds.formLayout(main_layout, edit=True,
                        attachForm=(vis_checkbox, "left", cls.FORM_OFFSET))
        cmds.formLayout(main_layout, edit=True,
                        attachForm=(vis_checkbox, "right", cls.FORM_OFFSET))
        
        cmds.showWindow(main_window)
        
        
    @classmethod
    def delete(cls):
        # ensure only one UI is ever displayed
        if cmds.window(cls.WINDOW_NAME, exists=True):
            cmds.deleteUI(cls.WINDOW_NAME, window=True)
        
    @classmethod
    def override(cls):
        # button press
        color_index = cmds.palettePort(cls.color_palette, query=True, setCurCell=True)
        DisplayColorOverride.override_color(color_index)
        
    @classmethod
    def turn_visibility_on(cls):
        DisplayColorOverride.turn_visibility_on()
        
    @classmethod
    def turn_visibility_off(cls):
        DisplayColorOverride.turn_visibility_off()
        
    @classmethod
    def default(cls):
        # button press
        DisplayColorOverride.use_defaults()
        
if __name__ == "__main__":
    DisplayColorOverrideUI.display() 
