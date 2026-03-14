#!/usr/bin/env python3
"""Cookie Export Helper — extracts cookies from your browser and saves them to .env.

Usage:
    1. Make sure you are logged into X/Instagram/LinkedIn in your browser
    2. Run: python3 jarvis/tools/export_cookies.py
    3. Follow the prompts — it will open a REAL Chrome window, load the site,
       and grab your cookies (Google won't block this)
"""

import asyncio
import base64
import json
import os
import sys

try:
    import undetected_chromedriver as uc
except ImportError:
    print(
        "❌ undetected-chromedriver is not installed.\n"
        "   Run: pip install undetected-chromedriver selenium"
    )
    sys.exit(1)


PLATFORMS = {
    "x": {
        "url": "https://x.com/home",
        "env_var": "X_COOKIES_B64",
        "check_text": "Log in",  # if we see this, not logged in
    },
    "instagram": {
        "url": "https://www.instagram.com/",
        "env_var": "IG_COOKIES_B64",
        "check_text": "Log in",
    },
    "linkedin": {
        "url": "https://www.linkedin.com/feed/",
        "env_var": "LINKEDIN_COOKIES_B64",
        "check_text": "Sign in",
    },
    "google": {
        "url": "https://accounts.google.com/",
        "env_var": "GOOGLE_COOKIES_B64",
        "check_text": "Sign in",
    },
}


def export_cookies_for(platform: str) -> None:
    """Open a visible Chrome window, let the user log in, then export cookies."""
    info = PLATFORMS[platform]
    print(f"\n🌐 Opening {platform.upper()} in a REAL Chrome window...")
    print("   👉 Log in to your account if you aren't already.")
    print("   👉 Once you're logged in and see your feed/home, come back here.\n")

    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,800")

    driver = uc.Chrome(
        options=options,
        use_subprocess=True,
        version_main=145,
        browser_executable_path="/home/cuthbert/.local/bin/google-chrome"
    )
    driver.get(info["url"])

    input("   ⏎  Press ENTER here after you've logged in... ")

    # Grab all cookies from the browser
    cookies = driver.get_cookies()
    print(f"   ✅ Grabbed {len(cookies)} cookies from {platform.upper()}.")

    driver.quit()

    # Encode as base64 JSON
    cookies_json = json.dumps(cookies).encode()
    encoded = base64.b64encode(cookies_json).decode()

    # Save to .env file
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    env_path = os.path.normpath(env_path)

    # Read existing .env
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # Update or append the cookie variable
    var_name = info["env_var"]
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f"{var_name}=") or line.startswith(f"# {var_name}="):
            lines[i] = f"{var_name}={encoded}\n"
            updated = True
            break

    if not updated:
        lines.append(f"{var_name}={encoded}\n")

    with open(env_path, "w") as f:
        f.writelines(lines)

    print(f"   💾 Saved to .env as {var_name}")


def main():
    print("🍪 Jarvis Cookie Export Tool (Undetected Chrome)")
    print("=" * 50)
    print("\nWhich platform do you want to export cookies for?\n")
    print("  1. X (Twitter)")
    print("  2. Instagram")
    print("  3. LinkedIn")
    print("  4. Google")
    print("  5. All of them")
    print()

    choice = input("Pick a number (1-5): ").strip()

    if choice == "1":
        export_cookies_for("x")
    elif choice == "2":
        export_cookies_for("instagram")
    elif choice == "3":
        export_cookies_for("linkedin")
    elif choice == "4":
        export_cookies_for("google")
    elif choice == "5":
        for p in ["x", "instagram", "linkedin", "google"]:
            export_cookies_for(p)
    else:
        print("❌ Invalid choice.")
        return

    print("\n✅ Done! Your cookies have been saved to the .env file.")
    print("   Jarvis can now access your accounts.\n")


if __name__ == "__main__":
    main()
