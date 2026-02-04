import os
import glob

base_dir = "frontend/public/reports"
files = glob.glob(os.path.join(base_dir, "**/*.pdf"), recursive=True)

print(f"Deleting {len(files)} fake PDF reports...")
for f in files:
    try:
        os.remove(f)
        print(f"Deleted: {f}")
    except Exception as e:
        print(f"Error deleting {f}: {e}")

print("Clean up complete.")
