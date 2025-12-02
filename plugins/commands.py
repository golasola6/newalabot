import os
import logging
import random
import asyncio
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import *
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_bad_files
from database.users_chats_db import db
from info import *
from utils import get_settings, get_size, is_req_subscribed, save_group_settings, temp, verify_user, check_token, check_verification, get_token, get_shortlink, get_tutorial, is_subscribed, lazy_has_subscribed, to_small_caps
from database.connections_mdb import active_connection
import re, asyncio, os, sys
import json
import base64
logger = logging.getLogger(__name__)
import pytz  # Make sure to handle timezone correctly
timezone = pytz.timezone("Asia/Kolkata")
import datetime
from math import ceil

BATCH_FILES = {}
DUMPLAZY = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    try:
        user_id = message.from_user.id
        if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            buttons = [[
                        InlineKeyboardButton('⤬ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                    ],[
                        InlineKeyboardButton('Aᴅᴢ Fʀᴇᴇ Mᴏᴠɪᴇꜱ ✅', callback_data='buy_premium'),
                        InlineKeyboardButton('✇ Jᴏɪɴ Oᴜʀ Cʜᴀɴɴᴇʟꜱ ✇', callback_data='main_channel')
                    ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            m=await message.reply_text("<i><b>ʜᴇʟʟᴏ. ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ \nᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ ʙʀᴏ . . .</b></i>")
            await m.edit_text("<b><i>ꜱᴛᴀʀᴛɪɴɢ...</i></b>")
            await asyncio.sleep(0.4)
            await m.delete()
            m=await message.reply_sticker("CAACAgUAAxkBAAEJ4GtkyPgEzpIUC_DSmirN6eFWp4KInAACsQoAAoHSSFYub2D15dGHfy8E")
            await asyncio.sleep(1)
            await m.delete()
            await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup, disable_web_page_preview=True)
            await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
            if not await db.get_chat(message.chat.id):
                total=await client.get_chat_members_count(message.chat.id)
                await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
                await db.add_chat(message.chat.id, message.chat.title)
            return 
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
        if len(message.command) != 2:
            buttons = [[
                InlineKeyboardButton('⤬ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
                InlineKeyboardButton('〄 Hᴇʟᴘ', callback_data='help'),
                InlineKeyboardButton('❗ Dɪꜱᴄʟᴀɪᴍᴇʀ', callback_data='copyright_info')
            ],[
                InlineKeyboardButton('💰 Buy Premium', callback_data='buy_premium'),
                InlineKeyboardButton('⍟ Aʙᴏᴜᴛ', callback_data='about')
            ],[
                InlineKeyboardButton('✇ Jᴏɪɴ Oᴜʀ Cʜᴀɴɴᴇʟꜱ ✇', callback_data='main_channel')
            ],
            [
                InlineKeyboardButton('Eᴀʀɴ Mᴏɴᴇʏ 💸', callback_data="shortlink_info")
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            m=await message.reply_text("<i><b>ʜᴇʟʟᴏ. ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ \nᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ ʙʀᴏ . . .</b></i>")
            await m.edit_text("<b><i>ꜱᴛᴀʀᴛɪɴɢ...</i></b>")
            await asyncio.sleep(0.4)
            await m.delete()
            m=await message.reply_sticker("CAACAgUAAxkBAAEJ4GtkyPgEzpIUC_DSmirN6eFWp4KInAACsQoAAoHSSFYub2D15dGHfy8E")
            await asyncio.sleep(1)
            await m.delete()
            await message.reply_photo(
                photo=random.choice(PICS),
                caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return

        if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help", "buy_premium"]:
            if message.command[1] == "buy_premium":
                btn = [[
                    InlineKeyboardButton('💸 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ 💸', url=USERNAME)
                ],[
                    InlineKeyboardButton('🗑 ᴄᴀɴᴄᴇʟ ᴘʀᴇᴍɪᴜᴍ 🗑', callback_data='close_data')
                ]]            
                await message.reply_text(
                    text=script.PREMIUM_TXT,
                    reply_markup=InlineKeyboardMarkup(btn),
                )
                return
        
        # if AUTH_CHANNEL and not await is_req_subscribed(client, message):
        #     try:
        #         invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL), creates_join_request=True)
        #     except ChatAdminRequired:
        #         logger.error("Make sure Bot is admin in Forcesub channel")
        #         return
        #     btn = [
        #         [
        #             InlineKeyboardButton(
        #                 "📢 REQUEST TO JOIN CHANNEL 1 📢", url=invite_link.invite_link
        #             )
        #         ],
        #         [
        #             InlineKeyboardButton(
        #                 "📢 REQUEST TO JOIN FOLDER 📢", url="https://t.me/addlist/Dwkw-BxEjkg4MmI1"
        #             )
        #         ],
                
        #     ]

        #     if message.command[1] != "subscribe":
        #         try:
        #             kk, file_id = message.command[1].split("_", 1)
        #             btn.append([InlineKeyboardButton("🔃 TRY AGAIN 🔃", callback_data=f"checksub#{kk}#{file_id}")])
        #         except (IndexError, ValueError):
        #             btn.append([InlineKeyboardButton("🔃 TRY AGAIN 🔃", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        #     await client.send_message(
        #         chat_id=message.from_user.id,
        #         text="**Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ɪɴ ᴏᴜʀ Bᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ sᴏ ʏᴏᴜ ᴅᴏɴ'ᴛ ɢᴇᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇ...\n\nIғ ʏᴏᴜ ᴡᴀɴᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇ, ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ 👇\n'📢 REQUEST TO JOIN CHANNEL 📢'\n'📢 REQUEST TO JOIN FOLDER 📢'\n ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴀɴᴅ ᴊᴏɪɴ ᴏᴜʀ ʙᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟ, ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ '🔃 TRY AGAIN 🔃' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ...\n\nTʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇs...**",
        #         reply_markup=InlineKeyboardMarkup(btn),
        #         parse_mode=enums.ParseMode.MARKDOWN
        #         )
        #     return
        if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
            buttons = [[
                InlineKeyboardButton('⤬ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
                InlineKeyboardButton('〄 Hᴇʟᴘ', callback_data='help'),
                InlineKeyboardButton('❗ Dɪꜱᴄʟᴀɪᴍᴇʀ', callback_data='copyright_info')
            ],[
                InlineKeyboardButton('💰 Buy Premium', callback_data='buy_premium'),
                InlineKeyboardButton('⍟ Aʙᴏᴜᴛ', callback_data='about')
            ],[
                InlineKeyboardButton('✇ Jᴏɪɴ Oᴜʀ Cʜᴀɴɴᴇʟꜱ ✇', callback_data='main_channel')
            ],
            [
                InlineKeyboardButton('Eᴀʀɴ Mᴏɴᴇʏ 💸', callback_data="shortlink_info")
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)      
            await message.reply_photo(
                photo=random.choice(PICS),
                caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return
        data = message.command[1]
        try:
            pre, file_id = data.split('_', 1)
        except:
            file_id = data
            pre = ""

# ==========================🚧 BARIER 1 🚧 ==========================================
        
        if AUTH_CHANNEL and not await lazy_has_subscribed(client, message):
            lazydeloper = 0
            lazybuttons = []
            for channel in AUTH_CHANNEL:
                lazydeloper = lazydeloper + 1
                try:
                    invite_link = await client.create_chat_invite_link(int(channel), creates_join_request=False)
                except ChatAdminRequired:
                    logger.error("Initail Force Sub is not working because of ADMIN ISSUE. Please make me admin there 🚩")
                    return
                lazybuttons.append([
                            InlineKeyboardButton(text=f"🚩 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ {lazydeloper} •", url=invite_link.invite_link),
                            ])

            if message.command[1] != "subscribe":
                try:
                    kk, file_id = message.command[1].split("_", 1)
                    pre = 'checksubp' if kk == 'filep' else 'checksub' 
                    lazybuttons.append([InlineKeyboardButton(f"𓆩ཫ♻ • {to_small_caps('Click To Verify')} • ♻ཀ𓆪", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
                except (IndexError, ValueError):
                    lazybuttons.append([InlineKeyboardButton(f"𓆩ཫ♻ • {to_small_caps('Click To Verify')} • ♻ཀ𓆪", callback_data=f"{pre}#{file_id}")])
            await client.send_message(
                chat_id=message.from_user.id,
                text=f"{script.FORCESUB_MSG.format(message.from_user.mention)}",
                reply_markup=InlineKeyboardMarkup(lazybuttons),
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
                )
            return            
# ====================================================================

# ====================================================================
        #6 => verification_steps ! [Youtube@LazyDeveloperr]
        # elif data.split("-", 1)[0] == "verify":
        #     userid = data.split("-", 2)[1]
        #     user_ids = message.from_user.id
        #     prex = DUMPLAZY[user_ids]["pre"]  
        #     lazy_file_id = DUMPLAZY[user_ids]["file_id"]
        #     # print(prex)
        #     # print(lazy_file_id)
        #     token = data.split("-", 3)[2]
        #     if str(message.from_user.id) != str(userid):
        #         return await message.reply_text(
        #             text="<b>Invalid link or Expired link !</b>",
        #             protect_content=True
        #         )
        #     is_valid = await check_token(client, userid, token)
        #     if is_valid == True:
        #         await message.reply_text(
        #             text=f"<b>Hey {message.from_user.mention}, You are successfully verified !\nNow you have unlimited access for all movies till today midnight.</b>",
        #             reply_markup=InlineKeyboardMarkup([[
        #                 InlineKeyboardButton("📺 GET FILE ✔", url=f"https://telegram.me/{temp.U_NAME}?start={prex}_{lazy_file_id}")
        #             ]]),
        #             protect_content=True
        #         )
        #         try:
        #             await verify_user(client, userid, token)
        #         except Exception as Lazy:
        #             print(Lazy)
        #     else:
        #         return await message.reply_text(
        #             text="<b>Invalid link or Expired link !</b>",
        #             protect_content=True
        #         )
        
# ====================================================================
        lzy = message.from_user.first_name
        
        daily_limit, subscription, assigned_channels, joined_channels = await lazybarier(client, lzy, user_id)
        
# ==========================🚧 BARIER 2 🚧 ==========================================
        # if pre != "" and file_id != "requestmovie":
        if data.startswith("grantfreevip"):
            # daily_limit, subscription, assigned_channels, _= await lazybarier(client, lzy, user_id)
            # Limit free users to 3 videos per day
            print('pass 1')
            if subscription == "free" and daily_limit <= 0:
                try:
                    print('pass 2')
                    lazybtn = []
                    lazydeloper = 0
                    for channel in assigned_channels:
                        if await is_subscribed(client, channel, user_id):
                            await db.users.update_one(
                                    {"id": user_id},
                                    {"$addToSet": {"joined_channels": channel}},  # Append channel if not already present
                                    upsert=True
                                )
                            updated_data = await db.get_user(user_id)
                            joined_channels = set(updated_data.get("joined_channels", []))
                            if assigned_channels.issubset(joined_channels):
                                expiry_time = datetime.datetime.now(timezone) + datetime.timedelta(hours=MAX_SUBSCRIPTION_TIME)  # 24 hours from now
                                expiry_str = expiry_time.strftime("%Y-%m-%d %H:%M:%S")  # Format as YYYY-MM-DD HH:MM:SS
                                await db.update_user({"id": message.from_user.id, "subscription": "limited", "subscription_expiry": expiry_str})
                                msg = await client.send_message(
                                                    user_id,
                                                    f"{script.VERIFIED_TEXT.format(message.from_user.mention,MAX_SUBSCRIPTION_TIME, expiry_str)}",
                                                    parse_mode=enums.ParseMode.HTML,
                                                    disable_web_page_preview=True
                                                )
                        else:
                            lazydeloper = lazydeloper + 1
                            invite_link = await client.create_chat_invite_link(int(channel), creates_join_request=True)
                            lazybtn.append([
                                    InlineKeyboardButton(f"{to_small_caps('🚩 Join Channel')} {lazydeloper}", url=invite_link.invite_link),
                                    ]) # bahut deemag khraab hua h is feature ko add krne mei #lazydeveloper 😢
                    print('pass 3')
                    lazy_updated_data = await db.get_user(user_id)
                    lazy_joined_channels = set(lazy_updated_data.get("joined_channels", []))
                    if not assigned_channels.issubset(lazy_joined_channels):
                        if message.command[1] != "subscribe":
                            try:
                                kk, file_id = message.command[1].split("_", 1)
                                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                                lazybtn.append([InlineKeyboardButton(f"𓆩ཫ♻ • {to_small_caps('Click To Verify')} • ♻ཀ𓆪", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
                            except (IndexError, ValueError):
                                lazybtn.append([InlineKeyboardButton(f"♻ ♡ • {to_small_caps('Click To Verify')} • ♡ ♻", callback_data=f"{pre}#{file_id}")])

                        # 

                        lazz = await message.reply_text(to_small_caps(script.UPGRADE_TEXT),
                                reply_markup=InlineKeyboardMarkup(lazybtn)
                                    )
                        LAZYCONTAINER[user_id] = {
                                "lazymsg": lazz,
                                "file_id": file_id,
                                "the_one&only_LazyDeveloper": True
                            }
                    return
                except Exception as e:
                    logging.info(f"Error in Barier: {e}")
                    return await message.reply(f"{script.FAILED_VERIFICATION_TEXT}")                

# ===========================[ ❤ PASS 🚀 ]======================================
        
        elif data.startswith("sendfiles"):
            try:
                userid = message.from_user.id if message.from_user else None
                chat_id = message.chat.id
                lzy = message.from_user.first_name
                files_ = await get_file_details(file_id)
                files = files_[0]
                if subscription == "free" and daily_limit <= 0:
                    # ghost_url = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=files_{file_id}")
                    lazyfile = await client.send_message(
                        chat_id=userid,
                        text=f"😱Oh no! {message.from_user.mention} 💔.\n{to_small_caps(script.EXPIRED_TEXT)}\n\n📺 ꜰɪʟᴇ ɴᴀᴍᴇ : <code>{files.file_name}</code> \n\n🫧 ꜰɪʟᴇ ꜱɪᴢᴇ : <code>{get_size(files.file_size)}</code>\n\n{to_small_caps('🚩GET #File Access ✔')}",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                # [
                                #     InlineKeyboardButton(f"{to_small_caps('📁 Continue with ADS 📁')}", url=ghost_url)
                                # ],
                                [
                                    InlineKeyboardButton("𓆩ཫ♥ • Get File Acccess • ♥ཀ𓆪", callback_data=f"grantfreevip#{file_id}")
                                ]
                            ]
                        )
                        )
                    await asyncio.sleep(1000)
                    await lazyfile.edit("<b>Your message is successfully deleted!!!</b>")
                    return
                else:
                    print(f"passed for {userid} ==> daily_limit ==> {daily_limit}")
                    pass
            except Exception as e:
                logging.info(f"Error handling sendfiles: {e}")
                return
        
        
        # ==============================
        if data.split("-", 1)[0] == "BATCH":
            sts = await message.reply("<b>Please wait...</b>")
            file_id = data.split("-", 1)[1]
            msgs = BATCH_FILES.get(file_id)
            if not msgs:
                file = await client.download_media(file_id)
                try: 
                    with open(file) as file_data:
                        msgs=json.loads(file_data.read())
                except:
                    await sts.edit("FAILED")
                    return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
                os.remove(file)
                BATCH_FILES[file_id] = msgs
            for msg in msgs:
                title = msg.get("title")
                size=get_size(int(msg.get("size", 0)))
                f_caption=msg.get("caption", "")
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                    except Exception as e:
                        logger.exception(e)
                        f_caption=f_caption
                if f_caption is None:
                    f_caption = f"{title}"
                try:
                    # Create the inline keyboard button with callback_data
                    await client.send_cached_media(
                        chat_id=message.from_user.id,
                        file_id=msg.get("file_id"),
                        caption=f_caption,
                        protect_content=msg.get('protect', False),
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=f'https://t.me/{SUPPORT_CHAT}'),
                                    InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                                ],[
                                    InlineKeyboardButton('𝗕𝗢𝗧 𝗢𝗪𝗡𝗘𝗥', url=f'https://t.me/Simplifytuber2')
                                ],
                                [
                                    InlineKeyboardButton('🚀 Fast Download / Watch Online🖥️', callback_data=f'generate_stream_link:{file_id}') #Don't change anything without contacting me @Simplifytuber2
                                ]
                            ]
                        )
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    logger.warning(f"Floodwait of {e.x} sec.")
                    await client.send_cached_media(
                        chat_id=message.from_user.id,
                        file_id=msg.get("file_id"),
                        caption=f_caption,
                        protect_content=msg.get('protect', False),
                        reply_markup=InlineKeyboardMarkup(
                            [
                            [
                            InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=f'https://t.me/{SUPPORT_CHAT}'),
                            InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                        ],[
                            InlineKeyboardButton("𝗕𝗢𝗧 𝗢𝗪𝗡𝗘𝗥", url=f'https://t.me/Simplifytuber2')
                            ],[ 
                                InlineKeyboardButton('🚀 Fast Download / Watch Online🖥️', callback_data=f'generate_stream_link:{file_id}') #Don't change anything without contacting me @Simplifytuber2
                                ]
                            ]
                        )
                    )
                except Exception as e:
                    logger.warning(e, exc_info=True)
                    continue
                await asyncio.sleep(1) 
            await sts.delete()
            return
        
        elif data.split("-", 1)[0] == "DSTORE":
            sts = await message.reply("<b>Please wait...</b>")
            b_string = data.split("-", 1)[1]
            decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
            try:
                f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
            except:
                f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
                protect = "/pbatch" if PROTECT_CONTENT else "batch"
            diff = int(l_msg_id) - int(f_msg_id)
            async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
                if msg.media:
                    media = getattr(msg, msg.media.value)
                    if BATCH_FILE_CAPTION:
                        try:
                            f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                        except Exception as e:
                            logger.exception(e)
                            f_caption = getattr(msg, 'caption', '')
                    else:
                        media = getattr(msg, msg.media.value)
                        file_name = getattr(media, 'file_name', '')
                        f_caption = getattr(msg, 'caption', file_name)
                    try:
                        await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                    except Exception as e:
                        logger.exception(e)
                        continue
                elif msg.empty:
                    continue
                else:
                    try:
                        await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
                        await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                    except Exception as e:
                        logger.exception(e)
                        continue
                await asyncio.sleep(1) 
            return await sts.delete()

        elif data.split("-", 1)[0] == "verify":
            userid = data.split("-", 2)[1]
            token = data.split("-", 3)[2]
            if str(message.from_user.id) != str(userid):
                return await message.reply_text(
                    text="<b>Invalid link or Expired link !</b>",
                    protect_content=True
                )
            is_valid = await check_token(client, userid, token)
            if is_valid == True:
                await message.reply_text(
                    text=f"<b>Hᴇʏ {message.from_user.mention}, Yᴏᴜ ᴀʀᴇ sᴜᴄᴄᴇssғᴜʟʟʏ ᴠᴇʀɪғɪᴇᴅ !\nNᴏᴡ ʏᴏᴜ ʜᴀᴠᴇ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇss ғᴏʀ ᴀʟʟ ᴍᴏᴠɪᴇs ᴛɪʟʟ ᴛʜᴇ ɴᴇxᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴡʜɪᴄʜ ɪs ᴀғᴛᴇʀ 12 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ.</b>",
                    protect_content=True
                )
                await verify_user(client, userid, token)
            else:
                return await message.reply_text(
                    text="<b>Invalid link or Expired link !</b>",
                    protect_content=True
                )

        elif data.startswith("short"):
            user = message.from_user.id
            chat_id = temp.SHORT.get(user)
            files_ = await get_file_details(file_id)
            files = files_[0]
            g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")
            k = await client.send_message(chat_id=user,text=f"<b>🍟Nᴀᴍᴇ ➠ : <code>{files.file_name}</code> \n\n🔗Sɪᴢᴇ ➠ : {get_size(files.file_size)}\n\n📂Fɪʟᴇ ʟɪɴᴋ ➠ : {g}\n\n<i>Note: This message is deleted in 20 minutes to avoid copyrights. Save the link to Somewhere else</i></b>", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton('📂 Dᴏᴡɴʟᴏᴀᴅ Nᴏᴡ 📂', url=g)
                        ], [
                            InlineKeyboardButton('⁉️ Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ ⁉️', url=await get_tutorial(chat_id))
                        ]
                    ]
                )
            )
            await asyncio.sleep(1000)
            await k.edit("<b>Your message is successfully deleted!!!</b>")
            return
            
        elif data.startswith("all"):
            files = temp.GETALL.get(file_id)
            if not files:
                return await message.reply('<b><i>No such file exist.</b></i>')
            filesarr = []
            for file in files:
                file_id = file.file_id
                files_ = await get_file_details(file_id)
                files1 = files_[0]
                title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1.file_name.split()))
                size=get_size(files1.file_size)
                f_caption=files1.caption
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                    except Exception as e:
                        logger.exception(e)
                        f_caption=f_caption
                if f_caption is None:
                    f_caption = f"{' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1.file_name.split()))}"
                if TOKEN_VERIFICATION and not await check_verification(client, message.from_user.id):
                    btn = [[
                        InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=")),
                        InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url='https://t.me/moviesimplyfytuber')
                    ]]
                    await message.reply_text(
                        text="<b>Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ!\nKɪɴᴅʟʏ ᴠᴇʀɪғʏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ Sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴀᴄᴄᴇss ᴛᴏ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇs ᴜɴᴛɪʟ 12 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ !</b>",
                        protect_content=True,
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    return
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if pre == 'filep' else False,
                    reply_markup=(
                        InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton("𝗕𝗢𝗧 𝗢𝗪𝗡𝗘𝗥", url=f'https://t.me/Simplifytuber2')
                                ],[
                                    InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=f'https://t.me/{SUPPORT_CHAT}'),
                                    InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                                ],[
                                    InlineKeyboardButton('🚀 Fast Download / Watch Online🖥️', callback_data=f'generate_stream_link:{file_id}') #Don't change anything without contacting me @Simplifytuber2
                                ]
                            ]
                        )
                        if user not in PREMIUM_USER 
                        else InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=f'https://t.me/{SUPPORT_CHAT}'),
                                    InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                                ],[
                                    InlineKeyboardButton('🚀 Fast Download / Watch Online🖥️', callback_data=f'generate_stream_link:{file_id}') #Don't change anything without contacting me @Simplifytuber2
                                ]
                            ]
                        )
                    )
                )
                filesarr.append(msg)
            
            #finally - overacting ka 1 rupees kaat lo 💘😊
            if subscription !="limited":
                await db.deduct_limit(user_id)
                # logging.info(f"\n\n::::::::::>> Tried to Deduct limit for user [{message.from_user.first_name}] :|::> ID ::> {user_id} :|::> AT : {datetime.datetime.now()}")
            else:
                pass
                # logging.info(f"\n\nFailed to deduct limit for user ::> [{message.from_user.first_name}] :| ID ::> {user_id} :|::> ERROR AT :  {datetime.datetime.now()}")

            k = await client.send_message(chat_id = message.from_user.id, text=f"<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie Files/Videos will be deleted in <b><u>20 minutes</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this ALL Files/Videos to your Saved Messages and Start Download there</i></b>")
            await asyncio.sleep(1200)
            for x in filesarr:
                await x.delete()
            await k.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")
            return    
            
        elif data.startswith("files"):
            user = message.from_user.id
            if temp.SHORT.get(user)==None:
                await message.reply_text(text="<b>Please Search Again in Group</b>")
            else:
                chat_id = temp.SHORT.get(user)
            settings = await get_settings(chat_id)
            if settings['is_shortlink'] and user not in PREMIUM_USER:
                files_ = await get_file_details(file_id)
                files = files_[0]
                g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")
                k = await client.send_message(chat_id=message.from_user.id,text=f"<b>📕Nᴀᴍᴇ ➠ : <code>{files.file_name}</code> \n\n🔗Sɪᴢᴇ ➠ : {get_size(files.file_size)}\n\n📂Fɪʟᴇ ʟɪɴᴋ ➠ : {g}\n\n<i>Note: This message is deleted in 20 minutes to avoid copyrights. Save the link to Somewhere else</i></b>", reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton('📂 Dᴏᴡɴʟᴏᴀᴅ Nᴏᴡ 📂', url=g)
                            ], [
                                InlineKeyboardButton('⁉️ Hᴏᴡ Tᴏ Dᴏᴡɴʟᴏᴀᴅ ⁉️', url=await get_tutorial(chat_id))
                            ]
                        ]
                    )
                )
                await asyncio.sleep(1199)
                await k.edit("<b>Your message is successfully deleted!!!</b>")
                return
        user = message.from_user.id
        files_ = await get_file_details(file_id)           
        if not files_:
            pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
            try:
                if TOKEN_VERIFICATION and not await check_verification(client, message.from_user.id):
                    btn = [[
                        InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=")),
                        InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url='https://t.me/moviesimplyfytuber')
                    ]]
                    await message.reply_text(
                        text="<b>Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ!\nKɪɴᴅʟʏ ᴠᴇʀɪғʏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ Sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴀᴄᴄᴇss ᴛᴏ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇs ᴜɴᴛɪʟ 12 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ !</b>",
                        protect_content=True,
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    return
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file_id,
                    protect_content=True if pre == 'filep' else False,
                    reply_markup=(
                        InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton("𝗕𝗢𝗧 𝗢𝗪𝗡𝗘𝗥", url=f'https://t.me/Simplifytuber2')
                                ],[
                                    InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=f'https://t.me/{SUPPORT_CHAT}'),
                                    InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                                ],[
                                    InlineKeyboardButton('🚀 Fast Download / Watch Online🖥️', callback_data=f'generate_stream_link:{file_id}') #Don't change anything without contacting me @Simplifytuber2
                                ]
                            ]
                        )
                        if user not in PREMIUM_USER
                        else InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=f'https://t.me/{SUPPORT_CHAT}'),
                                    InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                                ],[
                                    InlineKeyboardButton('🚀 Fast Download / Watch Online🖥️', callback_data=f'generate_stream_link:{file_id}') #Don't change anything without contacting me @Simplifytuber2
                                ]
                            ]
                        )
                    )
                )

                filetype = msg.media
                file = getattr(msg, filetype.value)
                title = '@moviesimplyfytuber' + ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), file.file_name.split()))
                size=get_size(file.file_size)
                f_caption = f"<code>{title}</code>"
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                    except:
                        return
                await msg.edit_caption(f_caption)
                btn = [[
                    InlineKeyboardButton("Get File Again", callback_data=f'delfile#{file_id}')
                ]]
                k = await msg.reply("<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>20 minutes</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</i></b>",quote=True)
                await asyncio.sleep(1200)
                await msg.delete()
                await k.edit_text("<b>Your File/Video is successfully deleted!!!\n\nClick below button to get your deleted file 👇</b>",reply_markup=InlineKeyboardMarkup(btn))
                return
            except:
                pass
            return await message.reply('No such file exist.')
        files = files_[0]
        title = '@moviesimplyfytuber  ' + ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files.file_name.split()))
        size=get_size(files.file_size)
        f_caption=files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption=f_caption
        if f_caption is None:
            f_caption = f"@moviesimplyfytuber  {' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files.file_name.split()))}"
        if TOKEN_VERIFICATION and not await check_verification(client, message.from_user.id):
            btn = [[
                InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=")),
                InlineKeyboardButton("Hᴏᴡ Tᴏ Vᴇʀɪғʏ", url='https://t.me/moviesimplyfytuber')            
            ]]
            await message.reply_text(
                text="<b>Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴠᴇʀɪғɪᴇᴅ!\nKɪɴᴅʟʏ ᴠᴇʀɪғʏ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ Sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴀᴄᴄᴇss ᴛᴏ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇs ᴜɴᴛɪʟ 12 ʜᴏᴜʀs ғʀᴏᴍ ɴᴏᴡ !</b>",
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            return
        msg = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if pre == 'filep' else False,
            reply_markup=(
                InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("𝗕𝗢𝗧 𝗢𝗪𝗡𝗘𝗥", url=f'https://t.me/Simplifytuber2')
                        ],[
                            InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=f'https://t.me/{SUPPORT_CHAT}'),
                            InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                        ],[
                            InlineKeyboardButton('🚀 Fast Download / Watch Online🖥️', callback_data=f'generate_stream_link:{file_id}') #Don't change anything without contacting me @Simplifytuber2
                        ]
                    ]
                )
                if user not in PREMIUM_USER
                else InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=f'https://t.me/{SUPPORT_CHAT}'),
                            InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                        ],[
                            InlineKeyboardButton('🚀 Fast Download / Watch Online🖥️', callback_data=f'generate_stream_link:{file_id}') #Don't change anything without contacting me @Simplifytuber2
                        ]
                    ]
                )
            )
        )
        
        
        #finally - overacting ka 1 rupees kaat lo 💘😊
        if subscription !="limited":
            await db.deduct_limit(user_id)
            # logging.info(f"\n\n::::::::::>> Tried to Deduct limit for user [{message.from_user.first_name}] :|::> ID ::> {user_id} :|::> AT : {datetime.datetime.now()}")
        else:
            pass
            # logging.info(f"\n\nFailed to deduct limit for user ::> [{message.from_user.first_name}] :| ID ::> {user_id} :|::> ERROR AT :  {datetime.datetime.now()}")

        btn = [[
            InlineKeyboardButton("Get File Again", callback_data=f'delfile#{file_id}')
        ]]
        k = await msg.reply("<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\nThis Movie File/Video will be deleted in <b><u>20 minutes</u> 🫥 <i></b>(Due to Copyright Issues)</i>.\n\n<b><i>Please forward this File/Video to your Saved Messages and Start Download there</i></b>",quote=True)
        await asyncio.sleep(1200)
        await msg.delete()
        await k.edit_text("<b>Your File/Video is successfully deleted!!!\n\nClick below button to get your deleted file 👇</b>",reply_markup=InlineKeyboardMarkup(btn))
        return
    except Exception as Lazyerr:
        print(Lazyerr)

