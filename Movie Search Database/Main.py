#-----Statement of Authorship----------------------------------------#
#
# This is an individual assessment task for QUT's teaching unit
# IFB104, "Building IT Systems", Semester 2, 2025. By submitting
# this code I agree that it represents my own work. I am aware of
# the University rule that a student must not act in a manner
# which constitutes academic dishonesty as stated and explained
# in QUT's Manual of Policies and Procedures, Section C/5.3
# "Academic Integrity" and Section E/2.1 "Student Code of Conduct".
#
# Put your student number here as an integer and your name as a
# character string:
#
student_number = 11024208
student_name = "Thomas Cox"
#
# NB: All files submitted for this assessable task will be subjected
# to automated plagiarism analysis using a tool such as the Measure
# of Software Similarity (http://theory.stanford.edu/~aiken/moss/).
#
#--------------------------------------------------------------------#

#-----Preamble-------------------------------------------------------#
from sys import exit as abort

if not isinstance(student_number, int):
    print('\nUnable to run: No student number supplied',
          '(must be an integer), aborting!\n')
    abort()
if not isinstance(student_name, str):
    print('\nUnable to run: No student name supplied',
          '(must be a character string), aborting!\n')
    abort()

#-----Student's Solution---------------------------------------------#
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox
import re
import sqlite3

# --- DARK MODE COLOR PALETTE ---
# These colors create a cohesive dark theme that's easy on the eyes
# and provides good contrast for readability
DARK_BG = "#212337"          # Main window background - deep navy blue
LIGHT_BG = "#282A3A"         # Secondary panels and frames - slightly lighter
ACCENT_BG = "#4B4D66"        # Headers and emphasis areas - medium blue-gray
WIDGET_BG = "#30334E"        # Widget backgrounds like listbox and text areas
WIDGET_ACTIVE = "#5053A6"    # Active/focused widget borders - bright purple
TEXT_COLOR = "#F3F3F3"       # Primary text - off-white for easy reading
SUBTEXT_COLOR = "#A3A3B8"    # Secondary text like labels - muted purple-gray
BUTTON_BG = "#393B57"        # Default button background - dark blue-gray
BUTTON_ACTIVE_BG = "#5053A6" # Button hover/active state - same as widget active
ENTRY_BG = "#23263A"         # Text input field background - darker than widget
HIGHLIGHT_COLOR = "#FFD369"  # Accent color for important elements - warm yellow

