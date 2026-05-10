# Implementation Plan - Connector: Bot & Mini App

This plan outlines the steps to build a real-time bridge between the NanoMed Telegram Bot and the React-based Mini App.

## User Review Required

> [!IMPORTANT]
> **API Server**: A new file `tma_server.py` will be created. It must run alongside the bot (on a different port, e.g., 8000) for the Mini App to function.
> **Mini App URL**: I will use a placeholder URL `https://nanomed-tma.test` in the bot's keyboard and the React app's API client. You will need to replace this with your actual hosting URL later.

## Proposed Changes

### 1. API Server (Backend Bridge)
Create a dedicated server to handle web requests.

#### [NEW] [tma_server.py](file:///c:/Users/sunna/.antigravity/Nanomed/tma_server.py)
- **FastAPI Application**: Set up routes for doctors, services, and bookings.
- **Validation**: Integrate the `validate_init_data` logic to secure every request.
- **Bot Notification**: When a booking is made via API, the server will call `bot.send_message` to notify the user.

### 2. Frontend Connectivity
Switch the React app from static mocks to dynamic API data.

#### [NEW] [api.js](file:///c:/Users/sunna/.antigravity/Nanomed/frontend/src/utils/api.js)
- Axios instance that automatically includes `Telegram.WebApp.initData` in headers.

#### [MODIFY] [App.jsx](file:///c:/Users/sunna/.antigravity/Nanomed/frontend/src/App.jsx)
- Fetch real doctor data and dashboard info on component mount.
- Update `handleBooking` to send a POST request to the API server.

### 3. Bot Integration
Add the entry point for the Mini App within Telegram.

#### [MODIFY] [patient_kb.py](file:///c:/Users/sunna/.antigravity/Nanomed/keyboards/patient_kb.py)
- Update `main_menu_kb` to include `WebAppInfo` button.

## Verification Plan

### Automated Tests
- Test API endpoints using `curl` or Postman (mocking `initData`).
- Verify database persistence after a successful booking.

### Manual Verification
- Open the bot, click the Mini App button, and verify the React app loads with real database data.
- Complete a booking in the Mini App and check if the bot sends a confirmation message immediately.
