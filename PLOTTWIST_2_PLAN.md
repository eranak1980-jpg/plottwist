# PlotTwist 2.0

## Product promise
You bring the people. PlotTwist runs the night.

## Core loop
1. The Alibis — cinematic shared opening + private role/secret.
2. The Evidence — concrete evidence changes the obvious theory.
3. The Contradiction — a timestamp or statement makes one timeline impossible.
4. The Accusation — each player forms a theory and votes privately.
5. The Reveal — culprit + reconstructed timeline + explanation of planted and genuine clues.

## Host
The creator is also a full player. Host-only controls are setup/emergency controls, not gameplay duties. The Game Master advances the experience.

## Personalization
Inside jokes are transformed into evidence with narrative purpose. They must not be pasted as arbitrary text.

## Player images
Optional, consent-based photo upload before game start. First implementation: private/local preview and role-card presentation. Production implementation requires durable object storage. Generative role portraits require an image-generation API and explicit player consent. Original uploads should be deleted on a defined retention schedule.

## Image concepts
- Culprit: cinematic noir role portrait, fictional game artwork.
- Witness: evidence-board / surveillance aesthetic.
- Missing person: fictional MISSING poster.
- Final reveal: cast poster and culprit reveal.

## Architecture
Keep production main stable. Develop 2.0 on `plottwist-2`, then merge after end-to-end test.
