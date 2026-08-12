"""Assemble a slide plan into PDF + image-PPTX + editable-PPTX.

- PDF and image-PPTX consume the pixel-perfect PNGs from deck_layouts (identical
  to each other by construction).
- editable-PPTX is a NATIVE python-pptx build (real text/shapes/pictures) reading
  the same slide plan + theme; it is close to, not pixel-identical with, the image
  outputs, and its text is editable (fonts depend on the viewer's machine).
"""
import os, tempfile
import pymupdf
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

import theme
import deck_layouts as L

LW, LH = 1280, 720
SLIDE_IN_W, SLIDE_IN_H = 13.333, 7.5


def IX(u):
    return Inches(u / LW * SLIDE_IN_W)


def IY(u):
    return Inches(u / LH * SLIDE_IN_H)


def FS(u):
    return Pt(u * 0.75)  # logical (1280-space) size -> PowerPoint points


def C(hex_str):
    return RGBColor(*theme.rgb(hex_str))


# ---------- pixel-perfect PNG rendering ----------
def render_pngs(plan, outdir, quality=88):
    """Render each slide to a JPEG (small, email-friendly; text stays crisp at 2x)."""
    os.makedirs(outdir, exist_ok=True)
    paths = []
    for i, rec in enumerate(plan):
        img = L.render_slide(rec)
        p = os.path.join(outdir, f"slide_{i + 1:02d}.jpg")
        img.save(p, format="JPEG", quality=quality, optimize=True, progressive=True)
        paths.append(p)
    return paths


# ---------- PDF (pymupdf) ----------
def build_pdf(png_paths, out_path):
    doc = pymupdf.open()
    for p in png_paths:
        page = doc.new_page(width=LW, height=LH)
        page.insert_image(pymupdf.Rect(0, 0, LW, LH), filename=p)
    doc.save(out_path, deflate=True)
    doc.close()


# ---------- image-slide PPTX ----------
def build_image_pptx(png_paths, out_path):
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_IN_W)
    prs.slide_height = Inches(SLIDE_IN_H)
    blank = prs.slide_layouts[6]
    for p in png_paths:
        slide = prs.slides.add_slide(blank)
        slide.shapes.add_picture(p, 0, 0, width=prs.slide_width, height=prs.slide_height)
    prs.save(out_path)


# ---------- native editable PPTX ----------
def _bg(slide, hex_str):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = C(hex_str)


