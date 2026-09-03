# 🕶️ Ray-Ban Meta Smart Glasses — Photo Studio & Converter Pro

A high-performance web studio and CLI suite to convert any photo (**PNG, JPG, WEBP, AVIF, BMP**) into authentic **3024 × 4032** images with realistic **Ray-Ban Meta Smart Glasses (Gen 2) & Meta AI** camera EXIF metadata.

Styled in the sleek **Flow NextGen** design system (Obsidian slate `#090d16`, glassmorphic cards, and Juicy Orange `#f97316` accents).

---

## ⚡ Highlights & Key Features

| Feature | Description |
| :--- | :--- |
| **All Image Formats** | Full support for **PNG (transparent alpha with matte/bokeh auto-fill)**, **JPG/JPEG**, **WEBP**, **AVIF**, and **BMP**. |
| **Direct Clipboard Paste** | Press `Cmd+V` / `Ctrl+V` anywhere on the page to paste images directly from clipboard. |
| **Batch Queue & ZIP** | Process 1 or 100+ images simultaneously. Bulk convert and download all as a single `.zip` archive. |
| **4 Smart Framing Modes** | • **Cover**: Fills 3:4 portrait without stretching.<br>• **Bokeh**: Creates an aesthetic blurred background from the original image (ideal for landscape/square).<br>• **Matte (Contain)**: Letterboxes/pillarboxes cleanly inside 3024×4032.<br>• **Stretch**: Direct dimension rescale. |
| **Hardware Profiles** | • *Ray-Ban Meta Gen 2 (Wayfarer)*<br>• *Ray-Ban Meta Gen 2 (Headliner)*<br>• *Ray-Ban Meta Gen 2 (Skyler)*<br>• *Meta AI Smart Glasses 2*<br>• *Ray-Ban Stories (Gen 1)* |
| **Realistic Optics EXIF** | Injects `f/2.2` aperture, `2.2mm` focal length (18mm 35mm equiv), `sRGB`, `Auto White Balance`, and `ExifVersion 0232`. |
| **Privacy & Geotagging** | Default: Complete GPS/device serial scrub. Optional: Spoof location coordinates (SF, NYC, London, Tokyo, Chennai). |
| **Multi-Channel Export** | • **⚡ 1-Click All-in-One**: Convert + Copy Base64 + Auto-Save.<br>• **📋 Copy Image**: Writes directly to OS clipboard (`ClipboardItem`) to paste in Twitter/Discord/Flow.<br>• **🔤 Copy Base64**: Pure Base64 string for API calls.<br>• **💾 Mobile Share Sheet**: Instant save to iOS Camera Roll / Android Gallery. |
| **100% Client-Side** | Zero backend servers, zero uploads. 100% private in-browser execution via HTML5 Canvas + `piexifjs`. |

---

## 🚀 Quick Start (Web App)

Run the included local preview server:

```bash
cd /home/haiva/custom-tools/meta-rayban-converter
python3 serve.py
```
Open **`http://localhost:8088`** in any browser.

---

## 💻 Python CLI Tool (`cli.py`)

For terminal automation, scripting, and batch rendering pipelines:

### 1. Single File Conversion
```bash
# Convert PNG to Ray-Ban Meta JPG (Cover mode)
python3 cli.py input.png output.jpg

# Convert with aesthetic Bokeh Blur background
python3 cli.py landscape.png -o output.jpg --fit blur --model wayfarer

# Output raw Base64 string to stdout
python3 cli.py photo.jpg --base64
```

### 2. Batch Processing a Directory
```bash
python3 cli.py ./my-photos/ --batch -o ./converted-meta/ --fit cover --model wayfarer
```

### 3. CLI Arguments
- `input`: Path to input image file or directory.
- `-o, --output`: Target output file or folder.
- `--fit`: `cover` (default), `blur`, `contain`, `stretch`.
- `--model`: `wayfarer` (default), `headliner`, `skyler`, `meta-ai`, `stories`.
- `--spoof-gps`: Optional `latitude,longitude` (e.g. `37.7749,-122.4194`).
- `--quality`: JPEG compression quality (1-100, default: `95`).
- `--base64`: Print Base64 string directly.

---

## 🛠️ Architecture & Technologies

- **Frontend**: HTML5, Vanilla ES6+, CSS Grid/Flexbox, Plus Jakarta Sans & JetBrains Mono fonts.
- **EXIF Engine**: `piexifjs` for binary JPEG APP1 segment injection.
- **Archive Engine**: `jszip` for client-side multi-file ZIP generation.
- **CLI Engine**: Python 3, `Pillow` (PIL), and `piexif`.
- **Zero Build Step**: No `npm install` or bundlers needed. Pure plug-and-play.
