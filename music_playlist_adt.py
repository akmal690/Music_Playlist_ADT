import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pygame
import os
import threading
import time
import wave
import numpy as np
import tempfile

# Ensure persistent temp_songs directory exists
TEMP_SONGS_DIR = os.path.join(os.path.dirname(__file__), 'temp_songs')
os.makedirs(TEMP_SONGS_DIR, exist_ok=True)

# Initialize pygame mixer for audio playback
try:
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except Exception as e:
    print(f"Audio initialization failed: {e}")
    AUDIO_AVAILABLE = False

class Song:
    def __init__(self, title, file_path=None):
        self.title = title
        self.file_path = file_path
        self.prev = None
        self.next = None

class Playlist:
    def __init__(self, name):
        self.name = name
        self.head = None
        self.tail = None

    def add_song(self, title, file_path=None):
        new_song = Song(title, file_path)
        if not self.head:
            self.head = self.tail = new_song
        else:
            self.tail.next = new_song
            new_song.prev = self.tail
            self.tail = new_song

    def remove_song(self, title):
        current = self.head
        while current:
            if current.title == title:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                return f"{title} removed from playlist."
            current = current.next
        return f"{title} not found."

    def rearrange_song(self, old_title, new_title):
        removed = self.remove_song(old_title)
        if "removed" in removed:
            self.add_song(new_title)
            return f"{old_title} replaced with {new_title}."
        return removed

    def get_all_songs(self):
        songs = []
        current = self.head
        while current:
            songs.append(current)
            current = current.next
        return songs

    def play_sequentially(self):
        songs = self.get_all_songs()
        return [song.title for song in songs]

    def play_shuffled(self):
        songs = self.get_all_songs()
        random.shuffle(songs)
        return [song.title for song in songs]

def generate_test_tone(frequency=440, duration=3, sample_rate=44100):
    """Generate a test tone and save it as a WAV file in temp_songs directory"""
    try:
        # Generate sine wave
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(2 * np.pi * frequency * t)
        
        # Convert to 16-bit integer
        tone = (tone * 32767).astype(np.int16)
        
        # Create a unique file name in temp_songs
        timestamp = int(time.time() * 1000)
        file_name = f"tone_{frequency}Hz_{timestamp}.wav"
        temp_path = os.path.join(TEMP_SONGS_DIR, file_name)
        
        # Save as WAV file
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(tone.tobytes())
        
        return temp_path
    except Exception as e:
        print(f"Error generating test tone: {e}")
        return None

def create_demo_songs():
    """Create demo songs with test tones"""
    demo_songs = []
    
    # Create different test tones
    tones = [
        (440, "A4 Note - 440Hz"),
        (523, "C5 Note - 523Hz"),
        (659, "E5 Note - 659Hz"),
        (784, "G5 Note - 784Hz"),
        (880, "A5 Note - 880Hz")
    ]
    
    for freq, name in tones:
        file_path = generate_test_tone(frequency=freq, duration=2)
        if file_path:
            demo_songs.append((name, file_path))
    
    return demo_songs