class MovieSearchApp:
    """
    Main application class for the MoviVision Media Movie Search system.
    
    This class handles the entire movie search application including:
    - GUI creation and management
    - Database connectivity and searching
    - Live search functionality as user types
    - Responsive layout that adapts to window size
    - Result pagination for large datasets
    - Search result caching for better performance
    """
    
    def __init__(self):
        """Initialize the movie search application with all necessary components."""
        # Create the main Tkinter window
        self.main_window = Tk()
        
        # Performance optimization - cache search results to avoid repeated database queries
        self.search_cache = {}
        
        # Pagination system to handle large result sets efficiently
        self.current_page = 1              # Which page of results we're viewing
        self.results_per_page = 50         # How many movies to show per page
        self.total_results = 0             # Total number of search results
        self.current_results = []          # All results from current search
        
        # Live search functionality - prevents excessive database calls while typing
        self.live_search_delay_id = None   # Timer ID for debouncing live search
        
        # Responsive layout system - tracks current display mode
        self.layout_mode = "horizontal"    # Either "horizontal" or "vertical" layout
        
        # Initialize the application in the correct order
        self.setup_main_window()           # Configure window properties first
        self.create_widgets()              # Create all GUI components
        self.bind_events()                 # Set up event handlers for user interaction
        
        # Check database connection after GUI is ready (100ms delay ensures GUI is loaded)
        self.main_window.after(100, self.check_database_connection)

    def setup_main_window(self):
        """Configure the main application window with appropriate size, styling, and behavior."""
        # Set the window title that appears in the title bar
        self.main_window.title("MoviVision Media Movie Search")
        
        # Set initial window size (width x height)
        self.main_window.geometry("950x760")
        
        # Set minimum window size to prevent UI elements from becoming unusable
        # Width must be at least 520px to keep search buttons visible
        self.main_window.minsize(520, 640)
        
        # Apply the dark theme background color to the main window
        self.main_window.configure(bg=DARK_BG)
        
        # Try to remove the default Tkinter icon for a cleaner, more professional look
        try:
            self.main_window.iconbitmap(default='')  # This removes the default Tk icon
        except:
            # If icon removal fails (some systems), just continue - not critical
            pass
        
        # Set up responsive layout - window will reorganize when user resizes it
        self.main_window.bind('<Configure>', self.on_window_resize)

    def create_widgets(self):
        """Create all GUI components in the correct top-to-bottom order."""
        # Build the interface from top to bottom - this order matters for proper layout
        self.create_header()         # Company branding and title at the top
        self.create_search_area()    # Search controls below the header
        self.create_status_area()    # Status messages below search
        self.create_content_area()   # Main content (movie list and details) in the middle
        self.create_pagination_area() # Page navigation controls at the bottom

    def create_header(self):
        """Create the application header with company branding and title."""
        # Create the main header container with fixed height for consistent appearance
        self.header_frame = Frame(self.main_window, bg=ACCENT_BG, height=88, relief=FLAT)
        self.header_frame.pack(fill=X, padx=12, pady=(12,10))
        
        # Prevent the frame from shrinking when we add content - maintains visual consistency
        self.header_frame.pack_propagate(False)
        
        # Main company title with movie emoji for visual appeal
        # Using large, bold font to establish brand presence
        self.company_label = Label(self.header_frame, text="🎬 MoviVision Media",
                                   font=("Segoe UI", 24, "bold"), fg=TEXT_COLOR, bg=ACCENT_BG)
        self.company_label.pack(pady=22)
        
        # Subtitle to explain the application's purpose
        # Smaller, lighter text that complements but doesn't compete with main title
        self.subtitle_label = Label(self.header_frame, text="Professional Movie Database System",
                                   font=("Segoe UI", 9), fg=SUBTEXT_COLOR, bg=ACCENT_BG)
        self.subtitle_label.pack()

    def create_search_area(self):
        """Create the search interface with filter dropdown, text entry, and action buttons."""
        # Main search container - uses lighter background to distinguish from main content
        self.search_frame = Frame(self.main_window, bg=LIGHT_BG, relief=FLAT, bd=1)
        self.search_frame.pack(fill=X, padx=12, pady=8)
        
        # Inner frame provides consistent padding around all search controls
        self.search_inner = Frame(self.search_frame, bg=LIGHT_BG)
        self.search_inner.pack(fill=X, padx=12, pady=10)
        
        # Label for the search filter dropdown - tells user what the dropdown does
        self.search_filter_label = Label(self.search_inner, text="Search by:", font=("Segoe UI", 10, "bold"),
                                         fg=HIGHLIGHT_COLOR, bg=LIGHT_BG)
        self.search_filter_label.pack(side=LEFT, padx=(0, 8))
        
        # Dropdown to select which field to search (movie title, actor, director, or all)
        # State="readonly" prevents user from typing custom values
        self.search_filter = Combobox(self.search_inner, font=("Segoe UI", 11), width=14, state="readonly")
        self.search_filter['values'] = ("All Fields", "Movie Title", "Actor Name", "Director Name")
        self.search_filter.set("All Fields")  # Default to searching all fields
        self.search_filter.pack(side=LEFT, padx=(0, 15))
        
        # Main search text entry field - where user types their search query
        # Uses fill=X and expand=True so it grows/shrinks with window width
        self.search_entry = Entry(self.search_inner, font=("Segoe UI", 12), width=20,
                                  bg=ENTRY_BG, fg=TEXT_COLOR, insertbackground=HIGHLIGHT_COLOR,
                                  relief=FLAT, highlightthickness=2, highlightbackground=WIDGET_ACTIVE,
                                  highlightcolor=HIGHLIGHT_COLOR, bd=6)
        self.search_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 12))
        
        # Search button - triggers the database search
        # Magnifying glass emoji makes purpose immediately clear
        self.search_button = Button(self.search_inner, text="🔍 Search", command=self.search_movies,
                                    font=("Segoe UI", 11, "bold"), bg=BUTTON_BG, fg=TEXT_COLOR,
                                    activebackground=BUTTON_ACTIVE_BG, activeforeground=TEXT_COLOR,
                                    relief=FLAT, padx=16, pady=6, cursor="hand2")
        self.search_button.pack(side=LEFT, padx=(0, 8))
        
        # Clear button - resets the search and clears results
        # Different color (reddish) to indicate destructive action
        self.clear_button = Button(self.search_inner, text="✖ Clear", command=self.clear_search,
                                   font=("Segoe UI", 11, "bold"), bg="#6B4C57", fg=TEXT_COLOR,
                                   activebackground="#8B5A6B", activeforeground=TEXT_COLOR,
                                   relief=FLAT, padx=12, pady=6, cursor="hand2")
        self.clear_button.pack(side=LEFT)
        
        # Set focus to search entry so user can immediately start typing
        self.search_entry.focus_set()

    def create_status_area(self):
        """Create the status message area that provides feedback to the user."""
        # Status area blends with main background - not meant to draw attention unless important
        self.status_frame = Frame(self.main_window, bg=DARK_BG)
        self.status_frame.pack(fill=X, padx=12, pady=6)
        
        # Status label shows search progress, results count, or error messages
        # Italic font suggests this is supplementary information
        # Color will change based on message type (info=yellow, error=red, success=blue)
        self.status_label = Label(self.status_frame, text="Press 'Search' to display available movies.",
                                  font=("Segoe UI", 11, "italic"), fg=HIGHLIGHT_COLOR, bg=DARK_BG)
        self.status_label.pack(pady=8)

    def create_content_area(self):
        """Create the main content area with movie list and details panels."""
        # Main container for the content - takes up most of the window space
        self.content_frame = Frame(self.main_window, bg=DARK_BG)
        self.content_frame.pack(fill=BOTH, expand=True, padx=12, pady=8)

        # === LEFT PANEL: Movie List ===
        # Panel for displaying the list of movies found by search
        self.left_frame = Frame(self.content_frame, bg=WIDGET_BG, relief=FLAT, bd=1)
        self.left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 8))
        
        # Header section for the movie list with clipboard emoji for visual context
        self.list_header = Frame(self.left_frame, bg=ACCENT_BG, height=35)
        self.list_header.pack(fill=X, padx=2, pady=2)
        self.list_header.pack_propagate(False)  # Maintain consistent header height
        self.list_label = Label(self.list_header, text="📋 Movie List", font=("Segoe UI", 12, "bold"),
                                fg=TEXT_COLOR, bg=ACCENT_BG)
        self.list_label.pack(pady=6)
        
        # Container for the listbox and its scrollbar
        self.list_frame = Frame(self.left_frame, bg=WIDGET_BG)
        self.list_frame.pack(fill=BOTH, expand=True, padx=2, pady=(0, 2))

        # The actual list widget that displays movie titles
        # Configured for dark theme with custom selection colors
        self.movie_listbox = Listbox(self.list_frame, font=("Segoe UI", 10),
                                     relief=FLAT, bd=0, highlightthickness=1,
                                     highlightbackground=WIDGET_ACTIVE, selectbackground=HIGHLIGHT_COLOR,
                                     selectforeground=DARK_BG, bg=WIDGET_BG, fg=TEXT_COLOR,
                                     activestyle="none", height=1, cursor="hand2")
        self.movie_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Scrollbar for the movie list - styled to match dark theme
        self.list_scrollbar = Scrollbar(self.list_frame, orient=VERTICAL, command=self.movie_listbox.yview,
                                        width=16, bg=ACCENT_BG, troughcolor=WIDGET_BG,
                                        activebackground=HIGHLIGHT_COLOR, relief=FLAT, bd=0,
                                        highlightthickness=0)
        self.list_scrollbar.pack(side=RIGHT, fill=Y)
        # Link the scrollbar to the listbox so they work together
        self.movie_listbox.config(yscrollcommand=self.list_scrollbar.set)

        # === RIGHT PANEL: Movie Details ===
        # Panel for displaying detailed information about the selected movie
        self.right_frame = Frame(self.content_frame, bg=WIDGET_BG, relief=FLAT, bd=1)
        self.right_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(8, 0))
        
        # Header section for movie details with film emoji
        self.details_header = Frame(self.right_frame, bg=ACCENT_BG, height=35)
        self.details_header.pack(fill=X, padx=2, pady=2)
        self.details_header.pack_propagate(False)  # Maintain consistent header height
        self.details_label = Label(self.details_header, text="🎬 Movie Details", font=("Segoe UI", 12, "bold"),
                                   fg=TEXT_COLOR, bg=ACCENT_BG)
        self.details_label.pack(pady=6)
        
        # Scrollable text area for displaying movie information
        # Uses ScrolledText which includes its own scrollbar
        # DISABLED state prevents user editing but allows programmatic updates
        self.details_text = ScrolledText(self.right_frame, font=("Segoe UI", 10), wrap=WORD, state=DISABLED,
                                         relief=FLAT, bd=0, highlightthickness=1,
                                         highlightbackground=WIDGET_ACTIVE, bg=WIDGET_BG, fg=TEXT_COLOR,
                                         padx=12, pady=8)
        self.details_text.pack(fill=BOTH, expand=True, padx=2, pady=(0, 2))

    def create_pagination_area(self):
        """Create the pagination controls for navigating through search results."""
        # Main container for pagination controls - slightly elevated appearance
        self.pagination_frame = Frame(self.main_window, bg=LIGHT_BG, relief=FLAT, bd=1)
        self.pagination_frame.pack(fill=X, padx=12, pady=(8, 12))
        
        # Inner container with padding for a clean, spaced layout
        # This creates visual breathing room around the navigation buttons
        self.pagination_inner = Frame(self.pagination_frame, bg=LIGHT_BG)
        self.pagination_inner.pack(fill=X, padx=12, pady=8)
        
        # Previous page button with left-pointing arrow for intuitive navigation
        # Disabled initially since we always start on page 1
        self.prev_button = Button(self.pagination_inner, text="◀ Previous", command=self.prev_page,
                                  font=("Segoe UI", 10, "bold"), state=DISABLED,
                                  bg=BUTTON_BG, fg=TEXT_COLOR, activebackground=BUTTON_ACTIVE_BG,
                                  activeforeground=TEXT_COLOR, relief=FLAT, padx=12, pady=6,
                                  cursor="hand2")
        self.prev_button.pack(side=LEFT, padx=(0, 12))
        
        # Center label showing current page and total pages
        # Uses expand=True to center it between the navigation buttons
        # Highlighted color makes it stand out as important information
        self.page_label = Label(self.pagination_inner, text="", font=("Segoe UI", 11, "bold"),
                                fg=HIGHLIGHT_COLOR, bg=LIGHT_BG)
        self.page_label.pack(side=LEFT, expand=True)
        
        # Next page button with right-pointing arrow for clear direction
        # Disabled initially and when we reach the last page of results
        self.next_button = Button(self.pagination_inner, text="Next ▶", command=self.next_page,
                                  font=("Segoe UI", 10, "bold"), state=DISABLED,
                                  bg=BUTTON_BG, fg=TEXT_COLOR, activebackground=BUTTON_ACTIVE_BG,
                                  activeforeground=TEXT_COLOR, relief=FLAT, padx=12, pady=6,
                                  cursor="hand2")
        self.next_button.pack(side=RIGHT, padx=(12, 0))

    def bind_events(self):
        """Set up all the event handlers that make the interface interactive."""
        # When user clicks on a movie in the list, show its details
        self.movie_listbox.bind('<<ListboxSelect>>', self.on_movie_select)
        
        # When user presses Enter in search box, trigger search immediately
        self.search_entry.bind('<Return>', lambda event: self.search_movies())
        
        # Live search: update results as user types (with debouncing)
        # This gives instant feedback but waits for a pause in typing
        self.search_entry.bind('<KeyRelease>', self.on_search_key_release)
        
        # When user changes the search filter dropdown, update results
        self.search_filter.bind('<<ComboboxSelected>>', lambda event: self.search_movies())
        
        # Keyboard navigation in the movie list for accessibility
        self.movie_listbox.bind('<Up>', self.on_listbox_navigate)
        self.movie_listbox.bind('<Down>', self.on_listbox_navigate)
        
        # Allow Enter key to select movie when list has focus
        self.movie_listbox.bind('<Return>', self.on_movie_select)
        
        # Apply visual hover effects to make buttons feel more responsive
        self.add_hover_effects()

    def add_hover_effects(self):
        """Add hover effects to buttons for better user experience."""
        # These helper functions handle the color changes when mouse enters/leaves buttons
        def on_enter(event, button, hover_color):
            """Change button color when mouse hovers over it"""
            button.configure(bg=hover_color)
        
        def on_leave(event, button, normal_color):
            """Restore button color when mouse leaves it"""
            button.configure(bg=normal_color)
        
        # Main search button - brightens when hovered to show it's interactive
        self.search_button.bind("<Enter>", lambda e: on_enter(e, self.search_button, BUTTON_ACTIVE_BG))
        self.search_button.bind("<Leave>", lambda e: on_leave(e, self.search_button, BUTTON_BG))
        
        # Clear button - uses a slightly different red shade for visual feedback
        self.clear_button.bind("<Enter>", lambda e: on_enter(e, self.clear_button, "#8B5A6B"))
        self.clear_button.bind("<Leave>", lambda e: on_leave(e, self.clear_button, "#6B4C57"))
        
        # Pagination buttons - both use the same hover behavior for consistency
        self.prev_button.bind("<Enter>", lambda e: on_enter(e, self.prev_button, BUTTON_ACTIVE_BG))
        self.prev_button.bind("<Leave>", lambda e: on_leave(e, self.prev_button, BUTTON_BG))
        self.next_button.bind("<Enter>", lambda e: on_enter(e, self.next_button, BUTTON_ACTIVE_BG))
        self.next_button.bind("<Leave>", lambda e: on_leave(e, self.next_button, BUTTON_BG))

    def on_window_resize(self, event):
        """Handle window resize events to switch between horizontal and vertical layouts."""
        # Only respond to resize events from the main window, not child widgets
        if event.widget != self.main_window: return
        
        # Check current window width to determine appropriate layout
        window_width = self.main_window.winfo_width()
        
        # Switch to vertical layout on narrow windows (660px threshold)
        # This prevents the interface from becoming cramped on smaller screens
        if window_width < 660 and self.layout_mode == "horizontal":
            self.switch_to_vertical_layout()
        # Switch back to horizontal layout when there's enough space
        # Horizontal layout is preferred as it shows more information at once
        elif window_width >= 660 and self.layout_mode == "vertical":
            self.switch_to_horizontal_layout()

    def switch_to_vertical_layout(self):
        """Rearrange interface for narrow windows by stacking panels vertically."""
        self.layout_mode = "vertical"
        # Remove both panels from their current positions
        self.left_frame.pack_forget()
        self.right_frame.pack_forget()
        # Stack them vertically with movie list on top, details below
        # This prioritizes the search results which users interact with first
        self.left_frame.pack(in_=self.content_frame, side=TOP, fill=BOTH, expand=True, padx=0, pady=(0, 7))
        self.right_frame.pack(in_=self.content_frame, side=TOP, fill=BOTH, expand=True, padx=0, pady=(7, 0))

    def switch_to_horizontal_layout(self):
        """Rearrange interface for wide windows by placing panels side by side."""
        self.layout_mode = "horizontal"
        # Remove both panels from their current positions
        self.left_frame.pack_forget()
        self.right_frame.pack_forget()
        # Place them side by side with movie list on left, details on right
        # This traditional layout feels natural for desktop users
        self.left_frame.pack(in_=self.content_frame, side=LEFT, fill=BOTH, expand=True, padx=(0, 7), pady=0)
        self.right_frame.pack(in_=self.content_frame, side=RIGHT, fill=BOTH, expand=True, padx=(7, 0), pady=0)

    def on_search_key_release(self, event):
        """Handle live search as user types, with debouncing to avoid too many searches."""
        # Ignore navigation keys that don't change the search text
        # This prevents unnecessary search triggers when user navigates within text
        if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Tab', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R']:
            return
        
        # Cancel any pending search to avoid multiple rapid searches
        # This "debouncing" technique improves performance and user experience
        if self.live_search_delay_id:
            self.main_window.after_cancel(self.live_search_delay_id)
        
        # Schedule a new search after 50ms delay
        # Short enough to feel instant, long enough to avoid search spam
        self.live_search_delay_id = self.main_window.after(50, self.live_search)

    def live_search(self):
        """Perform the actual live search if there's text in the search box."""
        search_text = self.search_entry.get().strip()
        # Only search if user has entered something
        # Empty search would return all movies, which could be overwhelming
        if search_text:
            self.search_movies()

    def clear_search(self):
        """Reset the search interface to its initial empty state."""
        # Clear the search input field
        self.search_entry.delete(0, END)
        
        # Remove all movies from the results list
        self.movie_listbox.delete(0, END)
        
        # Clear the movie details area
        # Need to enable editing, clear content, then disable again
        self.details_text.config(state=NORMAL)
        self.details_text.delete(1.0, END)
        self.details_text.config(state=DISABLED)
        self.current_page = 1
        self.update_pagination_display()
        self.status_label.config(text="Search cleared. Press 'Search' to display available movies.", fg=SUBTEXT_COLOR)

    def search_movies(self):
        """Execute a search based on current search terms and display results."""
        # Clear previous results to prepare for new search
        self.movie_listbox.delete(0, END)
        
        # Clear movie details area (temporarily enable to clear, then disable again)
        self.details_text.config(state=NORMAL)
        self.details_text.delete(1.0, END)
        self.details_text.config(state=DISABLED)
        
        # Get the current search parameters from the interface
        search_term = self.search_entry.get().strip()
        search_by = self.search_filter.get()
        
        # Show searching indicator if user entered a search term
        # This gives immediate feedback that the system is working
        if search_term:
            self.status_label.config(text="Searching database...", fg=HIGHLIGHT_COLOR)
            self.main_window.update_idletasks()  # Force UI update before database query
        
        try:
            # Use caching to avoid repeated database queries for the same search
            # This significantly improves performance for repeated searches
            cache_key = f"{search_term}_{search_by}"
            if cache_key in self.search_cache:
                # Use cached results for instant response
                self.current_results = self.search_cache[cache_key]
            else:
                # Perform new database search and cache the results
                self.current_results = self.search_database(search_term, search_by)
                self.search_cache[cache_key] = self.current_results
            
            # Set up pagination variables
            self.total_results = len(self.current_results)
            self.current_page = 1  # Always start at first page for new search
            
            # Display the first page of results
            self.display_current_page()
            
        except Exception as e:
            # Handle any database errors gracefully with user-friendly message
            self.status_label.config(text=f"Search error: {str(e)}", fg="#FF4F4F")
            print(f"Search error: {e}")  # Log detailed error for debugging

    def display_current_page(self):
        """Show the current page of search results in the movie list."""
        # Calculate which slice of results to show for this page
        start_idx = (self.current_page - 1) * self.results_per_page
        end_idx = min(start_idx + self.results_per_page, self.total_results)
        
        # Extract just the movies for this page from the full results
        page_results = self.current_results[start_idx:end_idx]
        
        # Add each movie title to the listbox for user selection
        for movie in page_results:
            self.movie_listbox.insert(END, movie["title"])
        
        # Update the status bar and pagination controls to reflect current state
        self.update_status_display()
        self.update_pagination_display()

    def update_status_display(self):
        """Update the status bar with information about current search results."""
        search_term = self.search_entry.get().strip()
        search_by = self.search_filter.get()
        
        if self.total_results == 0:
            # No results found - show appropriate message based on whether search was performed
            if search_term == "":
                # User hit search with no terms - probably a database issue
                self.status_label.config(text="No movies found in database.", fg="#FF4F4F")
            else:
                # Specific search returned no results
                self.status_label.config(text=f"No results found for '{search_term}' in {search_by.lower()}.", fg="#FF4F4F")
        else:
            # Show range of results currently displayed (e.g., "Showing 1-50 of 237")
            start_idx = (self.current_page - 1) * self.results_per_page + 1
            end_idx = min(self.current_page * self.results_per_page, self.total_results)
            
            if search_term == "":
                # Showing all movies (no search filter applied)
                self.status_label.config(text=f"Showing {start_idx}-{end_idx} of {self.total_results} movies", fg=HIGHLIGHT_COLOR)
            else:
                # Showing filtered results from a specific search
                self.status_label.config(text=f"Showing {start_idx}-{end_idx} of {self.total_results} results for '{search_term}' in {search_by.lower()}",
                                        fg=HIGHLIGHT_COLOR)

    def update_pagination_display(self):
        """Update pagination buttons and page counter based on current results."""
        # Calculate total pages needed for all results
        total_pages = (self.total_results + self.results_per_page - 1) // self.results_per_page
        
        if total_pages <= 1:
            # Only one page - hide pagination controls entirely
            self.prev_button.config(state=DISABLED)
            self.next_button.config(state=DISABLED)
            self.page_label.config(text="")
        else:
            # Multiple pages - enable/disable buttons based on current position
            # Previous button: disabled on first page, enabled otherwise
            self.prev_button.config(state=NORMAL if self.current_page > 1 else DISABLED)
            # Next button: disabled on last page, enabled otherwise
            self.next_button.config(state=NORMAL if self.current_page < total_pages else DISABLED)
            # Show current page position
            self.page_label.config(text=f"Page {self.current_page} of {total_pages}")

    def prev_page(self):
        """Navigate to the previous page of results."""
        if self.current_page > 1:
            self.current_page -= 1
            # Clear current display and show new page
            self.movie_listbox.delete(0, END)
            self.display_current_page()

    def next_page(self):
        """Navigate to the next page of results."""
        total_pages = (self.total_results + self.results_per_page - 1) // self.results_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            # Clear current display and show new page
            self.movie_listbox.delete(0, END)
            self.display_current_page()

    def on_listbox_navigate(self, event):
        """Handle keyboard navigation in the movie list."""
        # Use after_idle to ensure selection is updated before displaying details
        # This prevents timing issues with keyboard navigation
        self.main_window.after_idle(lambda: self.on_movie_select(None))

    def on_movie_select(self, event):
        """Display detailed information for the selected movie."""
        selection = self.movie_listbox.curselection()
        if selection:
            # Get the index of the selected item in the listbox
            selected_index = selection[0]
            
            # Calculate the actual index in the full results list
            # (accounting for pagination offset)
            start_idx = (self.current_page - 1) * self.results_per_page
            actual_index = start_idx + selected_index
            
            # Verify the index is valid (safety check)
            if actual_index < len(self.current_results):
                selected_movie = self.current_results[actual_index]
                
                # Enable the details text area for editing
                self.details_text.config(state=NORMAL)
                self.details_text.delete(1.0, END)
                
                # Format the movie information in a readable way
                details_content = f"Title: {selected_movie['title']}\n\n"
                details_content += f"Lead Actor: {selected_movie['lead_actor']}\n\n"
                details_content += f"Director: {selected_movie['director']}\n\n"
                details_content += f"Description:\n{selected_movie['description']}"
                
                # Insert the formatted content
                self.details_text.insert(1.0, details_content)
                
                # Highlight search terms in the details if user performed a search
                search_term = self.search_entry.get().strip()
                if search_term:
                    self.highlight_search_terms(self.details_text, search_term)
                
                # Disable editing again to make it read-only
                self.details_text.config(state=DISABLED)

    def highlight_search_terms(self, text_widget, search_term):
        """Highlight occurrences of the search term in the movie details."""
        if not search_term.strip(): return
        
        # Configure the highlight style with bright colors for visibility
        text_widget.tag_configure("highlight", background=HIGHLIGHT_COLOR, foreground=DARK_BG,
                                 font=("Segoe UI", 11, "bold"))
        
        # Get all text content from the widget
        content = text_widget.get(1.0, END)
        
        # Use regex for case-insensitive matching
        # re.escape prevents special characters in search term from being interpreted as regex
        pattern = re.compile(re.escape(search_term.strip()), re.IGNORECASE)
        
        # Find and highlight each occurrence
        for match in pattern.finditer(content):
            # Convert match positions to tkinter text widget coordinates
            start_pos = f"1.0+{match.start()}c"
            end_pos = f"1.0+{match.end()}c"
            text_widget.tag_add("highlight", start_pos, end_pos)

    def check_database_connection(self):
        """Verify database connectivity and display movie count to user."""
        try:
            # Attempt to connect with timeout to prevent hanging
            connection = sqlite3.connect('movies-1.db', timeout=10.0)
            if connection:
                cursor = connection.cursor()
                # Simple query to check if database is accessible and count movies
                cursor.execute("SELECT COUNT(*) FROM movies")
                movie_count = cursor.fetchone()[0]
                connection.close()
                
                # Display success message with movie count for user confidence
                self.status_label.config(text=f"Ready to search {movie_count} movies. Press 'Search' to begin.", fg=HIGHLIGHT_COLOR)
            else:
                # Connection failed for unknown reasons
                self.status_label.config(text="Database connection failed. Please check movies-1.db file.", fg="#FF4F4F")
        except Exception as e:
            # Handle any database errors gracefully with user-friendly message
            self.status_label.config(text=f"Database error: {str(e)}", fg="#FF4F4F")

    def connect_to_database(self):
        """Establish a connection to the movies database."""
        try:
            # Connect with timeout to prevent application hanging
            connection = sqlite3.connect('movies-1.db', timeout=10.0)
            cursor = connection.cursor()
            
            # Test connection with a simple query
            cursor.execute("SELECT COUNT(*) FROM movies")
            cursor.fetchone()  # Actually execute the query
            
            return connection
        except sqlite3.Error as e:
            # Log error details for debugging
            print(f"Database connection error: {e}")
            return None

    def clean_text(self, text):
        """Remove HTML, JavaScript, and formatting artifacts from database text."""
        if not text:
            return ""
        
        # Remove script tags and their content (security and cleanliness)
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove style tags and CSS content
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML comments
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        
        # Remove all remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Replace common HTML entities with their actual characters
        entity_replacements = {
            '&lt;': '<', '&gt;': '>', '&amp;': '&', '&quot;': '"', '&apos;': "'",
            '&nbsp;': ' ', '&ndash;': '–', '&mdash;': '—', '&ldquo;': '"', '&rdquo;': '"',
            '&lsquo;': "'", '&rsquo;': "'", '&hellip;': '...', '&copy;': '©', '&reg;': '®'
        }
        for entity, replacement in entity_replacements.items():
            text = text.replace(entity, replacement)
        
        # Remove JavaScript console.log statements that might have leaked in
        text = re.sub(r'console\.log\([^)]*\);?', '', text, flags=re.IGNORECASE)
        
        # Remove CSS property declarations (property: value;)
        text = re.sub(r'[a-z-]+\s*:\s*[^;]+;', '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace - collapse multiple spaces into single spaces
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Clean up trailing semicolons that might remain from code removal
        text = re.sub(r';+\s*$', '', text)
        
        return text

    def clean_description(self, text):
        """Clean movie description text and ensure it ends with proper punctuation."""
        cleaned_text = self.clean_text(text)
        
        # Add a period if the description doesn't end with punctuation
        # This makes the text look more polished and complete
        if cleaned_text and not cleaned_text.endswith(('.', '!', '?', ':', ';')):
            cleaned_text += '.'
        
        return cleaned_text

    def search_database(self, search_term="", search_by="All Fields"):
        """Query the database for movies matching the search criteria."""
        connection = self.connect_to_database()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor()
            
            # Base query joins movies with actors and directors
            # Uses LEFT JOINs to include movies even if they don't have lead actors or directors
            base_query = """
            SELECT DISTINCT m.title, a.full_name as lead_actor, d.full_name as director, m.description,
                   m.release_year, m.runtime_min, m.mpaa_rating
            FROM movies m
            LEFT JOIN castings c ON m.movie_id = c.movie_id AND c.role_name = 'Lead'
            LEFT JOIN actors a ON c.actor_id = a.actor_id
            LEFT JOIN direction dir ON m.movie_id = dir.movie_id
            LEFT JOIN directors d ON dir.director_id = d.director_id
            """
            
            if search_term.strip() == "":
                # No search term - return all movies alphabetically
                query = base_query + "ORDER BY m.title"
                cursor.execute(query)
            else:
                # Add wildcards for partial matching (e.g., "matrix" matches "The Matrix")
                search_pattern = f"%{search_term}%"
                
                if search_by == "Movie Title":
                    # Search only in movie titles
                    where_clause = "WHERE LOWER(m.title) LIKE LOWER(?)"
                    query = base_query + where_clause + " ORDER BY m.title"
                    cursor.execute(query, (search_pattern,))
                elif search_by == "Actor Name":
                    # Search only in actor names
                    where_clause = "WHERE LOWER(a.full_name) LIKE LOWER(?)"
                    query = base_query + where_clause + " ORDER BY m.title"
                    cursor.execute(query, (search_pattern,))
                elif search_by == "Director Name":
                    # Search only in director names
                    where_clause = "WHERE LOWER(d.full_name) LIKE LOWER(?)"
                    query = base_query + where_clause + " ORDER BY m.title"
                    cursor.execute(query, (search_pattern,))
                else:
                    # "All Fields" - search across title, actor, director, and description
                    # This gives the most comprehensive results but may be slower
                    where_clause = """WHERE LOWER(m.title) LIKE LOWER(?) 
                       OR LOWER(a.full_name) LIKE LOWER(?) 
                       OR LOWER(d.full_name) LIKE LOWER(?) 
                       OR LOWER(m.description) LIKE LOWER(?)"""
                    query = base_query + where_clause + " ORDER BY m.title"
                    cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
            
            # Fetch all matching results
            results = cursor.fetchall()
            movies = []
            
            # Process each database row into a clean movie dictionary
            for row in results:
                title, lead_actor, director, description = row[:4]
                
                # Create movie dictionary with cleaned data
                movie = {
                    'title': self.clean_text(title) if title else "",
                    'lead_actor': self.clean_text(lead_actor) if lead_actor else "Unknown",
                    'director': self.clean_text(director) if director else "Unknown",
                    'description': self.clean_description(description) if description else "No description available."
                }
                
                # Add additional fields if available (year, runtime, rating)
                if len(row) > 4:
                    movie['year'] = row[4] if row[4] else ""
                    movie['runtime'] = row[5] if row[5] else ""
                    movie['rating'] = self.clean_text(row[6]) if row[6] else ""
                
                movies.append(movie)
            
            connection.close()
            return movies
            
        except sqlite3.Error as e:
            # Handle database errors gracefully
            print(f"Database query error: {e}")
            if connection:
                connection.close()
            return []

    def run(self):
        """Start the application's main event loop."""
        # This enters tkinter's main loop, which handles all user interactions
        # The application will run until the user closes the window
        self.main_window.mainloop()

#-----Main Program to Run Student's Solution-------------------------#
if __name__ == "__main__":
    app = MovieSearchApp()
    app.run()