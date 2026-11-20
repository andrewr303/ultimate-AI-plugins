# Workflow cards

Use the matching card with the core skill and output contract. These are creative production methods; native support must be checked separately.

## Text-to-video

Create the entire scene rather than relying on unstated imagery. Specify the opening composition, subject/environment, action progression, camera, light, audio and final image. For a multi-scene story, identify what each scene contributes and give it enough screen time. Five variations keep the required story intact while changing an intentional directing approach.

## Image-to-video

An actual starting image controls the initial composition and visible identity. Inspect it when accessible. Record the subject's pose, scale, frame position, gaze, environment, light and apparent camera. Prioritize the desired motion and permitted changes; do not write an incompatible new opening.

Direct small scene-appropriate movements for a restrained brief: breathing, fabric response, practical motion and camera drift. For larger action, explain how it begins from the visible pose. Explicitly preserve product geometry, face, clothing and background elements that should stay fixed. Do not assume an image automatically becomes a native first-frame pin in every tool; tell the user where it must be assigned after checking the surface.

## Reference-to-video: stills and clips

Create a role map. A reference may control character identity, product geometry, wardrobe, setting layout, composition, visual style, movement pattern or opening/closing state. State the intended authority and the attributes that may be newly directed. A style reference should not accidentally substitute its subject; a motion reference should not import its actor, clothing, background or audio.

For several characters, map each to one stable role and description. Describe their positions and interactions so identities do not swap. For multiple products, keep counts and positions explicit. Resolve conflicting reference instructions in favor of the user's stated priorities; ask only when an unresolved conflict changes the deliverable materially.

A video reference is not automatically editable source footage or a source for its soundtrack. Verify whether the host accepts clip references, what role they play and whether audio is considered. If only key stills or a textual motion description can be used, label that fallback. Never claim to have watched an unavailable clip.

## First and last frame; last frame only; keyframes

For supplied first/last images, document exact asset assignment outside the prompt and the role labels inside it. Compare geometry and visual state. Specify what remains invariant, what travels, its path and speed, how the camera moves and how the action settles into the final frame. Use arrival/hold time when appropriate. Native pinning, where supported, requires actual image assignment; a prose instruction alone does not create it.

If only a closing image exists, create a compatible opening and a feasible approach that arrives at that image. If intermediate keyframes are requested, give their ordered times and desired states, with times inside the clip and endpoints handled separately. Recheck actual field semantics before emitting a native payload. Do not assume every reference UI supports timed keyframes.

When endpoints disagree materially, diagnose the conflict before writing a smooth physical bridge. Offer concrete choices: keep the shot continuous and increase time; use a deliberate cut or occlusion transition; prepare matching endpoint stills; or explicitly choose a fantasy transformation. Do not resolve a factual continuity error with an unrequested morph. Continue the non-dependent plan with the selected or clearly labeled feasible assumption.

## First scene and last scene described in text

These are story requirements, not uploaded images. Write detailed opening and closing scene direction and connect them through understandable events. If useful, supply optional still-image briefs for creating actual frame assets later. Label those as preparation prompts and do not count them as the five video variations. Do not claim anything is pinned until an actual supporting asset is assigned in a capable surface.

## Extension and continuation

Inspect the terminal portion of the source clip when available. Record pose, action phase, velocity, camera position/movement, focus, light, wardrobe, props and sound. Begin the continuation there. Avoid resetting the subject to an earlier pose or repeating an already completed action.

Use local time starting at 0 for the extension and show the mapping to the assembled sequence. Example: source 8 seconds plus a 4-second extension means local 0–4 maps to sequence 8–12; the final intended sequence is 12 seconds. This arithmetic is editorial planning, not a provider length guarantee. Describe intentional cuts explicitly. Verify whether extension can change resolution/aspect, append only, preserve earlier frames or use uploaded versus generated sources; do not infer these controls from ordinary generation mode.

## Video edit or restyle

Lead with what changes and where/when it changes. Protect subject identity, source motion, camera, timing, layout, text, sound and untouched regions as appropriate. A local fix should be a concise delta with preservation locks, even though initial-generation prompts are long. Do not use a complete new scene description that invites restaging when the goal is one small edit.

For a restyle, state visual medium and specific surface treatment while preserving motion, composition and story. For removal, replacement or a targeted object edit, explain the natural background or contact that should occupy the edited area. Verify native editing support before describing uploads or masks as accepted controls.

## Seamless loop

Choose a cycle whose opening and closing states can match: camera, object position, pose, light, environment and movement phase. An oscillation returns in both position and velocity; simply repeating a still may create a jerk. Direct the full cycle, settling/phase relation and sound seam. Keep the camera fixed unless a deliberate closed path can land in the opening state. Use matching endpoint assets only if supported and useful. Treat seamlessness as a target to inspect.

## Longer story, advertisement and storyboard

Break total runtime into scenes and shots that carry a clear progression. Establish continuity first, then script each unit with its own complete identity and set locks. If a target cannot reliably render the whole sequence in one native job, hand off independent clip prompts and an assembly plan. Do not conceal a 60-second film inside an unsupported 60-second generation setting.

For ads, fix product appearance, required claim wording, legal/user-provided copy and CTA. Do not invent performance claims. Preserve exact logo/text instructions; offer post-production text overlays when precision matters. For storyboards, separate panel/still preparation from animation prompts and maintain the same shot identifiers through the handoff.

## Repair or adapt an existing prompt

Retain all successful decisions and user locks. Diagnose a specific failure: subject drift, action overload, unreadable text, impossible camera, mismatched endpoints, unsupported native syntax or excessive scene changes. Make the smallest useful revision. If adapting to a shorter input allowance, remove redundant adjectives and lower-priority atmosphere before losing action, identity, endpoint constraints or exact text. A single repair remains a single repair unless alternatives are requested.
