# Bazaar Mitra – AI Voice Assistant for Local Commerce

## About the Project

Bazaar Mitra is an AI-powered voice assistant designed for local
commerce. It helps customers with product enquiries, basic support,
and other local business interactions through natural voice conversations.

This project was built as part of the
10 Days of Voice Agents – VoiceForBharat Edition.

## Key Features

- Natural voice conversations
- Hindi, English and Hinglish support
- Customer memory with consent
- Real product data lookup
- Outbound phone calls
- Human escalation
- Call analytics dashboard
- Specialist agent handoff
- Safety guardrails

## How It Works

User
↓
LiveKit
↓
Deepgram STT
↓
Google Gemini
↓
Tools / Memory / Specialist
↓
Murf Falcon TTS
↓
User

## Tech Stack

- Python
- LiveKit Agents
- Google Gemini
- Deepgram
- Murf Falcon
- SQLite
- HTTP APIs
- SIP / Telephony

## Project Journey

### Day 1
Built the basic voice agent.

### Day 2
Added personality, objectives and safety guardrails.

### Day 3
Customized the frontend.

### Day 4
Added persistent customer memory using SQLite.

### Day 5
Added real product catalogue lookup using an external API.

### Day 6
Added outbound calling using SIP/telephony.

### Day 7
Added human escalation for requests requiring human assistance.

### Day 8
Built a call analytics dashboard showing total,
successful and failed calls.

### Day 9
Added a specialist agent and conversation handoff.

### Day 10
Finalized the project documentation and shared the complete
voice-agent journey.

## Setup

1. Clone the repository.
2. Install the required dependencies.
3. Create a `.env.local` file.
4. Add your own API credentials.
5. Start the LiveKit agent.
6. Connect through the browser or configured telephony system.

## Challenges

Some of the main challenges during development were:

- Persistent memory across calls
- Integrating external product data
- Handling API failures and timeouts
- Configuring outbound SIP calls
- Implementing human escalation
- Connecting call data to analytics
- Passing conversations to a specialist agent

## Future Improvements

- Connect to real merchant inventory
- Add real order management
- Improve multilingual support
- Add richer analytics
- Add more specialist agents
- Integrate production-grade business systems


## Blog
https://dev.to/tilak_rajroy_f81d1723578/building-bazaar-mitra-my-10-day-journey-building-a-voice-ai-agent-for-local-commerce-eo0

## LinkedIn

www.linkedin.com/in/tilak-raj-roy-83b85440a

## 10 Days of Voice Agents

Built as part of the
10 Days of Voice Agents – VoiceForBharat Edition.

#VoiceForBharat
