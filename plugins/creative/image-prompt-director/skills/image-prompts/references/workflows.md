# Image workflows

Choose the requested operation before adding detail. A reference-led edit is a different task from generating a new scene. Apply the default five creative variations to whole concepts and complete rewrites, while keeping a selected local repair within its requested scope.

## Text to image

Build the complete visible scene from the user's words. Preserve supplied facts and choose the remaining visual details. Keep entity counts and relationships explicit. If designing a recurring invented character or product, establish distinctive stable anchors in every variation. Do not invent real brand claims or treat invented specifications as supplied facts.

## Image to image and reference reconstruction

Inspect accessible media. Describe only visible evidence; distinguish uncertain details from creative interpretation. Determine whether the user wants close reconstruction, a new composition with the same subject, a style transformation, or a new design inspired by selected qualities.

Give each input a narrow role. Identity, exact product geometry, pose, layout, style and palette may come from different inputs. When inputs conflict, follow the user's stated priority; if priority is material and absent, ask a focused question. Do not blend faces or product forms accidentally. State which traits transfer and which do not.

Reconstruction from a reference is an approximation goal. Do not promise pixel identity, a recovered original prompt, or exact camera metadata. If a reference's text must survive, transcribe it carefully and mark any illegible portions for confirmation.

## Multi-reference composition

Create a stable input map, for example:

- Reference A: person identity and face shape; not clothing or background.
- Reference B: garment cut, fabric and color; not the wearer's face.
- Reference C: room layout and perspective; not any people or signage.

Include this role map in every complete variation and provide required attachment instructions. State scale, contact and occlusion between combined elements: where the person's feet meet the floor, how fabric fits the body, which prop is in front, and how shadows share the same light source. Keep identity/product authority stronger than optional style influence.

Do not assume every target model accepts multiple inputs, weights, masks, or reference types. If native support is unknown, provide the portable prompt and mark input handling for confirmation. Do not imply that prose alone can turn an unsupported model into a reference-conditioned one.

## Local editing and inpainting

Lead with the exact desired change. Identify the region by visible boundaries or a supplied mask, then list what must remain: face identity, product geometry, crop, viewpoint, light, lettering, object count and surrounding pixels as appropriate.

Keep a small edit concise. Do not paste a new full scene brief that invites restaging. If the change affects shadows, reflections, occlusion or perspective, name the dependent adjustments and preserve unrelated areas. A mask constrains a tool only when that surface supports masks and the actual mask is supplied; do not invent mask coordinates.

Prompting does not guarantee pixel-identical preservation. If exact untouched pixels are essential, describe the need for compositing or a suitably constrained editing tool instead of promising it through wording.

## Outpainting and reframing

Specify the new canvas orientation and what is extended on each side. Lock the original subject, its scale and location unless the user requests a change. Continue perspective lines, light direction, texture scale, horizon, depth and existing scene logic across the join. Distinguish expanding the canvas from cropping or zooming out to re-render the subject. Give clear instructions for any newly exposed body parts, architecture or environment.

## Character and product consistency

With a supplied reference, use it as the authority instead of over-describing uncertain traits. Repeat a compact identity/product contract in every prompt. Preserve distinguishing geometry and marks, clothing if locked, material finish, colors, logo placement, orientation and any essential asymmetry.

With an invented text-only subject, define stable anchors once internally and repeat them in full in each output. Give each series subject a stable name/identifier and avoid changing its core design across scenes. A seed is not a cross-model identity control, and its availability is not assumed.

If the user wants five alternate character designs rather than one character in five images, varying identity is permitted. Make that distinction explicit in the working interpretation.

## Typography, posters, ads and editorial layout

Quote only the literal text that should appear in the image. Preserve spelling, punctuation, capitalization, numerals and line breaks. Specify reading order, typographic hierarchy, alignment, margins, contrast and the surface on which text sits. Use an exact-copy instruction and exclude additional lettering where appropriate.

If the user asks you to invent ad copy, create clearly fictional or generic creative copy within the brief; do not invent product efficacy, certifications, prices, discounts or endorsements. If copy is to be added later, reserve a defined clean region and explicitly keep it free of rendered text or distracting detail. Check that the subject and its shadow do not intrude into that region.

Do not claim that a model will render text perfectly. If the deliverable requires exact production typography, offer generation of the visual background with separate layout as an option when useful, while still delivering the requested prompt.

## Transparent assets, cutouts and icons

State that the output should have real alpha transparency, not a white canvas or visible checkerboard. Define the full silhouette, edge treatment, internal cutouts, detached parts and margin around the subject. Decide whether a shadow should be absent, contained, or supplied separately. Avoid transparent or reflective materials disappearing into the empty background; describe their visible edges and highlights when needed.

Keep requested native background/output controls in the settings note and verify support for the chosen surface. Words alone cannot guarantee an alpha channel. Do not add a background scene to a cutout prompt unless requested. For small icons, prioritize a legible silhouette and bounded detail rather than photorealistic microtexture.

## Illustration, architecture and information graphics

For illustration, specify medium, line weight, shape language, edge quality, texture, palette and depth cues. Do not force a camera simulation onto a flat graphic.

For architecture, define building scale, view, horizon, materials, structural logic, surrounding context and visible circulation. Preserve a supplied plan's actual geometry; do not invent compliance or engineering accuracy. Distinguish conceptual visualization from construction documentation.

For diagrams and infographics, identify the entities, correct labels, relationships and reading order. Use the user's verified facts; do not invent data. Specify a clear hierarchy and visual encoding. If the information is dense, prioritize a legible layout and indicate that final factual and typographic inspection is required.

## Panels, storyboards, contact sheets and image series

Specify whether the output is one composite image or separate files. For a composite, give panel count, grid, gutters, reading order and panel-local content. State whether labels belong in the rendered image or only in the accompanying explanation. Keep subjects and lighting consistent when required.

For separate images, deliver one independently usable prompt per required image within each requested direction. Repeat the series identity and visual system in every prompt. Do not rely on a previous chat message as the only carrier of continuity. Five variations of a series are five alternative creative directions; do not silently create five times the intended production workload when the user wanted just one finished series.

## Repair from a generated result

Inspect the result when available. Compare it with the original brief before changing the prompt. Identify the actual mismatch—wrong count, silhouette, face, crop, lettering, lighting, prop placement, or unwanted edit—and choose a specific correction. Keep an approved composition stable. Change one important issue at a time when practical.

If no output is available, write a proposed repair based on the user's report and say that it is based on that description. Do not claim visual inspection. Return one repaired prompt for a selected result unless the user asks for new alternatives.