class MusicPlayer:
    def __init__(self):
        self.current_song = None
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        self.current_position = 0
        self.playlist = None
        self.current_song_index = 0
        
        # Shuffle state
        self.shuffle_mode = False
        self.shuffle_order = []
        self.current_shuffle_index = -1
        
    def load_song(self, file_path):
        if not AUDIO_AVAILABLE:
            return False
        try:
            pygame.mixer.music.load(file_path)
            return True
        except Exception as e:
            print(f"Error loading song: {e}")
            return False
    
    def play(self):
        if not AUDIO_AVAILABLE:
            return False
        if self.current_song and not self.is_playing:
            try:
                pygame.mixer.music.play()
                self.is_playing = True
                self.is_paused = False
                return True
            except Exception as e:
                print(f"Error playing song: {e}")
                return False
        return False
    
    def pause(self):
        if not AUDIO_AVAILABLE:
            return False
        if self.is_playing:
            try:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.is_playing = False
                return True
            except Exception as e:
                print(f"Error pausing song: {e}")
                return False
        return False
    
    def unpause(self):
        if not AUDIO_AVAILABLE:
            return False
        if self.is_paused:
            try:
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.is_playing = True
                return True
            except Exception as e:
                print(f"Error unpausing song: {e}")
                return False
        return False
    
    def stop(self):
        if not AUDIO_AVAILABLE:
            return False
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            self.current_position = 0
            return True
        except Exception as e:
            print(f"Error stopping song: {e}")
            return False
    
    def set_volume(self, volume):
        if not AUDIO_AVAILABLE:
            return False
        self.volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.volume)
            return True
        except Exception as e:
            print(f"Error setting volume: {e}")
            return False
    
    def play_song(self, song):
        if song and song.file_path and os.path.exists(song.file_path):
            if self.load_song(song.file_path):
                self.current_song = song
                # Always reset state when playing a new song
                self.is_playing = True
                self.is_paused = False
                pygame.mixer.music.play()
                return True
        return False

    def enable_shuffle(self):
        if not self.playlist:
            return False
        songs = self.playlist.get_all_songs()
        self.shuffle_order = list(range(len(songs)))
        if not self.shuffle_order:
            self.shuffle_mode = False
            self.current_shuffle_index = -1
            return False
        random.shuffle(self.shuffle_order)
        self.shuffle_mode = True
        self.current_shuffle_index = 0
        return True

    def disable_shuffle(self):
        self.shuffle_mode = False
        self.shuffle_order = []
        self.current_shuffle_index = -1

    def get_next_index(self):
        songs = self.playlist.get_all_songs() if self.playlist else []
        if not songs:
            return None
        if self.shuffle_mode and self.shuffle_order:
            self.current_shuffle_index = (self.current_shuffle_index + 1) % len(self.shuffle_order)
            return self.shuffle_order[self.current_shuffle_index]
        return (self.current_song_index + 1) % len(songs)

    def get_prev_index(self):
        songs = self.playlist.get_all_songs() if self.playlist else []
        if not songs:
            return None
        if self.shuffle_mode and self.shuffle_order:
            self.current_shuffle_index = (self.current_shuffle_index - 1) % len(self.shuffle_order)
            return self.shuffle_order[self.current_shuffle_index]
        return (self.current_song_index - 1) % len(songs)

class PlaylistGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Playlist Manager with Player")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        self.playlist = Playlist("My Favorites")
        self.music_player = MusicPlayer()
        self.music_player.playlist = self.playlist
        
        self.create_widgets()
        self.setup_initial_songs()
        self.update_playlist_display()
        
        # Initial output message
        self.log_output("Music Playlist Manager started successfully!")
        if not AUDIO_AVAILABLE:
            self.log_output("WARNING: Audio playback is not available. Please install pygame properly.")
        else:
            self.log_output("Audio system initialized successfully.")

    def setup_initial_songs(self):
        # Create demo songs with test tones
        self.log_output("Creating demo songs with test tones...")
        demo_songs = create_demo_songs()
        
        if demo_songs:
            for title, file_path in demo_songs:
                self.playlist.add_song(title, file_path)
            self.log_output(f"Added {len(demo_songs)} demo songs with test tones")
        else:
            # Fallback to sample songs without file paths
            sample_songs = [
                ("_I am the ghost of the Uchiha_ __ Naruto Shippuden [ENG] __ Uchiha Madara Speech [AMV](MP3_70K).mp3", None),
                ("_trending top 10 attitude background musics __ top 10 attitude ringtones __ s.k top 10(MP3_70K).mp3", None),
                ("_Tum Hi Ho_ Aashiqui 2 Full Song With Lyrics _ Aditya Roy Kapur_ Shraddha Kapoor(MP3_70K).mp3", None)
            ]
            for title, file_path in sample_songs:
                self.playlist.add_song(title, file_path)
            self.log_output("Added sample songs (no audio files)")

    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="Music Playlist Manager with Player", 
                             font=("Arial", 20, "bold"), bg='#2c3e50', fg='white')
        title_label.pack(pady=10)

        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Left panel - Playlist management
        left_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Playlist display
        playlist_label = tk.Label(left_frame, text="Current Playlist:", 
                                font=("Arial", 12, "bold"), bg='#34495e', fg='white')
        playlist_label.pack(pady=5)

        # Playlist listbox with scrollbar
        list_frame = tk.Frame(left_frame, bg='#34495e')
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.playlist_listbox = tk.Listbox(list_frame, bg='#ecf0f1', fg='#2c3e50', 
                                         font=("Arial", 10), selectmode='single')
        playlist_scrollbar = tk.Scrollbar(list_frame, orient='vertical', command=self.playlist_listbox.yview)
        self.playlist_listbox.configure(yscrollcommand=playlist_scrollbar.set)
        
        self.playlist_listbox.pack(side='left', fill='both', expand=True)
        playlist_scrollbar.pack(side='right', fill='y')

        # Bind double-click to play song
        self.playlist_listbox.bind('<Double-Button-1>', self.play_selected_song)

        # Center panel - Controls
        center_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        center_frame.pack(side='left', fill='both', expand=True, padx=(10, 10))

        # Music Player Controls
        player_frame = tk.LabelFrame(center_frame, text="Music Player Controls", bg='#34495e', fg='white', font=("Arial", 12, "bold"))
        player_frame.pack(fill='x', padx=10, pady=5)

        # Player buttons frame
        player_buttons_frame = tk.Frame(player_frame, bg='#34495e')
        player_buttons_frame.pack(pady=10)

        # Play/Pause button
        self.play_pause_btn = tk.Button(player_buttons_frame, text="▶ Play", command=self.toggle_play_pause,
                                       bg='#27ae60', fg='white', font=("Arial", 12, "bold"), width=10)
        self.play_pause_btn.pack(side='left', padx=5)

        # Stop button
        stop_btn = tk.Button(player_buttons_frame, text="⏹ Stop", command=self.stop_music,
                            bg='#e74c3c', fg='white', font=("Arial", 12, "bold"), width=10)
        stop_btn.pack(side='left', padx=5)

        # Next button
        next_btn = tk.Button(player_buttons_frame, text="⏭ Next", command=self.next_song,
                            bg='#3498db', fg='white', font=("Arial", 12, "bold"), width=10)
        next_btn.pack(side='left', padx=5)

        # Previous button
        prev_btn = tk.Button(player_buttons_frame, text="⏮ Prev", command=self.previous_song,
                            bg='#9b59b6', fg='white', font=("Arial", 12, "bold"), width=10)
        prev_btn.pack(side='left', padx=5)

        # Volume control
        volume_frame = tk.Frame(player_frame, bg='#34495e')
        volume_frame.pack(pady=10)

        tk.Label(volume_frame, text="Volume:", bg='#34495e', fg='white', font=("Arial", 10)).pack(side='left')
        self.volume_scale = tk.Scale(volume_frame, from_=0, to=100, orient='horizontal', 
                                    command=self.set_volume, bg='#34495e', fg='white', 
                                    highlightbackground='#34495e', length=200)
        self.volume_scale.set(70)
        self.volume_scale.pack(side='left', padx=10)

        # Current song display
        self.current_song_label = tk.Label(player_frame, text="No song selected", 
                                          bg='#34495e', fg='#f39c12', font=("Arial", 10, "bold"))
        self.current_song_label.pack(pady=5)

        # Demo button
        demo_frame = tk.LabelFrame(center_frame, text="Demo Features", bg='#34495e', fg='white', font=("Arial", 10, "bold"))
        demo_frame.pack(fill='x', padx=10, pady=5)

        demo_btn = tk.Button(demo_frame, text="Generate Test Tone", command=self.generate_test_tone,
                            bg='#e67e22', fg='white', font=("Arial", 10, "bold"))
        demo_btn.pack(pady=5)

        # Add song section
        add_frame = tk.LabelFrame(center_frame, text="Add Song", bg='#34495e', fg='white', font=("Arial", 10, "bold"))
        add_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(add_frame, text="Song Title:", bg='#34495e', fg='white').pack(anchor='w', padx=5)
        self.add_entry = tk.Entry(add_frame, width=40, font=("Arial", 10))
        self.add_entry.pack(fill='x', padx=5, pady=2)
        
        # File selection button
        file_btn = tk.Button(add_frame, text="Select Music File", command=self.select_music_file,
                            bg='#f39c12', fg='white', font=("Arial", 10, "bold"))
        file_btn.pack(pady=5)
        
        add_btn = tk.Button(add_frame, text="Add Song", command=self.add_song,
                           bg='#27ae60', fg='white', font=("Arial", 10, "bold"))
        add_btn.pack(pady=5)

        # Remove song section
        remove_frame = tk.LabelFrame(center_frame, text="Remove Song", bg='#34495e', fg='white', font=("Arial", 10, "bold"))
        remove_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(remove_frame, text="Song Title:", bg='#34495e', fg='white').pack(anchor='w', padx=5)
        self.remove_entry = tk.Entry(remove_frame, width=40, font=("Arial", 10))
        self.remove_entry.pack(fill='x', padx=5, pady=2)
        
        remove_btn = tk.Button(remove_frame, text="Remove Song", command=self.remove_song,
                              bg='#e74c3c', fg='white', font=("Arial", 10, "bold"))
        remove_btn.pack(pady=5)

        # Play options section
        play_frame = tk.LabelFrame(center_frame, text="Play Options", bg='#34495e', fg='white', font=("Arial", 10, "bold"))
        play_frame.pack(fill='x', padx=10, pady=5)

        sequential_btn = tk.Button(play_frame, text="Play Sequentially", command=self.play_sequential,
                                 bg='#3498db', fg='white', font=("Arial", 10, "bold"))
        sequential_btn.pack(pady=5)
        
        shuffle_btn = tk.Button(play_frame, text="Play Shuffled", command=self.play_shuffled,
                               bg='#9b59b6', fg='white', font=("Arial", 10, "bold"))
        shuffle_btn.pack(pady=5)

        # Right panel - Output display (moved to right side)
        right_frame = tk.Frame(main_frame, bg='#34495e', relief='raised', bd=2)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))

        # Output display - Now on the right side
        output_frame = tk.LabelFrame(right_frame, text="Output & Status", bg='#34495e', fg='white', font=("Arial", 12, "bold"))
        output_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.output_text = tk.Text(output_frame, height=25, bg='#ecf0f1', fg='#2c3e50', 
                                 font=("Arial", 10), wrap='word')
        output_scrollbar = tk.Scrollbar(output_frame, orient='vertical', command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_scrollbar.set)
        
        self.output_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        output_scrollbar.pack(side='right', fill='y')

    def generate_test_tone(self):
        """Generate a test tone and add it to playlist"""
        self.log_output("Generating test tone...")
        file_path = generate_test_tone(frequency=440, duration=3)
        if file_path:
            title = f"Test Tone - 440Hz ({time.strftime('%H:%M:%S')})"
            self.playlist.add_song(title, file_path)
            self.update_playlist_display()
            self.log_output(f"Added test tone: {title}")
            self.log_output("Double-click the song to play it!")
        else:
            self.log_output("Error generating test tone")

    def select_music_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Music File",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac"), ("All Files", "*.*")]
        )
        if file_path:
            self.add_entry.delete(0, tk.END)
            self.add_entry.insert(0, os.path.basename(file_path))
            self.selected_file_path = file_path
            self.log_output(f"Selected file: {os.path.basename(file_path)}")

    def update_playlist_display(self):
        self.playlist_listbox.delete(0, tk.END)
        songs = self.playlist.get_all_songs()
        for i, song in enumerate(songs, 1):
            # Truncate long song names for display
            display_name = song.title[:50] + "..." if len(song.title) > 50 else song.title
            self.playlist_listbox.insert(tk.END, f"{i}. {display_name}")

    def add_song(self):
        title = self.add_entry.get().strip()
        if title:
            file_path = getattr(self, 'selected_file_path', None)
            self.playlist.add_song(title, file_path)
            self.update_playlist_display()
            self.add_entry.delete(0, tk.END)
            if hasattr(self, 'selected_file_path'):
                delattr(self, 'selected_file_path')
            self.log_output(f"Added song: {title}")
            if file_path:
                self.log_output(f"File path: {file_path}")
            else:
                self.log_output("Note: No file path provided - song cannot be played")
        else:
            messagebox.showwarning("Warning", "Please enter a song title!")

    def remove_song(self):
        title = self.remove_entry.get().strip()
        if title:
            result = self.playlist.remove_song(title)
            self.update_playlist_display()
            self.remove_entry.delete(0, tk.END)
            self.log_output(result)
        else:
            messagebox.showwarning("Warning", "Please enter a song title!")

    def play_selected_song(self, event=None):
        selection = self.playlist_listbox.curselection()
        if selection:
            index = selection[0]
            songs = self.playlist.get_all_songs()
            if 0 <= index < len(songs):
                song = songs[index]
                if song.file_path and os.path.exists(song.file_path):
                    if self.music_player.play_song(song):
                        self.current_song_label.config(text=f"Now Playing: {song.title[:40]}...")
                        self.play_pause_btn.config(text="⏸ Pause")
                        self.log_output(f"Playing: {song.title}")
                        self.music_player.current_song_index = index  # Track current index
                    else:
                        self.log_output(f"Error playing: {song.title}")
                else:
                    self.log_output(f"Could not play: {song.title} (file not found or no file path)")
                    messagebox.showinfo("Info", "This song has no file path. Please add songs with actual music files.")

    def toggle_play_pause(self):
        if self.music_player.is_playing:
            if self.music_player.pause():
                self.play_pause_btn.config(text="▶ Play")
                self.log_output("Music paused")
        elif self.music_player.is_paused:
            if self.music_player.unpause():
                self.play_pause_btn.config(text="⏸ Pause")
                self.log_output("Music resumed")
        else:
            # If nothing is playing, play the first song
            songs = self.playlist.get_all_songs()
            if songs:
                # Play the currently selected song if any, else the first song
                selection = self.playlist_listbox.curselection()
                if selection:
                    self.play_selected_song()
                else:
                    self.playlist_listbox.selection_clear(0, tk.END)
                    self.playlist_listbox.selection_set(0)
                    self.play_selected_song()

    def stop_music(self):
        if self.music_player.stop():
            self.play_pause_btn.config(text="▶ Play")
            self.current_song_label.config(text="No song selected")
            self.log_output("Music stopped")

    def next_song(self):
        songs = self.playlist.get_all_songs()
        if not songs:
            return
        if self.music_player.shuffle_mode and self.music_player.shuffle_order:
            tried = 0
            while tried < len(songs):
                next_index = self.music_player.get_next_index()
                if next_index is None:
                    break
                candidate = songs[next_index]
                if candidate.file_path and os.path.exists(candidate.file_path):
                    if self.music_player.play_song(candidate):
                        self.current_song_label.config(text=f"Now Playing: {candidate.title[:40]}...")
                        self.play_pause_btn.config(text="⏸ Pause")
                        self.log_output(f"Next (Shuffled): {candidate.title}")
                        self.music_player.current_song_index = next_index
                        self.playlist_listbox.selection_clear(0, tk.END)
                        self.playlist_listbox.selection_set(next_index)
                        return
                tried += 1
            self.log_output("No next playable song in shuffled order.")
        else:
            current_index = getattr(self.music_player, 'current_song_index', -1)
            if current_index == -1 and self.music_player.current_song:
                # Fallback: find index by object
                for i, song in enumerate(songs):
                    if song == self.music_player.current_song:
                        current_index = i
                        break
            if current_index >= 0:
                next_index = (current_index + 1) % len(songs)
                next_song = songs[next_index]
                if next_song.file_path and os.path.exists(next_song.file_path):
                    if self.music_player.play_song(next_song):
                        self.current_song_label.config(text=f"Now Playing: {next_song.title[:40]}...")
                        self.play_pause_btn.config(text="⏸ Pause")
                        self.log_output(f"Next song: {next_song.title}")
                        self.music_player.current_song_index = next_index
                        self.playlist_listbox.selection_clear(0, tk.END)
                        self.playlist_listbox.selection_set(next_index)
                else:
                    self.log_output(f"Next song has no file path: {next_song.title}")

    def previous_song(self):
        songs = self.playlist.get_all_songs()
        if not songs:
            return
        if self.music_player.shuffle_mode and self.music_player.shuffle_order:
            prev_index = self.music_player.get_prev_index()
            if prev_index is None:
                self.log_output("No previous song in shuffled order.")
                return
            prev_song = songs[prev_index]
            if prev_song.file_path and os.path.exists(prev_song.file_path):
                if self.music_player.play_song(prev_song):
                    self.current_song_label.config(text=f"Now Playing: {prev_song.title[:40]}...")
                    self.play_pause_btn.config(text="⏸ Pause")
                    self.log_output(f"Previous (Shuffled): {prev_song.title}")
                    self.music_player.current_song_index = prev_index
                    self.playlist_listbox.selection_clear(0, tk.END)
                    self.playlist_listbox.selection_set(prev_index)
            else:
                self.log_output(f"Previous song has no file path: {prev_song.title}")
        else:
            current_index = getattr(self.music_player, 'current_song_index', -1)
            if current_index == -1 and self.music_player.current_song:
                # Fallback: find index by object
                for i, song in enumerate(songs):
                    if song == self.music_player.current_song:
                        current_index = i
                        break
            if current_index >= 0:
                prev_index = (current_index - 1) % len(songs)
                prev_song = songs[prev_index]
                if prev_song.file_path and os.path.exists(prev_song.file_path):
                    if self.music_player.play_song(prev_song):
                        self.current_song_label.config(text=f"Now Playing: {prev_song.title[:40]}...")
                        self.play_pause_btn.config(text="⏸ Pause")
                        self.log_output(f"Previous song: {prev_song.title}")
                        self.music_player.current_song_index = prev_index
                        self.playlist_listbox.selection_clear(0, tk.END)
                        self.playlist_listbox.selection_set(prev_index)
                else:
                    self.log_output(f"Previous song has no file path: {prev_song.title}")

    def set_volume(self, value):
        volume = float(value) / 100.0
        if self.music_player.set_volume(volume):
            self.log_output(f"Volume set to {value}%")
        else:
            self.log_output("Error setting volume")

    def play_sequential(self):
        self.music_player.disable_shuffle()
        self.log_output("Shuffle disabled. Sequential mode active.")
        # Start playing the first playable song, if any
        songs = self.playlist.get_all_songs()
        for i, song in enumerate(songs):
            if song.file_path and os.path.exists(song.file_path):
                if self.music_player.play_song(song):
                    self.current_song_label.config(text=f"Now Playing: {song.title[:40]}...")
                    self.play_pause_btn.config(text="⏸ Pause")
                    self.log_output(f"Playing: {song.title}")
                    self.music_player.current_song_index = i
                    self.playlist_listbox.selection_clear(0, tk.END)
                    self.playlist_listbox.selection_set(i)
                    break
        else:
            self.log_output("No playable songs found to start sequential playback.")

    def play_shuffled(self):
        # Enable shuffle mode and start playback in shuffled order
        songs = self.playlist.get_all_songs()
        if not songs:
            self.log_output("Playlist is empty.")
            return
        if not self.music_player.enable_shuffle():
            self.log_output("Could not enable shuffle (no songs).")
            return
        started = False
        for _ in range(len(songs)):
            index = self.music_player.shuffle_order[self.music_player.current_shuffle_index]
            song = songs[index]
            if song.file_path and os.path.exists(song.file_path):
                if self.music_player.play_song(song):
                    self.current_song_label.config(text=f"Now Playing: {song.title[:40]}...")
                    self.play_pause_btn.config(text="⏸ Pause")
                    self.log_output(f"Playing (Shuffled): {song.title}")
                    self.music_player.current_song_index = index
                    self.playlist_listbox.selection_clear(0, tk.END)
                    self.playlist_listbox.selection_set(index)
                    started = True
                    break
            # Advance to next candidate if not playable
            self.music_player.get_next_index()
        if not started:
            self.log_output("No playable songs found for shuffle. Add songs with valid files.")

    def log_output(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.output_text.see(tk.END)
        # Force update the display
        self.output_text.update()

def main():
    root = tk.Tk()
    app = PlaylistGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
