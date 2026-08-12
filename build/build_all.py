"""Run the full catalogue build pipeline in order.

    python build/build_all.py

Steps:
  parse.py   South_India_Catalogue.md            -> build/catalogue.json
  images.py  slides/*.jpg (per SPEC)             -> build/images.json   (needs Pillow)
  logo.py    slides/jpuKa.jpg                     -> build/logo.json     (needs Pillow)
  build.py   template.html + the three JSON files -> exploreain-catalogue.html
"""
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))

for step in ["parse.py", "images.py", "logo.py", "build.py"]:
    print("\n=== " + step + " ===")
    subprocess.run([sys.executable, os.path.join(HERE, step)], check=True)

print("\nBuild complete.")
