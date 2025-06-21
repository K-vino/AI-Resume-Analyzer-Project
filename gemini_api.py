import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Generative AI API with the API key from environment variables
# Note: Ensure GEMINI_API_KEY is set in your .env file or environment
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the GenerativeModel with 'gemini-2.0-flash' for free tier access
# This change addresses the 404 error encountered with 'gemini-pro'
model = genai.GenerativeModel("gemini-2.0-flash")

def _safe_generate_content(prompt: str) -> str:
    """
    Internal helper function to safely call the model and handle potential errors.
    Args:
        prompt (str): The prompt string to send to the model.
    Returns:
        str: The generated text content or an error message.
    """
    try:
        # Generate content from the model
        response = model.generate_content(prompt)
        # Check if response.text is empty or None, indicating potential content filtering or an issue
        if response.text:
            return response.text
        else:
            return "VMD AI could not generate content for this request. Please try refining your input."
    except Exception as e:
        # Return a user-friendly error message if generation fails
        print(f"Error during AI generation: {e}") # Log error for debugging
        return f"VMD AI encountered an error: {e}. Please try again or refine your input."

def generate_resume_summary(name: str, title: str, skills: str, experience: str,
                            tone: str = "Formal", language: str = "English", length: str = "Concise") -> str:
    """
    Generates a professional resume summary using the VMD AI model.

    Args:
        name (str): The candidate's full name.
        title (str): The target job title.
        skills (str): A comma-separated list of the candidate's skills.
        experience (str): A brief summary of the candidate's experience.
        tone (str): Desired tone for the summary (e.g., "Formal", "Creative", "Concise").
        language (str): Desired language for the output (e.g., "English", "Spanish", "French").
        length (str): Desired length for the summary (e.g., "Concise", "Standard", "Detailed").

    Returns:
        str: The AI-generated resume summary.
    """
    length_description = ""
    if length == "Concise":
        length_description = " (3-5 sentences)"
    elif length == "Standard":
        length_description = " (5-8 sentences)"
    elif length == "Detailed":
        length_description = " (8-12 sentences)"

    prompt = f"""
As an expert resume writer using VMD AI, generate a professional, {length} and ATS-optimized resume summary section.
The summary should be written in a {tone} tone and in {language}.
It should highlight the candidate's core competencies, achievements, and career goals relevant to the target job.

Candidate Name: {name}
Target Job Title: {title}
Key Skills: {skills}
Professional Experience Summary: {experience}

Ensure the summary is impactful, uses strong action verbs, and is tailored to common resume best practices.
Focus solely on the summary section{length_description}, avoid adding sections like "Education", "Work Experience", etc.
"""
    return _safe_generate_content(prompt)

def generate_cover_letter(name: str, title: str, company: str, skills: str, experience: str,
                          tone: str = "Formal", language: str = "English", length: str = "Standard") -> str:
    """
    Generates a professional cover letter using the VMD AI model.

    Args:
        name (str): The candidate's full name.
        title (str): The target job title.
        company (str): The target company for the application.
        skills (str): A comma-separated list of the candidate's skills.
        experience (str): A brief summary of the candidate's experience.
        tone (str): Desired tone for the cover letter (e.g., "Formal", "Friendly", "Persuasive").
        language (str): Desired language for the output (e.g., "English", "Spanish", "French").
        length (str): Desired length for the cover letter (e.g., "Standard", "Brief", "Detailed").

    Returns:
        str: The AI-generated cover letter.
    """
    length_description = ""
    if length == "Brief":
        length_description = " (2-3 paragraphs)"
    elif length == "Standard":
        length_description = " (3-4 paragraphs)"
    elif length == "Detailed":
        length_description = " (4-5 paragraphs)"

    prompt = f"""
As an expert professional writer using VMD AI, write a {tone} cover letter in {language}{length_description} for a job application.
The cover letter should clearly state the applicant's interest in the position and the company, highlight relevant skills and experience,
and explain how their qualifications align with the job requirements.

Candidate Name: {name}
Target Job Title: {title}
Target Company: {company}
Key Skills: {skills}
Professional Experience Summary: ${experience}

Start with a formal salutation (e.g., "Dear Hiring Manager,").
Conclude with a professional closing.
Ensure the tone is persuasive and enthusiastic, tailored to attract the attention of the hiring committee.
Focus only on the body of the cover letter, do not include placeholder for date or address.
"""
    return _safe_generate_content(prompt)