# 
async def lazybarier(bot, l, user_id):
    print('br 1')
    user = await db.get_user(user_id) # user ko database se call krna h
    all_channels = await db.get_required_channels()
    # if isinstance(AUTH_CHANNEL, int):  
    #     all_channels.append(AUTH_CHANNEL)  # Lazy  
    # else:
    #     all_channels.extend(AUTH_CHANNEL)  # Lazy  
    temp.ASSIGNED_CHANNEL = all_channels
    # 
    if not user:
        joined_channels = set()
        for channel in all_channels:
            if await is_subscribed(bot, channel, user_id):
                joined_channels.add(channel)

        today = str(datetime.date.today())
        # new_assigned_channels = set(random.sample(all_channels, 2)) #  
        # new_assigned_channels = set(sorted(all_channels, reverse=True)[:2])
        new_assigned_channels = set(sorted(set(all_channels) - joined_channels)[:2])

        attach_data = {
            "id": user_id,
            "subscription": "free",
            "subscription_expiry": None,
            "daily_limit": DAILY_LIMIT,
            "assigned_channels": list(new_assigned_channels),
            "joined_channels": list(joined_channels) ,
            "last_access": today,
        }
        await db.update_user(attach_data)
        user = await db.get_user(user_id)
    print('br 2')
    subscription = user.get("subscription", "free")
    subscription_expiry = user.get("subscription_expiry")
    daily_limit = user.get("daily_limit", DAILY_LIMIT)
    last_access = user.get("last_access")
    assigned_channels = set(user.get("assigned_channels", []))
    joined_channels = set(user.get("joined_channels", []))
    
    today = str(datetime.date.today())
    print('br 3')
    if last_access != today:
        print("ok1")
        if subscription == "free":
            for channel in all_channels:
                if await is_subscribed(bot, channel, user_id):
                    joined_channels.add(channel)
                    print("ok2")
            new_channels = set(sorted(set(all_channels) - joined_channels)[:2])
            print("ok3")
            if not new_channels:
                joined_channels = set()  # Reset joined channels
                new_channels = set(random.sample(all_channels, 2))  # Pick 2 random channels
                print(f'new channels : {new_channels}')
            print("ok4")
            data = {"id": user_id,
                    "daily_limit": DAILY_LIMIT, 
                    "last_access": today,
                    "assigned_channels": list(new_channels),
                    "joined_channels": list(joined_channels),
                    }
            print(f"data {data}")
            await db.update_user(data)
            print("ok5")
    # Check for expired subscriptions
    # sabko indian time zone ke hisab se chlna pdega #LazyDeveloper 😂
    print('br 4')
    if subscription == "limited" and subscription_expiry:
        expiry_time = datetime.datetime.strptime(subscription_expiry, "%Y-%m-%d %H:%M:%S")
        expiry_time = timezone.localize(expiry_time)  # Ensure expiry time is in UTC
        current_time = datetime.datetime.now(timezone)  # Current time in IST
        if current_time > expiry_time:
            for channel in all_channels:
                if await is_subscribed(bot, channel, user_id):
                    joined_channels.add(channel)
            new_channels = set(sorted(set(all_channels) - joined_channels)[:2])
            if not new_channels:
                joined_channels = set()  # Reset joined channels
                new_channels = set(random.sample(all_channels, 2))  # Pick 2 random channels
            usersdata = {
                "id": user_id,
                "subscription": "free", 
                "subscription_expiry": None, 
                "daily_limit": DAILY_LIMIT,
                "assigned_channels": list(new_channels),
                "joined_channels": list(joined_channels),
                }
            await db.update_user(usersdata)

    print("br 5")
    updated_data = await db.get_user(user_id)
    daily_limit = updated_data.get("daily_limit", DAILY_LIMIT)
    subscription = updated_data.get("subscription", "free")
    assigned_channels = set(updated_data.get("assigned_channels", []))
    joined_channels = set(updated_data.get("joined_channels", []))
    print('br 6')
    return daily_limit, subscription, assigned_channels,joined_channels

