#!/usr/bin/env python3
"""
Meta Ray-Ban Glasses Photo Converter CLI
-----------------------------------------
Converts any image (PNG, JPG, WEBP, BMP, etc.) into authentic 3024x4032 
Ray-Ban Meta Smart Glasses photos with realistic optical EXIF metadata.

Usage:
  python3 cli.py input.png output.jpg
  python3 cli.py input.png -o output.jpg --fit blur --model wayfarer
  python3 cli.py ./my-folder/ --batch -o ./converted/ --fit cover
"""

import argparse
import base64
import datetime
import io
import os
import random
import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps
import piexif

TARGET_WIDTH = 3024
TARGET_HEIGHT = 4032

HARDWARE_PROFILES = {
    "wayfarer": {
        "make": "Meta",
        "model": "Ray-Ban Meta Smart Glasses",
        "software": "Meta View 174.0.0",
        "f_number": (22, 10),       # f/2.2
        "focal_length": (220, 100),  # 2.2 mm
        "focal_35mm": 18,
    },
    "headliner": {
        "make": "Meta",
        "model": "Ray-Ban Meta Smart Glasses (Headliner)",
        "software": "Meta View 174.0.0",
        "f_number": (22, 10),
        "focal_length": (220, 100),
        "focal_35mm": 18,
    },
    "skyler": {
        "make": "Meta",
        "model": "Ray-Ban Meta Smart Glasses (Skyler)",
        "software": "Meta View 174.0.0",
        "f_number": (22, 10),
        "focal_length": (220, 100),
        "focal_35mm": 18,
    },
    "meta-ai": {
        "make": "Meta AI",
        "model": "Ray-Ban Meta Smart Glasses 2",
        "software": "Meta View 174.0.0",
        "f_number": (22, 10),
        "focal_length": (220, 100),
        "focal_35mm": 18,
    },
    "stories": {
        "make": "Facebook",
        "model": "Ray-Ban Stories",
        "software": "Facebook View 120.0.0",
        "f_number": (24, 10),
        "focal_length": (240, 100),
        "focal_35mm": 20,
    }
}


def fit_cover(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Scale and center-crop image to exactly target dimensions."""
    src_w, src_h = img.size
    src_ratio = src_w / src_h
    target_ratio = target_w / target_h

    if src_ratio > target_ratio:
        # Source is wider: match height, crop width
        new_h = target_h
        new_w = int(src_w * (target_h / src_h))
    else:
        # Source is taller: match width, crop height
        new_w = target_w
        new_h = int(src_h * (target_w / src_w))

    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def fit_contain(img: Image.Image, target_w: int, target_h: int, bg_color=(10, 13, 20)) -> Image.Image:
    """Fit entire image inside target dimensions with matte background."""
    src_w, src_h = img.size
    ratio = min(target_w / src_w, target_h / src_h)
    new_w = int(src_w * ratio)
    new_h = int(src_h * ratio)

    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (target_w, target_h), bg_color)
    pos = ((target_w - new_w) // 2, (target_h - new_h) // 2)
    
    if resized.mode == "RGBA":
        canvas.paste(resized, pos, mask=resized.split()[3])
    else:
        canvas.paste(resized, pos)
    return canvas


def fit_blur(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Center image over an aesthetically blurred & zoomed backdrop of itself."""
    # 1. Background layer: cover & blur
    bg = fit_cover(img.convert("RGB"), target_w, target_h)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=55))
    
    # Darken background slightly for contrast
    dimmer = Image.new("RGB", (target_w, target_h), (0, 0, 0))
    bg = Image.blend(bg, dimmer, 0.25)

    # 2. Foreground layer: fit contain with margin
    margin = 80
    max_fg_w = target_w - (margin * 2)
    max_fg_h = target_h - (margin * 2)
    src_w, src_h = img.size
    ratio = min(max_fg_w / src_w, max_fg_h / src_h)
    new_w = int(src_w * ratio)
    new_h = int(src_h * ratio)

    fg = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    pos_x = (target_w - new_w) // 2
    pos_y = (target_h - new_h) // 2

    # Paste FG over BG
    if fg.mode == "RGBA":
        bg.paste(fg, (pos_x, pos_y), mask=fg.split()[3])
    else:
        bg.paste(fg, (pos_x, pos_y))
    return bg