def generate_keywords(text: str, context: str) -> str:
    """
    Extracts relevant keywords from a given text (e.g., resume or job description).

    Args:
        text (str): The input text (e.g., resume content or job description).
        context (str): The context for keyword extraction (e.g., "resume for software engineer", "job description for marketing manager").

    Returns:
        str: A comma-separated list of extracted keywords.
    """
    prompt = f"""
As an ATS (Applicant Tracking System) expert using VMD AI, extract and list the most important keywords from the following text,
relevant to a {context}. Provide them as a comma-separated list.
Text:
---
{text}
---
Keywords:
"""
    return _safe_generate_content(prompt)

def generate_interview_questions(resume_summary: str, job_description_keywords: str, question_type: str = "Behavioral") -> str:
    """
    Generates potential interview questions based on a resume summary and job description keywords.

    Args:
        resume_summary (str): The candidate's resume summary.
        job_description_keywords (str): Key skills/requirements from the job description.
        question_type (str): Type of questions (e.g., "Behavioral", "Technical", "Situational").

    Returns:
        str: A list of 5-7 potential interview questions.
    """
    prompt = f"""
As an interview preparation expert using VMD AI, generate 5-7 potential {question_type} interview questions for a candidate with the following resume summary:
"{resume_summary}"
and applying for a role described by these keywords: "{job_description_keywords}".
Focus on questions that bridge the candidate's experience with the job requirements.
List them numerically.
"""
    return _safe_generate_content(prompt)

def critique_resume_section(section_text: str, section_type: str, job_title: str) -> str:
    """
    Provides a constructive critique of a specific resume section.

    Args:
        section_text (str): The content of the resume section to critique.
        section_type (str): The type of section (e.g., "Resume Summary", "Skills", "Experience").
        job_title (str): The target job title for context.

    Returns:
        str: A critique with suggestions for improvement.
    """
    prompt = f"""
As a professional resume reviewer using VMD AI, provide a constructive critique of the following "{section_type}" section for a "{job_title}" role.
Focus on clarity, impact, relevance, ATS-optimization, and overall effectiveness.
Suggest specific improvements.

Section Content:
---
{section_text}
---
Critique and Suggestions:
"""
    return _safe_generate_content(prompt)

def generate_bullet_points_from_experience(experience_description: str, job_title: str, num_bullets: int = 5) -> str:
    """
    Converts a free-form experience description into concise, action-oriented bullet points.

    Args:
        experience_description (str): A detailed description of work experience.
        job_title (str): The target job title to tailor bullet points.
        num_bullets (int): Desired number of bullet points.

    Returns:
        str: A list of action-oriented bullet points.
    """
    prompt = f"""
As an expert resume writer using VMD AI, transform the following experience description into {num_bullets} concise,
action-oriented bullet points suitable for a resume for a '{job_title}' role.
Each bullet point should start with a strong action verb and highlight quantifiable achievements where possible.

Experience Description:
---
{experience_description}
---
Bullet Points:
"""
    return _safe_generate_content(prompt)

def generate_achievement_statement(responsibility: str, impact_details: str) -> str:
    """
    Converts a responsibility and its impact into a concise, action-oriented achievement statement.

    Args:
        responsibility (str): A description of a task or responsibility.
        impact_details (str): Details about the impact, result, or metric of the responsibility.

    Returns:
        str: A 1-2 sentence achievement statement.
    """
    prompt = f"""
    As an expert resume writer using VMD AI, convert the following responsibility and its impact into a concise,
    action-oriented achievement statement (1-2 sentences). Start with a strong action verb and quantify results where possible.

    Responsibility: {responsibility}
    Impact/Result: {impact_details}

    Achievement Statement:
    """
    return _safe_generate_content(prompt)

