package com.github.eileen.tlmtrumpet;

import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.neoforge.registries.DataPackRegistryEvent;

/**
 * Declares the datapack registry that holds the trumpet's fanfares.
 * <p>
 * Entries live at {@code data/<namespace>/tlmtrumpet/trumpet_call/<name>.json} - the doubled
 * namespace is how NeoForge lays out non-vanilla datapack registries, since the directory is
 * derived from the registry id's namespace and path.
 * <p>
 * No network codec is supplied, so the registry stays server-side. It does not need syncing: the
 * server resolves a call and broadcasts the chosen sound, and the client only ever sees a
 * {@code Holder<SoundEvent>} it can resolve on its own.
 */
public final class TlmTrumpetRegistries {
    public static final ResourceKey<Registry<TrumpetCall>> TRUMPET_CALLS = ResourceKey.createRegistryKey(
            ResourceLocation.fromNamespaceAndPath(TlmTrumpet.MOD_ID, "trumpet_call"));

    private TlmTrumpetRegistries() {
    }

    /** Wired up from the mod constructor; EventBusSubscriber's bus() is deprecated for removal. */
    public static void onNewDataPackRegistry(DataPackRegistryEvent.NewRegistry event) {
        event.dataPackRegistry(TRUMPET_CALLS, TrumpetCall.CODEC);
    }
}
