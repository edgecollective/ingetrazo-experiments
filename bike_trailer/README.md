# Bike trailer (Edge Collective, version 1.0)

A 3D model of the low-cost bike trailer on [edgecollective.io/projects/biketrailer](https://edgecollective.io/projects/biketrailer/):
- **Frame:** ½ in EMT conduit.
- **Wheels:** recycled 16 in kids' wheels, held in laser-cut steel dropouts.
- **Hitch:** a braided vinyl tube.

`bike_trailer.igz` shows it four ways, like the cold frame. Each has a saved view (Scene):

1. **Materials:** two 10 ft conduits, four dropouts, two wheels, 13 bolts and the vinyl tube.
2. **Bent main frame:** one 10 ft conduit (120 in) bent into the tongue and a loop around both wheels. The front cross member curves forward and bolts alongside the tongue.
3. **Assembled:** two inner bars from the second conduit, each bolted on top of the front and back cross members. Each wheel hangs between a short dropout on the outer bar and a long dropout on the inner bar, and a plywood deck sits on the inner bars.
4. **Exploded.**

Two more views:
- the frame without the deck;
- a close-up of the wheel mount, showing why the inner (long) dropout is one pipe diameter longer.

## What comes from the project, and what's estimated

- **From the project's files:**
  - **Dropouts:** sizes from the OpenSCAD files `ver_0.3_wide_short` and `_long`. The short one is a 45 × 55 mm plate, the long one 45 × 73 mm, both 3.2 mm stainless with an axle slot and two #10 holes.
  - **Bolts:** the parts list matches this model exactly. It has 8 × #10-24 × 2 in bolts for the dropouts, and 5 × #10-24 × 2½ in bolts: four for the inner-bar ends and one for the tongue joint.
- **Estimated from the photos and the "version 4" sketch:**
  - **Loop:** about 24 × 24 in, sized so the main frame uses exactly 120 in of conduit.
  - **Bends:** 4½ in radius.
  - **Tongue:** about 27 in ahead of the frame, angled in toward the bike's axle.
  - **Bar spacing:** inner bars 4.9 in inside the outer bars. That's a 100 mm hub plus two plates plus one pipe, which matches the sketch's "5".
  - **Axle height:** about 8 in, for a 16 in tire.

Real measurements can go in at the top of `generator/bt_geom.py`. `generator/build_igz.py` rebuilds the file.

---

# Version 4: closed loop (hand sketch + dry-fit photo)

`bike_trailer_v4.igz` follows the "version 4" sketch and the photo of the dry-fit frame. It has the same four stages as version 1 (materials, bent frame, assembled, exploded) and seven saved views. The bend numbers are on a **Notes** layer, which is hidden in the overview so it stays readable.

## Main frame: one 10 ft conduit, closed loop

Measured from the joint in the middle of the front cross member, going right (the sketch's top edge is the front):

| Section | Conduit (in) | Length |
|---|---|---|
| Front, right half | 0–10 | 10 in |
| Bend 1 (front right) | **10**–18 | 8 in |
| Right side | 18–42 | 24 in |
| Bend 2 (back right) | **42**–50 | 8 in |
| Back | 50–70 | 20 in |
| Bend 3 (back left) | **70**–78 | 8 in |
| Left side | 78–102 | 24 in |
| Bend 4 (front left) | **102**–110 | 8 in |
| Front, left half | 110–120 | 10 in |

The bold numbers are the sketch's circled marks.
- **Bend radius:** 8 in of conduit per 90° bend works out to a centreline radius of about 5.1 in. If your bender's radius is different, the marks shift.
- **Size:** about 30.9 × 34.9 in outside.
- **Joint:** the two ends butt together in a ½ in EMT set-screw coupling.

## Inner bars and wheels

- **Inner bars:** two 36 in pieces cut from the second conduit, leaving 48 in spare. They sit at the bend tangents (the 10 and 70 marks), about 5.1 in inside the sides (the sketch's "5"). Each bolts down through the front and back cross members with a #10-24 × 2½ in bolt.
- **Wheels:** each hangs between a side and its inner bar, with the axle at mid-length as in the photo. The clear gap is 111 mm: a 100 mm hub plus two 3.2 mm plates, with about 5 mm left for washers.
- **Dropouts:** the version 1 plates, short on the side and long on the inner bar. The inner bars sit one pipe diameter higher, so the long plate keeps the axle level.
- **Deck:** optional ½ in plywood, 21 × 34 in, on the inner bars and clear of the tires.

## Parts

- Two 10 ft ½ in EMT conduits
- One ½ in EMT set-screw coupling
- Four dropouts
- Eight #10-24 × 2 in bolts for the dropouts
- Four #10-24 × 2½ in bolts for the inner bars
- Two wheels with 100 mm front hubs
- Optional deck

## Assumptions to check

- **Wheel size:** 26 in, estimated from the photo. The sketch doesn't say. Change `WHEEL_IN`, `WR` and `RIM_R` in `generator/bt4_geom.py` if yours differ. Wheels up to about 30 in clear the cross members.
- **Front and joint:** I took the sketch's top edge as the front and put the joint there.
- **Axle mount:** in the photo the axles look like they pass straight through the bars. The model uses the version 1 dropouts instead.
- **No hitch:** the sketch has no tongue or hitch, so the model doesn't either. The 48 in spare from the second conduit is enough for a tongue like version 1's (about 27 in).

Rebuild with `generator/build_igz4.py`, run inside the Flatpak like `build_igz.py`. It loads `bt_geom.py`, then `bt4_geom.py` and `bt4_app.py`.

## Print set (black and white)

`print_v4/bike_trailer_v4_print.pdf` has nine pages:
1. Title and overview
2. Assembled, with and without the deck
3. Plan at 1:6.5, front up as in the sketch
4. Bending: the marked conduit, the loop with the circled marks, and the bend table
5. Wheel mount: render and section
6. Every piece laid out flat
7. Dropouts at full size; print at 100%
8. Exploded view
9. Parts list

The individual pages are PNGs in `print_v4/pages/`.

To rebuild:
1. With `bike_trailer_v4.igz` open in IngeTrazo and the bridge on, run `generator/shots4.py` for the hidden-line renders, then `generator/restore4.py`.
2. Run `generator/bt4_print.py OUT_DIR RENDER_DIR`.

# Variations: mobile hardware store (on the version 4 trailer)

Two quick concept sketches. The trailer itself is unchanged. Its 21 x 34 in deck becomes the floor of a plywood cabinet. Sizes were picked to fit the deck and clear the wheels; nothing is measured or load-checked.

## A: open stall (`bike_trailer_v4_hardware_store.igz`)

- **Drawers.** 14 on the back (customer) face: 12 small-parts drawers and 2 wide ones, each with a label card. One is shown pulled out.
- **Bin display.** 8 open-front hopper bins on two steps on the counter, which is 31.7 in above the ground.
- **Pegboard.** Double-sided, in a 1x2 frame over the axle, with a HARDWARE sign on top. The customer face holds tools and carded parts; the tow-side face holds rope and an extension cord.
- **Other parts.** A stock tote and cash box on the front half, a door to bulk storage on the front face, and 4 prop legs that clamp to the cross members to hold it level when unhitched.
- **Height.** The sign top is 58.4 in.
- **Groups and rebuild.** Groups are the assembled store and an exploded view. Rebuild with `generator/build_igz_store.py` (loads `bt_store_geom.py`, `bt_store_app.py`).

## B: tackle box (`bike_trailer_v4_tackle_store.igz`)

Closed for towing, it is a plain box 40.9 in high. Opened:

- **Back doors.** Two doors swing out 115 deg. Each is a shallow tray with three lipped shelves of parts jars. Behind them is a grid of 12 cubbies with parts boxes.
- **Cantilever trays.** A fixed 32-compartment tray sits on the cabinet. On each side, two 24-compartment trays ride on parallel steel arms and fan out over the wheels in steps, like a cantilever tackle box. That makes 128 compartments in the trays.
- **How the arms work.**
  - Each arm has pivots 4.61 in apart.
  - It swings from 49 deg inboard (closed) to 49 deg outboard (open), so tier 1 moves straight out 7 in and tier 2 moves 14 in.
  - Two parallel arms at each end keep the trays level.
  - Open width is 48.7 in.
- **Lid.** Hinged on the front edge, it stands up as a pegboard backboard with the sign. Its top is 74.9 in, and two stays hold it.
- **Groups and rebuild.** Groups are open and closed. Rebuild with `generator/build_igz_tackle.py` (loads `bt_store_geom.py`, `bt_tackle_geom.py`, `bt_tackle_app.py`).

Things to check:
- Top-heaviness and wind on the tall lid; a lid that folds in half would stand only about 17 in.
- Total weight on 26 in wheels.
- How the cabinet fixes to the deck and inner bars (the cabinet sides sit right over the inner bars, so U-bolts there would work).
