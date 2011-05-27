#!/usr/bin/env python

from gimpfu import *

def process_layers(layers):
    # Group layers by name
    groups = {}
    for layer in reversed(layers):
        name = layer.name.split()[0]
        if not name in groups:
            groups[name] = []
        groups[name].append(layer)

    tapes = []
    sheet_width = 0
    sheet_height = 0
    for layers in groups.values():
        lwidth = 0
        lheight = 0
        # Calculate layer bounds
        for l in layers:
            lwidth = max(lwidth, l.width)
            lheight = max(lheight, l.height)
        tapes.append((lwidth, lheight, layers))

        twidth = len(layers)*lwidth # tape width
        sheet_width = max(sheet_width, twidth)
        sheet_height = sheet_height+lheight

    return (sheet_width, sheet_height, tapes)

def make_animated_sprite(src, src_drawable):
    (sheet_width, sheet_height, tapes) = process_layers(src.layers)

    # Create new image
    img = gimp.Image(sheet_width, sheet_height, RGB)
    layer = gimp.Layer(img, "Sprite sheet", sheet_width, sheet_height,
                       src_drawable.type, 100, NORMAL_MODE)
    img.add_layer(layer, 0)

    y = 0
    for (lwidth, lheight, layers) in tapes:
        x = 0
        for l in layers:
            src.active_layer = l
            pdb.gimp_edit_copy(l)
            pdb.gimp_rect_select(img, x, y, lwidth, lheight, 2, 0, 0)
            pdb.gimp_edit_paste(layer, 1)
            pdb.gimp_floating_sel_anchor(pdb.gimp_image_get_floating_sel(img))
            x += lwidth
        y += lheight
    pdb.gimp_selection_none(img)

    disp = gimp.Display(img)
    gimp.displays_flush()

register("make_animated_sprite",
         "Make sprite sheet from layers",
         "Make sprite sheet from layers, layers must be grouped by name",
         "Stepan Zastupov",
         "Stepan Zastupov",
         "2011",
         "<Image>/Filters/Animation/Make sprite sheet",
         "RGB, RGBA",
         [],
         [],
         make_animated_sprite)

main()
