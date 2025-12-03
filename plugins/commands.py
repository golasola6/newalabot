import os
import logging
import random
import asyncio
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, Message
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import *
#5 => verification_steps ! [Youtube@LazyDeveloperr]
from utils import  check_verification, imdb,  get_token,  verify_user, check_token, get_settings, get_size, is_subscribed, save_group_settings, temp
from database.connections_mdb import active_connection
from urllib.parse import quote
import datetime
from utils import lazy_readable,schedule_deletion, lazy_has_subscribed, to_small_caps, get_shortlink
from database.users_chats_db import db 
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
import re
import json
import base64
logger = logging.getLogger(__name__)
import math
from pyrogram.errors import MessageNotModified,PeerIdInvalid,FloodWait
from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest
from database.users_chats_db import db
from info import ADMINS, AUTH_CHANNEL, CHANNELS_PER_PAGE, LAZYCONTAINER
from utils import temp
import re
from math import ceil
import pytz  # Make sure to handle timezone correctly
timezone = pytz.timezone("Asia/Kolkata")
from pyrogram.enums import ChatMemberStatus

BATCH_FILES = {}
DUMPLAZY = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    try:
        user_id = message.from_user.id
        if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            buttons = [[
                    InlineKeyboardButton('𓆩ཫ⛱ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ⛱ཀ𓆪', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('✇ Jᴏɪɴ Oᴜʀ Cʜᴀɴɴᴇʟꜱ ✇', callback_data='main_channel')
                  ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
            await asyncio.sleep(2) # 😢 https://github.com/LazyDeveloperr/LazyPrincess/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
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
                    InlineKeyboardButton('𓆩• Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ •𓆪', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                    ],
                    [
                    InlineKeyboardButton('〄 ᴜᴘᴅᴀᴛᴇꜱ', url=f'https://t.me/{MAIN_CHANNEL_USRNM}'),
                    InlineKeyboardButton('⛱ ɢʀᴏᴜᴘ', url=f'https://t.me/{MOVIE_GROUP_USERNAME}')
                    ],[
                    InlineKeyboardButton('⍟ ʜᴇʟᴘ', callback_data='help'),
                    InlineKeyboardButton('✇ ꜱᴜᴘᴘᴏʀᴛ', url=f'https://t.me/{SUPPORT_CHAT}'),
                    ],[
                    InlineKeyboardButton('𓆩ཫ💰 • ᴅᴏɴᴀᴛᴇ ᴜꜱ • 💰ཀ𓆪', url=DONATION_LINK),
                    ]]

            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply_photo(
                photo=random.choice(PICS),
                caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML,
                has_spoiler=True
            )
            return
        
# =============================================================================
        # try:
        #     if AUTH_CHANNEL and not await lazy_has_subscribed(client, message):
        #         lazydeloper = 0
        #         lazybuttons = []
        #         for channel in AUTH_CHANNEL:
        #             lazydeloper = lazydeloper + 1
        #             try:
        #                 invite_link = await client.create_chat_invite_link(int(channel), creates_join_request=False)
        #             except ChatAdminRequired:
        #                 logger.error("Initail Force Sub is not working because of ADMIN ISSUE. Please make me admin there 🚩")
        #                 return
        #             lazybuttons.append([
        #                         InlineKeyboardButton(text=f"🚩 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ {lazydeloper} •", url=invite_link.invite_link),
        #                         ])

        #         if message.command[1] != "subscribe":
        #             try:
        #                 kk, file_id = message.command[1].split("_", 1)
        #                 pre = 'checksubp' if kk == 'filep' else 'checksub' 
        #                 lazybuttons.append([InlineKeyboardButton(f"𓆩ཫ♻ • {to_small_caps('Click To Verify')} • ♻ཀ𓆪", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        #             except (IndexError, ValueError):
        #                 lazybuttons.append([InlineKeyboardButton(f"𓆩ཫ♻ • {to_small_caps('Click To Verify')} • ♻ཀ𓆪", callback_data=f"{pre}#{file_id}")])
        #         await client.send_message(
        #             chat_id=message.from_user.id,
        #             text=f"{script.FORCESUB_MSG.format(message.from_user.mention)}",
        #             reply_markup=InlineKeyboardMarkup(lazybuttons),
        #             parse_mode=enums.ParseMode.HTML,
        #             disable_web_page_preview=True
        #             )
        #         return
        # except Exception as lazy:
        #     print(f"Hello Sir , Please check err : {lazy} ")
        #     pass
        # ==========================🚧 BARIER 1 🚧 ==========================================

# =============================================================================

        if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:

            buttons = [[
                    InlineKeyboardButton('𓆩• Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ •𓆪', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                    ],
                    [
                    InlineKeyboardButton('〄 ᴜᴘᴅᴀᴛᴇꜱ', url=f'https://t.me/{MAIN_CHANNEL_USRNM}'),
                    InlineKeyboardButton('⛱ ɢʀᴏᴜᴘ', url=f'https://t.me/{MOVIE_GROUP_USERNAME}')
                    ],[
                    InlineKeyboardButton('⍟ ʜᴇʟᴘ', callback_data='help'),
                    InlineKeyboardButton('✇ ꜱᴜᴘᴘᴏʀᴛ', url=f'https://t.me/{SUPPORT_CHAT}'),
                    ],[
                    InlineKeyboardButton('𓆩ཫ💰 • ᴅᴏɴᴀᴛᴇ ᴜꜱ • 💰ཀ𓆪', url=DONATION_LINK),
                    ]]

            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply_photo(
                photo=random.choice(PICS),
                caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML,
                has_spoiler=True
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
                    invite_link = await client.create_chat_invite_link(int(channel), creates_join_request=True)
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
        #6 => verification_steps ! [Youtube@LazyDeveloperr]
        elif data.split("-", 1)[0] == "verify":
            userid = data.split("-", 2)[1]
            user_ids = message.from_user.id
            prex = DUMPLAZY[user_ids]["pre"]  
            lazy_file_id = DUMPLAZY[user_ids]["file_id"]
            # print(prex)
            # print(lazy_file_id)
            token = data.split("-", 3)[2]
            if str(message.from_user.id) != str(userid):
                return await message.reply_text(
                    text="<b>Invalid link or Expired link !</b>",
                    protect_content=True
                )
            is_valid = await check_token(client, userid, token)
            if is_valid == True:
                await message.reply_text(
                    text=f"<b>Hey {message.from_user.mention}, You are successfully verified !\nNow you have unlimited access for all movies till today midnight.</b>",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("📺 GET FILE ✔", url=f"https://telegram.me/{temp.U_NAME}?start={prex}_{lazy_file_id}")
                    ]]),
                    protect_content=True
                )
                try:
                    await verify_user(client, userid, token)
                except Exception as Lazy:
                    print(Lazy)
            else:
                return await message.reply_text(
                    text="<b>Invalid link or Expired link !</b>",
                    protect_content=True
                )
        
# ====================================================================
        # check verfication start
        try:
            print('A user hit this case....')
            zab_user_id = message.from_user.id
            if IS_LAZYUSER_VERIFICATION and not await check_verification(client, zab_user_id):
                # lazy_url = await get_token(client, zab_user_id, f"https://telegram.me/{temp.U_NAME}?start=")
                # lazy_verify_btn = [[
                #     InlineKeyboardButton("✅ Verify ✅", url=lazy_url)
                # ]]
                # await message.reply_text(
                #     text="You are not verified user ! please verify to get files.",
                #     reply_markup=InlineKeyboardMarkup(lazy_verify_btn)
                # )
                # return
                try:
                    print('A user hit this case....')
                    zab_user_id = message.from_user.id
                    
                    DUMPLAZY[zab_user_id] = {
                        'pre': pre,
                        'file_id' : file_id
                        }
                    
                    print(DUMPLAZY[zab_user_id])
                    lazy_url = await get_token(client, zab_user_id, f"https://telegram.me/{temp.U_NAME}?start=")
                    lazy_verify_btn = [[
                        InlineKeyboardButton("✅ Verify ✅", url=lazy_url)
                    ]]
                    await message.reply_text(
                        text="🚩 You are not verified user ! please verify to get unlimited files. 🚀",
                        reply_markup=InlineKeyboardMarkup(lazy_verify_btn)
                    )
                    return
                except Exception as e:
                    print(f"Exception occured : {str(e)}")
                # ./check verfication end

        except Exception as e:
            logging.info(f"Error in Barier: {e}")
            return await message.reply(f"{script.FAILED_VERIFICATION_TEXT}")                

        # ./check verfication end

# ====================================================================
# ====================================================================
        lzy = message.from_user.first_name
        daily_limit, subscription, assigned_channels, joined_channels = await lazybarier(client, lzy, user_id)
# ==========================🚧 BARIER 2 🚧 ==========================================

# =======================================================================
        ## token verification with subscription method
        # if subscription == "free" and daily_limit <= 0:
        #     try:
        #         try:
        #             print('A user hit this case....')
        #             zab_user_id = message.from_user.id
                    
        #             DUMPLAZY[zab_user_id] = {
        #                 'pre': pre,
        #                 'file_id' : file_id
        #                 }
                    
        #             print(DUMPLAZY[zab_user_id])
        #             lazy_url = await get_token(client, zab_user_id, f"https://telegram.me/{temp.U_NAME}?start=")
        #             lazy_verify_btn = [[
        #                 InlineKeyboardButton("✅ Verify ✅", url=lazy_url)
        #             ]]
        #             await message.reply_text(
        #                 text="🚩 You are not verified user ! please verify to get unlimited files. 🚀",
        #                 reply_markup=InlineKeyboardMarkup(lazy_verify_btn)
        #             )
        #             return
        #         except Exception as e:
        #             print(f"Exception occured : {str(e)}")
        #         # ./check verfication end

        #     except Exception as e:
        #         logging.info(f"Error in Barier: {e}")
        #         return await message.reply(f"{script.FAILED_VERIFICATION_TEXT}")                
        ## ./token verification with subscription method
# =======================================================================

        if data.startswith("grantfreevip"):
            # daily_limit, subscription, assigned_channels, _= await lazybarier(client, lzy, user_id)
            # Limit free users to 3 videos per day
            if subscription == "free" and daily_limit <= 0:
                try:
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
                                expiry_time = datetime.datetime.now(timezone) + datetime.timedelta(seconds=MAX_SUBSCRIPTION_TIME)  # 24 hours from now
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
                    try:
                        lazybtn = []
                        lazy_lota = []
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
                                    expiry_time = datetime.datetime.now(timezone) + datetime.timedelta(seconds=MAX_SUBSCRIPTION_TIME)  # 24 hours from now
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

                            lazz = await message.reply_text(to_small_caps(script.UPGRADE_TEXT),
                                    reply_markup=InlineKeyboardMarkup(lazybtn)
                                        )
                            LAZYCONTAINER[user_id] = {
                                    "lazymsg": lazz,
                                    "file_id": file_id,
                                    "the_one&only_LazyDeveloper": True
                                }
                            
                            lazy_lota.append(lazz)
                            asyncio.create_task(schedule_deletion(client, chat_id, lazy_lota, BATCH=True))
                            return
                    except Exception as e:
                        logging.info(f"Error in Barier: {e}")
                        return await message.reply(f"{script.FAILED_VERIFICATION_TEXT}")                

                    # ghost_url = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=files_{file_id}")
                    # lazyfile = await client.send_message(
                    #     chat_id=userid,
                    #     text=f"😱Oh no! {message.from_user.mention} 💔.\n{to_small_caps(script.EXPIRED_TEXT)}\n\n📺 ꜰɪʟᴇ ɴᴀᴍᴇ : <code>{files.file_name}</code> \n\n🫧 ꜰɪʟᴇ ꜱɪᴢᴇ : <code>{get_size(files.file_size)}</code>\n\n{to_small_caps('🚩GET #FREE VIP ⫶̊OR⫶̊ ✔KEEP ADS')}",
                    #     reply_markup=InlineKeyboardMarkup(
                    #         [
                    #             [
                    #                 InlineKeyboardButton(f"{to_small_caps('📁 Continue with ADS 📁')}", url=ghost_url)
                    #             ],
                    #             [
                    #                 InlineKeyboardButton("𓆩ཫ♥ • Get Free ACCESS • ♥ཀ𓆪", callback_data=f"grantfreevip#{file_id}")
                    #             ]
                    #         ]
                    #     )
                    #     )
                    return
                else:
                    print(f"passed for {userid} ==> daily_limit ==> {daily_limit}")
                    pass
            except Exception as e:
                logging.info(f"Error handling sendfiles: {e}")
                return
                
            # try:
                # lazybtn = []
                # lazydeloper = 0
                # for channel in assigned_channels:
                    # if await is_subscribed(client, channel, user_id):
                        # await db.users.update_one(
                                # {"id": user_id},
                                # {"$addToSet": {"joined_channels": channel}},  # Append channel if not already present
                                # upsert=True
                            # )
                        # updated_data = await db.get_user(user_id)
                        # joined_channels = set(updated_data.get("joined_channels", []))
                        # if assigned_channels.issubset(joined_channels):
                            # expiry_time = datetime.datetime.now(timezone) + datetime.timedelta(seconds=MAX_SUBSCRIPTION_TIME)  # 24 hours from now
                            # expiry_str = expiry_time.strftime("%Y-%m-%d %H:%M:%S")  # Format as YYYY-MM-DD HH:MM:SS
                            # await db.update_user({"id": message.from_user.id, "subscription": "limited", "subscription_expiry": expiry_str})
                            # msg = await client.send_message(
                                                # user_id,
                                                # f"{script.VERIFIED_TEXT.format(message.from_user.mention,MAX_SUBSCRIPTION_TIME, expiry_str)}",
                                                # parse_mode=enums.ParseMode.HTML,
                                                # disable_web_page_preview=True
                                            # )
                    # else:
                        # lazydeloper = lazydeloper + 1
                        # invite_link = await client.create_chat_invite_link(int(channel), creates_join_request=True)
                        # lazybtn.append([
                                # InlineKeyboardButton(f"{to_small_caps('🚩 Join Channel')} {lazydeloper}", url=invite_link.invite_link),
                                # ]) # bahut deemag khraab hua h is feature ko add krne mei #lazydeveloper 😢
                # 
                # lazy_updated_data = await db.get_user(user_id)
                # lazy_joined_channels = set(lazy_updated_data.get("joined_channels", []))
                # if not assigned_channels.issubset(lazy_joined_channels):
                    # if message.command[1] != "subscribe":
                        # try:
                            # kk, file_id = message.command[1].split("_", 1)
                            # pre = 'checksubp' if kk == 'filep' else 'checksub' 
                            # lazybtn.append([InlineKeyboardButton(f"𓆩ཫ♻ • {to_small_caps('Click To Verify')} • ♻ཀ𓆪", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
                        # except (IndexError, ValueError):
                            # lazybtn.append([InlineKeyboardButton(f"♻ ♡ • {to_small_caps('Click To Verify')} • ♡ ♻", callback_data=f"{pre}#{file_id}")])

                    

                    # lazz = await message.reply_text(to_small_caps(script.UPGRADE_TEXT),
                            # reply_markup=InlineKeyboardMarkup(lazybtn)
                                # )
                    # LAZYCONTAINER[user_id] = {
                            # "lazymsg": lazz,
                            # "file_id": file_id,
                            # "the_one&only_LazyDeveloper": True
                        # }
                    # return
            # except Exception as e:
                # logging.info(f"Error in Barier: {e}")
                # return await message.reply(f"{script.FAILED_VERIFICATION_TEXT}")                



        
        elif data.startswith("requestmovie"):
            user_id = message.chat.id
            await message.delete()
            await message.reply_text("<i><b>»» Please enter movie name...</b></i>",	
            reply_to_message_id=message.id,  
            reply_markup=ForceReply(True)) 


        files_ = await get_file_details(file_id)           
        if not files_:
            pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
            try:   
                share_url = f"https://t.me/{temp.U_NAME}?start=file_{file_id}"
                sharelazymsg = f"{to_small_caps('•❤ Access file at your fingertip ❤•')}\n{to_small_caps('🤝 Join us now for the latest movies and entertainment!')}"
                lazydeveloper_text = quote(sharelazymsg)
                
                # send_to_lazy_channel = diverting_channel if diverting_channel is not None else LAZY_DIVERTING_CHANNEL

                button = [
                    [
                        # InlineKeyboardButton(to_small_caps('▶Stream/Dl'), callback_data=f'generate_stream_link:{file_id}'),
                        InlineKeyboardButton(to_small_caps('🔁Share💕'), url=f"https://t.me/share/url?url={share_url}&text={lazydeveloper_text}")
                    
                    ],[
                        InlineKeyboardButton('𓆩ཫ💰 • ᴅᴏɴᴀᴛᴇ ᴜꜱ • 💰ཀ𓆪', url=DONATION_LINK),
                    ]]
                # Create the inline keyboard markup with the button
                keyboard = InlineKeyboardMarkup(button)
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file_id,
                    reply_markup=keyboard,
                    protect_content=True if pre == 'filep' else False,
                    )
                
                filetype = msg.media
                file = getattr(msg, filetype.value)
                title = file.file_name
                size=get_size(file.file_size)
                f_caption = f"<code>{title}</code>"
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                    except:
                        return
                along_with_lazy_info = f"<b><u>⚠ DELETING IN {lazy_readable(FILE_AUTO_DELETE_TIME)} ⚠\nꜰᴏʀᴡᴀʀᴅ & ꜱᴛᴀʀᴛ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴛʜᴇʀᴇ</u></b>"
                along_with_lazy_footer = f"<b>Dear {message.from_user.mention} ! {script.DONATION_TEXT}</b>"
                lazy_caption_template =f"{along_with_lazy_info}\n\n<b>{f_caption}</b>"
                await msg.edit_caption(lazy_caption_template)
                lazy_lota = []
                lazy_lota.append(msg)
                asyncio.create_task(schedule_deletion(client, message.from_user.id, lazy_lota, BATCH=True))

                # asyncio.create_task(send_lazy_video(client, message, send_to_lazy_channel, msg))

                return
            except:
                pass
            return await message.reply('No such file exist.')
        files = files_[0]
        title = files.file_name
        size=get_size(files.file_size)
        f_caption=files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption=f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        along_with_lazy_info = f"<b><u>⚠ DELETING IN {lazy_readable(FILE_AUTO_DELETE_TIME)} ⚠\nꜰᴏʀᴡᴀʀᴅ ᴀɴᴅ ꜱᴛᴀʀᴛ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴛʜᴇʀᴇ </u></b>"
        along_with_owner_info = f"<b>{to_small_caps('✅ File is permanent ✔ ')}\n{to_small_caps('♥ You can download file here✔')}</b>"
        along_with_lazy_footer = f"<b>Dear {message.from_user.mention} ! {script.DONATION_TEXT}</b>"
        lazy_caption_template =f"{along_with_lazy_info}\n\n<b>{f_caption}</b>"
        share_url = f"https://t.me/{temp.U_NAME}?start=file_{file_id}"
        sharelazymsg = f"{to_small_caps('•❤ Access file at your fingertip ❤•')}\n{to_small_caps('🤝 Join us now for the latest movies and entertainment!')}"
        lazydeveloper_text = quote(sharelazymsg)
        #file sending logic :
        # send_to_lazy_channel = diverting_channel if diverting_channel is not None else LAZY_DIVERTING_CHANNEL
        # 
        button = [
            [
                # InlineKeyboardButton(to_small_caps('▶Stream/Dl'), callback_data=f'generate_stream_link:{file_id}'),
                InlineKeyboardButton(to_small_caps('🔁Share💕'), url=f"https://t.me/share/url?url={share_url}&text={lazydeveloper_text}")
            
            ],[
                InlineKeyboardButton('𓆩ཫ💰 • ᴅᴏɴᴀᴛᴇ ᴜꜱ • 💰ཀ𓆪', url=DONATION_LINK),
            ]]
        # Create the inline keyboard markup with the button
        keyboard = InlineKeyboardMarkup(button)
        lazy_file = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption=lazy_caption_template,
            reply_markup=keyboard,  # Use the created keyboard
            protect_content=True if pre == 'filep' else False,
            )
        lazy_lota = []
        lazy_lota.append(lazy_file)
        asyncio.create_task(schedule_deletion(client, message.from_user.id, lazy_lota, BATCH=True))

        #finally - overacting ka 1 rupees kaat lo 💘😊
        if subscription !="limited":
            await db.deduct_limit(user_id)
            # logging.info(f"\n\n::::::::::>> Tried to Deduct limit for user [{message.from_user.first_name}] :|::> ID ::> {user_id} :|::> AT : {datetime.datetime.now()}")
        else:
            pass
            # logging.info(f"\n\nFailed to deduct limit for user ::> [{message.from_user.first_name}] :| ID ::> {user_id} :|::> ERROR AT :  {datetime.datetime.now()}")
        
    except PeerIdInvalid:
        return await message.reply("⭕ PLease wait... Until all setup is done!")
    except Exception as lazydeveloper:
        logging.info(lazydeveloper)

