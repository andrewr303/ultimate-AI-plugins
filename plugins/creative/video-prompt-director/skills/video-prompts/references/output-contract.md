# Complete output contract

This is an authoring structure, not provider API JSON. Use the user's requested format when one is given. Do not make them fill in a template before receiving useful work.

## Response opening

Use two or three short lines: workflow, target family/surface if known, and consequential assumptions. Identify duration/aspect choices as creative assumptions when not supplied. Include a media assignment table only if references exist; do not invent input files. Mark “not supplied” or “described by user, not inspected” accurately. Omit a generic questionnaire and an essay about prompting.

## Per variation

### Variation N — specific title

**Creative direction.** Explain the visible concept and its distinction from the other variations in a sentence. Supply enough art direction to establish the complete look: period/setting, medium, palette, materials, light, performance, pacing and sound. A variation should still be usable if copied without its siblings.

**Continuity and reference assignments.** Give the invariant cast/product/environment description and each actual asset's precise authority. Describe what the reference must not control where confusion is likely. Reference labels must resolve to an attachment, a user description, or an explicitly pending asset. For text-only generation, write a complete original continuity bible instead of fake reference slots.

**Timed scene/shot direction.** Use a compact timeline to organize the sequence, then complete shot payloads. For each shot show:

- Scene, shot number, sequence interval and local duration.
- Opening image/state, focal subject and readable composition.
- Timed subject action, environmental motion and camera behavior.
- Light, palette, focus and visible material details.
- Dialogue/speaker/time and ambience, practical sound and music direction, or deliberate quiet.
- Exact end pose/state, transition type and what the next shot must inherit.

For a one-shot request, use one scene and one shot with several timed beats. Do not insert a cut because it makes the default template easier. Different scenes are not mandatory for a brief that requires one location.

**Copyable shot payloads.** Each fenced `text` block is a usable prompt for one generation unit. Include shot-local timing and required identity/reference locks inside it. Repeat the critical information even if it also appears in the treatment. This limited repetition buys independence. Do not make the user combine a continuity paragraph from elsewhere with an incomplete prompt. A prompt block can contain readable labeled paragraphs; it need not be a single dense paragraph.

**Handoff outside the prompt.** List the actual media attachments and verified surface controls, if applicable. Unknown technical settings stay labeled “verify in selected surface” or are omitted. State whether the shot is to be generated independently and assembled, or whether a verified native multishot mode is intended. Include cut/overlay/audio assembly notes only where relevant. Do not place editorial instructions into a model that cannot execute them and pretend they are native features.

**Useful exclusions.** Prefer positive directions. Add only targeted exclusions that protect the brief, such as “no extra label text” or “keep the existing logo unchanged.” Put these in ordinary prose unless a separate negative field is verified for the selected surface. Do not attach a universal defect-word wall.

## Count, length and adaptation

The default is five full variations. Do not use a detailed variation 1 followed by four titles. A user-specified count or compact format supersedes this. The 650–1,200-word working range is for a useful short-sequence director pack; a tightly scoped edit may need only a few sentences. Longer films need enough shots and detail to cover the actual requested duration and story.

Avoid redundant giant master prompts plus identical giant shot prompts. The treatment carries sequence-level reasoning; copyable shots carry the exact local direction and necessary locks. Native input size is a separate constraint: if required, keep a full director pack and provide a clearly labeled shorter model payload for each shot. State any omitted low-priority detail; preserve subject, action, reference locks, timing and endpoints first.

When adapting to several models, keep five creative concepts total. Add a concise mapping outside each prompt or once for the shared interface. If actual syntax differs, provide the affected copyable payload or settings without multiplying every scene into five new concepts. User requests for a per-model count take precedence.

## Optional structured export

When the user asks for JSON, export valid JSON using an explicit authoring schema such as:

```json
{
  "workflow": "text-to-video",
  "creative_assumptions": {"duration_seconds": 12, "aspect_ratio": "16:9"},
  "variations": [
    {
      "title": "Filled specific concept",
      "continuity": "Complete invariant description",
      "shots": [
        {
          "id": "S1",
          "sequence_start_seconds": 0,
          "sequence_end_seconds": 12,
          "prompt": "Complete independently usable shot prompt"
        }
      ],
      "handoff": "Actual input assignment and assembly instructions"
    }
  ]
}
```

This schematic illustrates field types, not an acceptable finished result. Fill every requested variation and prompt, validate JSON syntax, and never present these authoring fields as an accepted provider request body. Do not emit placeholder descriptions in a completed creative task.
