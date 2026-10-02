package com.github.eileen.tlmtrumpet;

import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.neoforged.bus.api.EventPriority;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.event.entity.living.LivingEntityUseItemEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/**
 * Plays a random ZUNpet fanfare when Touhou Little Maid's trumpet summons the maids.
 * <p>
 * This is an addon rather than a fork: it never touches TLM's classes. The trumpet is
 * identified by registry name at runtime, so there is no compile-time dependency on TLM.
 */
@Mod(TlmTrumpet.MOD_ID)
public class TlmTrumpet {
    public static final String MOD_ID = "tlmtrumpet";
    public static final Logger LOGGER = LogManager.getLogger(MOD_ID);

    private static final ResourceLocation TRUMPET_ID = ResourceLocation.fromNamespaceAndPath("touhou_little_maid", "trumpet");
    /** Mirrors ItemTrumpet.MIN_USE_DURATION: below this the item was released too early to summon. */
    private static final int MIN_USE_DURATION = 20;
    /** The fanfares shipped with the mod. Datapacks add more; see TlmTrumpetRegistries. */
    private static final List<String> BUILT_IN_CALLS = List.of(
            "flowering_night", "true_hero_descending", "true_hero_chromatic",
            "minoriko_descending", "minoriko_ascending", "history_of_the_moon",
            "bad_apple_arch", "bad_apple_scalar",
            "gods_loved_arch", "gods_loved_ascending",
            "gods_loved_descending", "gods_loved_low");

    public static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(Registries.SOUND_EVENT, MOD_ID);
    public static final List<DeferredHolder<SoundEvent, SoundEvent>> TRUMPET_SOUNDS = registerTrumpetSounds();

    public TlmTrumpet(IEventBus modEventBus, ModContainer modContainer) {
        SOUNDS.register(modEventBus);
        modEventBus.addListener(TlmTrumpetRegistries::onNewDataPackRegistry);
    }

    /**
     * The built-in sounds still need registering in code so that {@code sounds.json} can map them to
     * audio files and give them a subtitle. The datapack registry only decides which of them, or of
     * anyone else's, actually get played.
     */
    private static List<DeferredHolder<SoundEvent, SoundEvent>> registerTrumpetSounds() {
        return BUILT_IN_CALLS.stream()
                .map(call -> "item.trumpet." + call)
                .map(name -> SOUNDS.register(name, () -> SoundEvent.createFixedRangeEvent(
                        ResourceLocation.fromNamespaceAndPath(MOD_ID, name), 16.0F)))
                .toList();
    }

    @EventBusSubscriber(modid = MOD_ID)
    public static final class Handler {
        /** Guards the "no calls loaded" warning so a broken pack cannot spam the log on every blow. */
        private static boolean warnedAboutEmptyRegistry = false;

        /** Reported once at startup so pack authors can see whether their additions were picked up. */
        @SubscribeEvent
        public static void onServerStarted(ServerStartedEvent event) {
            event.getServer().registryAccess().registry(TlmTrumpetRegistries.TRUMPET_CALLS).ifPresent(
                    registry -> LOGGER.info("Loaded {} trumpet call(s): {}", registry.size(),
                            registry.keySet().stream().map(ResourceLocation::toString).sorted().toList()));
        }

        /**
         * LivingEntity#releaseUsingItem posts this immediately before Item#releaseUsing, and its
         * duration is the same remaining-tick count ItemTrumpet tests. Running at LOWEST priority
         * means a mod that cancels the release - and so cancels the summon - also silences us,
         * because cancelled events are not delivered by default.
         * <p>
         * The pick happens here, on the server, and the chosen sound is broadcast, so every player
         * nearby hears the same call rather than each client rolling its own.
         */
        @SubscribeEvent(priority = EventPriority.LOWEST)
        public static void onStopUsingItem(LivingEntityUseItemEvent.Stop event) {
            if (event.getDuration() < MIN_USE_DURATION) {
                return;
            }
            if (!(event.getEntity() instanceof Player player) || player.level().isClientSide) {
                return;
            }
            // Compare by registry key rather than looking the item up, so this stays correct
            // whether or not Touhou Little Maid is present.
            ResourceLocation held = BuiltInRegistries.ITEM.getKey(event.getItem().getItem());
            if (!TRUMPET_ID.equals(held)) {
                return;
            }

            Level level = player.level();
            Registry<TrumpetCall> registry = level.registryAccess()
                    .registry(TlmTrumpetRegistries.TRUMPET_CALLS).orElse(null);
            if (registry == null) {
                return;
            }
            RandomSource random = level.getRandom();
            TrumpetCall call = pickWeighted(registry, random);
            if (call == null) {
                if (!warnedAboutEmptyRegistry) {
                    warnedAboutEmptyRegistry = true;
                    LOGGER.warn("No trumpet calls are loaded, so the trumpet will stay silent. "
                            + "Expected at least one entry under data/<namespace>/{}/trumpet_call/.", MOD_ID);
                }
                return;
            }
            level.playSeededSound(null, player.getX(), player.getY(), player.getZ(),
                    call.sound(), SoundSource.PLAYERS, call.volume(), call.pitch(), random.nextLong());
        }

        @Nullable
        private static TrumpetCall pickWeighted(Registry<TrumpetCall> registry, RandomSource random) {
            int total = 0;
            for (TrumpetCall call : registry) {
                total += call.weight();
            }
            if (total <= 0) {
                return null;
            }
            int roll = random.nextInt(total);
            for (TrumpetCall call : registry) {
                roll -= call.weight();
                if (roll < 0) {
                    return call;
                }
            }
            return null;
        }
    }
}