async def send_lazy_video(client, message, send_to_lazy_channel, lazy_file):
    try:
        lazy_lota = []
        member = await client.get_chat_member(send_to_lazy_channel, message.from_user.id)
        if member.status not in [ChatMemberStatus.OWNER, 
                                ChatMemberStatus.ADMINISTRATOR, 
                                ChatMemberStatus.MEMBER]:
            invite_link = await client.create_chat_invite_link(int(send_to_lazy_channel))
            lazy_invite_url = invite_link.invite_link

            fussx = await client.send_message(
            chat_id=message.from_user.id,
            text=f"🎉 File Uploaded here ✅\n\nHere is the channel link - Join & Get file 👇\n\n**{lazy_invite_url}**\n**{lazy_invite_url}**\n\n⚠Note: Dear {message.from_user.mention}, if you stay subscribed to the channel, you will receive direct links next time ❤",
            reply_markup=InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton(f"𓆩ཫ{to_small_caps('🔻 CHANGE CHANNEL ⭕')}ཀ𓆪", callback_data="setdivertingchannel")]
                            ]
                            )
                )
            lazy_lota.append(fussx)
            # print(f'User is not subscribed: Got url => {lazy_invite_url}')
        else:
            message_link = await client.get_messages(int(send_to_lazy_channel), lazy_file.id)
            file_link = message_link.link
            fassx = await client.send_message(
            chat_id=message.from_user.id,
            text=f"🎉You're already a channel member🎊\n\nHere is your direct download link 👇\n\n {file_link} \n {file_link} \n\n❤Thank you for staying with the channel, {message.from_user.mention}❤",
            reply_markup=InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton(f"𓆩ཫ{to_small_caps('🔻 CHANGE CHANNEL ⭕')}ཀ𓆪", callback_data="setdivertingchannel")]
                            ]
                            ))
            lazy_lota.append(fassx)
            # print(f'User is subscribed: Got LINK => {file_link}')
    except UserNotParticipant:
        invite_link = await client.create_chat_invite_link(int(send_to_lazy_channel))
        lazy_invite_url = invite_link.invite_link
        fassxx = await client.send_message(
            chat_id=message.from_user.id,
            text=f"🎉 File Uploaded here ✅\n\nHere is the channel link - Join & Get file 👇\n\n **{lazy_invite_url}**\n**{lazy_invite_url}**\n\n⚠Note: Dear {message.from_user.mention}, if you stay subscribed to the channel, you will receive direct links next time ❤",
            reply_markup=InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton(f"𓆩ཫ{to_small_caps('🔻 CHANGE CHANNEL ⭕')}ཀ𓆪", callback_data="setdivertingchannel")]
                            ]
                            )
                        )
        lazy_lota.append(fassxx)
    except PeerIdInvalid:
        invite_link = await client.create_chat_invite_link(int(send_to_lazy_channel))
        lazy_invite_url = invite_link.invite_link
        fassxx = await client.send_message(
            chat_id=message.from_user.id,
            text=f"❌ Please make sure i'm ADMIN in your channel : ({send_to_lazy_channel}) \n\n<b><u>☆ HOW TO FIX ISSUE ?👇</u><b>\n)ᕘ Click below btn to open channel.\n)ᕘGo to ADMINS section.\n)ᕘMake me ADMIN with all rights ✅",
            reply_markup=InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton(f"𓆩ཫ🚩{to_small_caps('+  MAKE ME ADMIN  +')}🚩ཀ𓆪", url=lazy_invite_url)]
                            ]
                            ))
    
        lazy_lota.append(fassxx)
    finally:
            try:
                if send_to_lazy_channel == LAZY_DIVERTING_CHANNEL:
                    lazy_lota.append(lazy_file)
                print("🚩PERSONAL CHANNEL DETECTED : STOPPED file for auto detetion")
            except Exception as lazydev:
                print(f"Not able to add file for auto deletion : {lazydev}")
                pass
            asyncio.create_task(schedule_deletion(client, message.from_user.id, lazy_lota, BATCH=True))

