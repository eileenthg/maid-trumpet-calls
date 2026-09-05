# Maid Trumpet Calls

An addon for [Touhou Little Maid](https://github.com/TartaricAcid/TouhouLittleMaid) that gives the
trumpet a random ZUNpet fanfare when it summons your maids. Minecraft 1.20.1, Forge.

## How it works

TLM's trumpet plays no sound of its own. This mod listens for Forge's
`LivingEntityUseItemEvent.Stop`, which fires from `LivingEntity#releaseUsingItem` immediately
before `Item#releaseUsing` and carries the same remaining-tick count that `ItemTrumpet` checks
against its 20-tick minimum. When that event reports a successful trumpet release, one of eight
sound events is chosen and played.

Two deliberate choices:

- **The random pick happens on the server** and the resulting `SoundEvent` is broadcast. A single
  sound event with eight entries in `sounds.json` would let each client roll its own variant, so
  players standing together would hear different calls for the same blow.
- **The trumpet is resolved by registry name** (`touhou_little_maid:trumpet`) through
  `ForgeRegistries`, so this builds with no compile-time dependency on TLM. TLM is a runtime
  dependency only, declared in `mods.toml`.

The listener runs at `LOWEST` priority. `LivingEntityUseItemEvent.Stop` is cancellable, and a
cancelled release means no maids are summoned - cancelled events are not delivered by default, so
running last means we stay silent in that case too.

## The sounds

Eight melodies, all played on the "Romantic Tp" ZUNpet samples from a Touhou soundfont, rendered
mono at 44.1 kHz with a small room reverb. Mono matters: Minecraft only spatialises mono sounds,
so a stereo file would play at constant volume with no distance falloff or panning.

| File | Melody | Tempo |
|---|---|---|
| `trumpet_0` | Undyne's theme arrangement, descending ending | 152 BPM |
| `trumpet_1` | Undyne's theme arrangement, chromatic ending | 152 BPM |
| `trumpet_2` | Flowering Night (Sakuya's theme) | 152 BPM |
| `trumpet_3` | BedrockSolid ZUNpet test, descending ending | 155 BPM |
| `trumpet_4` | BedrockSolid ZUNpet test, ascending ending | 155 BPM |
| `trumpet_5` | Clownplease "How to play the ZUNpet" | 155 BPM |
| `trumpet_6` | original, E flat minor | 152 BPM |
| `trumpet_7` | original, E flat minor | 152 BPM |

## Changing the sounds

Replace the `.ogg` files in `assets/tlmtrumpet/sounds/trumpet/`, or override the
`item.trumpet.N` entries from a resource pack. To change how many variants exist, edit
`SOUND_COUNT` in `TlmTrumpet.java` and add matching `sounds.json` entries and files - the item
picks uniformly from whatever is registered, so no other code changes are needed.

## Building

    ./gradlew build

Output lands in `build/libs/`.
