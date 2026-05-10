# Implementation Plan - NanoMed TMA Premium Upgrades

This plan outlines the steps to add advanced features to the NanoMed Telegram Mini App, focusing on patient trust and experience.

## User Review Required

> [!IMPORTANT]
> **Database Changes**: We will add `experience_years`, `bio`, and `image_url` to the `DoctorProfile`. I will populate these with mock data for existing doctors.
> **PDF Access**: To download medical records in the Mini App, the backend will need to serve a temporary decrypted stream or a secure link.

## Proposed Changes

### 1. Database Schema & Data Logic
Enhance models to support bio and detailed scheduling.

#### [MODIFY] [models.py](file:///c:/Users/sunna/.antigravity/Nanomed/database/models.py)
- Add `image_url`, `experience_years`, `bio_uz`, `bio_ru` to `DoctorProfile`.
- Add `description_uz`, `description_ru` to `Service`.

### 2. Backend API (TMA Bridge)
Expand the API to serve all user-specific data.

#### [MODIFY] [tma_api.py](file:///c:/Users/sunna/.antigravity/Nanomed/bot/tma_api.py)
- `get_doctor_full_info(doctor_id)`: Bio, services, and current rating.
- `get_patient_dashboard(patient_id)`: Upcoming appointments, queue status, and link to records.
- `get_queue_position(appointment_id)`: Logic based on scheduled time.

### 3. Frontend (React UI)
Transform the single-page app into a multi-tab professional dashboard.

#### [NEW] [Navbar.jsx](file:///c:/Users/sunna/.antigravity/Nanomed/frontend/src/components/Navbar.jsx)
- Bottom navigation for quick access to "Booking", "Appointments", and "Health".

#### [NEW] [DoctorSelection.jsx](file:///c:/Users/sunna/.antigravity/Nanomed/frontend/src/components/DoctorSelection.jsx)
- List of doctors with cards showing specialty, years of experience, and a star rating.

#### [NEW] [QueueStatus.jsx](file:///c:/Users/sunna/.antigravity/Nanomed/frontend/src/components/QueueStatus.jsx)
- A modern progress bar showing "Waiting" -> "Next" -> "In Consultation".

#### [MODIFY] [App.jsx](file:///c:/Users/sunna/.antigravity/Nanomed/frontend/src/App.jsx)
- Integrate navigation tabs and state for different views.

## Verification Plan

### Automated Tests
- Test queue position logic with various appointment times.
- Verify API response formats for bio and records.

### Manual Verification
- Verify the responsive layout of the new tabs on a mobile view.
- Test the transitions between "Doctor Selection" and "Service Choice".