async def lazybarier(bot, l, user_id):
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
        new_assigned_channels = set(sorted(set(all_channels) - joined_channels)[:1])

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
    subscription = user.get("subscription", "free")
    subscription_expiry = user.get("subscription_expiry")
    daily_limit = user.get("daily_limit", DAILY_LIMIT)
    last_access = user.get("last_access")
    assigned_channels = set(user.get("assigned_channels", []))
    joined_channels = set(user.get("joined_channels", []))
    
    today = str(datetime.date.today())
    if last_access != today:
        if subscription == "free":
            for channel in all_channels:
                if await is_subscribed(bot, channel, user_id):
                    joined_channels.add(channel)
            new_channels = set(sorted(set(all_channels) - joined_channels)[:2])
            if not new_channels:
                joined_channels = set()  # Reset joined channels
                new_channels = set(random.sample(all_channels, 2))  # Pick 2 random channels

            data = {"id": user_id,
                    "daily_limit": DAILY_LIMIT, 
                    "last_access": today,
                    "assigned_channels": list(new_channels),
                    "joined_channels": list(joined_channels),
                    }
            await db.update_user(data)

    # Check for expired subscriptions
    # sabko indian time zone ke hisab se chlna pdega #LazyDeveloper 😂
    if subscription == "limited" and subscription_expiry:
        expiry_time = datetime.datetime.strptime(subscription_expiry, "%Y-%m-%d %H:%M:%S")
        expiry_time = timezone.localize(expiry_time)  # Ensure expiry time is in UTC
        current_time = datetime.datetime.now(timezone)  # Current time in IST
        if current_time > expiry_time:
            # print("changing expiry time")
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
            logging.info(f"usersdata {usersdata}")

    updated_data = await db.get_user(user_id)
    daily_limit = updated_data.get("daily_limit", DAILY_LIMIT)
    subscription = updated_data.get("subscription", "free")
    assigned_channels = set(updated_data.get("assigned_channels", []))
    joined_channels = set(updated_data.get("joined_channels", []))
    
    return daily_limit, subscription, assigned_channels, joined_channels,

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

