# Clamshell mobile workstation: CNC package

A rolling box made of two half-cabinets hinged on one vertical edge. Swing half B out 90° and it becomes an L: half A gives you a fold-down desk at 29 in with storage above and below, and half B becomes a side cabinet. Close it and everything is shut inside a box on casters.

| Variant | Closed size (W × D × H) | Sheets | Parts | Desk support |
|---|---|---|---|---|
| V1 Basic | 30 × 24 × 49-1/2 in | 3 | 17 | folding lid stays (hardware) |
| V2 Studio | 36 × 24 × 49-1/2 in | 4 | 35 | lower doors swing out as desk legs |
| V3 Pro | 36 × 24 × 49-1/2 in | 4, stool included | 49 | same as V2 |

- **V2** adds cubbies, two bins, lipped shelves, a center divider and a pegboard back in B.
- **V3** adds a pencil drawer, a mail-slot organizer, a desk grommet and power bay, file slots in B, a pegboard over the desk, and a flat-pack stool.

## Files

- `cnc/V#_sheetN.dxf`: one file per 4 × 8 ft sheet, in inches. Layers:
  - `CUT_OUTSIDE`: part profiles. Cut outside the line, through.
  - `CUT_INSIDE`: slots, hand-holds and the grommet. Cut inside the line, through.
  - `DRILL_0.25`: pegboard holes, 1/4 in.
  - `LABELS` and `SHEET`: reference only. Do not cut these.
- `V#_cut_sheets.svg`: the nested sheets, with every part labeled by ID. It opens in any browser.
- `V#_cut_list.csv`: part ID, quantity, cut size, panel size, which sheet it's on, joinery features, and the hardware to buy.
- `generator/`: the parametric source (Python). The 3D model in IngeTrazo and these files both come from it.

## Before cutting

1. **Measure the plywood.** The design assumes T = 0.750 in. Real "3/4" sheets are often 0.70–0.72 in, and 18 mm Baltic birch is 0.709 in. Set `T` in `generator/cw_geom.py`, then run `python export.py <folder>` to regenerate. It needs `ezdxf`. Every slot, tab and dimension follows from `T`.
2. **Bit:** 1/4 in end mill. Every inside corner already has a 1/4 in dog-bone.
3. **Fit:** slots are 0.012 in wider than the tabs, for a snug glue fit. Cut a test joint from scrap first.
4. **Hold-downs:** use onion-skin or holding tabs in your CAM so small parts don't move.
5. **Assembly:** glue and clamp the through-tabs, which finish flush. Mount the hardware with #8 screws.

This is a design sketch, not tested furniture. Before relying on it:
- Load-test the desk leaf and the door legs.
- Lock both halves' casters when B is open.
- Hook B to A, so the L can't fold while someone is leaning on the desk.
