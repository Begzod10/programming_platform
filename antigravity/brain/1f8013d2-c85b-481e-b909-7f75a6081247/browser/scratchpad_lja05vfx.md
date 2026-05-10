# Gennis API Investigation Scratchpad

## Tasks:
- [x] Go to 'Groups' or 'My Groups' page (e.g., `https://admin.gennis.uz/platform/myGroups/6`).
- [ ] Capture network requests to identify API endpoints.
- [ ] Identify the endpoint for:
    - [ ] Login (infer from context or previous steps if possible).
    - [ ] Get Groups.
    - [ ] Get Students in a group.
- [ ] Find the 'Authorization' header value and format.
- [ ] Determine the API base URL.

## Findings:
- Current URL: `https://admin.gennis.uz/platform/myGroups/6`
- Groups found:
    - Spsh14:00 (ID 458)
    - Spsh16:00 (ID 506)
    - Dchj16:00 (ID 610)
    - Dchj10:00 (ID 757)
- Teacher ID: 6
- Students in 'My Students' page (ID 3):
    - Abdulaziz Abdulazizov (123123)
- Network request tool is currently failing with "chrome-devtools not found" error.
- Planning to look for API URLs in page scripts or console logs.
- Login token format confirmed: JWT (captured from console log).
