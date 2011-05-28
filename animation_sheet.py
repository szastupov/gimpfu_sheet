#!/usr/bin/env python

from gimpfu import *
import sys

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
    for (name, layers) in groups.items():
        theight = 0
        twidth = 0
        # Calculate tape bounds
        for l in layers:
            theight = max(theight, l.height)
            twidth += l.width
        tapes.append((name, twidth, theight, layers))

        sheet_width = max(sheet_width, twidth)
        sheet_height += theight

    return (sheet_width, sheet_height, tapes)

def make_animated_sprite(src, src_drawable):
    (sheet_width, sheet_height, tapes) = process_layers(src.layers)

    # Create new image
    img = gimp.Image(sheet_width, sheet_height, RGB)
    layer = gimp.Layer(img, "Sprite sheet", sheet_width, sheet_height,
                       src_drawable.type, 100, NORMAL_MODE)
    img.add_layer(layer, 0)

    out = sys.stdout
    out.write("%d\n" % len(tapes))

    y = 0
    for (tname, twidth, theight, layers) in tapes:
        x = 0
        out.write("\n%s %d\n" % (tname, len(layers)))
        for l in layers:
            out.write("%d %d %d %d\n" % (x, y, l.width, l.height))
            src.active_layer = l
            pdb.gimp_edit_copy(l)
            pdb.gimp_rect_select(img, x, y, l.width, l.height, 2, 0, 0)
            pdb.gimp_edit_paste(layer, 1)
            pdb.gimp_floating_sel_anchor(pdb.gimp_image_get_floating_sel(img))
            x += l.width
        y += theight
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
