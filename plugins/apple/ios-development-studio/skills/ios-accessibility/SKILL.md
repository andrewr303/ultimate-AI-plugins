---
name: ios-accessibility
description: "Implement or review iOS VoiceOver/Voice Control semantics, Dynamic Type, focus, contrast, non-color cues, right-to-left reading, reduced motion or reduced transparency. Use ios-design for general visual polish and ios-navigation for route behavior. Do not label static inspection a compliance certification or apply a visual redesign without a task need."
---

# Accessible iOS interaction

Read the [operating contract](../ios-development/references/operating-contract.md) first. Identify the user task, supported input/assistive modes and the view or change under review.

## Workflow

1. Inspect controls and their exposed semantics using [semantics and focus](references/semantics-and-focus.md). Prefer native controls. Verify labels, values, traits, grouping, actions and traversal order against the visible task.
2. Inspect large text, color/contrast, motion, transparency and direction using [adaptive accessibility](references/adaptive-accessibility.md). Preserve user settings instead of forcing a single presentation.
3. Test meaningful states, including validation errors, loading completion, selection, disabled actions and modal dismissal. Hidden content must not remain an accidental accessibility or hit-testing target.
4. Use available accessibility-tree inspection and device/simulator testing. VoiceOver, Voice Control, keyboard or switch behavior needs the relevant runtime check; screenshots alone cannot establish it.
5. Fix the smallest genuine barrier. Recheck the primary task with the relevant settings and verify that added announcements or grouping have not made interaction noisy or removed individual controls.

## Evidence and limits

Report the barrier, affected task, location, settings/tool used, change and observed result. Distinguish source-level risks from demonstrated runtime failures. If assistive testing is unavailable, list the exact remaining task/settings without claiming a pass.

Do not add redundant labels to every element, announce every update, hide required information to make large text fit, or replace semantic controls with custom gestures without equivalent actions. Do not infer accessibility solely from appearance or automated audit output. See [source map](../../docs/source-map.md).
