package gyros.gyrosclient;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.context.CommandContext;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

public class DiamondBlockCommand {

    public static void register() {

        CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) -> {

            registerCommand(dispatcher);

        });

    }

    private static void registerCommand(CommandDispatcher<CommandSourceStack> dispatcher) {

        dispatcher.register(
                Commands.literal("diamondblocks")
                        .then(Commands.argument("count", IntegerArgumentType.integer())
                        .executes(context -> {

                            ServerPlayer player = context.getSource().getPlayerOrException();
                            int count = IntegerArgumentType.getInteger(context, "count");
                            ItemStack diamonds = new ItemStack(Items.DIAMOND_BLOCK, count);
                            player.getInventory().add(diamonds);
                            context.getSource().sendSuccess(() -> Component.literal("Gave %s Diamond Block(s)".formatted(count)), false);
                            return 1;
                        }))
        );

    }

}