# Maid Trumpet Calls

An addon for [Touhou Little Maid](https://github.com/TartaricAcid/TouhouLittleMaid) that gives the
trumpet a random ZUNpet fanfare when it summons your maids. Minecraft 1.21.1, NeoForge.

Eight melodies ship with the mod, and **datapacks can add more**.

## How it works

TLM's trumpet plays no sound of its own. This mod listens for NeoForge's
`LivingEntityUseItemEvent.Stop`, which fires from `LivingEntity#releaseUsingItem` immediately
before `Item#releaseUsing` and carries the same remaining-tick count that `ItemTrumpet` checks
against its 20-tick minimum. When that event reports a successful trumpet release, one call is
chosen and played.

Two deliberate choices:

- **The pick happens on the server** and the resulting sound is broadcast. A single sound event
  with eight entries in `sounds.json` would let each client roll its own variant, so players
  standing together would hear different calls for the same blow.
- **The trumpet is matched by registry key** (`touhou_little_maid:trumpet`), so this builds with no
  compile-time dependency on TLM. TLM is a runtime dependency only.

The listener runs at `LOWEST` priority. `LivingEntityUseItemEvent.Stop` is cancellable, and a
cancelled release means no maids are summoned - cancelled events are not delivered by default, so
running last means we stay silent in that case too.

## Adding your own calls with a datapack

Calls live in a datapack registry. Drop JSON files at:

    data/<your_namespace>/tlmtrumpet/trumpet_call/<name>.json

The doubled `tlmtrumpet` is not a typo - NeoForge derives a datapack registry's directory from the
registry id's namespace *and* path.

**Reusing a sound that a mod already registered:**

```json
{ "sound": "tlmtrumpet:item.trumpet.flowering_night" }
```

**Defining a sound inline**, which is what you want for brand new audio:

```json
{
  "sound": { "sound_id": "mypack:my_horn", "range": 16 },
  "weight": 5,
  "volume": 0.8,
  "pitch": 1.1
}
```

| Field | Default | Notes |
|---|---|---|
| `sound` | required | a registered sound event id, or an inline `{ "sound_id", "range" }` |
| `weight` | `1` | relative chance; a call with weight 3 is three times as likely as weight 1 |
| `volume` | `1.0` | 0.0 - 4.0 |
| `pitch` | `1.0` | 0.5 - 2.0 |

### You also need a resource pack for new audio

A datapack alone cannot add sound. It says *which* calls exist; the actual `.ogg` and its
`sounds.json` entry are client resources, so new audio needs a resource pack alongside:

    assets/mypack/sounds.json
    assets/mypack/sounds/my_horn.ogg

with `sounds.json` mapping the id you referenced:

```json
{
  "my_horn": {
    "category": "voice",
    "sounds": [ { "name": "mypack:my_horn", "stream": false } ]
  }
}
```

Make the audio **mono** - Minecraft only spatialises mono sounds, so a stereo file plays at
constant volume with no distance falloff or panning.

The server logs how many calls loaded at startup, which is the quickest way to confirm a pack was
picked up:

    Loaded 10 trumpet call(s): [mypack:my_horn_call, tlmtrumpet:minoriko_ascending, ...]

### Replacing or removing the built-in calls

A datapack can override any built-in call by using the same path and file name under the
`tlmtrumpet` namespace - for example `data/tlmtrumpet/tlmtrumpet/trumpet_call/flowering_night.json`
pointed at a different sound. Datapack registries cannot *delete* entries, so to mute a built-in
call rather than replace it, override it with a near-silent sound or give the ones you do want a
much higher `weight`.

## The bundled sounds

Eight melodies played on the "Romantic Tp" ZUNpet samples from a Touhou soundfont, rendered mono at
44.1 kHz with a small room reverb.

| Call | Piece | Tempo | Length |
|---|---|---|---|
| `flowering_night` | Flowering Night | 152 BPM | 4.43 s |
| `true_hero_descending` | Battle Against a True Hero | 152 BPM | 5.71 s |
| `true_hero_chromatic` | Battle Against a True Hero | 152 BPM | 5.71 s |
| `minoriko_descending` | Because Princess Inada is Scolding Me | 155 BPM | 4.07 s |
| `minoriko_ascending` | Because Princess Inada is Scolding Me | 155 BPM | 4.07 s |
| `history_of_the_moon` | Gensokyo Millennium ~ History of the Moon | 155 BPM | 4.07 s |
| `bad_apple_arch` | Bad Apple!! | 152 BPM | 5.31 s |
| `bad_apple_scalar` | Bad Apple!! | 152 BPM | 4.13 s |

Where two calls share a piece they take the same opening and then part company, so the suffix names
the shape of the tail: `_descending` and `_ascending` for where the phrase ends up, `_chromatic` for
a chromatic fall, `_arch` and `_scalar` for an arched line against a plain scale.

See [`tools/`](tools/) for the pipeline that generated them and how to change or add melodies.

## Credits and attribution

The MIT license above covers the **code**. The audio is derivative work and is credited here rather
than claimed.

All eight calls are rendered from the "Romantic Tp" preset of a third-party Touhou soundfont
(`TOUHOU INSTRUMENT + DRUM KIT.sf2`) - the ZUNpet sound itself is not mine.

What is bundled is a transcribed **melody line** in each case, not anyone's arrangement, harmony or
recording:

| Call | Piece | Composer | Transcribed from |
|---|---|---|---|
| `flowering_night` | Flowering Night (Sakuya Izayoi's theme, *Imperishable Night*) | **ZUN** | PineappleDisciple's upload |
| `true_hero_descending`, `true_hero_chromatic` | Battle Against a True Hero (Undyne the Undying's theme, *Undertale*) | **Toby Fox** | Hakurei Gaming's arrangement |
| `minoriko_descending`, `minoriko_ascending` | 稲田姫様に叱られるから / Because Princess Inada is Scolding Me (Minoriko Aki's theme, *Mountain of Faith*) | **ZUN** | BedrockSolid's "ZUNpet test" |
| `history_of_the_moon` | 千年幻想郷 ～ History of the Moon / Gensokyo Millennium ~ History of the Moon (Eirin Yagokoro's theme, *Imperishable Night*) | **ZUN** | Clownplease's "How to play the ZUNpet" |
| `bad_apple_arch`, `bad_apple_scalar` | Bad Apple!! (*Lotus Land Story*) | **ZUN** | supplied as notation |

Touhou Project is by ZUN (Team Shanghai Alice); the Touhou tracks above are his compositions, and
the channels listed are where the melody was transcribed from rather than rights holders in it.
Undyne's theme is from Undertale by Toby Fox. Touhou Little Maid is by TartaricAcid and
contributors.

If you hold rights in any of the above and would rather a call were removed, open an issue and it
will be taken out - the datapack registry means removing one is a file deletion, not a code change.

## Building and testing

    ./gradlew build

`./gradlew runServer` and `runClient` need TLM present, since it is a required dependency - put a
TLM jar in `run/mods/` first.