# async def lazybarier(bot, l, user_id):
#     user = await db.get_user(user_id) # user ko database se call krna h
#     all_channels = await db.get_required_channels()
#     # if isinstance(AUTH_CHANNEL, int):  
#     #     all_channels.append(AUTH_CHANNEL)  # Lazy  
#     # else:
#     #     all_channels.extend(AUTH_CHANNEL)  # Lazy  
#     temp.ASSIGNED_CHANNEL = all_channels
#     # 
#     if not user:
#         # joined_channels = set()
#         # for channel in all_channels:
#         #     if await is_subscribed(bot, channel, user_id):
#         #         joined_channels.add(channel)

#         today = str(datetime.date.today())
#         # new_assigned_channels = set(random.sample(all_channels, 2)) #  
#         # new_assigned_channels = set(sorted(all_channels, reverse=True)[:2])
#         # new_assigned_channels = set(sorted(set(all_channels) - joined_channels)[:2])

#         attach_data = {
#             "id": user_id,
#             "subscription": "free",
#             "subscription_expiry": None,
#             "daily_limit": DAILY_LIMIT,
#             # "assigned_channels": list(new_assigned_channels),
#             # "joined_channels": list(joined_channels) ,
#             "last_access": today,
#             "diverting_channel": None
#         }
#         await db.update_user(attach_data)
#         user = await db.get_user(user_id)
#     subscription = user.get("subscription", "free")
#     subscription_expiry = user.get("subscription_expiry")
#     daily_limit = user.get("daily_limit", DAILY_LIMIT)
#     last_access = user.get("last_access")
#     # assigned_channels = set(user.get("assigned_channels", []))
#     # joined_channels = set(user.get("joined_channels", []))
    
