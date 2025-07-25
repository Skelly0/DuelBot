import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from typing import Dict, Optional
import asyncio

from game_logic import HexDuelGame, Match, Player, GameState

# Load environment variables
load_dotenv()

class DuelBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        self.game = HexDuelGame()
        self.active_matches: Dict[int, Match] = {}  # channel_id -> Match
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        print(f'Bot is in {len(self.guilds)} guilds')

bot = DuelBot()

@bot.tree.command(name="duel", description="Hex-Duel commands")
@app_commands.describe(
    action="The duel action to perform",
    opponent="The player to challenge (for challenge action)",
    best_of="Best of how many rounds (3, 5, or 7)",
    no_repeat="Forbid using same stance twice in a row",
    adjacency_mod="Apply +1/-1 modifier for adjacent/opposite stances",
    bait_switch="Allow one-time stance switching after declaration",
    first="First stance option",
    second="Second stance option",
    choice="Your secret stance choice",
    old="Old stance to replace (for switch)",
    new="New stance to replace with (for switch)"
)
async def duel_command(
    interaction: discord.Interaction,
    action: str,
    opponent: Optional[discord.Member] = None,
    best_of: Optional[int] = 3,
    no_repeat: Optional[bool] = False,
    adjacency_mod: Optional[bool] = False,
    bait_switch: Optional[bool] = False,
    first: Optional[str] = None,
    second: Optional[str] = None,
    choice: Optional[str] = None,
    old: Optional[str] = None,
    new: Optional[str] = None
):
    """Main duel command handler"""
    
    if action == "challenge":
        await handle_challenge(interaction, opponent, best_of, no_repeat, adjacency_mod, bait_switch)
    elif action == "accept":
        await handle_accept(interaction)
    elif action == "stance":
        await handle_stance_declaration(interaction, first, second)
    elif action == "pick":
        await handle_stance_pick(interaction, choice)
    elif action == "switch":
        await handle_stance_switch(interaction, old, new)
    elif action == "status":
        await handle_status(interaction)
    elif action == "cancel":
        await handle_cancel(interaction)
    elif action == "end":
        await handle_end(interaction)
    else:
        await interaction.response.send_message("Invalid action. Use: challenge, accept, stance, pick, switch, status, cancel, or end", ephemeral=True)

# Add choices for the action parameter
@duel_command.autocomplete('action')
async def action_autocomplete(interaction: discord.Interaction, current: str):
    actions = ["challenge", "accept", "stance", "pick", "switch", "status", "cancel", "end"]
    return [app_commands.Choice(name=action, value=action) for action in actions if current.lower() in action.lower()]

# Add choices for stance parameters
@duel_command.autocomplete('first')
@duel_command.autocomplete('second')
@duel_command.autocomplete('choice')
@duel_command.autocomplete('old')
@duel_command.autocomplete('new')
async def stance_autocomplete(interaction: discord.Interaction, current: str):
    stances = bot.game.STANCES
    return [app_commands.Choice(name=stance, value=stance) for stance in stances if current.lower() in stance.lower()]

async def handle_challenge(interaction: discord.Interaction, opponent: discord.Member, best_of: int, no_repeat: bool, adjacency_mod: bool, bait_switch: bool):
    """Handle challenge command"""
    if not opponent:
        await interaction.response.send_message("You must specify an opponent to challenge!", ephemeral=True)
        return
    
    if opponent.id == interaction.user.id:
        await interaction.response.send_message("You cannot challenge yourself!", ephemeral=True)
        return
    
    if opponent.bot:
        await interaction.response.send_message("You cannot challenge a bot!", ephemeral=True)
        return
    
    if best_of not in [3, 5, 7]:
        await interaction.response.send_message("Best of must be 3, 5, or 7!", ephemeral=True)
        return
    
    channel_id = interaction.channel_id
    if channel_id in bot.active_matches:
        await interaction.response.send_message("There's already an active match in this channel!", ephemeral=True)
        return
    
    # Create new match
    player1 = Player(user_id=interaction.user.id, username=interaction.user.display_name)
    player2 = Player(user_id=opponent.id, username=opponent.display_name)
    
    match = Match(
        channel_id=channel_id,
        player1=player1,
        player2=player2,
        best_of=best_of,
        no_repeat=no_repeat,
        adjacency_mod=adjacency_mod,
        bait_switch=bait_switch
    )
    
    bot.active_matches[channel_id] = match
    
    # Create challenge embed
    embed = discord.Embed(
        title="⚔️ Hex-Duel Challenge!",
        description=f"{interaction.user.mention} challenges {opponent.mention} to a duel!",
        color=discord.Color.orange()
    )
    embed.add_field(name="Format", value=f"Best of {best_of}", inline=True)
    embed.add_field(name="Options", value=format_options(no_repeat, adjacency_mod, bait_switch), inline=True)
    embed.add_field(name="Status", value="⏳ Waiting for acceptance", inline=False)
    embed.set_footer(text=f"{opponent.display_name}, use '/duel accept' to accept this challenge!")
    
    await interaction.response.send_message(content=f"{opponent.mention}", embed=embed)

