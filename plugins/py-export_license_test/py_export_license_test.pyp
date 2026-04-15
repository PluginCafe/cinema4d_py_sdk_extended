"""
"""
import c4d

def main() -> bool:
    """Registers the plugin suite and handles licensing in the boot phase.
    """
    data: str = c4d.ExportLicenses()

if __name__ == "__main__":
    main()