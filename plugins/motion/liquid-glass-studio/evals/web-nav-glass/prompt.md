---
tags: [liquid-glass-studio, web, implement]
max_turns: 60
timeout_seconds: 2400
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Give the top nav bar on our static site (index.html, styles.css) a liquid glass look, like the floating bars in iOS 26. It has to hold up in Chrome, Safari and Firefox and for people who turn on reduced transparency or high contrast, so include proper fallbacks. No build step and no npm packages, please; it is plain HTML, CSS and JS.

Input files: README.md, index.html, styles.css, assets/harbor.svg