@Client.on_message(filters.command("resetall_subs") & filters.user(ADMINS))
async def reset_all_subscriptions(client, message):
    try:

        await db.users.drop()
        await message.reply("✅ All user subscriptions have been reset to **Free** mode.\n\n")
    
    except Exception as e:
        await message.reply("⚠️ Failed to reset subscriptions. Check logs for errors.")

@Client.on_message(filters.command("reset_trending") & filters.user(ADMINS))
async def reset_trending_searched(client, message):
    try:

        await db.top_search.drop()
        await message.reply("✅ All Top Searches have been reset.")
    
    except Exception as e:
        await message.reply("⚠️ Failed to reset Trending. Check logs for errors.")

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
        pagination_buttons.append(InlineKeyboardButton(f"{BACK_BTN_TXT}", callback_data=f"page_{page-1}"))
    pagination_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="pages_info"))
    if page < total_pages:
        pagination_buttons.append(InlineKeyboardButton(f"{NEXT_BTN_TXT}", callback_data=f"page_{page+1}"))

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
@Client.on_message(filters.private & filters.command('channels') & filters.user(ADMINS))
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

@Client.on_message(filters.private & filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.private & filters.command('delete') & filters.user(ADMINS))
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
            # files indexed before https://github.com/LazyDeveloperr/lazyPrincess/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
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

