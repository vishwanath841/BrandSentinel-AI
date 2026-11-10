import os
import math
from typing import Dict, Any, List, Tuple
from PIL import Image
import numpy as np

def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Convert hex color string like #1E3A8A or 1E3A8A to (R, G, B)."""
    hex_clean = hex_str.lstrip("#")
    if len(hex_clean) == 3:
        hex_clean = "".join([c * 2 for c in hex_clean])
    if len(hex_clean) != 6:
        return (0, 0, 0)
    try:
        return (int(hex_clean[0:2], 16), int(hex_clean[2:4], 16), int(hex_clean[4:6], 16))
    except ValueError:
        return (0, 0, 0)

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB integers to #RRGGBB."""
    return f"#{int(r):02X}{int(g):02X}{int(b):02X}"

def color_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
    """Compute Euclidean color distance in RGB space."""
    return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2)

def calculate_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance for WCAG contrast ratio."""
    def channel_lum(val: int) -> float:
        c = val / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    
    r, g, b = rgb
    return 0.2126 * channel_lum(r) + 0.7152 * channel_lum(g) + 0.0722 * channel_lum(b)

def calculate_contrast_ratio(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """Calculate WCAG contrast ratio between two colors (range 1:1 to 21:1)."""
    lum1 = calculate_luminance(rgb1)
    lum2 = calculate_luminance(rgb2)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)

def extract_dominant_colors(file_path: str, k: int = 5) -> List[Dict[str, Any]]:
    """Extract dominant colors and their percentages using OpenCV / NumPy KMeans or PIL fallback."""
    try:
        import cv2
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError(f"Could not read image with cv2: {file_path}")
        
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Resize for speed and low memory consumption (lightweight architecture)
        img_small = cv2.resize(img_rgb, (150, 150), interpolation=cv2.INTER_AREA)
        pixels = img_small.reshape(-1, 3).astype(np.float32)

        # OpenCV KMeans
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 15, 0.2)
        flags = cv2.KMEANS_PP_CENTERS
        compactness, labels, centers = cv2.kmeans(pixels, k, None, criteria, 5, flags)

        # Count frequencies
        label_counts = np.bincount(labels.flatten())
        total_pixels = len(labels.flatten())

        dominant_colors = []
        for i in range(len(centers)):
            r, g, b = centers[i]
            percentage = round((label_counts[i] / total_pixels) * 100, 1)
            hex_code = rgb_to_hex(r, g, b)
            dominant_colors.append({
                "hex": hex_code,
                "rgb": [int(r), int(g), int(b)],
                "percentage": percentage
            })

        # Sort by percentage descending
        dominant_colors.sort(key=lambda x: x["percentage"], reverse=True)
        return dominant_colors

    except Exception:
        # Fallback using PIL
        img = Image.open(file_path).convert("RGB")
        img_small = img.resize((100, 100))
        colors = img_small.getcolors(maxcolors=10000) or []
        if not colors:
            return [{"hex": "#333333", "rgb": [51, 51, 51], "percentage": 100.0}]
        
        colors.sort(key=lambda x: x[0], reverse=True)
        total = sum(c[0] for c in colors[:k])
        results = []
        for count, rgb in colors[:k]:
            pct = round((count / total) * 100, 1) if total > 0 else 0
            results.append({
                "hex": rgb_to_hex(*rgb),
                "rgb": list(rgb),
                "percentage": pct
            })
        return results

def inspect_visual_assets(
    image_path: str,
    brand_primary: str = "#1E3A8A",
    brand_secondary: str = "#0284C7",
    brand_accent: str = "#10B981",
    brand_background: str = "#FFFFFF",
    tolerance: float = 65.0
) -> Dict[str, Any]:
    """Perform visual inspection on image against approved brand visual guidelines."""
    dominant_colors = extract_dominant_colors(image_path, k=5)
    
    brand_palette = {
        "primary": hex_to_rgb(brand_primary),
        "secondary": hex_to_rgb(brand_secondary),
        "accent": hex_to_rgb(brand_accent),
        "background": hex_to_rgb(brand_background)
    }

    brand_hexes = {
        "primary": brand_primary.upper(),
        "secondary": brand_secondary.upper(),
        "accent": brand_accent.upper(),
        "background": brand_background.upper()
    }

    # Match each dominant color to closest brand color
    matches = []
    compliant_pixel_percentage = 0.0
    issues = []

    for dom in dominant_colors:
        dom_rgb = tuple(dom["rgb"])
        best_brand_role = None
        min_dist = 999999.0
        
        for role, b_rgb in brand_palette.items():
            dist = color_distance(dom_rgb, b_rgb)
            if dist < min_dist:
                min_dist = dist
                best_brand_role = role

        is_match = min_dist <= tolerance
        if is_match:
            compliant_pixel_percentage += dom["percentage"]

        matches.append({
            "dominant_hex": dom["hex"],
            "percentage": dom["percentage"],
            "closest_brand_role": best_brand_role,
            "closest_brand_hex": brand_hexes.get(best_brand_role, ""),
            "distance": round(min_dist, 1),
            "is_within_tolerance": is_match
        })

    # Check contrast between top 2 colors for accessibility
    contrast_ratio = 1.0
    contrast_passes_wcag = True
    if len(dominant_colors) >= 2:
        contrast_ratio = round(calculate_contrast_ratio(tuple(dominant_colors[0]["rgb"]), tuple(dominant_colors[1]["rgb"])), 2)
        contrast_passes_wcag = contrast_ratio >= 3.0 # WCAG threshold for graphics / UI elements

    # Check image metadata (resolution, dimensions)
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            format_name = img.format
    except Exception:
        width, height = (800, 600)
        format_name = "IMAGE"

    # Evaluate overall visual score (0-100)
    palette_alignment_score = min(100.0, round(compliant_pixel_percentage * 1.2, 1))
    contrast_score = 100.0 if contrast_passes_wcag else 60.0
    resolution_score = 100.0 if (width >= 600 and height >= 400) else 70.0

    visual_score = round(
        (palette_alignment_score * 0.6) + (contrast_score * 0.25) + (resolution_score * 0.15),
        1
    )

    # Generate specific issues if violations detected
    if compliant_pixel_percentage < 40.0:
        issues.append({
            "category": "VISUAL",
            "severity": "HIGH",
            "flagged_text": f"Dominant color {dominant_colors[0]['hex']} deviates from approved palette",
            "explanation": f"Only {compliant_pixel_percentage:.1f}% of image pixels match approved brand colors ({brand_primary}, {brand_secondary}, {brand_accent}).",
            "evidence": f"Brand Visual Guidelines: Colors must align with Primary ({brand_primary}) or Secondary ({brand_secondary}) within tolerance {tolerance}.",
            "suggested_revision": f"Adjust image color grading or background tint toward primary brand hue {brand_primary}.",
            "revision_rationale": "Maintains visual identity and recognizable brand presentation across all promotional assets."
        })

    if not contrast_passes_wcag and contrast_ratio < 3.0:
        issues.append({
            "category": "ACCESSIBILITY",
            "severity": "MEDIUM",
            "flagged_text": f"Low visual contrast ratio ({contrast_ratio}:1)",
            "explanation": f"The contrast ratio between key dominant colors is {contrast_ratio}:1, below the WCAG minimum threshold of 3.0:1 for visual components.",
            "evidence": "Brand Accessibility Standard: Minimum contrast ratio 4.5:1 for body copy and 3.0:1 for graphical elements.",
            "suggested_revision": f"Increase contrast between foreground elements and background using approved dark text {brand_hexes['background']}.",
            "revision_rationale": "Ensures visual readability for individuals with low vision or color impairment."
        })

    if width < 400 or height < 300:
        issues.append({
            "category": "VISUAL",
            "severity": "LOW",
            "flagged_text": f"Low image resolution ({width}x{height}px)",
            "explanation": "Image dimensions are below recommended resolution for high-DPI displays.",
            "evidence": "Brand Asset Guidelines: Minimum asset resolution 600x400px.",
            "suggested_revision": "Export assets at standard or @2x retina resolution.",
            "revision_rationale": "Prevents pixelation and maintains crisp brand presentation."
        })

    return {
        "visual_score": visual_score,
        "compliant_pixel_percentage": round(compliant_pixel_percentage, 1),
        "dominant_colors": dominant_colors,
        "palette_matches": matches,
        "contrast_ratio": contrast_ratio,
        "contrast_passes_wcag": contrast_passes_wcag,
        "dimensions": {"width": width, "height": height, "format": format_name},
        "issues": issues
    }

