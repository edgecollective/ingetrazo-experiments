# Pallet cold frame

A cold frame built from recycled pallet wood. The box is made of 1x4 deck boards running horizontally, nailed into corner posts cut from the pallet's 2x4 stringers. The lid is two layers of 1x4 frame with a sheet of clear plastic sandwiched between them.

`cold_frame.igz` shows it four ways. Each has a saved view (Scene):

1. **Source pallet:** a standard 48 × 40 in pallet, with 1x4 deck boards about 40 in long and 2x4 stringers about 48 in long.
2. **Built upside down:** the smooth top edges sit on the bench. Flip the box when it's done, so the uneven ends end up on the soil.
3. **Finished:** the lid is hinged at the back and shown propped open.
4. **Exploded:** every part pulled apart, including both lid layers and the plastic.

## Box: 40 × 40 in outside

- **Front:** 2 boards high, about 7 in.
- **Back:** 3 boards high, about 10½ in.
- **Sides:** 2 boards high, plus one angled board on the outside face. The angled board's top edge runs from 7 in at the front to 10½ in at the back, which gives the lid a tilt of about 5°.
- **Posts:** four, one in each inside corner, cut from a stringer with the top cut to the slope. The front pair is about 7 in long, the back pair about 10½ in.

## Lid: 40 × 40 in, lapped

- **Bottom layer:** two full-width rails across the front and back, with the two side pieces cut to fit between them.
- **Top layer:** two full-length side pieces, with the front and back pieces cut to fit between them. Because the two layers are arranged opposite ways, every corner overlaps.
- **Plastic:** greenhouse film or clear polycarbonate, sandwiched between the two layers.
- **Hinges:** two strap hinges along the back (high) edge.

## Cut list

| Qty | Part | Stock | Length |
|---|---|---|---|
| 2 | Front boards | 1x4 | 40 in |
| 3 | Back boards | 1x4 | 40 in |
| 4 | Side boards | 1x4 | 38½ in |
| 2 | Angled side boards | 1x4 | 40 in (ends cut plumb) |
| 2 | Lid rails, bottom layer | 1x4 | 40 in |
| 2 | Lid sides, bottom layer | 1x4 | 33 in |
| 2 | Lid sides, top layer | 1x4 | 40 in |
| 2 | Lid rails, top layer | 1x4 | 33 in |
| 2 | Corner posts, front | 2x4 | about 7 in |
| 2 | Corner posts, back | 2x4 | about 10½ in |

That's 19 deck boards and one stringer. A pallet has about 12 deck boards, so plan on 2 pallets per frame.

## Assumptions to check

- **Board sizes:** the boards are assumed to be 3½ in wide and ¾ in thick. Pallet boards vary, and the heights follow from the board width.
- **Box shape:** the box is assumed square at 40 × 40 in, with the side boards cut to fit between the front and back boards.
- **Angled board:** it's drawn as a full board on the outside face, overlapping the second side board. If you instead rip one board on the diagonal to fill the triangle flush with the sides, one board makes both sides' fillers.

The model is generated from `generator/`. Edit the dimensions at the top of `cf_geom.py` to match your boards.
