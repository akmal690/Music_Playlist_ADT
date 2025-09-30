# Test Case Report: Music Playlist Manager with Player

## Test Environment

- **Platform:** Desktop (Windows/Linux/Mac)
- **Python Version:** 3.7+
- **Dependencies:**
  - tkinter
  - pygame
  - numpy
  - wave
- **Audio Output:** Required for full test (but audio absence is handled gracefully)

---

## Test Cases

### 1. **Application Launch and GUI Initialization**

- **Test Steps:**
  - Run the script: `python music_player.py`
- **Expected Result:**
  - A window titled "Music Playlist Manager with Player" opens.
  - The playlist contains 5 demo songs with test tones, or fallback sample songs.
  - Status output includes startup success message and audio initialization status.

---

### 2. **Add Song (with and without file)**

- **Test Steps:**
  - Enter a song title in the "Add Song" section and click "Add Song".
  - Click "Select Music File", choose a valid `.wav` or `.mp3` file, and add with a title.
- **Expected Result:**
  - Song appears in the playlist listbox.
  - If a file is selected, its path is shown in the output log.
  - Song without a file cannot be played (user is informed by messagebox and log).

---

### 3. **Remove Song**

- **Test Steps:**
  - Enter an existing song title in "Remove Song" and click "Remove Song".
  - Enter a non-existent title and try to remove.
- **Expected Result:**
  - Song is removed from the playlist if present; the playlist display updates.
  - Output log confirms removal or not-found status.

---

### 4. **Play a Song (Double-Click + Play Button)**

- **Test Steps:**
  - Double-click a test tone in the playlist.
  - Click "▶ Play" button with/without selection.
  - Pause, resume, and stop playback using control buttons.
- **Expected Result:**
  - Song plays via system audio if available.
  - Status label shows "Now Playing: ..."
  - Play/pause toggles work. Stop resets state.
  - If song lacks a file, info message and log are shown.

---

### 5. **Next/Previous Song**

- **Test Steps:**
  - Play a song, then click "Next" and "Prev" buttons.
- **Expected Result:**
  - Next/previous playable song starts; playlist selection and status update.
  - If next/previous song lacks a file, log warns user.

---

### 6. **Volume Control**

- **Test Steps:**
  - Move the volume slider in Music Player Controls.
- **Expected Result:**
  - Volume changes in real-time (if audio available).
  - Log shows current volume percentage.

---

### 7. **Generate Test Tone**

- **Test Steps:**
  - Click "Generate Test Tone" in the Demo Features section.
- **Expected Result:**
  - New test tone (440Hz) is generated and added to playlist.
  - Output log confirms addition.

---

### 8. **Sequential & Shuffled Play**

- **Test Steps:**
  - Click "Play Sequentially" and "Play Shuffled".
- **Expected Result:**
  - Output log lists all song titles in order/shuffled.
  - No actual playback for these buttons (they only log the order).

---

### 9. **Persistent temp_songs Directory**

- **Test Steps:**
  - Inspect `temp_songs` directory after running.
- **Expected Result:**
  - WAV files for generated tones are present.
  - Directory is not deleted between runs.

---

### 10. **Audio Unavailable Handling**

- **Test Steps:**
  - Temporarily remove or break `pygame` install, rerun app.
- **Expected Result:**
  - Startup warning appears: "Audio playback is not available..."
  - All player buttons are present but playback actions fail gracefully.
  - No crash on any operation.

---

## Pass/Fail Summary

| Test Case                    | Result  | Notes                                                   |
|------------------------------|---------|---------------------------------------------------------|
| Application Launch           | Pass    | GUI loads, demo songs generated, audio warning as needed|
| Add Song                     | Pass    | Both with/without file, log updates correctly           |
| Remove Song                  | Pass    | Accurate removal, handles missing title                 |
| Play/Pause/Stop              | Pass    | Playback works, UI updates, info on unplayable song     |
| Next/Prev Song               | Pass    | Navigation works, logs on missing files                 |
| Volume Control               | Pass    | Volume adjusts, log updates                            |
| Generate Test Tone           | Pass    | Test tone generated, playlist updates                   |
| Play Sequential/Shuffled     | Pass    | Correct order in log, no sound (by design)              |
| temp_songs Directory         | Pass    | Directory persists, files present                       |
| Audio Unavailable Handling   | Pass    | Graceful fallback, no crashes                           |

---

## Additional Notes

- **Performance:** Responsive even with many songs.
- **Robustness:** Handles missing files, missing audio backend, and invalid user actions gracefully.
- **Cross-Platform:** Works on Windows/Linux/Mac with Python 3.7+ and dependencies installed.
- **No memory leaks or crashes observed.**

---

## Conclusion

**All major test cases pass. This music playlist manager with player is robust and user-friendly for both playlist management and basic audio playback.**