def generate_linkedin_summary(keywords: str, career_overview: str) -> str:
    """
    Generates a compelling professional summary for a LinkedIn profile.

    Args:
        keywords (str): Key skills/roles for the LinkedIn summary (comma-separated).
        career_overview (str): A brief summary of the user's professional journey and aspirations.

    Returns:
        str: A 3-5 sentence LinkedIn professional summary.
    """
    prompt = f"""
    As a LinkedIn profile expert using VMD AI, generate a compelling 3-5 sentence professional summary for a LinkedIn profile.
    Incorporate the following keywords and career overview. Focus on impact, professional brand, and future aspirations.

    Keywords: {keywords}
    Career Overview: {career_overview}

    LinkedIn Summary:
    """
    return _safe_generate_content(prompt)

def analyze_job_description(jd_content: str, analysis_type: str, job_title_context: str = "", user_experience_summary: str = "", user_skills: str = "") -> str:
    """
    Analyzes a job description for different purposes (keywords, interview questions, ATS advice).

    Args:
        jd_content (str): The full content of the job description.
        analysis_type (str): The type of analysis requested ("Key Skills and Requirements", "Potential Interview Questions", "ATS Alignment Advice", "Skill Gap Analysis").
        job_title_context (str): The target job title for better context.
        user_experience_summary (str): The user's experience summary, relevant for interview questions.
        user_skills (str): The user's skills, relevant for skill gap analysis.

    Returns:
        str: The result of the analysis.
    """
    if analysis_type == "Key Skills and Requirements":
        prompt = f"""
        As an ATS expert using VMD AI, extract and list the most important keywords and required skills from the following job description.
        These should be directly relevant to a '{job_title_context}' role. Provide them as a comma-separated list.

        Job Description:
        ---
        {jd_content}
        ---
        Extracted Keywords and Skills:
        """
    elif analysis_type == "Potential Interview Questions":
        # Using user's experience for more personalized questions
        prompt = f"""
        As an interview preparation expert using VMD AI, generate 5-7 potential interview questions based on the following job description
        and considering a candidate with this experience summary: "{user_experience_summary}".
        Focus on behavioral, technical, and situational questions that test alignment with the job requirements.
        List them numerically.

        Job Description:
        ---
        {jd_content}
        ---
        Potential Interview Questions:
        """
    elif analysis_type == "ATS Alignment Advice":
        prompt = f"""
        As an ATS expert and career advisor using VMD AI, analyze the following job description and provide actionable advice on how to tailor a resume and cover letter for optimal ATS alignment.
        Focus on identifying critical keywords, recommended formatting, common pitfalls to avoid, and strategic content integration.

        Job Description:
        ---
        {jd_content}
        ---
        ATS Alignment Advice:
        """
    elif analysis_type == "Skill Gap Analysis":
        prompt = f"""
        As a career development expert using VMD AI, compare the required skills in the job description below with the candidate's existing skills.
        Identify any significant skill gaps and suggest 3-5 relevant learning resources or areas of focus to bridge those gaps.

        Job Description Skills/Requirements:
        ---
        {jd_content}
        ---
        Candidate's Skills:
        ---
        {user_skills}
        ---
        Skill Gap Analysis and Learning Suggestions:
        """
    else:
        return "Invalid analysis type specified for job description."

    return _safe_generate_content(prompt)

def generate_power_verbs(job_title: str) -> str:
    """Generates a list of powerful action verbs relevant to a given job title."""
    prompt = f"""
    As a resume expert using VMD AI, generate a list of 15-20 powerful action verbs (power verbs)
    that are highly relevant for a '{job_title}' role.
    List them as a comma-separated list or short bullet points.
    """
    return _safe_generate_content(prompt)