async def handle_accept(interaction: discord.Interaction):
    """Handle accept command"""
    channel_id = interaction.channel_id
    match = bot.active_matches.get(channel_id)
    
    if not match:
        await interaction.response.send_message("No active challenge in this channel!", ephemeral=True)
        return
    
    if match.state != GameState.WAITING_FOR_ACCEPT:
        await interaction.response.send_message("This match has already been accepted!", ephemeral=True)
        return
    
    if interaction.user.id != match.player2.user_id:
        await interaction.response.send_message("Only the challenged player can accept!", ephemeral=True)
        return
    
    # Accept the challenge
    match.state = GameState.DECLARING_STANCES
    
    embed = discord.Embed(
        title="⚔️ Hex-Duel Match - LIVE!",
        description=f"{match.player1.username} vs {match.player2.username}",
        color=discord.Color.green()
    )
    embed.add_field(name="Format", value=f"Best of {match.best_of}", inline=True)
    embed.add_field(name="Options", value=format_options(match.no_repeat, match.adjacency_mod, match.bait_switch), inline=True)
    embed.add_field(name="Round", value=f"{match.current_round}", inline=True)
    embed.add_field(name="Score", value=f"{match.player1.username}: {match.player1.score} | {match.player2.username}: {match.player2.score}", inline=False)
    embed.add_field(name="Next Step", value="Both players declare two stances using `/duel stance first second`", inline=False)
    
    await interaction.response.edit_message(embed=embed, content=None)

async def handle_stance_declaration(interaction: discord.Interaction, first: str, second: str):
    """Handle stance declaration"""
    if not first or not second:
        await interaction.response.send_message("You must specify both first and second stances!", ephemeral=True)
        return
    
    if not bot.game.validate_stance(first) or not bot.game.validate_stance(second):
        await interaction.response.send_message(f"Invalid stance! Valid stances: {', '.join(bot.game.STANCES)}", ephemeral=True)
        return
    
    if first == second:
        await interaction.response.send_message("You cannot declare the same stance twice!", ephemeral=True)
        return
    
    channel_id = interaction.channel_id
    match = bot.active_matches.get(channel_id)
    
    if not match:
        await interaction.response.send_message("No active match in this channel!", ephemeral=True)
        return
    
    if match.state != GameState.DECLARING_STANCES:
        await interaction.response.send_message("Not currently in stance declaration phase!", ephemeral=True)
        return
    
    user_id = interaction.user.id
    if user_id not in [match.player1.user_id, match.player2.user_id]:
        await interaction.response.send_message("You are not part of this match!", ephemeral=True)
        return
    
    # Check no_repeat rule
    if match.no_repeat:
        last_stance = match.last_stances.get(user_id)
        if last_stance in [first, second]:
            await interaction.response.send_message(f"You cannot use {last_stance} again (no-repeat rule)!", ephemeral=True)
            return
    
    # Set declared stances
    if user_id == match.player1.user_id:
        match.player1.declared_stances = [first, second]
    else:
        match.player2.declared_stances = [first, second]
    
    await interaction.response.send_message(f"**{interaction.user.display_name}** declared: **{first}** and **{second}**")
    
    # Check if both players have declared
    if match.player1.declared_stances and match.player2.declared_stances:
        match.state = GameState.PICKING_STANCES
        
        embed = discord.Embed(
            title="🎯 Secret Pick Phase",
            description="Both players have declared their stances. Now make your secret picks!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name=f"{match.player1.username}'s options",
            value=" | ".join(match.player1.declared_stances),
            inline=False
        )
        embed.add_field(
            name=f"{match.player2.username}'s options", 
            value=" | ".join(match.player2.declared_stances),
            inline=False
        )
        
        if match.bait_switch:
            embed.add_field(
                name="Bait & Switch",
                value="You may use `/duel switch old new` once before picking!",
                inline=False
            )
        
        embed.set_footer(text="Use '/duel pick choice' to make your secret selection!")
        
        await interaction.followup.send(embed=embed)

