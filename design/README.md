# design/

The source for every graphic on the profile, in ENTØ Studios' palette (Syne and Space Grotesk on #060606, #F0EDE8 and #C8FF57).

- `mac.py`: the top section, a classic Mac desktop in one bit, plus a Launcher window of buttons. GitHub gives each README image one link and strips image maps, so the desktop is cut into tiles that sit flush on a line: the About side opens the portfolio, the alert opens Gotham, and each Launcher button opens its repo. Every tile is a window onto the same drawing, so the seams line up. The script writes `assets/mac/` and the tile block between the `mac:start` and `mac:end` markers in the README. `live.py` pulls the numbers from the GitHub API.
- `build.py` and `typeset.py`: the section labels, principles and sign-off. Type is set as outlines, so the SVGs need no web fonts. Each animates with CSS and SMIL and holds still under reduced motion.
- `cards.html` and `render-cards.cjs`: the project cards, rendered from live screenshots in `shots/` with Playwright.
- The Gotham card is a GIF: the card with a loop of the trailer composited into its window by ffmpeg.

Rebuild: put Syne and Space Grotesk in `fonts/` (static 600 and 800 instances are cut from the variable fonts with fontTools), then run `python design/mac.py`, `python design/build.py` and `node design/render-cards.cjs`. Departure Mono (SIL OFL) goes in `fonts/` too.
