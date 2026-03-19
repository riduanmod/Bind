from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def convert(s):
    """Convert seconds to human readable format"""
    d, h = divmod(s, 86400)
    h, m = divmod(h, 3600)
    m, s = divmod(m, 60)
    return f"{d} দিন {h} ঘণ্টা {m} মিনিট {s} সেকেন্ড"

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
            
            # Parse the response
            email = data.get("email", "")
            email_to_be = data.get("email_to_be", "")
            countdown = data.get("request_exec_countdown", 0)
            
            # Create a more organized response
            account_status = ""
            message = ""
            
            if email == "" and email_to_be != "":
                account_status = "Pending Change"
                message = f"নতুন ইমেইল ({email_to_be}) যুক্ত হওয়ার অপেক্ষায় আছে।"
            elif email != "" and email_to_be == "":
                account_status = "Secured"
                message = "অ্যাকাউন্টটিতে ইমেইল যুক্ত করা আছে।"
            elif email == "" and email_to_be == "":
                account_status = "Unsecured"
                message = "অ্যাকাউন্টে কোনো ইমেইল যুক্ত নেই।"
            elif email != "" and email_to_be != "":
                account_status = "Changing"
                message = f"বর্তমান ইমেইল পরিবর্তন করে নতুন ইমেইল ({email_to_be}) যুক্ত করার অপেক্ষায় আছে।"
                
            result = {
                "status": "success",
                "status_code": response.status_code,
                "account_state": account_status,
                "message": message,
                "data": {
                    "linked_email": email if email else "নেই",
                    "pending_email": email_to_be if email_to_be else "নেই",
                    "time_remaining_seconds": countdown,
                    "time_remaining_text": convert(countdown) if countdown > 0 else "0",
                    "raw_data": data
                }
            }
            return result
        else:
            return {
                "status": "error",
                "status_code": response.status_code,
                "error": "গারেনা সার্ভার থেকে সঠিক তথ্য পাওয়া যায়নি। টোকেনটি চেক করুন।"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": f"সার্ভার এরর: {str(e)}"
        }

@app.route('/bind_info', methods=['GET'])
def bind_info_endpoint():
    """Endpoint to get bind information"""
    access_token = request.args.get('access_token')
    
    if not access_token:
        return jsonify({
            "status": "error",
            "error": "অনুগ্রহ করে একটি access_token দিন!"
        }), 400
    
    result = get_bind_info(access_token)
    
    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@app.route('/')
def home():
    """Functional Frontend HTML for Riduan FF Info"""
    return """
    <!DOCTYPE html>
    <html lang="bn">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Riduan FF Info - Bind Checker</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f0f2f5;
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 8px 16px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 500px;
                box-sizing: border-box;
            }
            h2 {
                color: #ff4757;
                text-align: center;
                margin-top: 0;
                border-bottom: 2px solid #f1f2f6;
                padding-bottom: 15px;
            }
            .input-group {
                margin-bottom: 20px;
            }
            input[type="text"] {
                width: 100%;
                padding: 12px;
                border: 2px solid #dfe4ea;
                border-radius: 8px;
                font-size: 16px;
                box-sizing: border-box;
                outline: none;
                transition: border-color 0.3s;
            }
            input[type="text"]:focus {
                border-color: #ff4757;
            }
            button {
                width: 100%;
                padding: 14px;
                background-color: #ff4757;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #ff6b81;
            }
            .loader {
                display: none;
                text-align: center;
                margin: 15px 0;
                color: #57606f;
                font-weight: bold;
            }
            .result-card {
                display: none;
                background-color: #f1f2f6;
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                border-left: 5px solid #2ed573;
            }
            .info-row {
                margin-bottom: 12px;
                display: flex;
                justify-content: space-between;
                border-bottom: 1px dashed #ced6e0;
                padding-bottom: 8px;
            }
            .info-row:last-child {
                border-bottom: none;
                margin-bottom: 0;
                padding-bottom: 0;
            }
            .label {
                font-weight: bold;
                color: #2f3542;
            }
            .value {
                color: #57606f;
                text-align: right;
                word-break: break-all;
                max-width: 60%;
            }
            .highlight {
                color: #ff4757;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Riduan FF Info Checker</h2>
            <p style="text-align: center; color: #747d8c; font-size: 14px; margin-bottom: 25px;">গ্যারেনা অ্যাকাউন্টের অ্যাক্সেস টোকেন দিয়ে ইমেইল স্ট্যাটাস চেক করুন</p>
            
            <div class="input-group">
                <input type="text" id="tokenInput" placeholder="আপনার Access Token এখানে দিন...">
            </div>
            <button onclick="fetchBindInfo()">Check Now</button>
            
            <div class="loader" id="loader">তথ্য খোঁজা হচ্ছে... একটু অপেক্ষা করুন।</div>
            
            <div class="result-card" id="resultCard">
                <div class="info-row">
                    <span class="label">অ্যাকাউন্টের অবস্থা:</span>
                    <span class="value highlight" id="resState"></span>
                </div>
                <div class="info-row">
                    <span class="label">যুক্ত থাকা ইমেইল:</span>
                    <span class="value" id="resCurrent"></span>
                </div>
                <div class="info-row">
                    <span class="label">পেন্ডিং ইমেইল:</span>
                    <span class="value" id="resPending"></span>
                </div>
                <div class="info-row">
                    <span class="label">বাকি সময়:</span>
                    <span class="value" id="resTime"></span>
                </div>
                <div style="margin-top: 15px; padding-top: 15px; border-top: 2px solid #dfe4ea; text-align: center; color: #2f3542; font-weight: bold;" id="resMessage">
                </div>
            </div>
        </div>

        <script>
            async function fetchBindInfo() {
                const token = document.getElementById('tokenInput').value.trim();
                const loader = document.getElementById('loader');
                const resultCard = document.getElementById('resultCard');
                
                if (!token) {
                    alert("অনুগ্রহ করে একটি অ্যাক্সেস টোকেন দিন!");
                    return;
                }

                // UI Reset
                resultCard.style.display = 'none';
                loader.style.display = 'block';

                try {
                    const response = await fetch(`/bind_info?access_token=${encodeURIComponent(token)}`);
                    const data = await response.json();
                    
                    loader.style.display = 'none';
                    resultCard.style.display = 'block';

                    if (data.status === 'success') {
                        resultCard.style.borderLeftColor = "#2ed573"; // Green border
                        document.getElementById('resState').innerText = data.account_state;
                        document.getElementById('resState').style.color = "#2ed573";
                        document.getElementById('resCurrent').innerText = data.data.linked_email;
                        document.getElementById('resPending').innerText = data.data.pending_email;
                        document.getElementById('resTime').innerText = data.data.time_remaining_text;
                        document.getElementById('resMessage').innerText = data.message;
                        document.getElementById('resMessage').style.color = "#2f3542";
                    } else {
                        resultCard.style.borderLeftColor = "#ff4757"; // Red border for error
                        document.getElementById('resState').innerText = "Error";
                        document.getElementById('resState').style.color = "#ff4757";
                        document.getElementById('resCurrent').innerText = "-";
                        document.getElementById('resPending').innerText = "-";
                        document.getElementById('resTime').innerText = "-";
                        document.getElementById('resMessage').innerText = data.error;
                        document.getElementById('resMessage').style.color = "#ff4757";
                    }
                } catch (error) {
                    loader.style.display = 'none';
                    alert("সার্ভারের সাথে কানেক্ট করা যাচ্ছে না।");
                }
            }
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
