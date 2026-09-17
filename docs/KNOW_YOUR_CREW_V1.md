# PlotTwist: Know Your Crew — V1

## One-sentence rule
בכל תור שחקן אחד עונה בסוד על שאלה עליו; האחרים מנחשים את התשובה. מי שמכיר את החבורה הכי טוב צובר הכי הרבה נקודות.

## Product principle
אם שחקן חדש לא מבין מה לעשות בתוך 30 שניות — המכניקה לא מספיק פשוטה.

## V1 scope
- Friends only
- 3–6 players
- 12–15 rounds
- 20–35 minutes
- Name + photo + Join
- Question → private answer → guesses → reveal → score → next
- No roles, chapters, alibis, long instructions or host-only knowledge

## Core loop
1. Spotlight player receives a question.
2. Spotlight player answers privately.
3. Everyone else predicts that answer privately.
4. Reveal happens simultaneously.
5. Correct predictors get 1 point.
6. The answer is saved into the Crew Memory.
7. Later questions can reference previous answers.

## Question families
### 1. KNOW ME
A scenario with 3–4 meaningful choices. Example: If Eran received €20,000 that had to be spent tonight, where would most of it go?

### 2. WHO IN THE ROOM?
Spotlight player chooses another player privately. Example: Who here would Eran call first if he was in real trouble at 3 AM?

### 3. RANK THEM
Spotlight player ranks the other players against a provocative but safe criterion. Example: Rank the others from most to least likely to survive a month without a phone.

### 4. PREDICT THE CREW
Everyone answers; players predict the room consensus. Example: Who would the group trust most to plan a surprise trip?

### 5. DILEMMA
Two uncomfortable/funny options reveal preferences. Example: One year of luxury with no travel, or one year traveling with a tiny budget?

### 6. PLOT TWIST CALLBACK
Generated from Crew Memory. Example: Earlier everyone called Roi the most frugal. Now Roi must spend ₪50,000 tonight. What does he spend it on?

## Question quality gate
A question ships only if the reveal has a realistic chance of causing a spoken reaction such as: “What?!”, “I knew it”, “Why him?”, “You don't know me at all”, or laughter.

Reject trivia-like questions unless reframed as a situation. Avoid generic favorites (favorite color, movie, food) unless the scenario creates stakes or social meaning.

## Difficulty / intimacy curve
Rounds 1–3: warm, funny, easy.
Rounds 4–7: personality and habits.
Rounds 8–11: relationships inside the room, trust and choices.
Rounds 12–15: callbacks, contradictions, stronger social reveals.

Never jump directly into sensitive material. V1 should avoid health, trauma, politics, religion, finances as personal disclosure, sexuality, infidelity allegations, illegal behavior accusations, body/appearance judgments, or humiliating content.

## Scoring
- Correct prediction: +1
- Exact Rank Them position: +1 per correct position, capped at 2 for a round
- Predict the Crew consensus correctly: +2
- No points for the spotlight player's own answer

Primary winner: highest prediction score = “Knows the Crew Best”.

## Crew Memory
Store structured facts rather than free-form prose where possible:
- player preference
- selected player
- group consensus
- rank result
- confidence / agreement strength
- round number

Callback rule: never invent a personal fact. A callback may only reference a fact produced in the current game.

## Dynamic question engine
The AI should combine a stored fact with a new hypothetical. Examples:
- Most spontaneous → forced planning scenario
- Most frugal → forced spending scenario
- Most trusted → secret/leadership scenario
- Preferred travel partner → survival/road-trip scenario
- Most organized → chaos scenario

Goal: the game becomes increasingly specific to this exact group.

## Visual system
Photos are part of gameplay, not decoration.

### Standard reveals
Fast motion/card animation using uploaded portraits, names, votes and score. No generative delay.

### Hero AI reveals
Only 3–4 per game, selected after high-reaction questions or meaningful consensus. Examples:
- Desert island selection → chosen pair on cinematic island, others humorously left on a boat/dock.
- Most likely to become a millionaire → fictional premium business-magazine cover scene.
- Best travel partner → cinematic airport/adventure scene.
- Final Crew Poster → group scene based only on labels earned during the game.

Hero reveals should look like coherent cinematic scenes, not pasted head cutouts. Generate asynchronously so gameplay never waits on the image.

## Endgame
Show:
- 🏆 Knows the Crew Best
- 🎭 Most Unpredictable (others guessed them wrong most often)
- 🔮 Most Predictable (others guessed them correctly most often)
- 🤝 Most Chosen / Trusted (only if supported by actual game answers)
- one or two additional labels derived only from played questions

Finish with a premium AI Crew Poster and shareable result card.

## Prototype success criteria
Do not expand V1 unless a playtest shows:
1. New players understand the loop within 30 seconds without explanation.
2. First spontaneous laugh/debate happens within 2 minutes.
3. At least one callback gets a stronger reaction than its source question.
4. Players spend more time looking/talking at each other than reading instructions.
5. At least one player voluntarily asks for another round / another game.

## Build order
1. Curate question bank.
2. Run no-code simulated playtests.
3. Validate scoring and callback rules.
4. Prototype only the core loop.
5. Add standard visual reveals.
6. Add 3–4 asynchronous Hero AI reveals.
7. Add final Crew Poster.
8. Only after Friends V1 works: Couple mode and other audiences.

## Parked concept
World Takeover remains a separate future PlotTwist strategy/negotiation game and is not part of Know Your Crew V1.