# Re-Authentication via VNC

When you get a "Re-Auth Needed" notification, your Panopto session has expired.

## Steps

1. Open `http://<your-vps-ip>:6080` in any browser
2. You'll see the VPS desktop via noVNC
3. Open Chromium (should be in the taskbar or run `chromium-browser`)
4. Navigate to your Panopto URL
5. Log in with your university credentials
6. Approve the Duo push on your phone
7. Once logged in, close the browser tab (cookies are saved automatically)
8. Close the noVNC tab — done

The next scheduled run will pick up the valid session cookies.

## Frequency

Depends on your university's session timeout. Typically every 1-2 weeks.
If it expires during class, you'll get the re-auth notification ~5 minutes before class starts (the script runs at 2:25pm).