#     today = str(datetime.date.today())
#     if last_access != today:
#         if subscription == "free":
#             # for channel in all_channels:
#             #     if await is_subscribed(bot, channel, user_id):
#             #         joined_channels.add(channel)
#             # new_channels = set(sorted(set(all_channels) - joined_channels)[:2])
#             # if not new_channels:
#             #     joined_channels = set()  # Reset joined channels
#             #     new_channels = set(random.sample(all_channels, 2))  # Pick 2 random channels

#             data = {"id": user_id,
#                     "daily_limit": DAILY_LIMIT, 
#                     "last_access": today,
#                     # "assigned_channels": list(new_channels),
#                     # "joined_channels": list(joined_channels),
#                     }
#             await db.update_user(data)

#     # Check for expired subscriptions
#     # sabko indian time zone ke hisab se chlna pdega #LazyDeveloper 😂
#     if subscription == "limited" and subscription_expiry:
#         expiry_time = datetime.datetime.strptime(subscription_expiry, "%Y-%m-%d %H:%M:%S")
#         expiry_time = timezone.localize(expiry_time)  # Ensure expiry time is in UTC
#         current_time = datetime.datetime.now(timezone)  # Current time in IST
#         if current_time > expiry_time:
#             # print("changing expiry time")
#             # for channel in all_channels:
#             #     if await is_subscribed(bot, channel, user_id):
#             #         joined_channels.add(channel)
#             # new_channels = set(sorted(set(all_channels) - joined_channels)[:2])
#             # if not new_channels:
#             #     joined_channels = set()  # Reset joined channels
#             #     new_channels = set(random.sample(all_channels, 2))  # Pick 2 random channels
#             usersdata = {
#                 "id": user_id,
#                 "subscription": "free", 
#                 "subscription_expiry": None, 
#                 "daily_limit": DAILY_LIMIT,
#                 # "assigned_channels": list(new_channels),
#                 # "joined_channels": list(joined_channels),
#                 }
#             await db.update_user(usersdata)
#             logging.info(f"usersdata {usersdata}")