@Client.on_message(filters.private & filters.command('deleteall') & filters.user(ADMINS))
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
    await message.answer(f'• With ❤ {temp.B_NAME} ⛱')
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
    await save_group_settings(grp_id, 'url_mode', False)
    if settings is not None:
        buttons = [
                [
                    InlineKeyboardButton(
                        'Filter Button',
                        callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                    ),
                    InlineKeyboardButton(
                        'Single' if settings["button"] else 'Double',
                        callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        'Bot PM',
                        callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                    ),
                    InlineKeyboardButton(
                        '✅ Yes' if settings["botpm"] else '❌ No',
                        callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        'File Secure',
                        callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                    ),
                    InlineKeyboardButton(
                        '✅ Yes' if settings["file_secure"] else '❌ No',
                        callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        'IMDB',
                        callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                    ),
                    InlineKeyboardButton(
                        '✅ Yes' if settings["imdb"] else '❌ No',
                        callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        'Spell Check',
                        callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                    ),
                    InlineKeyboardButton(
                        '✅ Yes' if settings["spell_check"] else '❌ No',
                        callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        'Welcome',
                        callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                    ),
                    InlineKeyboardButton(
                        '✅ Yes' if settings["welcome"] else '❌ No',
                        callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                    ),
                ],
            ]
        
        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_text(
            text=f"<b>Change Your Settings for {title} As Your Wish ⚙</b>",
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

@Client.on_message(filters.command("set_tutorial"))
async def settutorial(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"I did'nt recognise you as an admin. Try again ")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("This command works only in group")
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
        return await message.reply("<b>ɢɪᴠᴇ ᴍᴇ ᴀ ᴛᴜᴛᴏʀɪᴀʟ ʟɪɴᴋ ᴀʟᴏɴɢ ᴡɪᴛʜ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.\n\nᴜꜱᴀɢᴇ : /set_tutorial <code>https://t.me/LazyTutorialLink/23</code></b>")
    elif len(message.command) == 2:
        reply = await message.reply_text("<b>ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...</b>")
        tutorial = message.command[1]
        await save_group_settings(grpid, 'tutorial', tutorial)
        await save_group_settings(grpid, 'is_tutorial', True)
        await reply.edit_text(f"<b>Tutorial added successfully ✔\n\nʏᴏᴜʀ ɢʀᴏᴜᴘ : {title}\n\nʏᴏᴜʀ ᴛᴜᴛᴏʀɪᴀʟ : <code>{tutorial}</code></b>")
    else:
        return await message.reply("<b>ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ɪɴᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ !\nᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ : /set_tutorial <code>https://t.me/LazyTutorialLink/23</code></b>")

@Client.on_message(filters.command("remove_tutorial"))
async def removetutorial(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"I did'nt recognise you as an admin. Please Try Again")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("This command only works in group !")
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
    reply = await message.reply_text("<b>ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ...</b>")
    await save_group_settings(grpid, 'is_tutorial', False)
    await reply.edit_text(f"<b>Tutorial link removed ✔</b>")
