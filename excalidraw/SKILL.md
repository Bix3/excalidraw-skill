---
name: excalidraw
description: Create, modify and render Excalidraw files such as .excalidraw and .excalidraw.png
---

# Excalidraw workflow

## Requirements:

If a command fails during operation because a dependency is missing, report the missing dependency and stop.

## Modify an existing PNG

1. Extract its scene once to a temporary `.excalidraw` file.
2. Edit that temporary scene, render it, and embed the edited scene into the new PNG.
3. Inspect the PNG. If corrections are needed, repeat step 2 using the same temporary scene.
4. Once satisfied, replace the original PNG.

If the PNG has no embedded scene, ask the user for the source file instead.

## Modify an existing Excalidraw file

1. Edit a temporary copy of the scene.
2. Render it and check the result before replacing the original scene.
3. If a PNG is requested, embed the edited scene in it.

## Create new

1. Write a valid `.excalidraw` scene.
2. Render it, check the result, and embed the scene into the PNG.
3. Save the PNG. Keep the `.excalidraw` file too if requested.

## Scene JSON and layout edits

`.excalidraw` is plain JSON. See the [official JSON schema](https://docs.excalidraw.com/docs/codebase/json-schema) for the document format and [element types](https://github.com/excalidraw/excalidraw/blob/master/packages/element/src/types.ts) for detailed fields. The schema page's commented example is illustrative, not valid JSON or a complete element template.

## Tools

The Python scripts are in `scripts/` beside this skill file. Paths below are relative to the skill directory; use full paths when working elsewhere.

```bash
# Extract a scene
python3 scripts/extract-excalidraw.py input.png scene.excalidraw

# Render a scene (choose dark or light)
excalidraw render scene.excalidraw --theme dark --out rendered.png

# Make the PNG editable
python3 scripts/embed-excalidraw.py scene.excalidraw rendered.png editable.excalidraw.png
```

For extraction-only or rendering-only requests, use just the needed steps.

## Always

- Name editable PNGs `*.excalidraw.png` by default, unless the user specifies another name.
- Preserve unrelated content and the original theme unless asked to change them.
- Keep temporary files beside the destination. Replace originals with `mv` only after all steps succeed.
- Delete temporary files on success or failure; keep only the requested outputs.