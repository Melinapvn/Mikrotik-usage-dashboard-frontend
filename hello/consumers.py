import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import traceback
import logging

# ----------------------
# Daily Usage Consumer
# ----------------------
logger = logging.getLogger("channels")

class DailyUsageConsumer(AsyncWebsocketConsumer):
    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        print("🟢 DailyUsageConsumer instance created:", self)

    async def connect(self):
        print("🟡 Trying to connect:", self.channel_name)
        try:
            self.group_name = "daily_usage"
            print("➡️ group name set:", self.group_name)
            print("channel layer", self.channel_layer)

            if not self.channel_layer:
                print("❌ channel_layer is None!")
            else:
                print("✅ channel_layer exists")

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            print("✅ group_add done")

            await self.accept()
            logger.debug(f"WebSocket connected: {self.channel_name}")
            print("✅ WebSocket daily connected successfully:", self.channel_name)

            await self.send(text_data=json.dumps({"message": "daily websocket connected"}))
            logger.debug(f"Sent welcome to {self.channel_name}")

            # اجرای ping/pong برای نگه‌داشتن اتصال
            asyncio.create_task(self.keep_alive())

            # فقط برای تست اگر Redis از group_channels پشتیبانی کنه
            try:
                members_func = getattr(self.channel_layer, "group_channels", None)
                if members_func:
                    members = await members_func(self.group_name)
                    print("👥 Current group members:", members)
            except Exception as e:
                print("⚠️ Could not fetch group members:", e)

        except Exception:
            print("❌ Exception in connect:")
            traceback.print_exc()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.debug(f"WebSocket disconnected: {self.channel_name}, code: {close_code}")
        except Exception as e:
            print("❌ Exception in disconnect:", e)
        print("🔴 Daily WS disconnected")

    async def receive(self, text_data):
        logger.debug(f"Received message from {self.channel_name}: {text_data}")
        print("📨 Received from client:", text_data)
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            print("❌ Invalid JSON received")
            return

        if data.get("action") == "refresh":
            print("🔄 Refresh requested by client")
            await self.send(text_data=json.dumps({"type": "initial", "message": "daily initial"}))

    async def send_update(self, event):
        print("📢 Consumer got update event:", event)
        try:
            payload = event.get("payload", {})
            await self.send(text_data=json.dumps(payload))
            print("✅ Event sent to client")
        except Exception:
            print("❌ Failed to send event to client:")
            traceback.print_exc()

    async def keep_alive(self):
        """Send a small ping every 15s to keep connection alive"""
        try:
            while True:
                await asyncio.sleep(15)
                await self.send(text_data=json.dumps({"ping": "pong"}))
                print("💓 keep-alive ping sent:", self.channel_name)
        except Exception:
            print("❌ Exception in keep_alive:")
            traceback.print_exc()

    
    

            
class MonthlyUsageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("monthly_usage", self.channel_name)
        await self.accept()
        print("✅ Monthly WS connected")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("monthly_usage", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("action") == "refresh":
            await self.send(text_data=json.dumps({"type": "initial", "message": "monthly initial"}))

    async def send_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))


class LiveUsageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("live_usage", self.channel_name)
        await self.accept()
        print("✅ Live WS connected")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("live_usage", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("action") == "refresh":
            await self.send(text_data=json.dumps({"type": "initial", "message": "live initial"}))

    async def send_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))


# Optional: user updates
class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("user_group", self.channel_name)
        await self.accept()
        print("✅ User WS connected")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("user_group", self.channel_name)

    async def send_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))                        