async def handle_stance_switch(interaction: discord.Interaction, old: str, new: str):
    """Handle bait-and-switch"""
    if not old or not new:
        await interaction.response.send_message("You must specify both old and new stances!", ephemeral=True)
        return
    
    channel_id = interaction.channel_id
    match = bot.active_matches.get(channel_id)
    
    if not match:
        await interaction.response.send_message("No active match in this channel!", ephemeral=True)
        return
    
    if not match.bait_switch:
        await interaction.response.send_message("Bait-and-switch is not enabled for this match!", ephemeral=True)
        return
    
    if match.state != GameState.PICKING_STANCES:
        await interaction.response.send_message("Not currently in picking phase!", ephemeral=True)
        return
    
    user_id = interaction.user.id
    if user_id not in [match.player1.user_id, match.player2.user_id]:
        await interaction.response.send_message("You are not part of this match!", ephemeral=True)
        return
    
    player = match.player1 if user_id == match.player1.user_id else match.player2
    
    if player.has_switched:
        await interaction.response.send_message("You have already used your switch!", ephemeral=True)
        return
    
    if old not in player.declared_stances:
        await interaction.response.send_message(f"{old} is not one of your declared stances!", ephemeral=True)
        return
    
    if not bot.game.validate_stance(new):
        await interaction.response.send_message(f"Invalid stance! Valid stances: {', '.join(bot.game.STANCES)}", ephemeral=True)
        return
    
    if new in player.declared_stances:
        await interaction.response.send_message(f"You already declared {new}!", ephemeral=True)
        return
    
    # Check no_repeat rule
    if match.no_repeat:
        last_stance = match.last_stances.get(user_id)
        if new == last_stance:
            await interaction.response.send_message(f"You cannot switch to {new} (no-repeat rule)!", ephemeral=True)
            return
    
    # Perform the switch
    player.declared_stances = [new if s == old else s for s in player.declared_stances]
    player.has_switched = True
    
    await interaction.response.send_message(f"**{interaction.user.display_name}** switched **{old}** → **{new}**")

async def handle_stance_pick(interaction: discord.Interaction, choice: str):
    """Handle secret stance pick"""
    if not choice:
        await interaction.response.send_message("You must specify your choice!", ephemeral=True)
        return
    
    channel_id = interaction.channel_id
    match = bot.active_matches.get(channel_id)
    
    if not match:
        await interaction.response.send_message("No active match in this channel!", ephemeral=True)
        return
    
    if match.state != GameState.PICKING_STANCES:
        await interaction.response.send_message("Not currently in picking phase!", ephemeral=True)
        return
    
    user_id = interaction.user.id
    if user_id not in [match.player1.user_id, match.player2.user_id]:
        await interaction.response.send_message("You are not part of this match!", ephemeral=True)
        return
    
    player = match.player1 if user_id == match.player1.user_id else match.player2
    
    if choice not in player.declared_stances:
        await interaction.response.send_message(f"{choice} is not one of your declared stances!", ephemeral=True)
        return
    
    if player.picked_stance:
        await interaction.response.send_message("You have already made your pick!", ephemeral=True)
        return
    
    # Set the pick
    player.picked_stance = choice
    
    await interaction.response.send_message(f"✅ You picked **{choice}**", ephemeral=True)
    
    # Announce publicly that player has locked in
    await interaction.followup.send(f"🔒 **{interaction.user.display_name}** has locked in their choice!")
    
    # Check if both players have picked
    if match.player1.picked_stance and match.player2.picked_stance:
        await resolve_round(interaction, match)

