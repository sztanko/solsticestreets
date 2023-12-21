#!/bin/bash

# Check if the required environment variables are set
if [[ -z "$TG_BOT" || -z "$TG_CHAT_ID" ]]; then
    echo "Please set the TG_BOT and TG_CHAT_ID environment variables."
    exit 1
fi

# Read the message from stdin
read -r message

# Send the message to Telegram
curl -s "https://api.telegram.org/bot$TG_BOT/sendMessage" \
    -d "chat_id=$TG_CHAT_ID" \
    -d "text=$message"

echo
echo "Message sent to Telegram: $message"