import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

COMPETITION = "jigsaw-toxic-comment-classification-challenge"

def run_kaggle():
    exe = shutil.which("kaggle")
    if exe:
        cmd = [exe, "competitions", "download", "-c", COMPETITION, "-p", str(RAW)]
    else:
        cmd = [sys.executable, "-m", "kaggle", "competitions", "download", "-c", COMPETITION, "-p", str(RAW)]
    print("Downloading official Jigsaw competition data...")
    subprocess.run(cmd, check=True)

def main():
    target = RAW / "train.csv"
    if target.exists():
        print(f"Already available: {target}")
        return

    try:
        run_kaggle()
    except Exception as exc:
        print("\nKaggle download failed.")
        print("Make sure you have:")
        print("1) accepted the Jigsaw competition rules on Kaggle")
        print("2) configured Kaggle API credentials")
        print("3) installed the Kaggle CLI: pip install kaggle")
        print(f"\nOriginal error: {exc}")
        raise SystemExit(1)

    zips = list(RAW.glob("*.zip"))
    if not zips:
        raise SystemExit("Kaggle command completed but no ZIP file was found.")

    for zip_path in zips:
        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()
            train_name = next((n for n in names if n.endswith("train.csv")), None)
            if train_name:
                print(f"Extracting {train_name}...")
                with z.open(train_name) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                print(f"Ready: {target}")
                return

    raise SystemExit("train.csv was not found inside downloaded ZIP files.")

if __name__ == "__main__":
    main()