async def resolve_round(interaction: discord.Interaction, match: Match):
    """Resolve the current round"""
    result = bot.game.resolve_round(match)
    
    # Create result embed
    embed = discord.Embed(
        title=f"⚔️ Round {match.current_round - 1} Results",
        color=discord.Color.gold()
    )
    
    # Stance matchup
    embed.add_field(
        name="Stance Matchup",
        value=f"**{match.player1.username}**: {result.player1_stance}\n**{match.player2.username}**: {result.player2_stance}",
        inline=True
    )
    
    # Advantage states
    adv_text = f"**{match.player1.username}**: {result.player1_advantage.title()}\n**{match.player2.username}**: {result.player2_advantage.title()}"
    embed.add_field(name="Advantage", value=adv_text, inline=True)
    
    # Dice rolls
    roll_text = f"**{match.player1.username}**: {result.player1_roll}"
    if result.player1_final_roll != result.player1_roll:
        roll_text += f" → {result.player1_final_roll}"
    roll_text += f"\n**{match.player2.username}**: {result.player2_roll}"
    if result.player2_final_roll != result.player2_roll:
        roll_text += f" → {result.player2_final_roll}"
    embed.add_field(name="Dice Rolls", value=roll_text, inline=True)
    
    # Winner
    winner_name = match.player1.username if result.winner_id == match.player1.user_id else match.player2.username
    embed.add_field(name="Round Winner", value=f"🏆 **{winner_name}**", inline=False)
    
    # Current score
    embed.add_field(
        name="Match Score",
        value=f"**{match.player1.username}**: {match.player1.score} | **{match.player2.username}**: {match.player2.score}",
        inline=False
    )
    
    if result.adjacency_mod_applied:
        embed.set_footer(text="Adjacency modifier applied")
    
    await interaction.followup.send(embed=embed)
    
    # Check if match is complete
    if match.state == GameState.MATCH_COMPLETE:
        await announce_match_winner(interaction, match)
    else:
        # Next round
        next_embed = discord.Embed(
            title=f"🎯 Round {match.current_round}",
            description="Declare your stances for the next round!",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=next_embed)

async def announce_match_winner(interaction: discord.Interaction, match: Match):
    """Announce the match winner"""
    if match.player1.score > match.player2.score:
        winner = match.player1
        loser = match.player2
    else:
        winner = match.player2
        loser = match.player1
    
    embed = discord.Embed(
        title="🏆 MATCH COMPLETE!",
        description=f"**{winner.username}** defeats **{loser.username}**!",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="Final Score",
        value=f"**{winner.username}**: {winner.score}\n**{loser.username}**: {loser.score}",
        inline=True
    )
    embed.add_field(
        name="Format",
        value=f"Best of {match.best_of}",
        inline=True
    )
    
    await interaction.followup.send(embed=embed)
    
    # Clean up match
    del bot.active_matches[match.channel_id]

