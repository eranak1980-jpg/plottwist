"""Compare the MIPO image providers on identical inputs, outside the live game."""
import argparse
import base64
import json
import os
import secrets
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kyc_visuals import QUALITY, SIZE, _file, decode_image, prompt_for


MODELS = {
    "gpt-image-2.5-flare": {},
    "gpt-image-2.6-flare": {"complexity": "low"},
    "gpt-image-2.6-sunburst": {"complexity": "low"},
}
SCENES = [
    ("Everyone is ready to leave. What is holding Alex up?", "Looking for their keys"),
    ("A group photo turns out badly. What does Alex do?", "Ask for one more photo"),
    ("Alex is hosting tonight. What do they ask friends to bring?", "Something to eat"),
]
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path, help="Synthetic or consented reference portrait")
    parser.add_argument("output", type=Path, help="New directory for blind samples and timings")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    mime = MIME.get(args.reference.suffix.lower())
    if not mime:
        parser.error("the reference must be a JPEG, PNG, or WebP")
    encoded = base64.b64encode(args.reference.read_bytes()).decode("ascii")
    reference = _file(f"data:{mime};base64,{encoded}", 0)
    if args.dry_run:
        print(f"{len(SCENES) * len(MODELS)} planned requests at {SIZE}, quality={QUALITY}")
        return
    if not os.getenv("OPENAI_API_KEY", "").strip():
        parser.error("configure OPENAI_API_KEY in the benchmark environment")

    from openai import OpenAI

    args.output.mkdir(parents=True, exist_ok=False)
    failures = 0
    with OpenAI(timeout=60, max_retries=0) as client, (args.output / "timings.jsonl").open("w") as log:
        for scene, (question, answer) in enumerate(SCENES, 1):
            prompt = prompt_for(question, answer, ["Alex"], "Alex", "", False, None)
            models = list(MODELS.items())
            secrets.SystemRandom().shuffle(models)
            for sample, (model, settings) in enumerate(models, 1):
                filename = f"scene-{scene}-sample-{sample}.jpg"
                row = {"scene": scene, "sample": filename, "model": model, **settings}
                started = time.monotonic()
                try:
                    result = client.images.edit(
                        model=model, image=[reference], prompt=prompt, size=SIZE, quality=QUALITY,
                        output_format="jpeg", output_compression=72, n=1, extra_body=settings,
                    )
                    row["api_seconds"] = round(time.monotonic() - started, 3)
                    _, image = decode_image("data:image/jpeg;base64," + result.data[0].b64_json)
                    (args.output / filename).write_bytes(image)
                    row["bytes"] = len(image)
                    if result.usage:
                        row["usage"] = result.usage.model_dump(exclude_none=True)
                except Exception as exc:
                    failures += 1
                    row["error"] = type(exc).__name__
                    row["status"] = getattr(exc, "status_code", None)
                    row["code"] = getattr(exc, "code", None)
                    row["param"] = getattr(exc, "param", None)
                log.write(json.dumps(row) + "\n")
                log.flush()
    print(f"{len(SCENES) * len(MODELS) - failures} images saved. {failures} failed requests.")
    sys.exit(bool(failures))


if __name__ == "__main__":
    main()
