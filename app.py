import streamlit as st
from gemini_api import (
    generate_resume_summary,
    generate_cover_letter,
    generate_keywords,
    generate_interview_questions,
    critique_resume_section,
    generate_bullet_points_from_experience,
    generate_achievement_statement,
    generate_linkedin_summary,
    analyze_job_description,
    generate_power_verbs,          # New function import
    expand_resume_section,         # New function import
    summarize_resume_section,      # New function import
    generate_thank_you_note,       # New function import
    generate_networking_message,   # New function import
    generate_career_path_suggestions, # New function import
    generate_learning_resources,   # New function import
    generate_salary_negotiation_script, # New function import
    generate_interview_answer_critique # New function import
)
import os
import json
import datetime
import time # For simulating progress bar delay
import re # For regex operations (e.g., email validation)

# --- 0. Configuration and Constants ---
# Default credentials for the mock login
DEFAULT_USERNAME = "vmduser"
DEFAULT_PASSWORD = "vmdpassword"

# Define available tones and languages
TONES = ["Formal", "Professional", "Concise", "Creative", "Persuasive", "Friendly", "Direct"]
LANGUAGES = ["English", "Spanish", "French", "German", "Italian", "Portuguese"]
RESUME_LENGTH_OPTIONS = ["Concise (3-5 sentences)", "Standard (5-8 sentences)", "Detailed (8-12 sentences)"]
COVER_LETTER_LENGTH_OPTIONS = ["Brief (2-3 paragraphs)", "Standard (3-4 paragraphs)", "Detailed (4-5 paragraphs)"]
CAREER_LEVELS = ["Entry-Level", "Junior", "Mid-Level", "Senior", "Lead", "Manager", "Director", "Executive"]
INDUSTRIES = [
    "Technology", "Healthcare", "Finance", "Education", "Manufacturing", "Retail",
    "Marketing", "Consulting", "Government", "Non-profit", "Media", "Travel & Hospitality"
]


# --- 1. Helper Functions (Moved to top for proper definition before use) ---