def _rect(slide, x, y, w, h, hex_str):
    from pptx.enum.shapes import MSO_SHAPE
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, IX(x), IY(y), IX(w), IY(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = C(hex_str)
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def _cropped(photo_path, wu, hu, tmpdir, tag):
    """Crop a source photo to the box aspect and return a temp PNG path."""
    if not photo_path or not os.path.exists(photo_path):
        img = L.placeholder(int(wu * 2), int(hu * 2), theme.BRAND_2)
    else:
        img = L.cover_crop(L.load_photo(photo_path), int(wu * 2), int(hu * 2))
    p = os.path.join(tmpdir, f"crop_{tag}.jpg")
    img.save(p, format="JPEG", quality=88, optimize=True, progressive=True)
    return p


def _text(slide, x, y, w, h, paras, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(IX(x), IY(y), IX(w), IY(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, (txt, fname, size, hexc, bold, spacing) in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.space_before = Pt(0); para.space_after = Pt(spacing)
        run = para.add_run(); run.text = txt
        run.font.name = fname; run.font.size = FS(size)
        run.font.bold = bold; run.font.color.rgb = C(hexc)
    return tb


SERIF_N = "Palatino Linotype"
SANS_N = "Segoe UI"
M = 74  # logical margin (~0.058*1280)


def _slide_native(prs, rec, tmpdir, idx):
    blank = prs.slide_layouts[6]
    s = prs.slides.add_slide(blank)
    lay = rec["layout"]

    if lay == "cover":
        s.shapes.add_picture(_cropped(rec.get("image"), LW, LH, tmpdir, f"cov{idx}"), 0, 0,
                             width=prs.slide_width, height=prs.slide_height)
        _rect(s, 0, LH * 0.55, LW, LH * 0.45, "#0a1520").fill.fore_color.rgb  # scrim-ish
        _text(s, M, LH * 0.60, LW * 0.7, LH * 0.32, [
            (rec["kicker"].upper(), SANS_N, 13, theme.GOLD, True, 8),
            (rec["title"], SERIF_N, 60, "#ffffff", False, 6),
            (rec.get("caption", ""), SANS_N, 16, "#eef2f6", False, 0),
        ])
    elif lay == "overview":
        _bg(s, theme.PAPER)
        _text(s, M, LH * 0.12, LW * 0.5, LH * 0.3,
              [(rec["headline"], SERIF_N, 46, theme.INK, False, 0)])
        _text(s, LW * 0.66, LH * 0.13, LW * 0.28, LH * 0.2,
              [(rec["caption"], SANS_N, 15, theme.INK_SOFT, False, 0)])
        thumbs = rec.get("thumbs", [])[:4]
        if thumbs:
            n = len(thumbs); gap = LW * 0.02
            avail = LW - 2 * M; tw = (avail - gap * (n - 1)) / n; th = LH * 0.34
            ty = LH - LH * 0.12 - th
            for i, p in enumerate(thumbs):
                tx = M + i * (tw + gap)
                s.shapes.add_picture(_cropped(p, tw, th, tmpdir, f"ov{idx}_{i}"),
                                     IX(tx), IY(ty), IX(tw), IY(th))
    elif lay == "feature-panel":
        pw = LW * 0.62
        s.shapes.add_picture(_cropped(rec.get("image"), LW - pw, LH, tmpdir, f"fp{idx}"),
                             IX(pw), 0, IX(LW - pw), prs.slide_height)
        _rect(s, 0, 0, pw, LH, theme.BRAND_2)
        _text(s, M, LH * 0.30, pw - 2 * M, LH * 0.5, [
            (rec.get("eyebrow", "").upper(), SANS_N, 13, "#e9c983", True, 10),
            (rec["headline"], SERIF_N, 44, "#ffffff", False, 8),
            (rec.get("caption", ""), SANS_N, 15, "#e8edf2", False, 0),
        ], anchor=MSO_ANCHOR.MIDDLE)
    elif lay == "feature-split":
        s.shapes.add_picture(_cropped(rec.get("image"), LW / 2, LH, tmpdir, f"fs{idx}"),
                             0, 0, IX(LW / 2), prs.slide_height)
        _bg(s, theme.PAPER)
        x = LW / 2 + LW * 0.06
        _rect(s, x, LH * 0.30, LW * 0.045, 4, theme.GOLD)
        _text(s, x, LH * 0.32, LW - M - x, LH * 0.5, [
            (rec.get("eyebrow", "").upper(), SANS_N, 13, theme.GOLD, True, 10),
            (rec["headline"], SERIF_N, 42, theme.INK, False, 8),
            (rec.get("caption", ""), SANS_N, 15, theme.INK_SOFT, False, 0),
        ])
    elif lay == "feature-framed":
        _bg(s, theme.PAPER)
        fx = LW * 0.57; fy = LH * 0.16
        fw = LW - M - fx; fh = LH - 2 * fy
        s.shapes.add_picture(_cropped(rec.get("image"), fw, fh, tmpdir, f"ff{idx}"),
                             IX(fx), IY(fy), IX(fw), IY(fh))
        _rect(s, M, LH * 0.34, LW * 0.045, 4, theme.GOLD)
        _text(s, M, LH * 0.36, LW * 0.42, LH * 0.4, [
            (rec.get("eyebrow", "").upper(), SANS_N, 13, theme.GOLD, True, 10),
            (rec["headline"], SERIF_N, 44, theme.INK, False, 8),
            (rec.get("caption", ""), SANS_N, 15, theme.INK_SOFT, False, 0),
        ])
    elif lay == "closing":
        _bg(s, theme.PAPER)
        y = LH * 0.32
        logo = L.LOGO_LIGHT
        if os.path.exists(logo):
            from PIL import Image as PImage
            im = PImage.open(logo); lh = LH * 0.075; lw = im.width * lh / im.height
            s.shapes.add_picture(logo, IX(M), IY(y), IX(lw), IY(lh)); y += lh + 34
        _rect(s, M, y, LW * 0.045, 4, theme.GOLD); y += 30
        _text(s, M, y, LW * 0.7, LH * 0.3, [
            (rec["title"], SERIF_N, 48, theme.INK, False, 8),
            (rec.get("caption", ""), SANS_N, 15.5, theme.INK_SOFT, False, 0),
        ])
    return s


def build_editable_pptx(plan, out_path, tmpdir):
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_IN_W)
    prs.slide_height = Inches(SLIDE_IN_H)
    for i, rec in enumerate(plan):
        _slide_native(prs, rec, tmpdir, i)
    prs.save(out_path)


# ---------- orchestration ----------
def generate(plan, slug, title, distroot):
    outdir = os.path.join(distroot, slug)
    png_dir = os.path.join(outdir, "slides")
    os.makedirs(png_dir, exist_ok=True)
    pngs = render_pngs(plan, png_dir)

    pdf = os.path.join(outdir, f"{slug}.pdf")
    pptx_img = os.path.join(outdir, f"{slug}.pptx")
    pptx_edit = os.path.join(outdir, f"{slug}-editable.pptx")
    build_pdf(pngs, pdf)
    build_image_pptx(pngs, pptx_img)
    with tempfile.TemporaryDirectory() as td:
        build_editable_pptx(plan, pptx_edit, td)
    return {"pdf": pdf, "pptx": pptx_img, "pptx_editable": pptx_edit, "slides": pngs}
