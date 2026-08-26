# PlotTwist MVP — v2

A zero-dependency Python web MVP for a personalized real-world AI party game.

## What works
- Create a personalized game using group name, relationship, location, inside joke, tone and intensity.
- Join from multiple phones using a 5-character room code.
- Browser session persists after refresh.
- Secret roles, secrets and objectives are generated per player.
- Four Game Master rounds with a personalized story.
- Secret voting and final vote results.
- Responsive mobile-first UI.

> The current "AI" story engine is intentionally local/deterministic-ish so the MVP can run with no API key or cost. The next layer can replace `assign_roles()` / `round_prompt()` with a real LLM call.

## Run
Requires Python 3.10+ only.

```bash
python app.py
```

Then open:

```text
http://localhost:5000
```

To test with multiple players on one computer, use separate/private browser windows. On a local Wi-Fi network, other phones can use your computer's LAN IP with port `5000` if your firewall allows it.

## Suggested next build step
1. Add OpenAI/other LLM generation behind a feature flag.
2. Generate a coherent case bible once per game (culprit, motive, clue graph, secrets).
3. Let the Game Master adapt later clues to player choices.
4. Add host safety controls and content rating.
5. Deploy to a simple web host and run 20 real group playtests.


## v3 — Optional real AI engine

The app now supports two engines:
- **Local**: works immediately, no API key or external service.
- **AI**: if `OPENAI_API_KEY` is set, a fresh coherent Hebrew mystery is generated for the exact group. If generation fails, the game automatically falls back to the local engine.

### Enable AI
macOS/Linux:
```bash
export OPENAI_API_KEY="your-key"
python app.py
```
Windows PowerShell:
```powershell
$env:OPENAI_API_KEY="your-key"
python app.py
```
Optionally set `OPENAI_MODEL`; default is `gpt-4.1-mini`.

### What v3 adds
- AI-generated title, victim, roles, secrets, objectives, and four coherent rounds.
- Safe local fallback so a broken/missing AI connection never blocks a game.
- The API reports whether the current case uses `ai` or `local` engine.
- No API key is bundled in this project.

## v4 — Live party experience

v4 adds the first "real product" layer:

- Join-by-QR generated locally by the app.
- Per-round countdown timer stored on the server.
- A new private clue for each player from round 2 onward.
- Live Game Master reactions: the host can summarize what just happened in the room and trigger a new twist. With an OpenAI key, the reaction is AI-generated; without one, the local engine still works.
- Live twists are broadcast to every player's screen on the next refresh.
- Safer fallback behavior: no AI dependency can prevent a game from running.

### Playing on multiple phones on the same Wi‑Fi
Run the server on the host computer and open it using that computer's LAN IP (for example `http://192.168.1.25:5000`) rather than `localhost`. The QR code uses the address that is currently open in the browser, so guests can scan it from their phones.

Install requirements:
```bash
pip install -r requirements.txt
python app.py
```

## v5 — Ready for first real playtest

- Three game modes at creation: Murder Mystery, Heist, Secret Night.
- A polished default Murder Mystery flow, so the first test is not dependent on AI quality.
- 20-second "How to play" onboarding before the host starts.
- Lightweight sound cues generated in-browser (no copyrighted audio files).
- Existing v4 features remain: QR join, private clues, timers, live GM reactions, voting and reveal.

The recommended first test is 4–8 adults, Murder Mystery, 45–60 minutes.

## v6 — Release Candidate / public-hosting ready

Adds:
- Hosting-friendly `PORT`, `DATABASE_PATH`, and optional `APP_BASE_URL`.
- `/health` endpoint for platform health checks.
- QR codes can use the public app URL.
- Security/no-cache headers for API responses.
- Post-game feedback: fun, clarity, replay intent, and a note.
- `.gitignore`, `Procfile`, and `start.sh`.

### Environment variables
- `PORT` — usually injected by the host.
- `DATABASE_PATH` — path to persistent SQLite storage if supported.
- `APP_BASE_URL` — e.g. `https://your-app.example.com`.
- `OPENAI_API_KEY` — optional; local engine still works without it.
- `OPENAI_MODEL` — optional model override.

### Hosting note
For a short private playtest, ephemeral SQLite is acceptable. For a broader beta, use persistent storage or move the data layer to managed SQL.
