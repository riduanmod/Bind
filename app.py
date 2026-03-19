from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# --- Helper Function (English Output) ---
def convert_seconds_to_human(s):
    """Convert seconds to human readable format in English"""
    d, h = divmod(s, 86400)
    h, m = divmod(h, 3600)
    m, s = divmod(m, 60)
    if d > 0:
        return f"{d}d {h}h {m}m"
    elif h > 0:
        return f"{h}h {m}m {s}s"
    else:
        return f"{m}m {s}s"

# --- Garena API Logic ---
def get_bind_info(access_token):
    """Get bind information from Garena API"""
    url = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
    payload = {'app_id': "100067", 'access_token': access_token}
    headers = {
        'User-Agent': "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip"
    }
    
    try:
        response = requests.get(url, params=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract basic data
            email = data.get("email", "")
            email_to_be = data.get("email_to_be", "")
            countdown = data.get("request_exec_countdown", 0)
            
            # Determine account state in English
            state = "Unknown"
            msg = ""
            
            if email == "" and email_to_be == "":
                state = "Unsecured"
                msg = "No email is currently bound to this account."
            elif email != "" and email_to_be == "":
                state = "Secured"
                msg = "An email is successfully bound and confirmed."
            elif email == "" and email_to_be != "":
                state = "Pending Creation"
                msg = f"A new email ({email_to_be}) is waiting to be bound."
            elif email != "" and email_to_be != "":
                state = "Pending Change"
                msg = f"Current email is being changed to ({email_to_be})."
                
            # রিটার্ন রেসপন্সে আগের সবগুলো অপশন যোগ করা হলো
            return {
                "status": "success",
                "status_code": response.status_code,
                "state": state,
                "message": msg,
                "data": {
                    "current_email": email if email else "",
                    "pending_email": email_to_be if email_to_be else "",
                    "countdown_seconds": countdown,
                    "remaining_time_human": convert_seconds_to_human(countdown) if countdown > 0 else "0",
                    "raw_response": data
                }
            }
        else:
            return {
                "status": "error",
                "status_code": response.status_code,
                "message": "Failed to connect to Garena. Token might be invalid.",
                "response_text": response.text[:500] if response.text else "No response body"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Server Error: {str(e)}"
        }

# --- API Endpoint ---
@app.route('/bind_info', methods=['GET'])
def bind_info_endpoint():
    access_token = request.args.get('access_token')
    
    if not access_token:
        return jsonify({
            "status": "error",
            "message": "Missing access_token parameter!"
        }), 400
    
    result = get_bind_info(access_token)
    return jsonify(result), (200 if result["status"] == "success" else 400)

# --- Professional Dark HTML Frontend ---
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Account Security Checker | Riduan FF Tools</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-color: #0a0a0c;
                --card-bg: #141417;
                --text-primary: #e0e0e0;
                --text-secondary: #a0a0a0;
                --accent: #ff4757;
                --accent-hover: #ff6b81;
                --border-color: #2a2a2e;
                --success: #2ed573;
            }

            * { box-sizing: border-box; margin: 0; padding: 0; }

            body {
                font-family: 'Poppins', sans-serif;
                background-color: var(--bg-color);
                color: var(--text-primary);
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                overflow: hidden;
            }

            @keyframes fadeInDown {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .main-wrapper {
                animation: fadeInDown 0.6s ease-out;
                width: 100%;
                max-width: 480px;
                padding: 20px;
            }

            .container {
                background-color: var(--card-bg);
                padding: 40px;
                border-radius: 16px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                border: 1px solid var(--border-color);
            }

            h1 { font-size: 24px; font-weight: 700; text-align: center; color: var(--accent); margin-bottom: 10px; }
            .subtitle { text-align: center; color: var(--text-secondary); font-size: 14px; margin-bottom: 30px; }

            .input-group { margin-bottom: 20px; }
            input[type="text"] {
                width: 100%; padding: 15px; background-color: rgba(255,255,255,0.03);
                border: 2px solid var(--border-color); border-radius: 8px; color: var(--text-primary);
                font-size: 15px; font-family: inherit; outline: none; transition: all 0.3s ease;
            }
            input[type="text"]:focus {
                border-color: var(--accent); background-color: rgba(255,255,255,0.05);
                box-shadow: 0 0 10px rgba(255, 71, 87, 0.2);
            }

            button {
                width: 100%; padding: 15px; background-color: var(--accent); color: white;
                border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer;
                transition: all 0.3s ease; font-family: inherit;
            }
            button:hover { background-color: var(--accent-hover); transform: translateY(-2px); }

            @keyframes slideInUp {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .result-card {
                display: none; background-color: rgba(255,255,255,0.02); border-radius: 12px;
                margin-top: 25px; padding: 20px; border: 1px solid var(--border-color);
                animation: slideInUp 0.5s ease-out;
            }

            .info-row {
                display: flex; justify-content: space-between; padding: 12px 0;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }
            .info-row:last-child { border-bottom: none; }
            .info-label { color: var(--text-secondary); font-size: 14px; }
            .info-value { color: var(--text-primary); font-size: 14px; text-align: right; word-break: break-all; max-width: 65%; }
            .highlight-state { font-weight: 600; text-transform: uppercase; font-size: 13px; letter-spacing: 1px; }
            .summary-msg { margin-top: 15px; text-align: center; font-size: 13px; color: var(--text-secondary); font-style: italic; }

            .loader {
                display: none; margin: 20px auto 0 auto; border: 3px solid rgba(255,255,255,0.1);
                border-radius: 50%; border-top: 3px solid var(--accent); width: 24px; height: 24px;
                animation: spin 1s linear infinite;
            }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    </head>
    <body>
        <div class="main-wrapper">
            <div class="container">
                <h1>Security Checker</h1>
                <p class="subtitle">Enter Garena Access Token to check bind status</p>
                
                <div class="input-group">
                    <input type="text" id="tokenInput" placeholder="Paste your token here..." autocomplete="off">
                </div>
                <button onclick="checkStatus()" id="btnText">Check Status</button>
                
                <div class="loader" id="loader"></div>
                
                <div class="result-card" id="resultCard">
                    <div class="info-row">
                        <span class="info-label">Account State</span>
                        <span class="info-value highlight-state" id="resState"></span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Linked Email</span>
                        <span class="info-value" id="resCurrent"></span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Pending Email</span>
                        <span class="info-value" id="resPending"></span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Time Remaining</span>
                        <span class="info-value" id="resTime"></span>
                    </div>
                    <p class="summary-msg" id="resMsg"></p>
                </div>
            </div>
        </div>

        <script>
            async function checkStatus() {
                const token = document.getElementById('tokenInput').value.trim();
                const loader = document.getElementById('loader');
                const resultCard = document.getElementById('resultCard');
                const btnText = document.getElementById('btnText');
                
                if (!token) {
                    alert("Please provide an access token.");
                    return;
                }

                resultCard.style.display = 'none';
                loader.style.display = 'block';
                btnText.innerText = "Processing...";
                btnText.disabled = true;

                try {
                    const response = await fetch(`/bind_info?access_token=${encodeURIComponent(token)}`);
                    const result = await response.json();
                    
                    await new Promise(r => setTimeout(r, 400));

                    loader.style.display = 'none';
                    btnText.innerText = "Check Status";
                    btnText.disabled = false;
                    resultCard.style.display = 'block';

                    const stateEl = document.getElementById('resState');

                    if (result.status === 'success') {
                        stateEl.innerText = result.state;
                        if(result.state === 'Secured') { stateEl.style.color = "#2ed573"; } 
                        else if (result.state === 'Unsecured') { stateEl.style.color = "#ffa502"; } 
                        else { stateEl.style.color = "#1e90ff"; }

                        // Updated to match the new JSON structure
                        document.getElementById('resCurrent').innerText = result.data.current_email || "None";
                        document.getElementById('resPending').innerText = result.data.pending_email || "None";
                        document.getElementById('resTime').innerText = result.data.remaining_time_human !== "0" ? result.data.remaining_time_human : "N/A";
                        document.getElementById('resMsg').innerText = result.message;
                    } else {
                        stateEl.innerText = "Error";
                        stateEl.style.color = "#ff4757";
                        document.getElementById('resCurrent').innerText = "N/A";
                        document.getElementById('resPending').innerText = "N/A";
                        document.getElementById('resTime').innerText = "N/A";
                        document.getElementById('resMsg').innerText = result.message;
                    }
                } catch (error) {
                    loader.style.display = 'none';
                    btnText.innerText = "Check Status";
                    btnText.disabled = false;
                    alert("Connection error. Please try again.");
                }
            }
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
