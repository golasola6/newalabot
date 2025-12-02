import motor.motor_asyncio
from info import DAILY_LIMIT, DATABASE_NAME, DATABASE_URI, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, P_TTI_SHOW_OFF, SINGLE_BUTTON, SPELL_CHECK_REPLY, PROTECT_CONTENT, AUTO_DELETE, MAX_BTN, AUTO_FFILTER, SHORTLINK_API, SHORTLINK_URL, IS_SHORTLINK, TUTORIAL, IS_TUTORIAL
# Free limit per user
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest
JOIN_REQUIRED = 1  # Number of channels user must join for unlimited access
import pytz
from datetime import datetime, timedelta, date
timezone = pytz.timezone("Asia/Kolkata")

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.users = self.db.userdata
        self.req = self.db.requests
        self.brutal = self.db.brutal
        self.channels = self.db.channels

    async def find_join_req(self, id):
        return bool(await self.req.find_one({'id': id}))
        
    async def add_join_req(self, id):
        await self.req.insert_one({'id': id})

    async def del_join_req(self):
        await self.req.drop()

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )

    def new_group(self, id, title):
        return dict(
            id = id,
            title = title,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id':int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        return self.col.find({})
    
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats
    
    async def add_chat(self, chat, title):
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)
    
    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id':int(chat)})
        return False if not chat else chat.get('chat_status') 

    async def re_enable_chat(self, id):
        chat_status=dict(
            is_disabled=False,
            reason="",
            )
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
        
    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})      
    
    async def get_settings(self, id):
        default = {
            'button': SINGLE_BUTTON,
            'botpm': P_TTI_SHOW_OFF,
            'file_secure': PROTECT_CONTENT,
            'imdb': IMDB,
            'spell_check': SPELL_CHECK_REPLY,
            'welcome': MELCOW_NEW_USERS,
            'auto_delete': AUTO_DELETE,
            'auto_ffilter': AUTO_FFILTER,
            'max_btn': MAX_BTN,
            'template': IMDB_TEMPLATE,
            'shortlink': SHORTLINK_URL,
            'shortlink_api': SHORTLINK_API,
            'is_shortlink': IS_SHORTLINK,
            'tutorial': TUTORIAL,
            'is_tutorial': IS_TUTORIAL
        }
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            return chat.get('settings', default)
        return default
    
    async def disable_chat(self, chat, reason="No Reason"):
        chat_status=dict(
            is_disabled=True,
            reason=reason,
            )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}}) 

    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count
    
    async def get_all_chats(self):
        return self.grp.find({})

    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']


    async def get_required_channels(self):
        channels_cursor = self.channels.find().sort('_id', -1)  # Fetch channels
        channels = await channels_cursor.to_list(length=None)  # Convert to list
        return [int(channel['channel_id']) for channel in channels]  # Ensure all IDs are integers
    
    async def add_new_required_channel(self, channel_id):
        # Check if the channel_id already exists
        existing_channel = await self.channels.find_one({"channel_id": channel_id})
        
        if existing_channel:
            return None  # Channel already exists, so don't insert
        
        # Insert only if it's not in the database
        result = await self.channels.insert_one({"channel_id": channel_id})
        return result.inserted_id  # Return the inserted channel's ID

        # New method to deduct the daily limit for free users

    async def remove_required_channel(self, channel_id):
        result = await self.channels.delete_one({"channel_id": channel_id})
        return result.deleted_count > 0  # Returns True if a channel was removed

    async def deduct_limit(self, user_id):
        user = await self.get_user(user_id)
        if user:
            subscription = user.get("subscription", "free")
            daily_limit = user.get("daily_limit", DAILY_LIMIT)
            
            # Check if the user is a free user
            if subscription == "free":
                if daily_limit > 0:
                    await self.users.update_one(
                        {"id": user_id},
                        {"$inc": {"daily_limit": -1}}
                    )
                    return True
                else:
                    return False  # No daily limit left
            return True  # No deduction for paid users
        return False  # User not found
   
    async def update_user(self, user_data):
        await self.users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)

    async def get_user(self, user_id):
        user_data = await self.users.find_one({"id": user_id})
        return user_data
    
    async def get_all_joins(self):
        return self.users.find({})
    


    async def has_prime_status(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            expiry_time_str = user_data.get("subscription_expiry")

            if expiry_time_str is None:
                print("NO SUBSCRIPTION ")
                return False

            try:
                # Convert expiry time string back to datetime (assumes it's in UTC)
                expiry_time = datetime.strptime(expiry_time_str, "%Y-%m-%d %H:%M:%S")

                # Ensure the datetime is in UTC (or another timezone if needed)
                expiry_time = pytz.utc.localize(expiry_time)

                # Get current time in UTC
                current_time = datetime.now(pytz.utc)

                # Check if the current time is still within the expiry time
                if current_time <= expiry_time:
                    return True
                else:
                    # If expired, reset the expiry field in the database
                    await self.users.update_one({"id": user_id}, {"$set": {"subscription": "free", "daily_limit": DAILY_LIMIT, "subscription_expiry": None}})
                    return False  # Subscription has expired

            except ValueError:
                print(f"⚠️ Invalid expiry time format for user {user_id}: {expiry_time_str}")
            
        return False
    async def get_user_data(self, user_id):
        return self.brutal.find_one({'user_id': user_id})

    async def update_user_subscription(self, user_id, channels_joined):
        expiry_time = datetime.timezone.utc() + timedelta(hours=24)
        self.brutal.update_one(
            {'user_id': user_id},
            {'$set': {'subscribed_channels': channels_joined, 'expiry': expiry_time}},
            upsert=True
        )
        
    async def handle_subscription_check(self, client, message):
        user_id = message.from_user.id
        user_data = await self.get_user_data(user_id)
        
        if not user_data:
            self.brutal.insert_one({'user_id': user_id, 'free_videos': 0, 'subscribed_channels': [], 'expiry': None})
            user_data = {'free_videos': 0, 'subscribed_channels': [], 'expiry': None}
        
        if user_data['free_videos'] < DAILY_LIMIT:
            self.brutal.update_one({'user_id': user_id}, {'$inc': {'free_videos': 1}})
            return True
        
        if user_data['expiry'] and datetime.now() < user_data['expiry']:
            return True
        
        required_channels = await self.get_required_channels()
        joined_channels = user_data.get('subscribed_channels', [])
        left_channels = list(set(required_channels) - set(joined_channels))
        
        if len(joined_channels) >= JOIN_REQUIRED:
            await self.update_user_subscription(user_id, joined_channels)
            return True
        
        btns = [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{channel}")] for channel in left_channels[:JOIN_REQUIRED]]
        btns.append([InlineKeyboardButton("🔄 Try Again", callback_data="check_subscription")])
        await client.send_message(
            chat_id=user_id,
            text="🚨 You must join at least 2 channels to continue!",
            reply_markup=InlineKeyboardMarkup(btns)
        )
        return False

db = Database(DATABASE_URI, DATABASE_NAME)
