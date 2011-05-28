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

    sheet_width = 0
    sheet_height = 0
    for layers in groups.values():
        twidth = sum(l.width for l in layers)
        sheet_width = max(sheet_width, twidth)

    tapes = []
    x = 0
    y = 0
    for (name, layers) in groups.items():
        twidth = sum(l.width for l in layers)
        if (twidth+x > sheet_width):
            x = 0
            y = sheet_height

        nlayers = []
        for l in layers:
            nlayers.append((x, y, l))
            sheet_height = max(sheet_height, y+l.height)
            x += l.width
        tapes.append((name, nlayers))

    return (sheet_width, sheet_height, tapes)

def make_animated_sprite(src, src_drawable, image_file, animation_file):
    gimp.progress_init("Generating sprite sheet")
    (sheet_width, sheet_height, tapes) = process_layers(src.layers)

    # Create new image
    img = gimp.Image(sheet_width, sheet_height, RGB)
    layer = gimp.Layer(img, "Sprite sheet", sheet_width, sheet_height,
                       src_drawable.type, 100, NORMAL_MODE)
    img.add_layer(layer, 0)

    if animation_file is None:
        out = sys.stdout
    else:
        out = open(animation_file, "w")
    out.write("%d\n" % len(tapes))

    ntape = 0
    for (name, layers) in tapes:
        ntape += 1
        gimp.progress_update(float(ntape)/len(tapes))
        out.write("\n%s %d\n" % (name, len(layers)))
        for (x, y, l) in layers:
            out.write("%d %d %d %d\n" % (x, y, l.width, l.height))
            src.active_layer = l
            pdb.gimp_edit_copy(l)
            pdb.gimp_rect_select(img, x, y, l.width, l.height, 2, 0, 0)
            pdb.gimp_edit_paste(layer, 1)
            pdb.gimp_floating_sel_anchor(pdb.gimp_image_get_floating_sel(img))
    pdb.gimp_selection_none(img)

    if image_file is None:
        disp = gimp.Display(img)
        gimp.displays_flush()
    else:
        pdb.gimp_file_save(img, layer, image_file, image_file)
        gimp.delete(img)

register("make_animated_sprite",
         "Make sprite sheet from layers",
         "Make sprite sheet from layers, layers must be grouped by name",
         "Stepan Zastupov",
         "Stepan Zastupov",
         "2011",
         "<Image>/Filters/Animation/Make sprite sheet",
         "RGB, RGBA",
         [
          (PF_FILE, "image_file", "Save image to (keep None to save manualy)", ""),
          (PF_FILE, "animation_file", "Save animation to", ".txt")
         ],
         [],
         make_animated_sprite)

main()
