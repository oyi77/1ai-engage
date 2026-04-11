import pandas as pd
import subprocess
import os
import json

def generate_proposal_fallback(lead_name, lead_business):
    """
    Local template fallback if LLM API fails.
    """
    return f"""
---PROPOSAL---
Subject: Strategic Partnership Proposal for {lead_name}

Dear {lead_name} Team,

I am Vilona from BerkahKarya. We have been monitoring your progress in {lead_business} and see significant potential for optimization through AI.

Our solution offers:
- Automated Lead Generation
- 24/7 AI Customer Engagement
- Efficiency scaling by 40%

I would love to discuss how we can help {lead_name} dominate the market.

Best regards,
Vilona
---WHATSAPP---
Halo Tim {lead_name}! Saya Vilona dari BerkahKarya. Saya lihat bisnis {lead_business} Anda potensial banget buat di-automate pake AI biar makin scale. Boleh ngobrol bentar soal peluang kerjasamanya?
"""

def generate_proposal(lead_name, lead_business):
    prompt = f"""
    Create a professional business proposal and a short WhatsApp draft for the following lead:
    Business Name: {lead_name}
    Niche: {lead_business}
    
    Our Company: BerkahKarya
    Services: AI Automation, Digital Marketing, and Software Development.
    Goal: Help them improve efficiency and revenue with AI.
    
    Format output:
    ---PROPOSAL---
    [Long professional text]
    ---WHATSAPP---
    [Short engaging text with clear call to action]
    """
    
    # Try multiple LLM tools
    for tool in ["gemini", "oracle"]:
        cmd = [tool, "ask", prompt] if tool == "gemini" else [tool, prompt]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout
        except:
            continue
            
    return generate_proposal_fallback(lead_name, lead_business)

def process_proposals(filename="data/leads.csv"):
    if not os.path.exists(filename):
        print("No leads file found.")
        return
    df = pd.read_csv(filename)
    os.makedirs("1ai-engage/proposals/drafts", exist_ok=True)
    
    for index, row in df.iterrows():
        name = row['displayName']
        if isinstance(name, str) and name.startswith('{'):
            try:
                name = json.loads(name.replace("'", '"'))['text']
            except:
                pass
        
        # Determine business type from categories or name
        business = "Local Business"
        
        print(f"Generating proposal for {name}...")
        proposal_text = generate_proposal(name, business)
        
        safe_name = "".join([c if c.isalnum() else "_" for c in str(name)])
        with open(f"1ai-engage/proposals/drafts/{index}_{safe_name}.txt", "w") as f:
            f.write(proposal_text)

if __name__ == "__main__":
    process_proposals()