def _save_current_input_state():
    """Saves a snapshot of all relevant input fields to a history stack."""
    current_state = {
        "name_input": st.session_state.get("name_input", ""),
        "job_title_input": st.session_state.get("job_title_input", ""),
        "company_input": st.session_state.get("company_input", ""),
        "skills_input": st.session_state.get("skills_input", ""),
        "experience_input": st.session_state.get("experience_input", ""),
        "doc_type": st.session_state.get("doc_type", "Resume"),
        "tone_select": st.session_state.get("tone_select", "Formal"),
        "language_select": st.session_state.get("language_select", "English"),
        "resume_length_select": st.session_state.get("resume_length_select", RESUME_LENGTH_OPTIONS[0]),
        "cl_length_select": st.session_state.get("cl_length_select", COVER_LETTER_LENGTH_OPTIONS[0]),
        "career_level_select": st.session_state.get("career_level_select", CAREER_LEVELS[0]),
        "industry_select": st.session_state.get("industry_select", INDUSTRIES[0]),
        "education_input": st.session_state.get("education_input", ""),
        "projects_input": st.session_state.get("projects_input", ""),
        "achievements_input": st.session_state.get("achievements_input", ""),
        "certifications_input": st.session_state.get("certifications_input", ""),
        "portfolio_link_input": st.session_state.get("portfolio_link_input", ""),
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.input_history_stack.append(current_state)
    # Limit history to prevent excessive memory usage
    st.session_state.input_history_stack = st.session_state.input_history_stack[-5:] # Keep last 5 states

def _load_input_state(state_index):
    """Loads a previous input state from the history stack."""
    if st.session_state.input_history_stack and 0 <= state_index < len(st.session_state.input_history_stack):
        state = st.session_state.input_history_stack[state_index]
        st.session_state.name_input = state["name_input"]
        st.session_state.job_title_input = state["job_title_input"]
        st.session_state.company_input = state["company_input"]
        st.session_state.skills_input = state["skills_input"]
        st.session_state.experience_input = state["experience_input"]
        st.session_state.doc_type = state["doc_type"]
        st.session_state.tone_select = state["tone_select"]
        st.session_state.language_select = state["language_select"]
        st.session_state.resume_length_select = state.get("resume_length_select", RESUME_LENGTH_OPTIONS[0])
        st.session_state.cl_length_select = state.get("cl_length_select", COVER_LETTER_LENGTH_OPTIONS[0])
        st.session_state.career_level_select = state.get("career_level_select", CAREER_LEVELS[0])
        st.session_state.industry_select = state.get("industry_select", INDUSTRIES[0])
        st.session_state.education_input = state.get("education_input", "")
        st.session_state.projects_input = state.get("projects_input", "")
        st.session_state.achievements_input = state.get("achievements_input", "")
        st.session_state.certifications_input = state.get("certifications_input", "")
        st.session_state.portfolio_link_input = state.get("portfolio_link_input", "")
        st.success(f"Input state from {state['timestamp']} loaded successfully.")
        st.experimental_rerun() # Rerun to update the UI with loaded values
    else:
        st.warning("Invalid history state selected.")

def generate_html_preview(document_type, content):
    """
    Generates a simple HTML string for previewing the generated document.
    """
    clean_content = content.replace('\n', '<br>') # Convert newlines to HTML breaks
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{document_type} Preview</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 20px; }}
            h1 {{ color: #4CAF50; }}
            h2 {{ color: #333; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 20px; }}
            ul {{ list-style-type: disc; margin-left: 20px; }}
            li {{ margin-bottom: 5px; }}
            p {{ margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <h1>{document_type} Preview</h1>
        <hr>
        <div style="white-space: pre-wrap; word-wrap: break-word;">{clean_content}</div>
    </body>
    </html>
    """
    return html_template

def clear_form():
    """Clears all input fields on the main form and resets document type."""
    _save_current_input_state() # Save current state before clearing
    st.session_state.name_input = ""
    st.session_state.job_title_input = ""
    st.session_state.company_input = ""
    st.session_state.skills_input = ""
    st.session_state.experience_input = ""
    st.session_state.generated_output = ""
    st.session_state.doc_type = "Resume"
    st.session_state.tone_select = "Formal"
    st.session_state.language_select = "English"
    st.session_state.resume_length_select = RESUME_LENGTH_OPTIONS[0]
    st.session_state.cl_length_select = COVER_LETTER_LENGTH_OPTIONS[0]
    st.session_state.career_level_select = CAREER_LEVELS[0]
    st.session_state.industry_select = INDUSTRIES[0]
    st.session_state.education_input = ""
    st.session_state.projects_input = ""
    st.session_state.achievements_input = ""
    st.session_state.certifications_input = ""
    st.session_state.portfolio_link_input = ""
    st.session_state.common_skills = []
    st.session_state.job_role_template = "None"
    st.session_state.ai_tool_select = "None" # Reset selected tool
    st.session_state.last_generated_html_preview = "" # Clear preview
    st.success("All input fields cleared!")
    st.experimental_rerun() # Rerun to ensure all widgets update their display values

def toggle_theme():
    """Toggles between light and dark themes."""
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'
    st.experimental_rerun() # Rerun to apply theme changes immediately

def save_generation_to_history(doc_type, title, content):
    """
    Saves a generated document to the session history.
    Limits history to the last 10 documents.
    """
    st.session_state.generated_documents.append({
        "type": doc_type,
        "title": title,
        "content": content,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    # Keep only the most recent 10 generations
    st.session_state.generated_documents = st.session_state.generated_documents[-10:]

# --- New Helper Functions for Input Validation ---
def validate_email(email):
    """Validates if the input is a valid email format."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def validate_url(url):
    """Validates if the input is a valid URL format."""
    return re.match(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", url) is not None

def logout():
    """Logs the user out and clears session state."""
    st.session_state.current_user = None
    # Optionally clear other session state variables relevant to the user's session
    keys_to_clear = [key for key in st.session_state.keys() if key not in ['theme']] # Keep theme
    for key in keys_to_clear:
        del st.session_state[key]
    st.experimental_rerun()


# --- 2. Streamlit Page Configuration ---
st.set_page_config(
    page_title="VMD AI: Smart Career Document Generator",
    layout="wide", # Use 'wide' layout for more space
    initial_sidebar_state="expanded", # Keep sidebar expanded by default
    menu_items={
        'Get Help': 'mailto:support@vmdaiai.com',
        'Report a bug': 'mailto:bugs@vmdaiai.com',
        'About': '#about-section'
    }
)

# --- 3. Session State Initialization (Cont.) ---
# Re-initialize after helper functions are defined to ensure proper state management
# for new inputs
# (Already done at the very top, ensuring all keys exist)


# --- 4. Mock User Authentication ---

def show_login_screen():
    """Displays a simple mock login form."""
    st.empty() # Clear main content before displaying login
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Welcome to VMD AI!</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555;'>Your Smart Career Document Generator</h3>", unsafe_allow_html=True)
    st.markdown("---")

    with st.form("login_form"):
        st.write("Please log in to continue:")
        # Default username and password are now constants
        username = st.text_input("Username", key="login_username_input")
        password = st.text_input("Password", type="password", key="login_password_input")
        login_button = st.form_submit_button("Log In")

        if login_button:
            if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
                st.session_state.current_user = username
                st.success(f"Welcome, {username}!")
                st.experimental_rerun() # Rerun to switch to main app
            else:
                st.error(f"Invalid username or password. Please try '{DEFAULT_USERNAME}' and '{DEFAULT_PASSWORD}'.")

# Check if user is logged in
if st.session_state.current_user is None:
    show_login_screen()
    st.stop() # Stop execution here if not logged in

# --- 6. Main Application Layout and Theming ---

# Apply theme based on session state (using inline CSS for Canvas environment)
if st.session_state.theme == 'dark':
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #1a1a2e; /* Dark background */
            color: #e0e0e0; /* Light text */
        }
        .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            background-color: #2e2e4a;
            color: #e0e0e0;
            border-color: #4a4a6e;
        }
        .stSelectbox > div > div > div, .stRadio > div, .stRadio > label {
            color: #e0e0e0;
        }
        .stExpander {
            background-color: #2e2e4a;
            border-radius: 0.5rem;
            border: 1px solid #4a4a6e;
        }
        .stExpander > div > div > p, .stExpander > div > div > div > p {
            color: #e0e0e0;
        }
        .stMarkdown, .stText { /* Ensure markdown and generic text also adopt dark theme colors */
            color: #e0e0e0;
        }
        .stButton button { /* Styling for buttons in dark mode */
            background-color: #4CAF50;
            color: white;
            border-radius: 0.5rem;
            border: none;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f3f4f6; /* Light background */
            color: #374151; /* Dark text */
        }
        .stTextInput > div > div > input, .stTextArea > div > div > textarea {
            background-color: white;
            color: #374151;
            border-color: #d1d5db;
        }
        .stSelectbox > div > div > div, .stRadio > div, .stRadio > label {
            color: #374151;
        }
        .stExpander {
            background-color: white;
            border-radius: 0.5rem;
            border: 1px solid #d1d5db;
        }
        .stExpander > div > div > p, .stExpander > div > div > div > p {
            color: #374151;
        }
        .stMarkdown, .stText { /* Ensure markdown and generic text also adopt light theme colors */
            color: #374151;
        }
        .stButton button { /* Styling for buttons in light mode */
            background-color: #4CAF50;
            color: white;
            border-radius: 0.5rem;
            border: none;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# --- Sidebar Content ---
with st.sidebar:
    st.image("https://placehold.co/150x50/B8B8F0/FFFFFF?text=VMD+AI+Logo", use_column_width=True) # Placeholder for a logo
    st.markdown(f"**Logged in as:** `{st.session_state.current_user}`")
    st.button(f"Switch to {'Dark' if st.session_state.theme == 'light' else 'Light'} Mode", on_click=toggle_theme)
    st.button("Logout", on_click=logout, type="secondary") # New Feature: Logout Button
    st.markdown("---")
    st.header("💡 VMD AI Toolkit")
    st.markdown("""
        Unlock your career potential with AI-powered resume and cover letter generation.
        Our VMD AI engine crafts professional, ATS-optimized documents tailored to your needs.
    """)
    st.info(f"Documents Generated: {st.session_state.ai_usage_count}")
    st.markdown("---")
    st.subheader("Need Help?")
    st.markdown("[Visit our FAQ](#faq-section) | [Contact Us](#contact-us)")
    st.markdown("---")

    # Feature: Session History Display in Sidebar
    if st.session_state.generated_documents:
        st.subheader("Recent Generations")
        # Ensure history is sorted by timestamp descending
        sorted_history = sorted(st.session_state.generated_documents, key=lambda x: x['timestamp'], reverse=True)
        for i, doc in enumerate(sorted_history):
            with st.expander(f"**{doc['type']}** - {doc['title'][:30]}... ({doc['timestamp'].split(' ')[1]})"): # Show time only
                st.write(doc['content'][:150] + "...") # Show a snippet
                if st.button(f"Load {doc['type']} {i+1} into Editor", key=f"load_doc_{i}"):
                    st.session_state.generated_output = doc['content']
                    st.session_state.doc_type = doc['type']
                    # Attempt to pre-fill inputs if possible (more advanced parsing needed for perfect match)
                    if doc['type'] == "Resume":
                        st.session_state.name_input = doc['title'].replace("Resume Summary for ", "")
                    elif doc['type'] == "Cover Letter":
                        st.session_state.company_input = doc['title'].replace("Cover Letter for ", "")
                    st.success(f"Loaded '{doc['type']}' into output area.")
                    # No st.experimental_rerun() needed here, as direct session_state modification triggers rerun

    st.markdown("---")
    # Feature: Input History / Undo
    if len(st.session_state.input_history_stack) > 1:
        st.subheader("Input History (Undo/Redo)")
        current_state_index = len(st.session_state.input_history_stack) - 1
        history_options = [
            f"State {i+1} ({s['timestamp'].split(' ')[1]}): {s['doc_type']}"
            for i, s in enumerate(st.session_state.input_history_stack)
        ]
        selected_history_index = st.selectbox(
            "Select a previous input state:",
            range(len(history_options)),
            format_func=lambda x: history_options[x],
            index=current_state_index,
            key="input_history_select_box"
        )
        if st.button("Load Selected State", key="load_history_state_btn"):
            _load_input_state(selected_history_index)
            # st.experimental_rerun() removed, _load_input_state now handles it.

    st.markdown("---")
    # Feature: Mock User Profile Management
    st.subheader("My Profile (Mock)")
    with st.expander("Edit Profile Details"):
        st.session_state.user_profile["full_name"] = st.text_input("Full Name", value=st.session_state.user_profile["full_name"], key="profile_full_name")
        st.session_state.user_profile["email"] = st.text_input("Email", value=st.session_state.user_profile["email"], key="profile_email")
        # Validate email format
        if st.session_state.user_profile["email"] and not validate_email(st.session_state.user_profile["email"]):
            st.error("Invalid email format.")
        
        st.session_state.user_profile["phone"] = st.text_input("Phone", value=st.session_state.user_profile["phone"], key="profile_phone")
        st.session_state.user_profile["linkedin"] = st.text_input("LinkedIn URL", value=st.session_state.user_profile["linkedin"], key="profile_linkedin")
        # Validate LinkedIn URL format
        if st.session_state.user_profile["linkedin"] and not validate_url(st.session_state.user_profile["linkedin"]):
            st.error("Invalid LinkedIn URL format.")
            
        st.session_state.user_profile["portfolio"] = st.text_input("Portfolio URL", value=st.session_state.user_profile["portfolio"], key="profile_portfolio")
        # Validate Portfolio URL format
        if st.session_state.user_profile["portfolio"] and not validate_url(st.session_state.user_profile["portfolio"]):
            st.error("Invalid Portfolio URL format.")

        if st.button("Save Profile", key="save_profile_btn"):
            if (st.session_state.user_profile["email"] and not validate_email(st.session_state.user_profile["email"])) or \
               (st.session_state.user_profile["linkedin"] and not validate_url(st.session_state.user_profile["linkedin"])) or \
               (st.session_state.user_profile["portfolio"] and not validate_url(st.session_state.user_profile["portfolio"])):
                st.error("Please correct invalid inputs before saving profile.")
            else:
                st.success("Profile details saved (locally to session)!")
    
    # Feature: Pre-fill from Profile Button
    if st.button("Pre-fill from Profile", help="Loads profile data into the main input form."):
        st.session_state.name_input = st.session_state.user_profile["full_name"]
        st.session_state.linkedin_url_input = st.session_state.user_profile["linkedin"] # Assuming a LinkedIn URL input in main form
        st.success("Profile details pre-filled into main form!")
        st.experimental_rerun()


# --- Main Content Area ---
st.header("📄 Your Smart Career Document Generator")
st.markdown("Craft compelling resumes and cover letters with the power of VMD AI.")

# --- Document Type Selection ---
st.markdown("---")
st.subheader("1. Choose Your Document Type")
col1, col2 = st.columns(2)
with col1:
    st.radio(
        "Select Document",
        ["Resume", "Cover Letter"],
        key="doc_type",
        help="Choose whether you want to generate a Resume Summary or a Cover Letter."
    )
with col2:
    st.write("") # Spacer
    st.write("") # Spacer
    if st.session_state.doc_type == "Resume":
        st.info("VMD AI will generate a concise, ATS-optimized resume summary for you.")
    else:
        st.info("VMD AI will create a professional, tailored cover letter.")

st.markdown("---")

# --- User Input Form ---
st.subheader("2. Enter Your Details")

with st.expander("Click to expand/collapse Input Form", expanded=True):
    # Input fields with session state keys for persistence and character count hints
    st.text_input(
        "Your Full Name *",
        placeholder="e.g., Jane Doe",
        key="name_input",
        value=st.session_state.get("name_input", ""), # Pre-fill if exists in session state
        help="Enter your full name as you want it to appear on your document."
    )
    st.text_input(
        "Target Job Title *",
        placeholder="e.g., Senior Software Engineer",
        key="job_title_input",
        value=st.session_state.get("job_title_input", ""),
        help="Specify the exact job title you are applying for. This helps VMD AI tailor the content."
    )

    # Dynamic input for Target Company (only for Cover Letter)
    if st.session_state.doc_type == "Cover Letter":
        st.text_input(
            "Target Company Name *",
            placeholder="e.g., Google Inc.",
            key="company_input",
            value=st.session_state.get("company_input", ""),
            help="Enter the name of the company you are applying to. Essential for personalized cover letters."
        )
    else:
        # Clear company input if not generating cover letter
        if "company_input" in st.session_state:
            st.session_state.company_input = ""

    st.text_area(
        "Your Key Skills (comma-separated) *",
        placeholder="e.g., Python, SQL, Machine Learning, Project Management, Agile",
        height=100,
        key="skills_input",
        value=st.session_state.get("skills_input", ""),
        help="List your most relevant technical and soft skills, separated by commas. Max 200 words."
    )
    # Add a character counter for skills (example)
    if st.session_state.skills_input:
        st.markdown(f"*(Words: {len(st.session_state.skills_input.split())}, Characters: {len(st.session_state.skills_input)})*")


    st.text_area(
        "Brief Summary of Your Professional Experience *",
        placeholder="e.g., 5+ years of experience in leading cross-functional teams, developing scalable web applications, and optimizing database performance...",
        height=200,
        key="experience_input",
        value=st.session_state.get("experience_input", ""),
        help="Provide a concise overview of your career, responsibilities, and key achievements. Max 500 words."
    )
    # Add a character counter for experience
    if st.session_state.experience_input:
        st.markdown(f"*(Words: {len(st.session_state.experience_input.split())}, Characters: {len(st.session_state.experience_input)})*")

    # --- New Feature: Education, Projects, Achievements, Certifications Inputs ---
    st.markdown("---")
    st.subheader("Additional Profile Details (Optional)")
    col_det1, col_det2 = st.columns(2)
    with col_det1:
        st.text_area(
            "Education Summary:",
            placeholder="e.g., Master's in Computer Science from XYZ University, 2022",
            height=100, key="education_input", value=st.session_state.get("education_input", ""),
            help="Summarize your academic background."
        )
        st.text_area(
            "Key Projects (brief descriptions):",
            placeholder="e.g., Developed a data analytics dashboard using Python and Tableau, resulting in 15% improved reporting efficiency.",
            height=150, key="projects_input", value=st.session_state.get("projects_input", ""),
            help="Highlight 1-3 significant projects with brief descriptions and impact."
        )
    with col_det2:
        st.text_area(
            "Achievements & Awards:",
            placeholder="e.g., Awarded 'Employee of the Year' 2023; Led initiative that saved $50k annually.",
            height=100, key="achievements_input", value=st.session_state.get("achievements_input", ""),
            help="List any significant achievements, awards, or recognition."
        )
        st.text_area(
            "Certifications:",
            placeholder="e.g., PMP, AWS Certified Solutions Architect, Certified Scrum Master",
            height=150, key="certifications_input", value=st.session_state.get("certifications_input", ""),
            help="List relevant professional certifications."
        )
    
    st.text_input(
        "Portfolio/Personal Website Link:",
        placeholder="https://yourportfolio.com",
        key="portfolio_link_input", value=st.session_state.get("portfolio_link_input", ""),
        help="Provide a link to your online portfolio or personal website."
    )
    # Validate portfolio URL
    if st.session_state.portfolio_link_input and not validate_url(st.session_state.portfolio_link_input):
        st.error("Invalid Portfolio URL format. Please enter a valid URL (e.g., https://example.com).")


    # --- Feature: Tone, Language, and Length Selection ---
    st.markdown("---")
    st.subheader("3. Customization Options")
    colA, colB, colC = st.columns(3)
    with colA:
        st.selectbox(
            "Select Tone",
            TONES,
            key="tone_select",
            index=TONES.index(st.session_state.tone_select), # Set initial value from session state
            help="Choose the desired tone for your generated document."
        )
    with colB:
        st.selectbox(
            "Select Language",
            LANGUAGES,
            key="language_select",
            index=LANGUAGES.index(st.session_state.language_select), # Set initial value from session state
            help="Select the language for the generated document. Note: AI performance may vary by language."
        )
    with colC:
        if st.session_state.doc_type == "Resume":
            st.selectbox(
                "Select Length",
                RESUME_LENGTH_OPTIONS,
                key="resume_length_select",
                index=RESUME_LENGTH_OPTIONS.index(st.session_state.resume_length_select),
                help="Choose the approximate length of the generated resume summary."
            )
        else: # Cover Letter
            st.selectbox(
                "Select Length",
                COVER_LETTER_LENGTH_OPTIONS,
                key="cl_length_select",
                index=COVER_LETTER_LENGTH_OPTIONS.index(st.session_state.cl_length_select),
                help="Choose the approximate length of the generated cover letter."
            )

    # --- New Feature: Career Level and Industry Selector ---
    colD, colE = st.columns(2)
    with colD:
        st.selectbox(
            "Your Career Level",
            CAREER_LEVELS,
            key="career_level_select",
            index=CAREER_LEVELS.index(st.session_state.career_level_select),
            help="Your current or target career level. Helps VMD AI tailor formality and depth."
        )
    with colE:
        st.selectbox(
            "Target Industry",
            INDUSTRIES,
            key="industry_select",
            index=INDUSTRIES.index(st.session_state.industry_select),
            help="The industry of the job you are applying for. Helps VMD AI use relevant jargon and focus."
        )
    
    # --- Feature: Pre-defined Skill Tags & Job Role Selection ---
    st.markdown("---")
    st.subheader("Quick Select Options & Sample Data")
    colF, colG = st.columns(2)
    with colF:
        st.session_state.common_skills = st.multiselect(
            "Add Common Skills (Optional)",
            ["Problem-Solving", "Communication", "Teamwork", "Leadership", "Data Analysis", "Cloud Computing", "Cybersecurity", "Project Management", "Customer Service", "Sales", "Financial Modeling"],
            default=st.session_state.common_skills, # Persist selection
            help="Select common skills to append to your existing skills. Duplicates will be removed."
        )
        if st.session_state.common_skills:
            current_skills_list = [s.strip() for s in st.session_state.skills_input.split(',') if s.strip()]
            combined_skills = list(set(current_skills_list + st.session_state.common_skills))
            st.session_state.skills_input = ", ".join(combined_skills)

    with colG:
        st.selectbox(
            "Load Job Role Template (Optional)",
            ["None", "Software Developer", "Data Scientist", "Marketing Specialist", "Project Manager", "Customer Support", "HR Manager", "Financial Analyst"],
            key="job_role_template",
            index=["None", "Software Developer", "Data Scientist", "Marketing Specialist", "Project Manager", "Customer Support", "HR Manager", "Financial Analyst"].index(st.session_state.job_role_template),
            help="Selecting a template can pre-fill your Job Title and suggest skills (will overwrite existing inputs if applied)."
        )
        # Handle the template application logic
        if st.session_state.job_role_template != "None":
            if st.session_state.job_role_template == "Software Developer":
                st.session_state.job_title_input = "Software Developer"
                st.session_state.skills_input = "Python, Java, JavaScript, REST APIs, Databases, Agile, Git, AWS, Docker"
                st.session_state.experience_input = "Designed, developed, and deployed scalable web applications using modern frameworks. Collaborated with cross-functional teams to deliver high-quality software solutions and optimize system performance."
            elif st.session_state.job_role_template == "Data Scientist":
                st.session_state.job_title_input = "Data Scientist"
                st.session_state.skills_input = "Python (Pandas, NumPy, Scikit-learn), R, SQL, Machine Learning, Statistical Modeling, Data Visualization, Big Data, Predictive Analytics"
                st.session_state.experience_input = "Developed and implemented machine learning models for predictive analytics, improving business decision-making. Performed extensive data analysis, visualization, and reporting."
            elif st.session_state.job_role_template == "Marketing Specialist":
                st.session_state.job_title_input = "Marketing Specialist"
                st.session_state.skills_input = "Digital Marketing, SEO, SEM, Social Media Marketing, Content Creation, Analytics, Campaign Management, HubSpot, Google Ads"
                st.session_state.experience_input = "Managed and optimized digital marketing campaigns across various platforms, significantly increasing brand visibility and lead generation. Created engaging content and analyzed campaign performance."
            elif st.session_state.job_role_template == "Project Manager":
                st.session_state.job_title_input = "Project Manager"
                st.session_state.skills_input = "Project Planning, Risk Management, Stakeholder Communication, Agile, Scrum, Budget Management, Team Leadership, JIRA, Confluence"
                st.session_state.experience_input = "Successfully led multiple complex projects from initiation to closure, ensuring on-time and within-budget delivery. Managed diverse teams and communicated effectively with stakeholders."
            elif st.session_state.job_role_template == "Customer Support":
                st.session_state.job_title_input = "Customer Support Specialist"
                st.session_state.skills_input = "Customer Service, Communication, Problem-Solving, Conflict Resolution, CRM Software (e.g., Salesforce), Technical Support, Empathy"
                st.session_state.experience_input = "Provided excellent customer support, resolving complex issues and improving customer satisfaction ratings. Trained new team members and contributed to knowledge base articles."
            elif st.session_state.job_role_template == "HR Manager":
                st.session_state.job_title_input = "HR Manager"
                st.session_state.skills_input = "Recruitment, Employee Relations, Performance Management, Compensation & Benefits, HRIS, Talent Development, Compliance"
                st.session_state.experience_input = "Managed full-cycle recruitment, developed employee retention programs, and ensured HR compliance. Provided strategic HR guidance to management."
            elif st.session_state.job_role_template == "Financial Analyst":
                st.session_state.job_title_input = "Financial Analyst"
                st.session_state.skills_input = "Financial Modeling, Data Analysis, Budgeting, Forecasting, Valuation, Excel (Advanced), PowerPoint, SQL"
                st.session_state.experience_input = "Conducted in-depth financial analysis, prepared detailed reports, and developed financial models to support strategic business decisions. Contributed to budget planning and performance tracking."
            st.session_state.job_role_template = "None" # Reset to "None" after applying to prevent re-application
            st.experimental_rerun() # Rerun to update inputs


    # New Feature: Load Sample Data Button
    if st.button("Load Sample Data (for testing)", help="Pre-fills all fields with sample data for quick testing."):
        st.session_state.name_input = "Alex Johnson"
        st.session_state.job_title_input = "Marketing Specialist"
        st.session_state.company_input = "Innovate Corp."
        st.session_state.skills_input = "Digital Marketing, SEO, Content Creation, Social Media Management, Google Analytics, Campaign Optimization"
        st.session_state.experience_input = "Managed digital marketing campaigns across multiple platforms, increasing online presence by 30% and lead generation by 15%. Developed and executed content strategies for various social media channels and blog posts."
        st.session_state.doc_type = "Resume"
        st.session_state.tone_select = "Professional"
        st.session_state.language_select = "English"
        st.session_state.resume_length_select = "Standard (5-8 sentences)"
        st.session_state.cl_length_select = "Standard (3-4 paragraphs)"
        st.session_state.career_level_select = "Mid-Level"
        st.session_state.industry_select = "Marketing"
        st.session_state.education_input = "Bachelor of Business Administration, University of Sampletown, 2018"
        st.session_state.projects_input = "Developed a local business SEO audit tool; Led a university marketing campaign that increased student engagement by 25%."
        st.session_state.achievements_input = "Awarded 'Marketing Innovator of the Year' 2023; Exceeded Q4 lead targets by 20%."
        st.session_state.certifications_input = "Google Ads Certification, HubSpot Content Marketing Certification"
        st.session_state.portfolio_link_input = "https://alexjohnsonportfolio.com"
        st.success("Sample data loaded! Click 'Generate Document' to see results.")
        st.experimental_rerun() # Rerun to update UI with sample data


# --- Generate Button ---
st.markdown("---")
col_btn1, col_btn2 = st.columns([0.7, 0.3])
with col_btn1:
    generate_button = st.button(
        "🚀 Generate Document with VMD AI",
        use_container_width=True,
        type="primary",
        help="Click to generate your resume summary or cover letter."
    )
with col_btn2:
    clear_button = st.button(
        "🔄 Clear All Inputs",
        on_click=clear_form, # Assign helper function to clear inputs
        use_container_width=True,
        help="Clear all text fields and reset the form."
    )

# --- 7. Document Generation Logic ---

if generate_button:
    _save_current_input_state() # Save current state before attempting generation

    # Validate user inputs
    errors = []
    if not st.session_state.name_input.strip():
        errors.append("Your Full Name is required.")
    if not st.session_state.job_title_input.strip():
        errors.append("Target Job Title is required.")
    if not st.session_state.skills_input.strip():
        errors.append("Key Skills are required.")
    if not st.session_state.experience_input.strip():
        errors.append("Professional Experience Summary is required.")
    if st.session_state.doc_type == "Cover Letter" and not st.session_state.company_input.strip():
        errors.append("Target Company is required for a Cover Letter.")
    if st.session_state.portfolio_link_input and not validate_url(st.session_state.portfolio_link_input):
        errors.append("Invalid Portfolio URL format.")

    if errors:
        for error in errors:
            st.error(error)
        st.session_state.generated_output = "" # Clear output if validation fails
    else:
        st.session_state.generated_output = "" # Clear previous output
        st.session_state.last_generated_html_preview = "" # Clear previous preview
        with st.spinner("VMD AI is crafting your document... Please wait."):
            progress_bar = st.progress(0)
            
            doc_title_for_history = ""
            try:
                if st.session_state.doc_type == "Resume":
                    # Pass selected length option
                    length_option = st.session_state.resume_length_select.split(' ')[0] # Get 'Concise', 'Standard', 'Detailed'
                    st.session_state.generated_output = generate_resume_summary(
                        st.session_state.name_input,
                        st.session_state.job_title_input,
                        st.session_state.skills_input,
                        st.session_state.experience_input,
                        st.session_state.tone_select,
                        st.session_state.language_select,
                        length_option
                    )
                    doc_title_for_history = f"Resume Summary for {st.session_state.name_input}"
                else: # Cover Letter
                    # Pass selected length option
                    length_option = st.session_state.cl_length_select.split(' ')[0] # Get 'Brief', 'Standard', 'Detailed'
                    st.session_state.generated_output = generate_cover_letter(
                        st.session_state.name_input,
                        st.session_state.job_title_input,
                        st.session_state.company_input,
                        st.session_state.skills_input,
                        st.session_state.experience_input,
                        st.session_state.tone_select,
                        st.session_state.language_select,
                        length_option
                    )
                    doc_title_for_history = f"Cover Letter for {st.session_state.company_input}"
                
                # Simulate progress for better UX
                for i in range(100):
                    progress_bar.progress(i + 1)
                    time.sleep(0.01) # Small delay to see animation

                progress_bar.empty() # Remove progress bar after completion

                if "VMD AI encountered an error" in st.session_state.generated_output:
                    st.error(st.session_state.generated_output)
                else:
                    st.success(f"🎉 Your {st.session_state.doc_type} has been generated by VMD AI!")
                    st.session_state.ai_usage_count += 1 # Increment AI usage counter
                    save_generation_to_history(st.session_state.doc_type, doc_title_for_history, st.session_state.generated_output)
                    st.session_state.last_generated_html_preview = generate_html_preview(st.session_state.doc_type, st.session_state.generated_output)

            except Exception as e:
                st.error(f"An unexpected error occurred during generation: {e}")
                st.session_state.generated_output = "" # Clear output on error
                st.session_state.last_generated_html_preview = ""

# --- 8. Output Display Area ---
if st.session_state.generated_output:
    st.markdown("---")
    st.subheader("Your Generated Document")
    
    # Feature: Tabbed Output Display (Text vs. Preview)
    output_tab, preview_tab = st.tabs(["Text Output", "HTML Preview (Basic)"])

    with output_tab:
        st.text_area(
            f"{st.session_state.doc_type} from VMD AI:",
            value=st.session_state.generated_output,
            height=450,
            key="generated_output_display", # Use a unique key for the display area
            help="This is the AI-generated content. You can copy it or perform further actions below."
        )

        col_dl1, col_dl2, col_dl3 = st.columns(3)
        with col_dl1:
            st.download_button(
                label="📥 Download as TXT",
                data=st.session_state.generated_output.encode("utf-8"),
                file_name=f"{st.session_state.doc_type.replace(' ', '_').lower()}_{st.session_state.name_input.replace(' ', '_').lower()}_vmd_ai.txt",
                mime="text/plain",
                help="Download the generated document as a plain text file."
            )
        with col_dl2:
            # Client-side copy (Streamlit doesn't have a direct copy to clipboard button)
            # This is a common workaround using JS, but won't work in basic Canvas.
            # For a full Streamlit deployment, this would be a custom component or a hack.
            # For now, we will simply provide a text for manual copy.
            st.markdown(
                """
                <button onclick="navigator.clipboard.writeText(document.querySelector('textarea[data-testid=\"stTextarea\"]').value)" 
                        style="background-color:#007BFF;color:white;padding:10px 20px;border-radius:5px;border:none;cursor:pointer;width:100%;">
                    📋 Copy to Clipboard
                </button>
                <script>
                // This script targets the Streamlit textarea and copies its content.
                // It might not work in all embedded environments due to security restrictions.
                // In a live Streamlit app, this often needs st.components.v1.html.
                const copyButton = document.querySelector('button[onclick*="navigator.clipboard"]');
                if (copyButton) {
                    copyButton.addEventListener('click', function() {
                        const textarea = document.querySelector('textarea[data-testid="stTextarea"]');
                        if (textarea) {
                            textarea.select();
                            textarea.setSelectionRange(0, 99999); // For mobile devices
                            document.execCommand('copy');
                            // Removed alert: Use Streamlit's native st.success/info if possible for feedback
                            // alert('Content copied to clipboard!');
                        }
                    });
                }
                </script>
                """,
                unsafe_allow_html=True
            )
        with col_dl3:
            # Feature: Share via Email (Mock)
            # In a real app, this would integrate with an SMTP server or email API
            email_subject = f"Your VMD AI Generated {st.session_state.doc_type}"
            email_body = f"Hello,\n\nHere is your generated {st.session_state.doc_type} from VMD AI:\n\n{st.session_state.generated_output}\n\nBest regards,\nVMD AI Team"
            st.markdown(f'<a href="mailto:?subject={email_subject}&body={email_body}" target="_blank" style="display: inline-block; background-color: #f63366; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; width: 100%; text-align: center;">✉️ Share via Email</a>', unsafe_allow_html=True)


    with preview_tab:
        if st.session_state.last_generated_html_preview:
            # Feature: Document Preview
            st.subheader("HTML Preview")
            # Use Streamlit's experimental_singleton to display HTML content
            # Note: This is a simplified preview. Full HTML rendering might require st.components.v1.html in a deployed app.
            st.markdown(st.session_state.last_generated_html_preview, unsafe_allow_html=True)
            st.info("This is a basic HTML preview. For accurate formatting, copy the text into a document editor.")
        else:
            st.info("Generate a document first to see its HTML preview.")

    # --- Feature: Quick Feedback Mechanism ---
    st.markdown("---")
    st.subheader("Was this document helpful?")
    feedback = st.radio("Your feedback helps us improve VMD AI:", ["Yes, very helpful!", "It was okay.", "Needs improvement."], horizontal=True, key="feedback_radio")
    if st.button("Submit Feedback", key="submit_feedback_btn"):
        st.success(f"Thank you for your feedback: '{feedback}'! We appreciate it.")
        # In a real app, you'd save this feedback to a database.

    # --- Feature: Basic Rating System ---
    st.markdown("---")
    st.subheader("Rate AI Output Quality")
    rating = st.slider("How would you rate the quality of the generated document (1-5 stars)?", 1, 5, 3, key="output_rating_slider")
    if st.button("Submit Rating", key="submit_rating_btn"):
        st.success(f"Thank you for rating the document {rating} stars! This helps VMD AI learn.")
        # Save rating to a backend if available

    # --- Feature: Simple ATS Score Estimator (Mock/AI-based) ---
    st.markdown("---")
    st.subheader("VMD AI: ATS Score Estimator (Beta)")
    st.info("This is a simulated ATS score based on common keywords. For best results, use the 'Generate Keywords' tool first.")
    
    col_ats1, col_ats2 = st.columns(2)
    with col_ats1:
        user_skills_for_ats = st.text_area("Your Skills for ATS (comma-separated):", value=st.session_state.get('skills_input', ''), height=80, key="ats_user_skills")
    with col_ats2:
        job_keywords_for_ats = st.text_area("Job Keywords (from JD):", height=80, key="ats_job_keywords")

    if st.button("Estimate ATS Score", key="estimate_ats_score_btn"):
        if user_skills_for_ats.strip() and job_keywords_for_ats.strip():
            user_skill_list = [s.strip().lower() for s in user_skills_for_ats.split(',') if s.strip()]
            job_keyword_list = [k.strip().lower() for k in job_keywords_for_ats.split(',') if k.strip()]

            matched_keywords = set(user_skill_list).intersection(set(job_keyword_list))
            total_job_keywords = len(job_keyword_list)
            
            if total_job_keywords > 0:
                score_percentage = (len(matched_keywords) / total_job_keywords) * 100
                st.success(f"Estimated ATS Match Score: {score_percentage:.2f}%")
                st.write(f"Matched Keywords: {', '.join(list(matched_keywords)) if matched_keywords else 'None'}")
                if score_percentage < 50:
                    st.warning("Consider adding more relevant keywords from the job description to improve your score.")
                elif score_percentage < 75:
                    st.info("Good match! Aim for higher by integrating more specific terms.")
                else:
                    st.balloons()
                    st.success("Excellent match! Your document is highly optimized for this job.")
            else:
                st.warning("Please provide job keywords to estimate ATS score.")
        else:
            st.warning("Please provide both your skills and job keywords for ATS estimation.")

    # --- Feature: Advanced Prompt Engineering Tips ---
    st.markdown("---")
    st.subheader("⚙️ Advanced Prompt Engineering Tips for VMD AI")
    st.markdown("""
    To get even better results from VMD AI, consider these advanced prompting techniques:
    * **Be Explicit:** Clearly state the desired output format (e.g., "Use bullet points:", "Start with 'Dear [Name]:'").
    * **Define Persona:** Ask VMD AI to act as an expert (e.g., "As a senior recruiter...", "As a marketing expert...").
    * **Set Constraints:** Specify length, tone, or specific phrases to include/exclude.
    * **Provide Examples:** If you have a specific style in mind, give a small example in your input.
    * **Iterate:** If the first output isn't perfect, refine your prompt and try again.
    """)
    st.markdown("""
    <details>
    <summary>Example Advanced Prompt for Resume Summary:</summary>
    <pre>
    "Generate a 3-sentence resume summary for a Full Stack Developer.
    The tone should be confident and highlight problem-solving skills.
    Start with 'Highly skilled'.
    Name: John Doe, Job: Full Stack Developer, Skills: React, Node.js, AWS, Experience: 7 years building scalable web apps."
    </pre>
    </details>
    """, unsafe_allow_html=True)


    # --- New Feature: Additional AI Tools (Expanded) ---
    st.markdown("---")
    st.subheader("🚀 Enhance Your Application with VMD AI Tools")
    st.markdown("Leverage VMD AI for more advanced career preparation tasks.")

    st.selectbox( # Corrected: Removed assignment to session_state here
        "Select an additional VMD AI tool:",
        ["None",
         "Resume: Generate Keywords from Job Description",
         "Resume: Critique Section",
         "Resume: Convert Experience to Bullet Points",
         "Resume: Achievement Statement Builder",
         "Resume: Power Verb Suggester", # New Tool
         "Resume: Section Expander",    # New Tool
         "Resume: Section Summarizer",  # New Tool
         "Cover Letter: Opening/Closing Suggester", # New Tool
         "Interview: Generate Interview Questions",
         "Interview: Behavioral Question Prompter (STAR)", # New Tool
         "Interview: Interview Answer Evaluator", # New Tool
         "Interview: Post-Interview Thank You Note", # New Tool
         "Networking: LinkedIn Profile Summary Suggestions",
         "Networking: Message Composer", # New Tool
         "Career: Skill Gap Analyzer", # New Tool
         "Career: Career Path Explorer", # New Tool
         "Career: Learning Resource Recommender", # New Tool
         "Career: Salary Negotiation Script Generator", # New Tool
         "Job Search: Job Description Analyzer (Upload)",
         "Job Search: Resume/CL Checklist" # New Tool
         ],
        key="ai_tool_select",
        index=["None",
               "Resume: Generate Keywords from Job Description",
               "Resume: Critique Section",
               "Resume: Convert Experience to Bullet Points",
               "Resume: Achievement Statement Builder",
               "Resume: Power Verb Suggester",
               "Resume: Section Expander",
               "Resume: Section Summarizer",
               "Cover Letter: Opening/Closing Suggester",
               "Interview: Generate Interview Questions",
               "Interview: Behavioral Question Prompter (STAR)",
               "Interview: Interview Answer Evaluator",
               "Interview: Post-Interview Thank You Note",
               "Networking: LinkedIn Profile Summary Suggestions",
               "Networking: Message Composer",
               "Career: Skill Gap Analyzer",
               "Career: Career Path Explorer",
               "Career: Learning Resource Recommender",
               "Career: Salary Negotiation Script Generator",
               "Job Search: Job Description Analyzer (Upload)",
               "Job Search: Resume/CL Checklist"
               ].index(st.session_state.ai_tool_select)
    )

    # --- Tool Implementations ---

    if st.session_state.ai_tool_select == "Resume: Generate Keywords from Job Description":
        st.markdown("### VMD AI: Keyword Extractor")
        job_desc_text = st.text_area(
            "Paste Job Description here:",
            height=150,
            key="job_desc_keywords_input",
            value=st.session_state.job_desc_keywords_input,
            help="VMD AI will extract key terms for ATS optimization."
        )
        keyword_context = st.text_input(
            "Context for keywords (e.g., 'software engineering role'):",
            key="keyword_context_input",
            value=st.session_state.get('job_title_input', ''), # Pre-fill with user's job title
            help="Helps VMD AI understand what kind of keywords to look for."
        )
        if st.button("Extract Keywords", key="extract_keywords_btn"):
            if job_desc_text.strip() and keyword_context.strip():
                with st.spinner("VMD AI is extracting keywords..."):
                    keywords_result = generate_keywords(job_desc_text, keyword_context)
                    st.text_area("Extracted Keywords:", value=keywords_result, height=100, key="extracted_keywords_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please provide both job description and context to extract keywords.")

    elif st.session_state.ai_tool_select == "Resume: Critique Section":
        st.markdown("### VMD AI: Resume Section Critique")
        critique_section_text = st.text_area(
            "Paste the resume section to critique:",
            height=200,
            key="critique_section_text_input",
            value=st.session_state.critique_section_text_input,
            help="e.g., your resume summary, skills, or experience section."
        )
        critique_section_type = st.selectbox(
            "Type of Section:",
            ["Resume Summary", "Skills", "Experience", "Education", "Projects", "Achievements"],
            key="critique_section_type_select",
            index=["Resume Summary", "Skills", "Experience", "Education", "Projects", "Achievements"].index(st.session_state.critique_section_type_select)
        )
        critique_job_title = st.text_input(
            "Target Job Title (for context):",
            value=st.session_state.get('job_title_input', ''),
            key="critique_job_title_input",
            help="Helps VMD AI provide relevant critique."
        )
        if st.button("Get Critique", key="get_critique_btn"):
            if critique_section_text.strip() and critique_job_title.strip():
                with st.spinner("VMD AI is analyzing your section..."):
                    critique_result = critique_resume_section(
                        critique_section_text,
                        critique_section_type,
                        critique_job_title
                    )
                    st.text_area("Critique from VMD AI:", value=critique_result, height=250, key="critique_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please provide the section text and target job title for critique.")

    elif st.session_state.ai_tool_select == "Resume: Convert Experience to Bullet Points":
        st.markdown("### VMD AI: Experience to Bullet Points Converter")
        bullet_exp_desc = st.text_area(
            "Paste your detailed experience description:",
            height=200,
            key="bullet_exp_desc_input",
            value=st.session_state.bullet_exp_desc_input,
            help="Provide a paragraph describing your work experience, and VMD AI will convert it to bullet points."
        )
        bullet_job_title = st.text_input(
            "Target Job Title (for tailoring bullet points):",
            value=st.session_state.get('job_title_input', ''),
            key="bullet_job_title_input",
            help="Helps VMD AI create relevant and impactful bullet points."
        )
        num_bullets = st.slider("Number of bullet points to generate:", 3, 7, 5, key="num_bullets_slider")
        if st.button("Convert to Bullet Points", key="convert_bullet_btn"):
            if bullet_exp_desc.strip() and bullet_job_title.strip():
                with st.spinner("VMD AI is converting to bullet points..."):
                    bullet_points_result = generate_bullet_points_from_experience(
                        bullet_exp_desc,
                        bullet_job_title,
                        num_bullets
                    )
                    st.text_area("Converted Bullet Points:", value=bullet_points_result, height=200, key="converted_bullet_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please provide the experience description and target job title.")

    elif st.session_state.ai_tool_select == "Resume: Achievement Statement Builder":
        st.markdown("### VMD AI: Achievement Statement Builder")
        raw_responsibility = st.text_area(
            "Describe a responsibility or task you performed:",
            height=100, key="raw_responsibility_input",
            help="e.g., 'Managed social media accounts' or 'Developed features for a web application.'"
        )
        impact_details = st.text_area(
            "What was the impact, result, or metric?",
            height=100, key="impact_details_input",
            help="e.g., 'Increased engagement by 20%', 'Reduced load time by 15%', 'Improved user satisfaction'."
        )
        if st.button("Build Achievement Statement", key="build_achievement_btn"):
            if raw_responsibility.strip() and impact_details.strip():
                with st.spinner("VMD AI is crafting your achievement statement..."):
                    achievement_result = generate_achievement_statement(raw_responsibility, impact_details) # Use new dedicated function
                    st.text_area("Achievement Statement:", value=achievement_result, height=100, key="achievement_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please describe both the responsibility and its impact.")

    # New Tool: Power Verb Suggester
    elif st.session_state.ai_tool_select == "Resume: Power Verb Suggester":
        st.markdown("### VMD AI: Power Verb Suggester")
        power_verb_job_title = st.text_input(
            "Target Job Title (for relevant verbs):",
            value=st.session_state.get('job_title_input', ''),
            key="power_verb_job_title_input",
            help="Get action verbs tailored to your profession."
        )
        if st.button("Suggest Power Verbs", key="suggest_verbs_btn"):
            if power_verb_job_title.strip():
                with st.spinner("VMD AI is finding powerful verbs..."):
                    verbs_result = generate_power_verbs(power_verb_job_title)
                    st.text_area("Suggested Power Verbs:", value=verbs_result, height=150, key="power_verbs_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please provide a job title to suggest power verbs.")
    
    # New Tool: Resume Section Expander
    elif st.session_state.ai_tool_select == "Resume: Section Expander":
        st.markdown("### VMD AI: Resume Section Expander")
        brief_section_text = st.text_area(
            "Paste a brief resume section or bullet point:",
            height=100, key="brief_section_expander_input",
            help="e.g., 'Managed team projects' or 'Developed a new algorithm'."
        )
        expanded_section_type = st.selectbox(
            "Type of Section to Expand:",
            ["Experience Bullet Point", "Project Description", "Summary Statement"],
            key="expanded_section_type_select"
        )
        expanded_job_title = st.text_input(
            "Job Title (for context):",
            value=st.session_state.get('job_title_input', ''),
            key="expanded_job_title_input",
            help="Helps VMD AI generate relevant details."
        )
        if st.button("Expand Section", key="expand_section_btn"):
            if brief_section_text.strip() and expanded_job_title.strip():
                with st.spinner("VMD AI is expanding your section..."):
                    expanded_result = expand_resume_section(brief_section_text, expanded_section_type, expanded_job_title)
                    st.text_area("Expanded Section:", value=expanded_result, height=250, key="expanded_section_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please provide brief text and job title to expand the section.")

    # New Tool: Resume Section Summarizer
    elif st.session_state.ai_tool_select == "Resume: Section Summarizer":
        st.markdown("### VMD AI: Resume Section Summarizer")
        detailed_section_text = st.text_area(
            "Paste a detailed resume section to summarize:",
            height=250, key="detailed_section_summarizer_input",
            help="e.g., a long experience paragraph or project description."
        )
        summarized_section_type = st.selectbox(
            "Type of Section to Summarize:",
            ["Experience", "Project", "Summary", "Education"],
            key="summarized_section_type_select"
        )
        target_sentences = st.slider("Target length (sentences):", 1, 5, 3, key="target_sentences_slider")
        if st.button("Summarize Section", key="summarize_section_btn"):
            if detailed_section_text.strip():
                with st.spinner("VMD AI is summarizing your section..."):
                    summarized_result = summarize_resume_section(detailed_section_text, summarized_section_type, target_sentences)
                    st.text_area("Summarized Section:", value=summarized_result, height=150, key="summarized_section_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please paste the detailed section to summarize.")

    # New Tool: Cover Letter Opening/Closing Suggester
    elif st.session_state.ai_tool_select == "Cover Letter: Opening/Closing Suggester":
        st.markdown("### VMD AI: Cover Letter Opening/Closing Suggester")
        cl_purpose = st.text_area(
            "What is the main purpose/context of your cover letter?",
            height=100, key="cl_purpose_input",
            help="e.g., 'Applying for a marketing specialist role at ABC Corp', 'Expressing interest in a data science internship'."
        )
        cl_tone = st.selectbox(
            "Desired Tone for Opening/Closing:",
            TONES, key="cl_tone_select_tool",
            index=TONES.index(st.session_state.tone_select)
        )
        if st.button("Suggest Openings/Closings", key="suggest_cl_parts_btn"):
            if cl_purpose.strip():
                with st.spinner("VMD AI is suggesting openings and closings..."):
                    # This uses generate_keywords as a general text generation tool
                    cl_parts_prompt = f"""
                    As an expert cover letter writer using VMD AI, generate a professional opening paragraph (2-3 sentences)
                    and a closing paragraph (2-3 sentences) for a cover letter with the following purpose and tone.

                    Purpose: {cl_purpose}
                    Tone: {cl_tone}

                    ---
                    Opening Suggestion:
                    ---
                    Closing Suggestion:
                    """
                    cl_parts_result = generate_keywords(cl_parts_prompt, "cover letter parts")
                    st.text_area("Suggested Opening and Closing:", value=cl_parts_result, height=250, key="cl_parts_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please describe the purpose of your cover letter.")

    elif st.session_state.ai_tool_select == "Interview: Generate Interview Questions":
        st.markdown("### VMD AI: Interview Question Generator")
        iq_resume_sum = st.text_area(
            "Paste your Resume Summary:",
            value=st.session_state.get("generated_output", ""), # Pre-fill with generated resume if available
            height=150,
            key="iq_resume_sum_input",
            help="Provide your resume summary (or a detailed overview)."
        )
        iq_job_keywords = st.text_area(
            "Paste Job Description Keywords (comma-separated):",
            key="iq_job_keywords_input",
            value=st.session_state.iq_job_keywords_input,
            height=100,
            help="List key skills/requirements from the job description for tailored questions."
        )
        iq_question_type = st.selectbox("Type of Questions:", ["Behavioral", "Technical", "Situational", "General"], key="iq_type_select")
        if st.button("Generate Interview Questions", key="generate_iq_btn"):
            if iq_resume_sum.strip() and iq_job_keywords.strip():
                with st.spinner("VMD AI is generating questions..."):
                    questions_result = generate_interview_questions(iq_resume_sum, iq_job_keywords, iq_question_type)
                    st.text_area("Potential Interview Questions:", value=questions_result, height=200, key="generated_iq_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please provide both resume summary and job keywords for interview questions.")
    
    # New Tool: Behavioral Question Prompter (STAR)
    elif st.session_state.ai_tool_select == "Interview: Behavioral Question Prompter (STAR)":
        st.markdown("### VMD AI: Behavioral Question Prompter (STAR Method)")
        behavioral_skill = st.text_input(
            "What behavioral skill do you want to practice?",
            key="behavioral_skill_input",
            help="e.g., 'Leadership', 'Problem-solving', 'Teamwork', 'Dealing with conflict'."
        )
        behavioral_context = st.text_area(
            "Briefly describe a situation related to this skill:",
            height=100, key="behavioral_context_input",
            help="e.g., 'Led a challenging project', 'Faced a difficult customer issue'."
        )
        if st.button("Get STAR Prompt", key="get_star_prompt_btn"):
            if behavioral_skill.strip():
                with st.spinner("VMD AI is generating a STAR method prompt..."):
                    star_prompt_text = f"""
                    As an interview coach using VMD AI, create a behavioral interview question focused on '{behavioral_skill}'.
                    Then, provide a brief outline using the STAR method (Situation, Task, Action, Result) for how a candidate might answer it,
                    incorporating the context: "{behavioral_context}".

                    Behavioral Question:
                    STAR Method Outline:
                    """
                    star_result = generate_keywords(star_prompt_text, "STAR method interview prep")
                    st.text_area("STAR Method Prompt & Outline:", value=star_result, height=250, key="star_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please specify a behavioral skill.")

    # New Tool: Interview Answer Evaluator
    elif st.session_state.ai_tool_select == "Interview: Interview Answer Evaluator":
        st.markdown("### VMD AI: Interview Answer Evaluator")
        eval_question = st.text_area(
            "Interview Question:",
            height=80, key="eval_question_input",
            help="The question you want to practice answering."
        )
        user_mock_answer = st.text_area(
            "Your Mock Answer:",
            height=200, key="user_mock_answer_input",
            help="Paste your answer here. Try to use the STAR method if applicable."
        )
        eval_job_title = st.text_input(
            "Job Title Context (for evaluation):",
            value=st.session_state.get('job_title_input', ''),
            key="eval_job_title_input",
            help="Helps VMD AI evaluate relevance."
        )
        if st.button("Evaluate Answer", key="evaluate_answer_btn"):
            if eval_question.strip() and user_mock_answer.strip() and eval_job_title.strip():
                with st.spinner("VMD AI is evaluating your answer..."):
                    critique_answer_result = generate_interview_answer_critique(eval_question, user_mock_answer, eval_job_title)
                    st.text_area("Evaluation & Suggestions:", value=critique_answer_result, height=300, key="answer_evaluation_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please provide the question, your answer, and job title context.")
    
    # New Tool: Post-Interview Thank You Note
    elif st.session_state.ai_tool_select == "Interview: Post-Interview Thank You Note":
        st.markdown("### VMD AI: Thank You Note Generator")
        ty_name = st.text_input("Interviewer's Name:", key="ty_name_input")
        ty_company = st.text_input("Company Name:", value=st.session_state.get('company_input', ''), key="ty_company_input")
        ty_job_title = st.text_input("Job Title Applied For:", value=st.session_state.get('job_title_input', ''), key="ty_job_title_input")
        ty_interview_date = st.date_input("Interview Date:", key="ty_interview_date_input", value=datetime.date.today())
        ty_discussion_points = st.text_area(
            "Key discussion points/topics (comma-separated):",
            height=100, key="ty_discussion_points_input",
            help="e.g., 'Project X discussion', 'My experience with Python', 'Company culture'."
        )
        if st.button("Generate Thank You Note", key="generate_ty_note_btn"):
            if ty_name.strip() and ty_company.strip() and ty_job_title.strip() and ty_discussion_points.strip():
                with st.spinner("VMD AI is drafting your thank you note..."):
                    ty_note_result = generate_thank_you_note(
                        ty_name, ty_company, ty_job_title, str(ty_interview_date), ty_discussion_points
                    )
                    st.text_area("Suggested Thank You Note (Email Body):", value=ty_note_result, height=300, key="ty_note_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please fill in all required fields for the thank you note.")

    elif st.session_state.ai_tool_select == "Networking: LinkedIn Profile Summary Suggestions":
        st.markdown("### VMD AI: LinkedIn Profile Summary Suggestions")
        linkedin_keywords = st.text_area(
            "Key skills/roles for LinkedIn summary (comma-separated):",
            value=st.session_state.get('skills_input', ''), height=100, key="linkedin_keywords_input",
            help="e.g., 'Software Engineer, Cloud Architect, Leadership, Agile'."
        )
        linkedin_experience_summary = st.text_area(
            "Brief career overview for LinkedIn:",
            value=st.session_state.get('experience_input', ''), height=150, key="linkedin_experience_input",
            help="A summary of your professional journey and aspirations."
        )
        if st.button("Generate LinkedIn Summary", key="generate_linkedin_btn"):
            if linkedin_keywords.strip() and linkedin_experience_summary.strip():
                with st.spinner("VMD AI is generating LinkedIn summary..."):
                    linkedin_summary_result = generate_linkedin_summary(linkedin_keywords, linkedin_experience_summary) # Use new dedicated function
                    st.text_area("Suggested LinkedIn Summary:", value=linkedin_summary_result, height=200, key="linkedin_summary_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please provide both keywords and a career overview for LinkedIn summary.")

    # New Tool: Networking Message Composer
    elif st.session_state.ai_tool_select == "Networking: Message Composer":
        st.markdown("### VMD AI: Networking Message Composer")
        my_role = st.text_input("Your current/target role:", value=st.session_state.get('job_title_input', ''), key="my_role_input")
        target_role = st.text_input("Role of the person you want to connect with:", key="target_role_input")
        message_purpose = st.text_area(
            "What is the purpose of your message?",
            height=100, key="message_purpose_input",
            help="e.g., 'Informational interview', 'Job referral', 'Industry insights', 'Collaborate on a project'."
        )
        common_ground = st.text_area(
            "Any common ground or specific connection?",
            height=70, key="common_ground_input",
            help="e.g., 'We both attended XYZ university', 'I saw your recent post on ABC topic'."
        )
        if st.button("Compose Message", key="compose_message_btn"):
            if my_role.strip() and target_role.strip() and message_purpose.strip():
                with st.spinner("VMD AI is composing your message..."):
                    networking_message_result = generate_networking_message(my_role, target_role, message_purpose, common_ground)
                    st.text_area("Suggested Networking Message:", value=networking_message_result, height=250, key="networking_message_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please provide your role, target role, and message purpose.")

    # New Tool: Skill Gap Analyzer
    elif st.session_state.ai_tool_select == "Career: Skill Gap Analyzer":
        st.markdown("### VMD AI: Skill Gap Analyzer")
        jd_skills_input = st.text_area(
            "Paste required skills from Job Description (comma-separated):",
            height=100, key="jd_skills_gap_input",
            help="List skills exactly as they appear in the job posting."
        )
        my_current_skills_input = st.text_area(
            "Your current skills (comma-separated):",
            value=st.session_state.get('skills_input', ''), height=100, key="my_skills_gap_input",
            help="Your complete list of skills."
        )
        if st.button("Analyze Skill Gap", key="analyze_skill_gap_btn"):
            if jd_skills_input.strip() and my_current_skills_input.strip():
                with st.spinner("VMD AI is analyzing skill gaps..."):
                    skill_gap_result = analyze_job_description(jd_skills_input, "Skill Gap Analysis", user_skills=my_current_skills_input)
                    st.text_area("Skill Gap Analysis & Suggestions:", value=skill_gap_result, height=250, key="skill_gap_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please provide both job description skills and your current skills.")

    # New Tool: Career Path Explorer
    elif st.session_state.ai_tool_select == "Career: Career Path Explorer":
        st.markdown("### VMD AI: Career Path Explorer")
        current_role_cp = st.text_input(
            "Your current role (optional):",
            value=st.session_state.get('job_title_input', ''), key="current_role_cp_input",
            help="Your current job title to help VMD AI suggest relevant paths."
        )
        skills_cp = st.text_area(
            "Your key skills (comma-separated):",
            value=st.session_state.get('skills_input', ''), height=100, key="skills_cp_input",
            help="List your most proficient skills."
        )
        experience_cp = st.text_area(
            "Summary of your experience:",
            value=st.session_state.get('experience_input', ''), height=150, key="experience_cp_input",
            help="Briefly describe your professional experience."
        )
        if st.button("Explore Career Paths", key="explore_career_paths_btn"):
            if skills_cp.strip() and experience_cp.strip():
                with st.spinner("VMD AI is exploring career paths..."):
                    career_paths_result = generate_career_path_suggestions(skills_cp, experience_cp, current_role_cp)
                    st.text_area("Suggested Career Paths:", value=career_paths_result, height=250, key="career_paths_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please provide your skills and experience to explore career paths.")

    # New Tool: Learning Resource Recommender
    elif st.session_state.ai_tool_select == "Career: Learning Resource Recommender":
        st.markdown("### VMD AI: Learning Resource Recommender")
        skill_to_learn = st.text_input(
            "Skill you want to learn/improve:",
            key="skill_to_learn_input",
            help="e.g., 'TensorFlow', 'Strategic Planning', 'Public Speaking'."
        )
        current_role_lr = st.text_input(
            "Your current/target role (for relevance):",
            value=st.session_state.get('job_title_input', ''), key="current_role_lr_input",
            help="Helps VMD AI recommend highly relevant resources."
        )
        if st.button("Recommend Resources", key="recommend_resources_btn"):
            if skill_to_learn.strip() and current_role_lr.strip():
                with st.spinner("VMD AI is recommending learning resources..."):
                    learning_resources_result = generate_learning_resources(skill_to_learn, current_role_lr)
                    st.text_area("Recommended Learning Resources:", value=learning_resources_result, height=250, key="learning_resources_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please provide the skill and your current/target role.")

    # New Tool: Salary Negotiation Script Generator
    elif st.session_state.ai_tool_select == "Career: Salary Negotiation Script Generator":
        st.markdown("### VMD AI: Salary Negotiation Script Generator")
        negotiation_job_title = st.text_input(
            "Job Title of Offer:",
            value=st.session_state.get('job_title_input', ''), key="negotiation_job_title_input"
        )
        negotiation_company = st.text_input(
            "Company Making Offer:",
            value=st.session_state.get('company_input', ''), key="negotiation_company_input"
        )
        initial_offer = st.text_input(
            "Initial Salary Offer (e.g., $80,000):",
            key="initial_offer_input"
        )
        desired_range = st.text_input(
            "Your Desired Salary Range (e.g., $90,000 - $100,000):",
            key="desired_range_input"
        )
        key_achievements_neg = st.text_area(
            "Your key achievements/value propositions (comma-separated):",
            value=st.session_state.get('achievements_input', ''), height=100, key="key_achievements_neg_input",
            help="Reminders of your value that AI can incorporate."
        )
        if st.button("Generate Negotiation Script", key="generate_negotiation_script_btn"):
            if negotiation_job_title.strip() and negotiation_company.strip() and initial_offer.strip() and desired_range.strip() and key_achievements_neg.strip():
                with st.spinner("VMD AI is generating negotiation script..."):
                    negotiation_script_result = generate_salary_negotiation_script(
                        negotiation_job_title, negotiation_company, initial_offer, desired_range, key_achievements_neg
                    )
                    st.text_area("Suggested Negotiation Script:", value=negotiation_script_result, height=350, key="negotiation_script_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please fill in all negotiation script details.")

    # Job Description Analyzer (Upload)
    elif st.session_state.ai_tool_select == "Job Search: Job Description Analyzer (Upload)":
        st.markdown("### VMD AI: Job Description Analyzer")
        uploaded_jd_file = st.file_uploader(
            "Upload a Job Description (TXT file)",
            type=["txt"], key="jd_uploader",
            help="Upload a plain text file containing the job description for analysis."
        )
        analysis_type_jd = st.selectbox(
            "Select Analysis Type:",
            ["Key Skills and Requirements", "Potential Interview Questions", "ATS Alignment Advice", "Skill Gap Analysis"],
            key="jd_analysis_type_select_tool" # Unique key for this widget in the tool section
        )
        
        jd_content = ""
        if uploaded_jd_file is not None:
            jd_content = uploaded_jd_file.read().decode("utf-8")
            st.text_area("Uploaded Job Description Content:", value=jd_content, height=200, disabled=True)

        if st.button("Analyze Job Description", key="analyze_jd_btn"):
            if jd_content.strip():
                with st.spinner(f"VMD AI is performing {analysis_type_jd} on the job description..."):
                    analysis_result = analyze_job_description(
                        jd_content,
                        analysis_type_jd, # Use analysis_type_jd
                        st.session_state.job_title_input,
                        st.session_state.experience_input,
                        st.session_state.skills_input # Pass user skills for Skill Gap Analysis
                    )
                    st.text_area(f"Analysis Result ({analysis_type_jd}):", value=analysis_result, height=300, key="jd_analysis_output")
                    st.session_state.ai_usage_count += 1
            else:
                st.warning("Please upload a job description file to perform analysis.")

    # New Tool: Resume/CL Checklist
    elif st.session_state.ai_tool_select == "Job Search: Resume/CL Checklist":
        st.markdown("### VMD AI: Document Checklist")
        st.info("Use this checklist to ensure your resume and cover letter are polished and ready!")
        st.markdown("""
        #### Resume Checklist:
        - [x] Is my contact information accurate and clearly visible?
        - [x] Is my resume summary/objective concise and tailored to the job?
        - [x] Have I used action verbs at the beginning of each bullet point?
        - [x] Have I quantified my achievements with numbers/metrics where possible?
        - [x] Is my experience listed in reverse chronological order?
        - [x] Are there any typos or grammatical errors? (Crucial!)
        - [x] Is the formatting clean, consistent, and easy to read?
        - [x] Have I included relevant keywords from the job description?
        - [x] Is my resume concise (typically 1 page for every 10 years of experience, max 2 pages)?
        - [x] Is my education section accurate and complete?
        - [x] Have I included relevant projects or certifications?

        #### Cover Letter Checklist:
        - [x] Is the letter addressed to a specific hiring manager (if known)?
        - [x] Does the opening paragraph grab attention and state the purpose?
        - [x] Have I clearly stated why I'm interested in *this specific company and role*?
        - [x] Have I highlighted relevant skills and experiences from my background?
        - [x] Does it explicitly connect my qualifications to the job description's requirements?
        - [x] Is the tone professional and enthusiastic?
        - [x] Have I proofread for typos and grammatical errors?
        - [x] Is it concise (typically 3-4 paragraphs)?
        - [x] Does it have a strong call to action in the closing?
        - [x] Is my contact information included in the closing?
        """)
        st.success("Remember: A perfect document significantly boosts your chances!")


# --- 10. Additional Information Sections ---
st.markdown("---")
st.subheader("💡 Tips for Best Results with VMD AI")
st.markdown("""
* **Be Specific:** Provide as much detail as possible in your inputs (e.g., specific skills, quantifiable achievements in experience).
* **Review and Refine:** AI-generated content is a great starting point, but always review and customize it to perfectly match your unique profile and the job requirements.
* **Use Keywords:** Integrate keywords from the job description into your inputs, especially skills and experience, to improve ATS compatibility.
* **Experiment with Tone:** Try different tones (e.g., 'Professional' vs. 'Concise') to see which best fits your style and the job.
* **Proofread Carefully:** Always proofread the generated content for any grammatical errors or awkward phrasing.
* **Quantify Achievements:** Where possible, provide numbers or metrics in your experience summary (e.g., "Increased sales by 15%", "Managed a budget of $X"). This makes your experience more impactful.
* **Tailor for Each Application:** While VMD AI helps automate, taking a few extra minutes to fine-tune each document for a specific job description significantly boosts your chances.
""")
st.markdown("---")
st.header("FAQs (Frequently Asked Questions)", anchor="faq-section")
st.markdown("""
<details>
<summary>What is VMD AI?</summary>
VMD AI is an advanced AI-powered platform designed to assist job seekers in generating professional and ATS-optimized resumes and cover letters. It leverages large language models to understand your inputs and craft compelling career documents.
</details>
<br>
<details>
<summary>Is VMD AI free to use?</summary>
Yes, the core generation features of VMD AI are available for free. We utilize a free tier of AI models to provide this service. While the service itself is free, standard internet usage charges from your provider may apply.
</details>
<br>
<details>
<summary>How can I download my generated document as a PDF?</summary>
Currently, direct PDF download is not supported within this browser-based application. You can easily copy the generated text using the 'Copy to Clipboard' button and paste it into any document editor (like Microsoft Word, Google Docs, or LibreOffice Writer), then save or export it as a PDF. This method ensures maximum control over the final formatting of your document.
</details>
<br>
<details>
<summary>How accurate is the AI-generated content?</summary>
VMD AI strives for high accuracy and relevance based on your inputs. However, AI models can sometimes generate unexpected results or require further refinement. We recommend always reviewing the content thoroughly and making any necessary adjustments to ensure it perfectly reflects your qualifications and meets your expectations. Your feedback on output quality helps us improve!
</details>
<br>
<details>
<summary>What is ATS optimization?</summary>
ATS stands for Applicant Tracking System. Many companies use these systems to scan and filter resumes based on keywords and formatting. VMD AI is designed to help you include relevant keywords and structure your content in a way that is easily parsable by ATS, increasing your chances of getting noticed by recruiters.
</details>
<br>
<details>
<summary>Can I save my inputs or generated documents?</summary>
This application uses Streamlit's session state to temporarily store your inputs and recently generated documents (up to 10). This data will persist as long as your browser session is active. For permanent storage, we recommend downloading your generated documents or copying the text.
</details>
""", unsafe_allow_html=True)


st.markdown("---")
st.header("Contact Us", anchor="contact-us")
st.markdown("""
If you have any questions, feedback, or require support regarding VMD AI, please reach out to us:
* **Email:** support@vmdaiai.com
* **Website:** [www.vmdaiai.com](https://www.example.com) (Placeholder for VMD AI official website)
* **Follow us on:** [LinkedIn](https://www.linkedin.com/) | [Twitter](https://twitter.com/)
""")

# Feature: Mock Subscription/Pricing Section
st.markdown("---")
st.subheader("🌟 Upgrade Your VMD AI Experience (Coming Soon!)")
st.markdown("""
While the core features of VMD AI are free, we are working on premium features to further enhance your job search:
* **Unlimited Generations:** Remove daily limits on document generation.
* **Advanced AI Models:** Access to more powerful and nuanced AI models for superior content.
* **Personalized Coaching:** AI-driven personalized tips and coaching for interviews.
* **Priority Support:** Faster response times for all your queries.
* **Integrated PDF Export:** Generate and download professional PDF documents directly.
* **Resume/Cover Letter Templates:** Choose from a library of modern, customizable templates.
* **Cloud Storage Integration:** Save and access your documents securely from anywhere.
* **Advanced ATS Score Analysis:** More in-depth analysis and specific recommendations.
* **Interview Coaching Sessions:** Interactive mock interview sessions with AI feedback.
* **Career Path Visualization:** Visual tools to explore and plan your career trajectory.
""")
st.markdown("Stay tuned for VMD AI Pro!")

st.markdown("---")
# Feature: Testimonials/Success Stories (Mock)
st.subheader("Hear From Our Users!")
col_test1, col_test2, col_test3 = st.columns(3)
with col_test1:
    st.markdown("""
    "VMD AI helped me land my dream job! The cover letter it generated was spot on."
    - **Sarah K., Marketing Manager**
    """)
with col_test2:
    st.markdown("""
    "The ATS keyword analysis is a game-changer. My resume suddenly started getting noticed."
    - **David P., Software Engineer**
    """)
with col_test3:
    st.markdown("""
    "I used the interview question generator to practice, and it really boosted my confidence."
    - **Emily R., Data Analyst**
    """)

st.markdown("---")
# Feature: Road-map/Future Features Section
st.subheader("VMD AI Development Roadmap")
st.markdown("""
We are continuously working to bring you more powerful features. Here's what's coming next:
* **Version 1.2 (Q3 2025):**
    * Enhanced PDF generation with multiple templates.
    * Improved AI context understanding for complex queries.
    * User dashboard for managing multiple profiles.
* **Version 1.5 (Q4 2025):**
    * Integration with job boards for direct application.
    * AI-powered job matching and recommendation engine.
    * Collaborative features for resume review with peers.
* **Beyond:**
    * Mobile application development.
    * Personalized career coaching modules.
    * Integration with professional networking platforms.
""")

st.markdown("---")
# Feature: Disclaimers
st.subheader("Important Disclaimers")
st.markdown("""
* **AI-Generated Content:** While VMD AI uses advanced models, the generated content is a suggestion. Always review, edit, and personalize it to ensure it accurately reflects your qualifications and the specific job you're applying for.
* **ATS Score Estimator:** The ATS score is a simplified estimate based on keyword matching. Actual ATS systems are complex and may use proprietary algorithms. This tool is for guidance only.
* **Data Privacy:** This application stores your input and generated documents only within your current browser session. No personal data is stored on our servers (mock backend). Clear your browser's session data to remove local information.
* **Professional Advice:** VMD AI is a tool to assist with document creation. It does not replace professional career counseling or legal advice.
""")


st.markdown("---")
st.markdown('<p id="about-section" style="text-align: center;">© 2025 VMD AI. All rights reserved. <br> Powered by an advanced language model.</p>', unsafe_allow_html=True)
