# design/

The source for every graphic on the profile, in ENTØ Studios' palette (Syne and Space Grotesk on #060606, #F0EDE8 and #C8FF57).

- `mac.py`: the top section, a classic Mac desktop in one bit. The portrait is my café photo, cut out and Atkinson-dithered at its display size; the window zooms open, the portrait draws in and the pointer double-clicks Gotham, all in SMIL. `live.py` pulls the numbers from the GitHub API.
- `build.py` and `typeset.py`: the section labels, principles and sign-off. Type is set as outlines, so the SVGs need no web fonts. Each animates with CSS and SMIL and holds still under reduced motion.
- `cards.html` and `render-cards.cjs`: the project cards, rendered from live screenshots in `shots/` with Playwright.
- The Gotham card is a GIF: the card with a loop of the trailer composited into its window by ffmpeg.

Rebuild: put Syne and Space Grotesk in `fonts/` (static 600 and 800 instances are cut from the variable fonts with fontTools), then run `python design/mac.py`, `python design/build.py` and `node design/render-cards.cjs`. Departure Mono (SIL OFL) goes in `fonts/` too.
