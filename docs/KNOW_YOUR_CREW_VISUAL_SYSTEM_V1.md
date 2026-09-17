# PlotTwist: Know Your Crew — Visual Reveal System V1

## Goal
Visuals are punchlines and shareable rewards, not decoration. They must increase the social reaction to a reveal without slowing the game.

## Rule
Normal Reveal is instant. AI visual generation runs asynchronously. Never block Next while waiting for an image/video.

## Visual cadence
12-round game:
- 8–9 Instant Reveals: animated UI only.
- 2–3 Hero Image Reveals: cinematic AI image using player photos with consent.
- Maximum 1 Premium Motion Reveal: optional 3–5 second animation after the image exists.
- 1 Final Crew Poster.

## Instant Reveal language
Every reveal should have a mini build-up:
1. Lock answers.
2. 3…2…1…
3. Subject answer appears large.
4. Correct predictors pop in.
5. Score increments.
6. Optional short punchline generated from factual game context.

No long paragraphs.

## Hero Reveal templates
### Desert Island
Selected pair: relaxed, smiling, cinematic tropical island scene.
Unselected friends: humorous background beat such as tiny rescue boat / distant pier / holding luggage.
No humiliation; expressions playful.

### Dream Trip
Selected pair: premium travel-poster scene tailored to destination vibe.
Others: playful airport gate / missed boarding visual beat.

### Millionaire
Chosen player: fictional luxury/business magazine cover composition without copying real magazine trademarks.
Friends: humorous assistants / celebrating entourage.

### 3AM Rescue
Subject and chosen friend: cinematic late-night rescue scene, e.g. broken-down car / rain / ridiculous suitcase situation.

### Start a Company
Subject + chosen partner: exaggerated founder launch scene, fictional company backdrop, confetti, mock product launch.

### Spontaneous Move Abroad
Subject: one suitcase, airport/departure-board style environment, friends reacting behind.

## Quality bar
- Preserve recognizable identity.
- Integrate people into one coherent scene; no pasted heads.
- Consistent lighting, perspective and skin tone.
- Cinematic but comedic, premium rather than meme-template cheap.
- No text rendered inside generated image unless it is later overlaid by the app.
- Mobile-first 4:5 or square crop safe area.
- Never alter body/face in a humiliating or sexualized way without an explicit adult-mode product decision later.

## Consent
Photo upload is optional. Explicit consent before AI transformation. If a player has no photo, use a premium illustrated avatar / initials card; the round must still work.

## Latency UX
When Hero Reveal triggers:
- Reveal answer immediately.
- Show "Your scene is cooking…" as a secondary status.
- Players may press Next.
- When ready, scene is stored in Gallery and can surface between rounds or at end.
- Never make four players stare at a loading spinner.

## Final Crew Poster
At game end create a shareable 4:5 poster using only factual game outcomes, e.g.:
- Crew Champion — highest score
- Most Unpredictable — lowest prediction accuracy by others
- Most Chosen — most selected in positive Who-in-the-Room prompts
- Plot Twist — answer with largest prediction miss

Avoid personality diagnoses. Labels must derive directly from game events.

Poster includes PlotTwist branding and a small CTA suitable for sharing, but not at the expense of the group visual.

## Future motion
Motion is V2, not required for proving gameplay. If tested later:
- 3–5 seconds
- one simple action
- preserve faces
- no dialogue/lip-sync required
- image-first fallback always available