#     updated_data = await db.get_user(user_id)
#     daily_limit = updated_data.get("daily_limit", DAILY_LIMIT)
#     subscription = updated_data.get("subscription", "free")
#     assigned_channels = set(updated_data.get("assigned_channels", []))
#     joined_channels = set(updated_data.get("joined_channels", []))
#     # diverting_channel = updated_data.get("diverting_channel", None)
    
#     return daily_limit, subscription, assigned_channels, joined_channels
@Client.on_message(filters.command("reset_user") & filters.user(ADMINS))  # Only admin can use it
async def delete_user(client, message):
    try:
        # Extract user ID from the command
        if len(message.command) < 2:
            return await message.reply_text("❌ **Usage:** `/reset_user <user_id>`")
        
        target_user_id = int(message.command[1])

        # Delete user from database
        result = await db.users.delete_one({"id": target_user_id})

        if result.deleted_count > 0:
            await message.reply_text(f"✅ **User {target_user_id} has been removed from the database!**")
        else:
            await message.reply_text(f"⚠️ **User {target_user_id} not found in the database!**")

    except Exception as e:
        await message.reply_text("⚠️ **Failed to delete user. Check logs for details.**")

@Client.on_message(filters.command("approveall") & filters.user(ADMINS))  # Only admins can use it
async def approveall_user(client, message):
    try:
        if len(message.command) < 2:
            return await message.reply_text("❌ **Usage:** `/approveall <channel_id>`")

        target_channel_id = int(message.command[1])
        await message.reply(to_small_caps("Please wait...\nProcessing your request..."))
        # ✅ Get all user IDs correctly
        users = await db.get_all_joins() 
        print(users)
        approved_count = 0
        async for user in users:
            lazyidx = user.get('id')
            if lazyidx:  # ✅ Only approve users with pending requests
                try:
                    await client.approve_chat_join_request(target_channel_id, lazyidx)
                    approved_count += 1
                except:
                    pass
            else:
                print(f"⚠️ Skipped {lazyidx} (No pending request)")

        await message.reply_text(f"✅ Approved ::>> {approved_count} users")

    except Exception as e:
        print(f"⚠️ Error in approveall_user: {e}")
        await message.reply_text("💔 **Failed to approve users. Check logs for details.**")

