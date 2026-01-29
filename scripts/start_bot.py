#!/usr/bin/env python3

"""
Credit Platform Bot 
-----------------------
1. Fetch emails from Gmail (Realtime)
2. Analyze with AI (Stateless)
3. Send to Next.js API (Local DB)
"""

import os
import sys
import time
import logging
import requests
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_processor import EmailProcessor
from scripts.gmail_fetch import fetch_and_return_emails

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("CreditBot")

load_dotenv()

API_URL = "http://localhost:3000/api/webhook/email"

def main():
    print("\n" + "="*50)
    print(" CREDIT PLATFORM BOT - STARTING...")
    print("="*50 + "\n")
    
    # 1. Init AI
    logger.info(" Loading AI models...")
    try:
        processor = EmailProcessor()
        logger.info(" AI Models loaded!")
    except Exception as e:
        logger.error(f" Error loading AI: {e}")
        return

    print("\n BOT IS ONLINE! Polling Gmail...\n")
    
    loop_count = 0
    try:
        while True:
            loop_count += 1
            if loop_count % 5 == 0:
                print(f"-- Cycle {loop_count} --")

            # 2. Fetch from Gmail
            try:
                # Fetch new emails (raw dicts)
                emails = fetch_and_return_emails(max_results=5)
                
                if emails:
                    print(f"\n {len(emails)} NEW EMAIL(S) FOUND!\n")
                    
                    for email_data in emails:
                        subject = email_data.get("subject", "No Subject")
                        sender = email_data.get("sender", "Unknown")
                        
                        print(f"    Processing: '{subject}' (From: {sender})")
                        
                        try:
                            # 3. Process (Stateless)
                            result = processor.process_email_data(email_data)
                            
                            if result.get("status") == "skipped_sent":
                                print(f"       Skipped (Sent by us)")
                                continue
                                
                            # 4. Send to Next.js API
                            # Merge result with original status for the API
                            payload = result
                            payload['status'] = 'processed' 
                            
                            # Log analysis result
                            data = result.get("extracted_data", {})
                            sim = result.get("similarity_results", {})
                            print(f"       Analyzed: Intent={sim.get('top_intent')} Conf={sim.get('confidence')}")
                            
                            # Send via HTTP
                            try:
                                resp = requests.post(API_URL, json=payload, timeout=10)
                                if resp.status_code == 200:
                                    print(f"       [SUCCESS] Sent to API: OK")
                                else:
                                    print(f"       [ERROR] API Error {resp.status_code}: {resp.text}")
                            except Exception as api_err:
                                print(f"       [ERROR] Failed to contact API: {api_err}")

                        except Exception as proc_err:
                            logger.error(f" Error processing email: {proc_err}")
                
            except Exception as e:
                logger.error(f" Fetch Error: {e}")

            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n Stopping bot.")

if __name__ == "__main__":
    main()
