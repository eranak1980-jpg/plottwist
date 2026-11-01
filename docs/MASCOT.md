# MIPO comic mascot — approved concept 3

The user approved the outlined purple comic speech-bubble character on 1 November 2026. Reference: ChatGPT Library `libfile_c6a7020c6e588191824d31d7b49c639e` (Mischievous purple speech-bubble mascot.png).

## Production

Artwork generated with built-in `image_gen`, using the approved sheet as the edit reference and true transparent background. PNG originals are retained by ChatGPT. Repository assets are converted to 384-pixel RGBA WebP; no background removal, recolouring, redrawing or cropping in code. Five poses together are small enough for the public app shell. Runtime has no generation call or voice dependency.

Shared final prompt:

> EDIT / extract a production-ready SINGLE character from the approved MIPO character sheet reference. Use ONLY the bold outlined comic speech-bubble character shown in the reference; preserve the exact same design, purple gradients, dark purple thick outlines, white cartoon gloves, slender purple arms and legs, white chunky sneakers, eye style, and small bottom-left chat-bubble tail. Output exactly ONE centered full-body mascot, no other characters or duplicates, no sheet, no labels. Clean polished 2.5D cel-shaded artwork as in the approved reference, not rubber or jelly, not photorealistic. Square canvas with real transparent alpha background. Full body and fingertips completely visible with approximately 8% clear padding on all sides; body centered, feet near lower baseline, consistent frontal three-quarter view as reference. Preserve expressive personality. No text, no logos, no floor, no environment, no cast shadow beyond the character, no background white rectangle.

Pose instructions appended individually:

- `smirk`: Confident friendly mischievous smirk, eyebrows slightly raised, both white-gloved hands casually resting at hips, both shoes planted. Neutral idle pose, not winking.
- `surprise`: Genuine comic surprise: both eyes very wide open, raised eyebrows, small open O-shaped mouth, both white-gloved hands up with palms forward beside the face, both shoes planted.
- `suspicious`: Amused suspicious sideways glance, one eyebrow raised and the other lowered, closed-mouth crooked knowing smile, one white glove thoughtfully touching chin, the other on hip, both shoes planted. Not angry or sad.
- `wink`: Cheeky celebratory wink: one eye open, the other clearly closed, big friendly grin, one white-gloved hand pointing sideways, the other giving a thumbs up, both shoes planted.
- `celebrate`: Joyful victory expression: broad open smile, happy eyes with one eye winking, both white-gloved fists raised in celebration, one sneaker lifted slightly as in a tiny victory hop. No confetti or external props.

## Behaviour

`mascot.js` is shared by the game and `/static/mascot-preview.html`. All missed predictions show surprise; multiple identical wrong predictions show suspicious side-eye. Correct predictions show a wink; the finished game shows victory. Waiting uses a quiet smirk. The illustration changes with the event and CSS provides brief whole-character motion; these are not skeletal or frame-by-frame facial animations. Reduced-motion disables movement. Art never gates next-round controls, scoring or gameplay.