@Client.on_message(filters.private & filters.command("add_channel") & filters.user(ADMINS))
async def setup_force_channel(client, message):
    if len(message.command) < 2:
        await message.reply("⚠️ Usage: /add_channel <channel_id>")
        return

    channel_id = message.command[1]

    # Try to insert the new channel
    inserted_channel_id = await db.add_new_required_channel(channel_id)

    if inserted_channel_id:
        await message.reply(f"✅ Channel ID: {channel_id} has been successfully added.")
    else:
        await message.reply(f"⚠️ Channel ID: {channel_id} is already in the list.")

@Client.on_message(filters.private & filters.command("remove_channel") & filters.user(ADMINS))
async def remove_force_channel(client, message):
    if len(message.command) < 2:
        await message.reply("⚠️ Usage: /remove_channel <channel_id>")
        return

    channel_id = message.command[1]

    removed = await db.remove_required_channel(channel_id)

    if removed:
        await message.reply(f"✅ Channel ID: {channel_id} has been removed successfully.")
    else:
        await message.reply(f"❌ Channel ID: {channel_id} was not found in the list.")

async def generate_channel_keyboard(client, page=1):
    channels = await db.get_required_channels()
    
    if not channels:
        return None  
    
    total_pages = ceil(len(channels) / CHANNELS_PER_PAGE)
    page = max(1, min(page, total_pages))  #lazy page bounding
    
    start = (page - 1) * CHANNELS_PER_PAGE
    end = start + CHANNELS_PER_PAGE
    keyboard = []

    for channel_id in channels[start:end]:
        try:
            chat = await client.get_chat(channel_id)
            channel_name = f"{to_small_caps(chat.title)}"
        except:
            channel_name = f"{to_small_caps('❌ADMIN❌')}"
        
        clean_channel_id = str(channel_id).replace("-100", "")  # Remove "-100"
        
        row = [
            InlineKeyboardButton(f"📢 {channel_name}", callback_data=f"info_{channel_id}"),
            InlineKeyboardButton(f"{clean_channel_id}", callback_data=f"info_{channel_id}"),
            InlineKeyboardButton("🗑 Remove", callback_data=f"remove_{channel_id}")
        ]
        keyboard.append(row)

    # Pagination buttons
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(InlineKeyboardButton(f"<", callback_data=f"page_{page-1}"))
    pagination_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="pages_info"))
    if page < total_pages:
        pagination_buttons.append(InlineKeyboardButton(f">", callback_data=f"page_{page+1}"))

    keyboard.append(pagination_buttons)  # Add pagination row

    return InlineKeyboardMarkup(keyboard)

@Client.on_message(filters.private & filters.command("list_channels") & filters.user(ADMINS))
async def list_required_channels(client, message):
    try:
        keyboard = await generate_channel_keyboard(client, page=1)
        
        if not keyboard:
            await message.reply("⚠️ No required channels found.")
            return
        
        await message.reply("📌 **Required Channels:**", reply_markup=keyboard)
    except Exception as e:
        logging.info(e)

@Client.on_callback_query(filters.regex(r"^(page|remove|info)_(.+)"))
async def callback_handler(client, query):
    action, data = query.data.split("_", 1)

    if action == "page":
        page = int(data)
        keyboard = await generate_channel_keyboard(client, page)
        
        if keyboard:
            await query.message.edit_reply_markup(reply_markup=keyboard)  
    elif action == "info":
        channel_id = data.replace("-100", "")
        await query.answer(f"CHANNEL ID: {channel_id}", show_alert=True)

    elif action == "remove":
        channel_id = data 
        success = await db.remove_required_channel(channel_id)

        if success:
            keyboard = await generate_channel_keyboard(client, page=1)
            if keyboard:
                await query.message.edit_reply_markup(reply_markup=keyboard) 
            else:
                await query.message.edit_text("⚠️ No required channels found.")
            
            await query.answer("✅ Channel removed successfully!", show_alert=True)
        else:
            await query.answer("❌ Failed to remove the channel. Please try again.", show_alert=True)

# ======================================================

# 
@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('THALAPATHY.LOG')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not supported file format')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('File is successfully deleted from database')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('File is successfully deleted from database')
        else:
            # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('File is successfully deleted from database')
            else:
                await msg.edit('File not found in database')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="YES", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer('Piracy Is Crime')
    await message.message.edit('Succesfully Deleted All The Indexed Files.')