async def handle_status(interaction: discord.Interaction):
    """Handle status command"""
    channel_id = interaction.channel_id
    match = bot.active_matches.get(channel_id)
    
    if not match:
        await interaction.response.send_message("No active match in this channel!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📊 Match Status",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Players",
        value=f"{match.player1.username} vs {match.player2.username}",
        inline=False
    )
    embed.add_field(
        name="Score",
        value=f"**{match.player1.username}**: {match.player1.score} | **{match.player2.username}**: {match.player2.score}",
        inline=False
    )
    embed.add_field(name="Round", value=str(match.current_round), inline=True)
    embed.add_field(name="Format", value=f"Best of {match.best_of}", inline=True)
    embed.add_field(name="State", value=match.state.value.replace('_', ' ').title(), inline=True)
    
    if match.state == GameState.DECLARING_STANCES:
        declared = []
        if match.player1.declared_stances:
            declared.append(f"✅ {match.player1.username}")
        else:
            declared.append(f"⏳ {match.player1.username}")
        if match.player2.declared_stances:
            declared.append(f"✅ {match.player2.username}")
        else:
            declared.append(f"⏳ {match.player2.username}")
        embed.add_field(name="Declarations", value="\n".join(declared), inline=False)
    
    elif match.state == GameState.PICKING_STANCES:
        picked = []
        if match.player1.picked_stance:
            picked.append(f"🔒 {match.player1.username}")
        else:
            picked.append(f"⏳ {match.player1.username}")
        if match.player2.picked_stance:
            picked.append(f"🔒 {match.player2.username}")
        else:
            picked.append(f"⏳ {match.player2.username}")
        embed.add_field(name="Secret Picks", value="\n".join(picked), inline=False)
        
        # Show declared stances
        if match.player1.declared_stances:
            embed.add_field(
                name=f"{match.player1.username}'s Options",
                value=" | ".join(match.player1.declared_stances),
                inline=True
            )
        if match.player2.declared_stances:
            embed.add_field(
                name=f"{match.player2.username}'s Options",
                value=" | ".join(match.player2.declared_stances),
                inline=True
            )
    
    await interaction.response.send_message(embed=embed)

async def handle_cancel(interaction: discord.Interaction):
    """Handle cancel command"""
    channel_id = interaction.channel_id
    match = bot.active_matches.get(channel_id)
    
    if not match:
        await interaction.response.send_message("No active match in this channel!", ephemeral=True)
        return
    
    user_id = interaction.user.id
    if user_id not in [match.player1.user_id, match.player2.user_id]:
        await interaction.response.send_message("Only match participants can cancel!", ephemeral=True)
        return
    
    # Create confirmation view
    view = CancelConfirmView(match, user_id)
    await interaction.response.send_message(
        f"Are you sure you want to cancel the match between {match.player1.username} and {match.player2.username}?",
        view=view,
        ephemeral=True
    )

async def handle_end(interaction: discord.Interaction):
    """Handle end command (mods only)"""
    # Check if user has manage messages permission (basic mod check)
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Only moderators can force-end matches!", ephemeral=True)
        return
    
    channel_id = interaction.channel_id
    match = bot.active_matches.get(channel_id)
    
    if not match:
        await interaction.response.send_message("No active match in this channel!", ephemeral=True)
        return
    
    # End the match
    del bot.active_matches[channel_id]
    
    embed = discord.Embed(
        title="🛑 Match Ended",
        description=f"Match between {match.player1.username} and {match.player2.username} was ended by a moderator.",
        color=discord.Color.red()
    )
    
    await interaction.response.send_message(embed=embed)

class CancelConfirmView(discord.ui.View):
    def __init__(self, match: Match, user_id: int):
        super().__init__(timeout=30)
        self.match = match
        self.user_id = user_id
    
    @discord.ui.button(label="Yes, Cancel Match", style=discord.ButtonStyle.danger)
    async def confirm_cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Only the person who initiated the cancel can confirm!", ephemeral=True)
            return
        
        # Cancel the match
        del bot.active_matches[self.match.channel_id]
        
        embed = discord.Embed(
            title="❌ Match Cancelled",
            description=f"Match between {self.match.player1.username} and {self.match.player2.username} was cancelled.",
            color=discord.Color.red()
        )
        
        await interaction.response.edit_message(content=None, embed=embed, view=None)
    
    @discord.ui.button(label="No, Keep Playing", style=discord.ButtonStyle.secondary)
    async def cancel_cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Only the person who initiated the cancel can confirm!", ephemeral=True)
            return
        
        await interaction.response.edit_message(content="Match continues!", view=None)

def format_options(no_repeat: bool, adjacency_mod: bool, bait_switch: bool) -> str:
    """Format match options for display"""
    options = []
    if no_repeat:
        options.append("No Repeat")
    if adjacency_mod:
        options.append("Adjacency Mod")
    if bait_switch:
        options.append("Bait & Switch")
    
    return ", ".join(options) if options else "Standard"

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token.")
        exit(1)
    
    bot.run(token)
