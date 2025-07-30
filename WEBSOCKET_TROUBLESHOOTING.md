# WebSocket Connection Issue - Troubleshooting Guide

## 🔍 **Issue Summary**

**Problem**: WebSocket connection to `ws://localhost:8000/ws/live-session/appointment_54/` failed

**Error**: `WebSocket connection to 'ws://localhost:8000/ws/live-session/appointment_54/' failed`

## 🚀 **Quick Fix Steps**

### **Step 1: Start Server with ASGI Support**

The most common cause is that the server isn't running with ASGI support. Use one of these methods:

**Method A: Use the ASGI startup script**
```bash
python start_server_asgi.py
```

**Method B: Use Django's built-in ASGI server**
```bash
python manage.py runserver --noreload
```

**Method C: Use Daphne (recommended for production)**
```bash
pip install daphne
daphne calmconnect_backend.asgi:application
```

### **Step 2: Verify Server is Running**

Check if the server is running by visiting:
- http://localhost:8000/

You should see the Django welcome page or your application.

### **Step 3: Test WebSocket Connection**

Run the WebSocket diagnostic test:
```bash
python test_websocket_connection.py
```

## 🔧 **Configuration Verification**

### **1. ASGI Configuration (calmconnect_backend/asgi.py)**
✅ **Verified**: ASGI application is properly configured with:
- ProtocolTypeRouter for HTTP and WebSocket
- AuthMiddlewareStack for authentication
- AllowedHostsOriginValidator for security
- Proper routing to websocket_urlpatterns

### **2. Channel Layers (settings.py)**
✅ **Verified**: InMemoryChannelLayer is configured:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}
```

### **3. WebSocket Routing (mentalhealth/routing.py)**
✅ **Verified**: Routes are properly configured:
```python
websocket_urlpatterns = [
    re_path(r'ws/live-session/(?P<room_id>\w+)/$', 
            consumers.LiveSessionConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_id>\w+)/$', 
            consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/test/$', 
            consumers.TestConsumer.as_asgi()),
]
```

### **4. Consumer Implementation (mentalhealth/consumers.py)**
✅ **Verified**: LiveSessionConsumer is properly implemented with:
- Connection handling
- Message routing
- Authentication checks
- Error handling

## 🚨 **Common Issues and Solutions**

### **Issue 1: Server Not Running with ASGI**
**Symptoms**: Connection refused errors
**Solution**: 
```bash
python start_server_asgi.py
```

### **Issue 2: Authentication Problems**
**Symptoms**: 403 Forbidden or connection denied
**Solution**: Ensure user is logged in and has access to the session

### **Issue 3: CORS Issues**
**Symptoms**: Connection fails in browser
**Solution**: Add CORS headers or use same origin

### **Issue 4: Port Already in Use**
**Symptoms**: Server won't start
**Solution**: 
```bash
# Kill existing process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
python manage.py runserver 8001
```

## 🔍 **Debugging Steps**

### **Step 1: Check Server Logs**
Look for these messages when starting the server:
```
🚀 Starting Django server with ASGI support...
📡 WebSocket support enabled
🌐 Server will be available at: http://localhost:8000
🔌 WebSocket endpoint: ws://localhost:8000/ws/
```

### **Step 2: Browser Console Debugging**
Open browser Developer Tools (F12) and check Console for:
```
WebSocket connected
WebSocket disconnected
WebSocket error: [error details]
```

### **Step 3: Network Tab Analysis**
In Developer Tools → Network tab:
1. Filter by "WS" (WebSocket)
2. Look for failed connection attempts
3. Check the request/response details

### **Step 4: Test with Simple WebSocket**
Try connecting to the test endpoint:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/test/');
ws.onopen = () => console.log('Connected!');
ws.onerror = (e) => console.error('Error:', e);
```

## 🎯 **Expected Behavior**

### **When Working Correctly:**
1. **Server Startup**: ASGI server starts without errors
2. **WebSocket Connection**: Browser connects successfully
3. **Live Session**: Video/chat functionality works
4. **Console Messages**: "WebSocket connected" appears

### **Connection Flow:**
```
Browser → ws://localhost:8000/ws/live-session/appointment_54/
         ↓
Django ASGI → ProtocolTypeRouter
         ↓
AuthMiddlewareStack → Check authentication
         ↓
URLRouter → Route to LiveSessionConsumer
         ↓
LiveSessionConsumer → Handle connection
```

## 🛠️ **Advanced Troubleshooting**

### **If Still Not Working:**

1. **Check Dependencies**:
   ```bash
   pip install channels
   pip install daphne
   ```

2. **Verify ASGI Application**:
   ```python
   from calmconnect_backend.asgi import application
   print(type(application))  # Should be ProtocolTypeRouter
   ```

3. **Test with Daphne**:
   ```bash
   pip install daphne
   daphne calmconnect_backend.asgi:application
   ```

4. **Check for Port Conflicts**:
   ```bash
   netstat -ano | findstr :8000
   ```

5. **Verify Firewall/Antivirus**: Ensure port 8000 isn't blocked

## 🎉 **Success Indicators**

When the WebSocket connection is working:
- ✅ Server starts without ASGI errors
- ✅ Browser console shows "WebSocket connected"
- ✅ Live session page loads without connection errors
- ✅ Video/chat functionality works
- ✅ No 404 or 500 errors in Network tab

## 🚀 **Next Steps**

1. **Start the server** with ASGI support
2. **Test the connection** using the diagnostic script
3. **Check browser console** for connection status
4. **Report any specific errors** for further debugging

The WebSocket infrastructure is properly configured - the issue is likely just the server startup method! 