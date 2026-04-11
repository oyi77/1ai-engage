import os
import subprocess
import pandas as pd

def send_whatsapp(phone, message):
    if not phone:
        return
    # Use wacli
    cmd = ["wacli", "send", "--target", phone, "--message", message]
    subprocess.run(cmd)

def send_email(email, subject, body):
    if not email:
        return
    # Use himalaya or stableemail
    # himalaya: himalaya send --to email --subject subject --body body
    cmd = ["himalaya", "send", "--to", email, "--subject", subject, "--body", body]
    subprocess.run(cmd)

def blast(filename="1ai-engage/data/leads.csv"):
    if not os.path.exists(filename):
        print("No leads file found.")
        return
    df = pd.read_csv(filename)
    
    for index, row in df.iterrows():
        email = row.get('email')
        phone = row.get('internationalPhoneNumber') or row.get('phone')
        
        name = row['displayName']
        if isinstance(name, str) and name.startswith('{'):
            try:
                name = json.loads(name.replace("'", '"'))['text']
            except:
                pass
        
        safe_name = "".join([c if c.isalnum() else "_" for c in str(name)])
        draft_path = f"1ai-engage/proposals/drafts/{index}_{safe_name}.txt"
        if os.path.exists(draft_path):
            with open(draft_path, "r") as f:
                content = f.read()
            
            # Simple splitter
            parts = content.split("---WHATSAPP---")
            proposal = parts[0].replace("---PROPOSAL---", "").strip()
            wa_draft = parts[1].strip() if len(parts) > 1 else proposal
            
            if phone:
                print(f"Blasting WA to {phone}...")
                send_whatsapp(phone, wa_draft)
            
            if email:
                print(f"Blasting Email to {email}...")
                send_email(email, "Collaboration Proposal from BerkahKarya", proposal)

if __name__ == "__main__":
    blast()
