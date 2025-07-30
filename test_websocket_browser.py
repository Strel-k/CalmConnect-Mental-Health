<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test</title>
</head>
<body>
    <h1>WebSocket Connection Test</h1>
    <div id="status">Connecting...</div>
    <div id="messages"></div>
    
    <script>
        const statusDiv = document.getElementById('status');
        const messagesDiv = document.getElementById('messages');
        
        function addMessage(message) {
            const div = document.createElement('div');
            div.textContent = new Date().toLocaleTimeString() + ': ' + message;
            messagesDiv.appendChild(div);
        }
        
        // Test different WebSocket URLs
        const testUrls = [
            'ws://localhost:8000/ws/test/',
            'ws://localhost:8000/ws/live-session/test_room/',
            'ws://localhost:8000/ws/chat/test_room/'
        ];
        
        let currentTest = 0;
        
        function testNextUrl() {
            if (currentTest >= testUrls.length) {
                addMessage('All tests completed');
                return;
            }
            
            const url = testUrls[currentTest];
            addMessage(`Testing: ${url}`);
            
            const ws = new WebSocket(url);
            
            ws.onopen = function() {
                addMessage(`✅ Connected to ${url}`);
                statusDiv.textContent = 'Connected!';
                statusDiv.style.color = 'green';
                
                // Send a test message
                ws.send('Hello WebSocket!');
            };
            
            ws.onmessage = function(event) {
                addMessage(`📨 Received: ${event.data}`);
            };
            
            ws.onerror = function(error) {
                addMessage(`❌ Error with ${url}: ${error}`);
            };
            
            ws.onclose = function(event) {
                addMessage(`🔌 Closed: ${event.code} - ${event.reason}`);
                
                // Test next URL after a delay
                setTimeout(() => {
                    currentTest++;
                    testNextUrl();
                }, 1000);
            };
        }
        
        // Start testing
        testNextUrl();
    </script>
</body>
</html> 