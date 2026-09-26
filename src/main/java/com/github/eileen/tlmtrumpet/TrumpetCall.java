package com.github.eileen.tlmtrumpet;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.core.Holder;
import net.minecraft.sounds.SoundEvent;

/**
 * One fanfare the trumpet can play, loaded from a datapack.
 * <p>
 * {@code sound} uses {@link SoundEvent#CODEC}, so an entry may either name a sound event that some
 * mod has registered:
 *
 * <pre>{@code { "sound": "tlmtrumpet:item.trumpet.0" } }</pre>
 *
 * or define one inline, which is what a datapack plus resource pack combination needs since a
 * datapack cannot register into {@code minecraft:sound_event} by itself:
 *
 * <pre>{@code { "sound": { "sound_id": "mypack:my_horn", "range": 16 } } }</pre>
 *
 * The inline form produces a direct {@link Holder}, which survives the trip to the client because
 * {@code SoundEvent.STREAM_CODEC} writes direct holders as a location plus range rather than a
 * registry id. The client then resolves that location through its own {@code sounds.json}.
 */
public record TrumpetCall(Holder<SoundEvent> sound, int weight, float volume, float pitch) {
    public static final Codec<TrumpetCall> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            SoundEvent.CODEC.fieldOf("sound").forGetter(TrumpetCall::sound),
            Codec.intRange(1, Integer.MAX_VALUE).optionalFieldOf("weight", 1).forGetter(TrumpetCall::weight),
            Codec.floatRange(0.0F, 4.0F).optionalFieldOf("volume", 1.0F).forGetter(TrumpetCall::volume),
            Codec.floatRange(0.5F, 2.0F).optionalFieldOf("pitch", 1.0F).forGetter(TrumpetCall::pitch)
    ).apply(instance, TrumpetCall::new));
}
