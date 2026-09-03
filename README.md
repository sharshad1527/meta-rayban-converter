# Ray-Ban Meta Photo Converter

A client-side web tool and CLI to convert photos (PNG, JPG, WEBP, AVIF) into 3024×4032 portrait images with authentic Ray-Ban Meta camera metadata.

Everything runs locally in the browser or terminal. No files are uploaded to any server.

---

## Features

- **Format support:** Works with PNG (transparent alpha handled cleanly), JPG/JPEG, WEBP, and AVIF.
- **Framing modes:**
  - `Crop to Fill`: Scales and center-crops into a 3:4 portrait (3024×4032).
  - `Blur Fill`: Centers the photo over an aesthetically blurred version of the background (useful for landscape or square shots).
  - `Fit`: Centers the original photo inside the frame with dark letterboxing.
- **Hardware profiles:**
  - Ray-Ban Meta Gen 2 (Wayfarer, Headliner, Skyler)
  - Ray-Ban Stories (Gen 1)
- **Camera EXIF tags:** Injects `Make: Meta`, `Model: Ray-Ban Meta Smart Glasses`, `f/2.2` aperture, `2.2mm` focal length (18mm equivalent), `sRGB`, and `Meta View` software tags while stripping GPS coordinates.
- **Quick actions:**
  - Convert & Download (single tap)
  - Copy Base64 string directly
  - Copy Image raster to clipboard (for pasting straight into Discord, Slack, or web apps)

---

## Web App

Start the local server:

```bash
python3 serve.py
```

Open `http://localhost:8088` in your browser.

---

## CLI Usage

You can also run batch or single conversions from the terminal:

```bash
# Convert a single PNG using blur fill
python3 cli.py input.png -o output.jpg --fit blur --model wayfarer

# Batch convert an entire folder
python3 cli.py ./photos/ --batch -o ./converted/ --fit cover

# Output pure Base64 to stdout
python3 cli.py input.png --base64
```