@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return
    
    settings = await get_settings(grp_id)

    try:
        if settings['max_btn']:
            settings = await get_settings(grp_id)
    except KeyError:
        await save_group_settings(grp_id, 'max_btn', False)
        settings = await get_settings(grp_id)
    if 'is_shortlink' not in settings.keys():
        await save_group_settings(grp_id, 'is_shortlink', False)
    else:
        pass

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton(
                    'Rᴇsᴜʟᴛ Pᴀɢᴇ',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Bᴜᴛᴛᴏɴ' if settings["button"] else 'Tᴇxᴛ',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Fɪʟᴇ Sᴇɴᴅ Mᴏᴅᴇ',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Mᴀɴᴜᴀʟ Sᴛᴀʀᴛ' if settings["botpm"] else 'Aᴜᴛᴏ Sᴇɴᴅ',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Pʀᴏᴛᴇᴄᴛ Cᴏɴᴛᴇɴᴛ',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["file_secure"] else '✘ Oғғ',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Iᴍᴅʙ',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["imdb"] else '✘ Oғғ',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Sᴘᴇʟʟ Cʜᴇᴄᴋ',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["spell_check"] else '✘ Oғғ',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Wᴇʟᴄᴏᴍᴇ Msɢ',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["welcome"] else '✘ Oғғ',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ',
                    callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '10 Mɪɴs' if settings["auto_delete"] else '✘ Oғғ',
                    callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Aᴜᴛᴏ-Fɪʟᴛᴇʀ',
                    callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["auto_ffilter"] else '✘ Oғғ',
                    callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Mᴀx Bᴜᴛᴛᴏɴs',
                    callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '10' if settings["max_btn"] else f'{MAX_B_TN}',
                    callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'ShortLink',
                    callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✔ Oɴ' if settings["is_shortlink"] else '✘ Oғғ',
                    callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
                ),
            ],
        ]

        btn = [[
                InlineKeyboardButton("Oᴘᴇɴ Hᴇʀᴇ ↓", callback_data=f"opnsetgrp#{grp_id}"),
                InlineKeyboardButton("Oᴘᴇɴ Iɴ PM ⇲", callback_data=f"opnsetpm#{grp_id}")
              ]]

        reply_markup = InlineKeyboardMarkup(buttons)
        if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            await message.reply_text(
                text="<b>Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴏᴘᴇɴ sᴇᴛᴛɪɴɢs ʜᴇʀᴇ ?</b>",
                reply_markup=InlineKeyboardMarkup(btn),
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
            )
        else:
            await message.reply_text(
                text=f"<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Sᴇᴛᴛɪɴɢs Fᴏʀ {title} As Yᴏᴜʀ Wɪsʜ ⚙</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
            )



@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    sts = await message.reply("Checking template")
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    if len(message.command) < 2:
        return await sts.edit("No Input!!")
    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"Successfully changed template for {title} to\n\n{template}")


@Client.on_message((filters.command(["request", "Request"]) | filters.regex("#request") | filters.regex("#Request")) & filters.group)
async def requests(bot, message):
    if REQST_CHANNEL is None or SUPPORT_CHAT_ID is None: return # Must add REQST_CHANNEL and SUPPORT_CHAT_ID to use this feature
    if message.reply_to_message and SUPPORT_CHAT_ID == message.chat.id:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        success = True
        content = message.reply_to_message.text
        try:
            if REQST_CHANNEL is not None:
                btn = [[
                        InlineKeyboardButton('View Request', url=f"{message.reply_to_message.link}"),
                        InlineKeyboardButton('Show Options', callback_data=f'show_option#{reporter}')
                      ]]
                reported_post = await bot.send_message(chat_id=REQST_CHANNEL, text=f"<b>𝖱𝖾𝗉𝗈𝗋𝗍𝖾𝗋 : {mention} ({reporter})\n\n𝖬𝖾𝗌𝗌𝖺𝗀𝖾 : {content}</b>", reply_markup=InlineKeyboardMarkup(btn))
                success = True
            elif len(content) >= 3:
                for admin in ADMINS:
                    btn = [[
                        InlineKeyboardButton('View Request', url=f"{message.reply_to_message.link}"),
                        InlineKeyboardButton('Show Options', callback_data=f'show_option#{reporter}')
                      ]]
                    reported_post = await bot.send_message(chat_id=admin, text=f"<b>𝖱𝖾𝗉𝗈𝗋𝗍𝖾𝗋 : {mention} ({reporter})\n\n𝖬𝖾𝗌𝗌𝖺𝗀𝖾 : {content}</b>", reply_markup=InlineKeyboardMarkup(btn))
                    success = True
            else:
                if len(content) < 3:
                    await message.reply_text("<b>You must type about your request [Minimum 3 Characters]. Requests can't be empty.</b>")
            if len(content) < 3:
                success = False
        except Exception as e:
            await message.reply_text(f"Error: {e}")
            pass
        
    elif SUPPORT_CHAT_ID == message.chat.id:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        success = True
        content = message.text
        keywords = ["#request", "/request", "#Request", "/Request"]
        for keyword in keywords:
            if keyword in content:
                content = content.replace(keyword, "")
        try:
            if REQST_CHANNEL is not None and len(content) >= 3:
                btn = [[
                        InlineKeyboardButton('View Request', url=f"{message.link}"),
                        InlineKeyboardButton('Show Options', callback_data=f'show_option#{reporter}')
                      ]]
                reported_post = await bot.send_message(chat_id=REQST_CHANNEL, text=f"<b>𝖱𝖾𝗉𝗈𝗋𝗍𝖾𝗋 : {mention} ({reporter})\n\n𝖬𝖾𝗌𝗌𝖺𝗀𝖾 : {content}</b>", reply_markup=InlineKeyboardMarkup(btn))
                success = True
            elif len(content) >= 3:
                for admin in ADMINS:
                    btn = [[
                        InlineKeyboardButton('View Request', url=f"{message.link}"),
                        InlineKeyboardButton('Show Options', callback_data=f'show_option#{reporter}')
                      ]]
                    reported_post = await bot.send_message(chat_id=admin, text=f"<b>𝖱𝖾𝗉𝗈𝗋𝗍𝖾𝗋 : {mention} ({reporter})\n\n𝖬𝖾𝗌𝗌𝖺𝗀𝖾 : {content}</b>", reply_markup=InlineKeyboardMarkup(btn))
                    success = True
            else:
                if len(content) < 3:
                    await message.reply_text("<b>You must type about your request [Minimum 3 Characters]. Requests can't be empty.</b>")
            if len(content) < 3:
                success = False
        except Exception as e:
            await message.reply_text(f"Error: {e}")
            pass

    else:
        success = False
    
    if success:
        '''if isinstance(REQST_CHANNEL, (int, str)):
            channels = [REQST_CHANNEL]
        elif isinstance(REQST_CHANNEL, list):
            channels = REQST_CHANNEL
        for channel in channels:
            chat = await bot.get_chat(channel)
        #chat = int(chat)'''
        link = await bot.create_chat_invite_link(int(REQST_CHANNEL))
        btn = [[
                InlineKeyboardButton('Join Channel', url=link.invite_link),
                InlineKeyboardButton('View Request', url=f"{reported_post.link}")
              ]]
        await message.reply_text("<b>Your request has been added! Please wait for some time.\n\nJoin Channel First & View Request</b>", reply_markup=InlineKeyboardMarkup(btn))
    
@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_msg(bot, message):
    if message.reply_to_message:
        target_id = message.text.split(" ", 1)[1]
        out = "Users Saved In DB Are:\n\n"
        success = False
        try:
            user = await bot.get_users(target_id)
            users = await db.get_all_users()
            async for usr in users:
                out += f"{usr['id']}"
                out += '\n'
            if str(user.id) in str(out):
                await message.reply_to_message.copy(int(user.id))
                success = True
            else:
                success = False
            if success:
                await message.reply_text(f"<b>Your message has been successfully send to {user.mention}.</b>")
            else:
                await message.reply_text("<b>This user didn't started this bot yet !</b>")
        except Exception as e:
            await message.reply_text(f"<b>Error: {e}</b>")
    else:
        await message.reply_text("<b>Use this command as a reply to any message using the target chat id. For eg: /send userid</b>")

