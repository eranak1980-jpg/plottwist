# PlotTwist: Know Your Crew — Adaptive Game Engine V1

## Product promise
The game starts with good questions and becomes uniquely about this exact group as it learns from their choices.

## Core state
Store only game-relevant choices and outcomes:
- players
- subject per round
- prompt id/type
- subject answer
- each prediction
- correctness
- selections of other players
- score
- hero visual eligibility
- short factual memory statement

## Subject rotation
No player should be Subject twice before everyone has been Subject once, except a special callback that explicitly needs them. Over 12 rounds with 4 players, target 3 subject rounds each.

## Question mix
For 12 rounds:
- Know Me: 4
- Who in the Room: 4
- Dilemma: 1
- Predict the Crew: 1
- Adaptive Callback: 2
Rank Them excluded from default V1 playtest.

## Difficulty curve
Rounds 1–3: obvious mechanics, low emotional risk, funny fantasy.
Rounds 4–6: trust, lifestyle, travel, money, partnership.
Rounds 7–9: room-reading and stronger social choices.
Rounds 10–12: callbacks, contradictions, personalized final questions.

## Question selection score
Candidate question receives points for:
+ clear in one read
+ answerable in under 10 seconds
+ creates prediction disagreement
+ likely to trigger post-reveal conversation
+ new topic not recently used
+ fits number of players
+ supports a visual reveal

Reject / heavily penalize:
- trivia about the person
- yes/no with obvious answer
- sensitive health, religion, politics, sexuality, trauma, finances or protected-trait inference
- questions that invite cruelty or public humiliation
- repeated "who is best/worst" framing
- questions requiring a long explanation

## Factual memory objects
Example:
{
  "subject":"Eran",
  "topic":"windfall",
  "choice":"travel",
  "round":4,
  "confidence":"explicit_answer"
}

Example:
{
  "subject":"Daniel",
  "topic":"island_companion",
  "choice_player":"Yuval",
  "round":2,
  "confidence":"explicit_answer"
}

The engine may say: "Earlier Daniel chose Yuval for the island."
It must not convert that into: "Daniel is emotionally dependent on Yuval."

## Callback recipes
### Escalate
Earlier choice + harder version.
"Earlier you chose travel. Now the trip goes wrong — who do you call?"

### Contradict
Earlier group label + scenario that challenges it.
"You all predicted Maya would save the money. Now saving is forbidden — what does she do?"

### Combine
Two factual memories into one scenario.
"Eran chose Thailand, and Daniel was his 3AM call. The flight is cancelled at midnight — what does Eran do first?"

### Payoff
Bring an early answer back near the end.
"Round 2: Ron said he would take Noa to the island. Final round: who does Ron trust to choose the way home?"

### Group mirror
Use prediction pattern rather than personality claim.
"Three of you predicted the same answer for Yuval twice tonight. Will you agree again?"

## Callback constraints
- First callback no earlier than Round 6.
- At least 2 rounds between callbacks about same player.
- Quote/restate only information actually produced in this game.
- Callback must still be understandable if player forgot the earlier round.
- Never punish a player for inconsistency; inconsistency is framed as a fun Plot Twist.

## Scoring
Normal correct prediction: +1.
Final Round: +2.
Predict-the-Crew: +1 if player correctly predicts plurality winner.
No negative points in V1.

Ties: celebrate co-winners; no forced tiebreaker required. Optional one-question tiebreaker only if group taps "Break the tie".

## Visual trigger score
Hero visual candidate if:
- answer selects another player, OR
- scenario has a strong physical fantasy (island, trip, millionaire, company, rescue), AND
- no visual generated in previous 2 rounds, AND
- all depicted players have consented photos or avatar fallback.

## Final outcomes
Compute directly:
- Crew Champion: highest score.
- Hardest to Predict: lowest percentage of correct predictions by others on their Subject rounds (minimum 2 eligible rounds).
- Most Chosen: most selected player across positive/neutral Who-in-the-Room rounds.
- Biggest Plot Twist: Subject answer with lowest prediction match rate.

## UX invariant
At every point a first-time player should know the next action from one primary button / instruction. Never require host narration to progress.
