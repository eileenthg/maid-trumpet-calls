package com.github.eileen.tlmtrumpet;

import com.google.common.collect.Lists;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

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

    private static final ResourceLocation TRUMPET_ID = new ResourceLocation("touhou_little_maid", "trumpet");
    /** Mirrors ItemTrumpet.MIN_USE_DURATION: below this the item was released too early to summon. */
    private static final int MIN_USE_DURATION = 20;
    private static final int SOUND_COUNT = 8;

    public static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, MOD_ID);
    public static final List<RegistryObject<SoundEvent>> TRUMPET_SOUNDS = registerTrumpetSounds();

    public TlmTrumpet() {
        SOUNDS.register(FMLJavaModLoadingContext.get().getModEventBus());
    }

    private static List<RegistryObject<SoundEvent>> registerTrumpetSounds() {
        List<RegistryObject<SoundEvent>> sounds = Lists.newArrayListWithCapacity(SOUND_COUNT);
        for (int i = 0; i < SOUND_COUNT; i++) {
            String name = "item.trumpet." + i;
            sounds.add(SOUNDS.register(name, () -> SoundEvent.createFixedRangeEvent(new ResourceLocation(MOD_ID, name), 16.0F)));
        }
        return List.copyOf(sounds);
    }

    @Mod.EventBusSubscriber(modid = MOD_ID)
    public static final class Handler {
        /**
         * LivingEntity#releaseUsingItem posts this immediately before Item#releaseUsing, and its
         * duration is the same remaining-tick count ItemTrumpet tests. Running at LOWEST priority
         * means a mod that cancels the release - and so cancels the summon - also silences us,
         * because cancelled events are not delivered by default.
         * <p>
         * The random pick happens here, on the server, and the chosen SoundEvent is broadcast, so
         * every player nearby hears the same call rather than each client rolling its own.
         */
        @SubscribeEvent(priority = EventPriority.LOWEST)
        public static void onStopUsingItem(LivingEntityUseItemEvent.Stop event) {
            if (event.getDuration() < MIN_USE_DURATION) {
                return;
            }
            if (!(event.getEntity() instanceof Player player) || player.level().isClientSide) {
                return;
            }
            Item trumpet = ForgeRegistries.ITEMS.getValue(TRUMPET_ID);
            if (trumpet == null || !event.getItem().is(trumpet)) {
                return;
            }
            Level level = player.level();
            RandomSource random = level.getRandom();
            SoundEvent sound = TRUMPET_SOUNDS.get(random.nextInt(TRUMPET_SOUNDS.size())).get();
            level.playSound(null, player.getX(), player.getY(), player.getZ(), sound, SoundSource.PLAYERS, 1.0F, 1.0F);
        }
    }
}