@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot, message):
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, This command won't work in groups. It only works on my PM !</b>")
    else:
        pass
    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, Give me a keyword along with the command to delete files.</b>")
    k = await bot.send_message(chat_id=message.chat.id, text=f"<b>Fetching Files for your query {keyword} on DB... Please wait...</b>")
    files, total = await get_bad_files(keyword)
    await k.delete()
    #await k.edit_text(f"<b>Found {total} files for your query {keyword} !\n\nFile deletion process will start in 5 seconds !</b>")
    #await asyncio.sleep(5)
    btn = [[
       InlineKeyboardButton("Yes, Continue !", callback_data=f"killfilesdq#{keyword}")
       ],[
       InlineKeyboardButton("No, Abort operation !", callback_data="close_data")
    ]]
    await message.reply_text(
        text=f"<b>Found {total} files for your query {keyword} !\n\nDo you want to delete?</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("shortlink"))
async def shortlink(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Turn off anonymous admin and try again this command")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, This command only works on groups !\n\n<u>Follow These Steps to Connect Shortener:</u>\n\n1. Add Me in Your Group with Full Admin Rights\n\n2. After Adding in Grp, Set your Shortener\n\nSend this command in your group\n\n—> /shortlink ""{your_shortener_website_name} {your_shortener_api}\n\n#Sample:-\n/shortlink kpslink.in CAACAgUAAxkBAAEJ4GtkyPgEzpIUC_DSmirN6eFWp4KInAACsQoAAoHSSFYub2D15dGHfy8E\n\nThat's it!!! Enjoy Earning Money 💲\n\n[[[ Trusted Earning Site - https://kpslink.in]]]\n\nIf you have any Doubts, Feel Free to Ask me - @Simplifytuber2</b>")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>You don't have access to use this command!\n\nAdd Me to Your Own Group as Admin and Try This Command\n\nFor More PM Me With This Command</b>")
    else:
        pass
    try:
        command, shortlink_url, api = data.split(" ")
    except:
        return await message.reply_text("<b>Command Incomplete :(\n\nGive me a shortener website link and api along with the command !\n\nFormat: <code>/shortlink kpslink.in e3d82cdf8f9f4783c42170b515d1c271fb1c4500</code></b>")
    reply = await message.reply_text("<b>Please Wait...</b>")
    shortlink_url = re.sub(r"https?://?", "", shortlink_url)
    shortlink_url = re.sub(r"[:/]", "", shortlink_url)
    await save_group_settings(grpid, 'shortlink', shortlink_url)
    await save_group_settings(grpid, 'shortlink_api', api)
    await save_group_settings(grpid, 'is_shortlink', True)
    await reply.edit_text(f"<b>Successfully added shortlink API for {title}.\n\nCurrent Shortlink Website: <code>{shortlink_url}</code>\nCurrent API: <code>{api}</code></b>")
    
@Client.on_message(filters.command("setshortlinkoff") & filters.user(ADMINS))
async def offshortlink(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("I will Work Only in group")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    await save_group_settings(grpid, 'is_shortlink', False)
    # ENABLE_SHORTLINK = False
    return await message.reply_text("Successfully disabled shortlink")
    
@Client.on_message(filters.command("setshortlinkon") & filters.user(ADMINS))
async def onshortlink(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("I will Work Only in group")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    await save_group_settings(grpid, 'is_shortlink', True)
    # ENABLE_SHORTLINK = True
    return await message.reply_text("Successfully enabled shortlink")

@Client.on_message(filters.command("shortlink_info"))
async def showshortlink(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Turn off anonymous admin and try again this command")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, This Command Only Works in Group\n\nTry this command in your own group, if you are using me in your group</b>")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    chat_id=message.chat.id
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
#     if 'shortlink' in settings.keys():
#         su = settings['shortlink']
#         sa = settings['shortlink_api']
#     else:
#         return await message.reply_text("<b>Shortener Url Not Connected\n\nYou can Connect Using /shortlink command</b>")
#     if 'tutorial' in settings.keys():
#         st = settings['tutorial']
#     else:
#         return await message.reply_text("<b>Tutorial Link Not Connected\n\nYou can Connect Using /set_tutorial command</b>")
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>Tʜɪs ᴄᴏᴍᴍᴀɴᴅ Wᴏʀᴋs Oɴʟʏ Fᴏʀ ᴛʜɪs Gʀᴏᴜᴘ Oᴡɴᴇʀ/Aᴅᴍɪɴ\n\nTʀʏ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ ʏᴏᴜʀ Oᴡɴ Gʀᴏᴜᴘ, Iғ Yᴏᴜ Aʀᴇ Usɪɴɢ Mᴇ Iɴ Yᴏᴜʀ Gʀᴏᴜᴘ</b>")
    else:
        settings = await get_settings(chat_id) #fetching settings for group
        if 'shortlink' in settings.keys() and 'tutorial' in settings.keys():
            su = settings['shortlink']
            sa = settings['shortlink_api']
            st = settings['tutorial']
            return await message.reply_text(f"<b>Shortlink Website: <code>{su}</code>\n\nApi: <code>{sa}</code>\n\nTutorial: <code>{st}</code></b>")
        elif 'shortlink' in settings.keys() and 'tutorial' not in settings.keys():
            su = settings['shortlink']
            sa = settings['shortlink_api']
            return await message.reply_text(f"<b>Shortener Website: <code>{su}</code>\n\nApi: <code>{sa}</code>\n\nTutorial Link Not Connected\n\nYou can Connect Using /set_tutorial command</b>")
        elif 'shortlink' not in settings.keys() and 'tutorial' in settings.keys():
            st = settings['tutorial']
            return await message.reply_text(f"<b>Tutorial: <code>{st}</code>\n\nShortener Url Not Connected\n\nYou can Connect Using /shortlink command</b>")
        else:
            return await message.reply_text("Shortener url and Tutorial Link Not Connected. Check this commands, /shortlink and /set_tutorial")


@Client.on_message(filters.command("set_tutorial"))
async def settutorial(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Turn off anonymous admin and try again this command")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("This Command Work Only in group\n\nTry it in your own group")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return
    else:
        pass
    if len(message.command) == 1:
        return await message.reply("<b>Give me a tutorial link along with this command\n\nCommand Usage: /set_tutorial your tutorial link</b>")
    elif len(message.command) == 2:
        reply = await message.reply_text("<b>Please Wait...</b>")
        tutorial = message.command[1]
        await save_group_settings(grpid, 'tutorial', tutorial)
        await save_group_settings(grpid, 'is_tutorial', True)
        await reply.edit_text(f"<b>Successfully Added Tutorial\n\nHere is your tutorial link for your group {title} - <code>{tutorial}</code></b>")
    else:
        return await message.reply("<b>You entered Incorrect Format\n\nFormat: /set_tutorial your tutorial link</b>")

@Client.on_message(filters.command("remove_tutorial"))
async def removetutorial(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Turn off anonymous admin and try again this command")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("This Command Work Only in group\n\nTry it in your own group")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return
    else:
        pass
    reply = await message.reply_text("<b>Please Wait...</b>")
    await save_group_settings(grpid, 'is_tutorial', False)
    await reply.edit_text(f"<b>Successfully Removed Your Tutorial Link!!!</b>")

@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(text="**🔄 𝙿𝚁𝙾𝙲𝙴𝚂𝚂𝙴𝚂 𝚂𝚃𝙾𝙿𝙴𝙳. 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙸𝙽𝙶...**", chat_id=message.chat.id)       
    await asyncio.sleep(3)
    await msg.edit("**✅️ 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙴𝙳. 𝙽𝙾𝚆 𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝙼𝙴**")
    os.execl(sys.executable, sys.executable, *sys.argv)