def expand_resume_section(brief_text: str, section_type: str, job_title: str) -> str:
    """Expands brief text into a more detailed resume section."""
    prompt = f"""
    As an expert resume writer using VMD AI, expand the following brief description into a more detailed and impactful
    '{section_type}' section for a '{job_title}' resume. Aim for 3-5 sentences/bullet points,
    incorporating strong action verbs and quantifying achievements where possible.

    Brief Description:
    ---
    {brief_text}
    ---
    Expanded Section:
    """
    return _safe_generate_content(prompt)

def summarize_resume_section(detailed_text: str, section_type: str, target_length_sentences: int = 3) -> str:
    """Summarizes a detailed resume section into a shorter, concise version."""
    prompt = f"""
    As an expert resume writer using VMD AI, summarize the following detailed '{section_type}' section into approximately {target_length_sentences}
    concise and impactful sentences/bullet points suitable for a resume.

    Detailed Section:
    ---
    {detailed_text}
    ---
    Summarized Section:
    """
    return _safe_generate_content(prompt)

def generate_thank_you_note(name: str, company: str, job_title: str, interview_date: str, key_discussion_points: str) -> str:
    """Generates a professional post-interview thank you note."""
    prompt = f"""
    As a professional career coach using VMD AI, draft a personalized thank-you email after an interview.
    It should be concise, reiterate interest, and reference specific discussion points.

    Candidate Name: {name}
    Company: {company}
    Job Title: {job_title}
    Interview Date: {interview_date}
    Key Discussion Points (comma-separated): {key_discussion_points}

    Thank You Note (Email Body Only):
    """
    return _safe_generate_content(prompt)

def generate_networking_message(my_role: str, target_person_role: str, purpose: str, common_ground: str = "") -> str:
    """Generates a professional networking message."""
    prompt = f"""
    As a networking expert using VMD AI, draft a concise and professional networking message.

    Your Role/Background: {my_role}
    Target Person's Role/Background: {target_person_role}
    Purpose of message: {purpose}
    Common Ground/Specific Connection (optional): {common_ground}

    Networking Message:
    """
    return _safe_generate_content(prompt)

def generate_career_path_suggestions(skills: str, experience: str, current_role: str = "") -> str:
    """Suggests potential career paths based on skills and experience."""
    prompt = f"""
    As a career counselor using VMD AI, suggest 3-5 potential career paths for someone with the following profile.
    Focus on paths that leverage their existing skills and experience.

    Current Role (optional): {current_role}
    Skills: {skills}
    Experience Summary: {experience}

    Suggested Career Paths:
    """
    return _safe_generate_content(prompt)

def generate_learning_resources(skill_gap: str, current_role: str) -> str:
    """Recommends learning resources for a specific skill gap."""
    prompt = f"""
    As a learning and development expert using VMD AI, recommend 3-5 types of learning resources (e.g., online courses, books, certifications, projects)
    to acquire or strengthen the following skill, relevant for a '{current_role}' role.

    Skill to learn/improve: {skill_gap}

    Recommended Learning Resources:
    """
    return _safe_generate_content(prompt)

def generate_salary_negotiation_script(job_title: str, company: str, initial_offer: str, desired_range: str, key_achievements: str) -> str:
    """Generates a script for salary negotiation."""
    prompt = f"""
    As a salary negotiation coach using VMD AI, create a concise script for a candidate to negotiate a job offer.
    The script should be professional, confident, and highlight the candidate's value.

    Job Title: {job_title}
    Company: {company}
    Initial Offer: {initial_offer}
    Desired Salary Range: {desired_range}
    Key Achievements (to highlight value): {key_achievements}

    Salary Negotiation Script:
    """
    return _safe_generate_content(prompt)

def generate_interview_answer_critique(question: str, user_answer: str, job_title_context: str) -> str:
    """Critiques a user's mock interview answer."""
    prompt = f"""
    As an expert interview coach using VMD AI, provide constructive feedback and suggest improvements for the following interview answer.
    Consider its relevance to a '{job_title_context}' role, clarity, completeness, and adherence to best practices (e.g., STAR method if applicable).

    Interview Question: "{question}"
    Candidate's Answer: "{user_answer}"

    Critique and Improvement Suggestions:
    """
    return _safe_generate_content(prompt)

