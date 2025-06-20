import streamlit as st
from gemini_api import generate_resume, generate_cover_letter
import pdfkit
import os

st.set_page_config(page_title="AI Resume & Cover Letter Generator", layout="centered")

st.title("📄 Smart Resume & Cover Letter Generator")

st.sidebar.markdown("💡 Powered by **Google Gemini API**")

option = st.radio("What would you like to generate?", ["Resume", "Cover Letter"])

st.subheader("Enter Your Details")

name = st.text_input("Your Name")
job_title = st.text_input("Job Title")
skills = st.text_area("List Your Skills (comma-separated)")
experience = st.text_area("Brief Summary of Your Experience")

if option == "Cover Letter":
    company = st.text_input("Target Company")

if st.button("Generate"):
    with st.spinner("Generating using Gemini AI..."):
        if option == "Resume":
            result = generate_resume(name, job_title, skills, experience)
        else:
            result = generate_cover_letter(name, job_title, company, skills, experience)
        
        st.success(f"{option} Generated!")
        st.text_area(f"Your {option}:", value=result, height=300)

        # Save to PDF
        with open("output.html", "w", encoding="utf-8") as f:
            f.write(f"<h2>{option}</h2><p>{result}</p>")
        pdfkit.from_file("output.html", "output.pdf")

        with open("output.pdf", "rb") as f:
            st.download_button(
                label="📥 Download PDF",
                data=f,
                file_name=f"{option.lower().replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