def fit_stretch(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Direct stretch to target dimensions."""
    return img.convert("RGB").resize((target_w, target_h), Image.Resampling.LANCZOS)


def degrees_to_dms_rational(deg_float: float):
    """Convert float degrees into EXIF GPS rational triple."""
    abs_deg = abs(deg_float)
    deg = int(abs_deg)
    rem = (abs_deg - deg) * 60.0
    min_ = int(rem)
    sec = round((rem - min_) * 60.0, 4)
    sec_rational = (int(sec * 10000), 10000)
    return ((deg, 1), (min_, 1), sec_rational)


def build_exif_dict(profile_name="wayfarer", timestamp=None, gps_coords=None):
    """Construct authentic Ray-Ban Meta Smart Glasses EXIF dictionary."""
    prof = HARDWARE_PROFILES.get(profile_name, HARDWARE_PROFILES["wayfarer"])
    now = timestamp or datetime.datetime.now()
    dt_str = now.strftime("%Y:%m:%d %H:%M:%S")

    # Zeroth IFD (Image metadata)
    zeroth_ifd = {
        piexif.ImageIFD.Make: prof["make"].encode("utf-8"),
        piexif.ImageIFD.Model: prof["model"].encode("utf-8"),
        piexif.ImageIFD.Software: prof["software"].encode("utf-8"),
        piexif.ImageIFD.Orientation: 1,
        piexif.ImageIFD.XResolution: (72, 1),
        piexif.ImageIFD.YResolution: (72, 1),
        piexif.ImageIFD.ResolutionUnit: 2,  # Inches
        piexif.ImageIFD.DateTime: dt_str.encode("utf-8"),
    }

    # Exif IFD (Camera & lens metadata)
    iso_val = random.choice([50, 64, 80, 100, 125, 160, 200, 249])
    exif_ifd = {
        piexif.ExifIFD.ExifVersion: b"0232",
        piexif.ExifIFD.DateTimeOriginal: dt_str.encode("utf-8"),
        piexif.ExifIFD.DateTimeDigitized: dt_str.encode("utf-8"),
        piexif.ExifIFD.ColorSpace: 1,  # sRGB
        piexif.ExifIFD.PixelXDimension: TARGET_WIDTH,
        piexif.ExifIFD.PixelYDimension: TARGET_HEIGHT,
        piexif.ExifIFD.FNumber: prof["f_number"],
        piexif.ExifIFD.FocalLength: prof["focal_length"],
        piexif.ExifIFD.FocalLengthIn35mmFilm: prof["focal_35mm"],
        piexif.ExifIFD.ExposureProgram: 2,  # Normal program
        piexif.ExifIFD.ISOSpeedRatings: iso_val,
        piexif.ExifIFD.MeteringMode: 2,     # Center-weighted average
        piexif.ExifIFD.Flash: 0,            # Flash did not fire
        piexif.ExifIFD.WhiteBalance: 0,     # Auto white balance
        piexif.ExifIFD.SceneCaptureType: 0, # Standard
    }

    # GPS IFD
    gps_ifd = {}
    if gps_coords:
        try:
            lat, lon = gps_coords
            lat_ref = b"N" if lat >= 0 else b"S"
            lon_ref = b"E" if lon >= 0 else b"W"
            gps_ifd = {
                piexif.GPSIFD.GPSVersionID: (2, 3, 0, 0),
                piexif.GPSIFD.GPSLatitudeRef: lat_ref,
                piexif.GPSIFD.GPSLatitude: degrees_to_dms_rational(lat),
                piexif.GPSIFD.GPSLongitudeRef: lon_ref,
                piexif.GPSIFD.GPSLongitude: degrees_to_dms_rational(lon),
            }
        except Exception as e:
            print(f"Warning: Failed to encode GPS coordinates ({e}). Stripping GPS.")
            gps_ifd = {}

    return {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": gps_ifd, "1st": {}, "thumbnail": None}


def convert_image(
    input_path: Path,
    output_path: Path,
    fit_mode="cover",
    model="wayfarer",
    matte_color=(10, 13, 20),
    gps_coords=None,
    quality=95
):
    """Load image, transform, inject EXIF, and save as Ray-Ban Meta JPEG."""
    # 1. Load image and normalize orientation
    with Image.open(input_path) as raw_img:
        img = ImageOps.exif_transpose(raw_img)
        if img is None:
            img = raw_img.copy()
        
        # Ensure proper color space
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.mode else "RGB")

        # 2. Apply fit mode
        if fit_mode == "cover":
            # Handle RGBA flattening first
            if img.mode == "RGBA":
                bg = Image.new("RGB", img.size, matte_color)
                bg.paste(img, mask=img.split()[3])
                img = bg
            result_img = fit_cover(img.convert("RGB"), TARGET_WIDTH, TARGET_HEIGHT)
        elif fit_mode == "contain":
            result_img = fit_contain(img, TARGET_WIDTH, TARGET_HEIGHT, bg_color=matte_color)
        elif fit_mode == "blur":
            result_img = fit_blur(img, TARGET_WIDTH, TARGET_HEIGHT)
        elif fit_mode == "stretch":
            result_img = fit_stretch(img, TARGET_WIDTH, TARGET_HEIGHT)
        else:
            raise ValueError(f"Unknown fit mode: {fit_mode}")

    # 3. Build EXIF
    exif_dict = build_exif_dict(profile_name=model, gps_coords=gps_coords)
    exif_bytes = piexif.dump(exif_dict)

    # 4. Save with injected EXIF
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result_img.save(output_path, format="JPEG", exif=exif_bytes, quality=quality, optimize=True)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert photos to 3024x4032 with authentic Ray-Ban Meta Smart Glasses EXIF."
    )
    parser.add_argument("input", help="Input image file or directory (when using --batch)")
    parser.add_argument("-o", "--output", help="Output file path or destination directory")
    parser.add_argument(
        "--fit",
        choices=["cover", "contain", "blur", "stretch"],
        default="cover",
        help="Framing/Fit mode: cover (default), contain, blur, stretch",
    )
    parser.add_argument(
        "--model",
        choices=list(HARDWARE_PROFILES.keys()),
        default="wayfarer",
        help="Ray-Ban Meta hardware profile (default: wayfarer)",
    )
    parser.add_argument(
        "--spoof-gps",
        help="Optional latitude,longitude (e.g. '37.7749,-122.4194'). Default: GPS stripped.",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=95,
        help="JPEG export quality (1-100, default: 95)",
    )
    parser.add_argument(
        "--base64",
        action="store_true",
        help="Print Base64 representation to stdout instead of saving",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch process all images inside the input directory",
    )

    args = parser.parse_args()
    input_p = Path(args.input).resolve()

    gps_coords = None
    if args.spoof_gps:
        try:
            parts = [float(x.strip()) for x in args.spoof_gps.split(",")]
            if len(parts) == 2:
                gps_coords = (parts[0], parts[1])
        except Exception:
            print("Error: Invalid GPS format. Expected 'latitude,longitude'.", file=sys.stderr)
            sys.exit(1)

    if args.batch or input_p.is_dir():
        if not input_p.is_dir():
            print(f"Error: {input_p} is not a directory.", file=sys.stderr)
            sys.exit(1)

        out_dir = Path(args.output).resolve() if args.output else input_p / "converted_rayban"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".avif"}
        files = [f for f in input_p.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]
        
        if not files:
            print(f"No supported image files found in {input_p}")
            sys.exit(0)

        print(f"🕶️  Batch converting {len(files)} image(s) to Ray-Ban Meta {args.model.upper()}...")
        for idx, file in enumerate(files, 1):
            out_file = out_dir / f"{file.stem}_meta_3024x4032.jpg"
            convert_image(
                file,
                out_file,
                fit_mode=args.fit,
                model=args.model,
                gps_coords=gps_coords,
                quality=args.quality
            )
            print(f"  [{idx}/{len(files)}] ✅ {file.name} -> {out_file.name}")
        print(f"🎉 All done! Saved to: {out_dir}")
        return

    # Single File Process
    if not input_p.is_file():
        print(f"Error: File not found: {input_p}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        out_p = Path(args.output).resolve()
    else:
        out_p = input_p.parent / f"{input_p.stem}_meta_3024x4032.jpg"

    convert_image(
        input_p,
        out_p,
        fit_mode=args.fit,
        model=args.model,
        gps_coords=gps_coords,
        quality=args.quality
    )

    if args.base64:
        with open(out_p, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            print(b64)
    else:
        print(f"🕶️  Converted: {input_p.name} -> {out_p}")
        print(f"📐 Specs: 3024×4032 | Model: {HARDWARE_PROFILES[args.model]['model']} | Fit: {args.fit}")


if __name__ == "__main__":
    main()
