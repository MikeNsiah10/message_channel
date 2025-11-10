# Message Board Application (Client–Hub–Channel)

##  Overview
This project was developed as part of a university course assignment.  
It implements a distributed **message board system** with three main components:

- **Hub**: The central registry that manages channel registration and coordinates communication.
- **Channel**: Individual message boards where users can post and read messages.
- **Client**: A Flask-based web interface for users to interact with the hub and channels.

⚠️ **Note**: The original hub server was provided temporarily by the professor and is no longer active.  
This repository now serves as a **portfolio project**, demonstrating the architecture and implementation.

---

##  Features
- **Channel registration**: Channels can be registered with the hub using a name, endpoint, and authentication key.
- **Message posting**: Clients can send messages to a channel.
- **Message retrieval**: Clients can view messages from channels in a web interface.
- **Authentication**: Channels are protected with an `authkey` to prevent unauthorized access.
- **Flask UI**: Simple, user-friendly interface for interacting with the system.

---

## Architecture

- The **Client** connects to the Hub to discover available channels.
- The **Hub** keeps track of registered channels and their endpoints.
- The **Channel** hosts the actual message board content and responds to client requests.

---

## Getting Started

### 1. Clone the repository
```
git clone https://github.com/MikeNsiah10/message_channel.git
cd message-channel
```

## Install Dependendies
```
pip install -r requirements.txt
```

## Code Organization
 ```hub.py.
• Run with
> python hub.py
• Runs on localhost, port 5555
• channel.py – The starter code for a channel
• Run with
> python channel.py
• After that, register your channel (in a separate terminal) with
> flask –app channel.py register
• client.py – The client application
• Run with
> python client.py
• Open displayed URL in browser
```


```bash
git clone https://github.com/<your-username>/message_board_app.git
cd message_board_app
