import os
import re
from datetime import timedelta
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
user_warnings = {}
BAD_WORDS = ["abusiveword1", "badword2", "spamlink.com"]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('Bot is ready on Discloud for 24/7 moderation!')

@bot.command(name='join')
async def join_vc(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"🔊 Joined `{channel.name}`!")
    else:
        await ctx.send("❌ Aap pehle kisi Voice Channel mein join kijiye.")

@bot.command(name='leave')
async def leave_vc(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Voice Channel se leave kar diya.")
    else:
        await ctx.send("❌ Main kisi Voice Channel mein nahi hun.")

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick_user(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 **{member.display_name}** ko kick kar diya gaya. Reason: {reason}")

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban_user(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 **{member.display_name}** ko ban kar diya gaya. Reason: {reason}")

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 {amount} messages saaf kar diye gaye!", delete_after=3)

@bot.command(name='timeout')
@commands.has_permissions(moderate_members=True)
async def timeout_user(ctx, member: discord.Member, minutes: int, *, reason="Rule violation"):
    duration = timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"🔇 **{member.display_name}** ko {minutes} minute ke liye mute/timeout kar diya gaya.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content_lower = message.content.lower()
    contains_bad_word = any(word in content_lower for word in BAD_WORDS)
    is_excessive_caps = len(message.content) > 10 and sum(1 for c in message.content if c.isupper()) / len(message.content) > 0.7

    if contains_bad_word or is_excessive_caps:
        await message.delete()
        user_id = message.author.id
        user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
        warn_count = user_warnings[user_id]

        if warn_count == 1:
            await message.channel.send(
                f"⚠️ {message.author.mention}, Discord server rules mat todiye! (Warning 1/3)",
                delete_after=5
            )
        elif warn_count == 2:
            try:
                await message.author.timeout(timedelta(minutes=10), reason="Repeated Rule Violation")
                await message.channel.send(
                    f"🔇 {message.author.mention} ko 10 minutes ke liye timeout kiya gaya rules todne par. (Warning 2/3)"
                )
            except Exception as e:
                print(f"Error executing timeout: {e}")
        elif warn_count >= 3:
            try:
                await message.author.kick(reason="Automated Penalty: 3 Rule Violations")
                await message.channel.send(
                    f"🚨 {message.author.display_name} ko repeated rule violations ke karan kick kar diya gaya."
                )
                user_warnings[user_id] = 0
            except Exception as e:
                print(f"Error executing kick: {e}")

    await bot.process_commands(message)

if __name__ == "__main__":
    # Token directly embedded here
    bot.run("MTU1OTEyNDI4MTI0MDMzMDI4MQ.GPI1ey.gM-ZCir1tsjysZ_S2BuB9uRefoimK8tIavfILk")
