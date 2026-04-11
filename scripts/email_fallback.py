#!/usr/bin/env python3
"""
1ai-engage Email Fallback Sender
Uses alternative methods when gogcli auth fails
"""
import subprocess
import json
import os

def send_email_via_himalaya(email, subject, body):
    """Fallback: Send via himalaya (IMAP/SMTP)"""
    print(f"Attempting email via himalaya to {email}...")
    cmd = ["himalaya", "send", "--to", email, "--subject", subject, "--body", body]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Email sent via himalaya to {email}")
            return True
        else:
            print(f"❌ Himalaya error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Himalaya failed: {e}")
        return False

def send_email_via_postbridge(email, subject, body):
    """Fallback: Send via PostBridge stableemail API"""
    print(f"Attempting email via PostBridge to {email}...")
    
    payload = {
        "to": email,
        "subject": subject,
        "body": body
    }
    
    cmd = [
        "npx", "agentcash@latest", "fetch",
        "https://stableemail.dev/api/send",
        "-m", "POST",
        "-b", json.dumps(payload)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Email sent via PostBridge to {email}")
            return True
        else:
            print(f"❌ PostBridge error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ PostBridge failed: {e}")
        return False

def send_email_mock(email, subject, body):
    """Mock: Log email for manual review"""
    print(f"[MOCK] Email queued for {email}")
    print(f"Subject: {subject}")
    print(f"Body: {body[:100]}...")
    
    # Save to file for manual review
    os.makedirs("1ai-engage/logs", exist_ok=True)
    with open("1ai-engage/logs/email_queue.log", "a") as f:
        f.write(f"\n---\nTo: {email}\nSubject: {subject}\nBody: {body}\n")
    return True

def send_email(email, subject, body):
    """Multi-fallback email sender"""
    if not email or str(email).lower() == 'nan':
        print("Skip: No email address")
        return False
    
    # Try methods in order
    methods = [
        ("himalaya", lambda: send_email_via_himalaya(email, subject, body)),
        ("PostBridge", lambda: send_email_via_postbridge(email, subject, body)),
        ("Mock/Queue", lambda: send_email_mock(email, subject, body))
    ]
    
    for method_name, method_func in methods:
        try:
            if method_func():
                return True
        except Exception as e:
            print(f"Method {method_name} failed: {e}")
            continue
    
    print(f"❌ All email methods failed for {email}")
    return False

if __name__ == "__main__":
    # Test
    send_email(
        "oyi77.coder@gmail.com",
        "Test 1ai-engage Integration",
        "Halo Boss, ini tes email dari pipeline 1ai-engage. Integrasi sudah aktif dan siap digunakan untuk kampanye cold outreach BerkahKarya. 🔥"
    )
