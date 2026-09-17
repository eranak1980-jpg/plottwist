# Know Your Crew — Internal Simulation 01

Purpose: stress-test clarity, pacing, scoring and callbacks before coding. Synthetic players only: Alex, Maya, Dan, Noa.

## Test assumptions
- 4 players
- 12 rounds
- One spotlight player per Know Me / Who in Room round
- Everyone except spotlight predicts
- +1 correct prediction
- Callback facts may only use results already generated in this simulation

## Simulated run

### R1 — Warm / Know Me — Alex
Question: Free flight leaves in three hours. What does Alex do?
Alex answer: invites someone from the room.
Predictions: Maya correct, Dan correct, Noa says packs alone.
Result: immediate simple reveal; 2 points distributed.
Stored fact: Alex = socially spontaneous.

### R2 — Who in Room — Maya
Question: Who would Maya call first if something went badly wrong at 3 AM?
Maya chooses Noa.
Predictions: Alex→Noa correct, Dan→Alex, Noa→Noa correct.
Reaction potential: Dan can naturally ask “Why Noa?” without game instruction.
Stored fact: Maya trusts Noa in crisis.

### R3 — Dilemma — Dan
Question: Unlimited travel/basic hotels OR luxury hotels/two trips a year?
Dan chooses unlimited travel.
Predictions: 2/3 correct.
Stored fact: Dan prioritizes travel frequency over luxury.

### R4 — Predict the Crew
Question: Who will the room vote best at organizing a group vacation?
Consensus result: Noa.
Players predicting consensus: Alex and Maya correct.
Stored fact: group sees Noa as organizer.

### R5 — Who in Room — Noa
Question: Who would Noa choose for a month-long trip with no itinerary?
Noa chooses Alex.
Only Maya predicts Alex.
Stored fact: Noa chooses Alex for spontaneous travel.

### R6 — Rank Them — Alex
Question: Rank others from calmest to most chaotic in a travel disaster.
Alex: Noa → Maya → Dan.
Predictions scored by exact positions, cap 2.
Observation: ranking is understandable but UI must make drag/drop unnecessary; use three tap slots or sequential choice.
Stored fact: Alex sees Noa as calmest and Dan as most chaotic.

### R7 — Callback — Noa
Source facts: R4 Noa = organizer; R5 Noa chose Alex for spontaneous trip.
Question: Everyone trusts Noa to organize the trip — but Alex convinces Noa to leave tomorrow with nothing booked. What is the FIRST thing Noa secretly insists on arranging: hotel / flights home / budget / nothing at all?
Noa: hotel.
Predictions split.
Why callback works: references two facts from this exact session and creates tension between them.

### R8 — Know Me — Maya
Question: Maya suddenly becomes famous. What is she most likely famous for?
Answer: viral accident.
Only Dan predicts it.
Stored fact: Maya sees herself as accidental/chaotic fame rather than planned public success.

### R9 — Callback — Dan
Source fact: R3 Dan chooses lots of travel over luxury.
Question: Dan gets a free luxury suite tonight, but using it means cancelling a spontaneous weekend flight. What does he keep?
Dan keeps flight.
3/3 predict correctly.
Result: strong “we know you now” moment; callback is easy because source fact was memorable.

### R10 — Stronger Who in Room — Alex
Question: If Alex had amazing news and could tell only one person here for 24 hours, who hears it?
Alex chooses Maya.
Predictions split.
Stored fact: Alex chooses Maya for first good-news call.

### R11 — Callback / contradiction test — Alex
Source facts: R1 Alex socially spontaneous; R10 Alex chooses Maya for important news.
Question: Alex is offered a job abroad tonight and must decide before morning. Who influences the decision most: Maya / whole group / nobody / asks for more time?
Alex chooses Maya.
Potential reaction: reinforces a relationship discovered during play without inventing it.

### R12 — Double-points Predict the Crew
Question: Based on everything tonight, who will the room vote hardest to predict?
Synthetic consensus: Maya.
Final scores resolve winner.

## Findings

### What passed
- Core rule remains explainable in one sentence.
- Every action has a reason: predict correctly to score.
- Spotlight player does not need to perform or improvise a speech.
- Conversation can happen naturally after reveal; it is not required to advance the game.
- Callbacks materially improve specificity by R7–R11.
- Game can work without generative AI during every round.

### Risks found
1. Rank Them is mechanically heavier than other rounds. Keep to maximum 2 per game and use tap-based ordering.
2. Predict the Crew can confuse “my own answer” vs “what I think the room will answer.” UI must explicitly say: FIRST vote privately, THEN predict the group result, or simplify to a single consensus-vote round in V1.
3. Too many trust/relationship questions can feel like a friendship ranking. Cap strong Who-in-Room questions and mix with scenarios/dilemmas.
4. A callback that merely repeats the source fact is boring. It must create a new scenario, inversion or trade-off.
5. AI images cannot block Next. Standard reveal must happen instantly; Hero visual arrives asynchronously and can appear as a bonus reveal when ready.

## V1 adjustments after simulation
- 12 rounds default, not 15.
- Composition target: 3 Know Me, 3 Who in Room, 2 Dilemma, 1 Rank Them, 1 Predict Crew, 2 callbacks.
- First callback no earlier than round 6.
- Hero visuals: maximum 3 during gameplay + final poster.
- Never require spoken justification to proceed.
- Reveal screen may show a short optional prompt such as “Why them? 👀” but Next is always available.

## Go / no-go for prototype
Mechanics pass internal simulation. Next validation must be a human no-code playtest. Do not rebuild the production app until humans demonstrate: fast comprehension, spontaneous reaction, and desire for another round.