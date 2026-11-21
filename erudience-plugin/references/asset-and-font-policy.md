# Asset, typography and deterministic rendering policy

## Sources
Website repo `bishal-paul-git/erudience-main`: `src/index.css` imports DM Sans + Inter; body DM Sans with Inter fallback; headings Inter; `tailwind.config.ts` confirms. Refresh source each job. Brand Social OS repo `bishal-paul-git/erudience-social-os`: `BRAND.md`, `BUSINESS.md`, `AGENTS.md`, visual director/image carousel/brand QA agents. Website typography has owner-approved precedence for this plugin: heading Inter 600–800, body DM Sans 400–500, CTA Inter 600. Do not call a font exact unless installed and actually used.

## Logo packaging truth
Official candidates: `src/assets/logo-horizontal.png`, `src/assets/erudience-icon.png`; `src/assets/logo-icon.jpg` unconfirmed. The package deliberately includes NO logo binary until its authentic bytes are successfully retrieved and verified. Source path is NOT equivalent to packaged asset. On run, retrieve actual bytes through authorised connector or public URL, inspect decoded image, compute SHA256, preserve original pixel content and aspect ratio; composite in footer without effects. If fetch fails, status LOGO_BLOCKED; do not create invented logo or claim fully approved brand output. Store approved binary locally in authorised runtime only, never secrets.

## Brand tokens
Paper #F6F1E9; Ink #14120E; Emerald #10B981; Deep Green #0A6E3E; Ink Soft #615B4C; Near-Black Green #0A100E; Mint hsl(158 64% 72%). Refresh current brand policy and record conflicts. No invented CRM screens, fake customer metrics or unverified ROI.

## Output
1080x1350 4:5 PNG RGB/sRGB; headline Inter bold, copy DM Sans; safe margins >=64px unless explicitly reviewed; correct copy; original logo footer only; CTA verified. Fonts are NOT redistributed in plugin archive. The included renderer requires an installed font path and fails rather than silently claiming exact font.
