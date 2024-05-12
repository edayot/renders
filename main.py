import os

def main(release: str):
    print(f"Release {release}!")




if __name__ == "__main__":
    release = os.getenv("MC_VERSION", "1.20.6")
    main(release)