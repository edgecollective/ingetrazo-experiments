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
