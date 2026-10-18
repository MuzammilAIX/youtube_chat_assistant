
from pathlib import Path
from faster_whisper import WhisperModel

# Automatically find an MP3 in the project root
audio_files = list(Path(".").glob("*.mp3"))

if not audio_files:
    raise FileNotFoundError(
        "No MP3 file found in the current project folder."
    )

audio_path = audio_files[0]
print(f"Audio file: {audio_path.name}")
print("Loading Whisper model...")

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8",
)

print("Transcribing audio. Please wait...")

segments, info = model.transcribe(
    str(audio_path),
    beam_size=5,
    vad_filter=True,
)

lines = []

for segment in segments:
    line = (
        f"[{segment.start:.2f}s - {segment.end:.2f}s] "
        f"{segment.text.strip()}"
    )
    lines.append(line)
    print(line)

Path("transcript.txt").write_text(
    "\n".join(lines),
    encoding="utf-8",
)

print("\nTranscription completed!")
print(f"Detected language: {info.language}")
print(f"Saved transcript: {Path('transcript.txt').resolve()}")
