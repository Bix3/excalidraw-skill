---
name: excalidraw
description: Create, modify, and render editable Excalidraw PNGs (.excalidraw.png) and Excalidraw scenes (.excalidraw).
---

# Excalidraw Skill

## Rules

These apply to all workflows.

- **Default output:** An editable PNG named `*.excalidraw.png`. Save a JSON scene (`*.excalidraw`) only if requested, or if it's the file being edited.
- **Missing dependencies:** If a command fails because of a missing dependency, report it and stop.
- **File safety:** Edit temporary files kept beside the destination. Replace originals only after successful rendering and inspection. Delete temporary files on success or failure, and keep only the requested outputs.
- **Preservation:** Keep unrelated content and elements, and keep existing styles unless told to change them. Avoid unnecessary changes to element properties. Style new elements to match the scene rather than applying the defaults below.
- **Theme:** Use the requested theme. Otherwise keep the original theme, or light if there is none.

## Workflows

### Create or Modify

1. Set up a temporary scene:
   - **PNG:** Extract the embedded scene. If it has none, stop and ask for the source file.
   - **New diagram:** Create a valid JSON scene.
   - **`.excalidraw` file:** Copy it.
2. Build or edit the scene as requested.
3. Render it and visually inspect the PNG: every requested change is there, and unrelated content and styles are intact.
4. Repeat steps 2–3 on the same temporary scene until correct. Re-extracting from a PNG would discard your edits.
5. Save the result:
   - **PNG or new diagram:** Embed the final scene in the rendered PNG and save it, replacing any original.
   - **`.excalidraw` file:** Replace the original. If a PNG is requested, embed the final scene in the rendered PNG.

### Extract Only

Extract the embedded scene and save it as a `.excalidraw` file. Do not modify or render it unless requested.

### Render Only

Render the scene and inspect the output. Embed the scene unless a plain PNG is requested.

## Commands

Script paths are relative to this skill's directory. Use absolute paths when working elsewhere.

```bash
# Extract an embedded scene
python scripts/extract-excalidraw.py input.png scene.excalidraw

# Render a scene (--theme light or dark)
excalidraw render scene.excalidraw --theme light --out rendered.png

# Embed a scene into a PNG
python scripts/embed-excalidraw.py scene.excalidraw rendered.png editable.excalidraw.png
```

## Scene Format

Scenes are plain JSON. See the [official JSON schema](https://docs.excalidraw.com/docs/codebase/json-schema) and [element type definitions](https://github.com/excalidraw/excalidraw/blob/master/packages/element/src/types.ts). The commented examples in the schema docs are illustrative, not complete, valid JSON.

Default text and shape styles, as minimal element templates rather than complete scene objects:

```json
{
  "type": "text",
  "text": "Label",
  "fontFamily": 5,
  "fontSize": 20,
  "lineHeight": 1.25,
  "textAlign": "left",
  "verticalAlign": "top",
  "strokeColor": "#1e1e1e"
}
```

```json
{
  "type": "rectangle",
  "roughness": 1,
  "strokeWidth": 2,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "roundness": null
}
```

## Subagents

For well-specified scene edits or JSON generation, prefer a fast subagent when available, and still inspect the rendered PNG before accepting the result.