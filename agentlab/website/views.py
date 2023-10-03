

import os
import sys

p = os.path.abspath( 'd:/twist/Documents/vs_code/AgentLab/')
if p not in sys.path:
    sys.path.append(p)
from flask import Blueprint,render_template,request
from agentlab.main_remLC import process_pdf,query

views= Blueprint(__name__,"views")

# @views.route('/')
# def home():
#     return render_template('index.html')

@views.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pdf_file = request.files["pdf"]
        questions = request.form["questions"]
        if pdf_file:
            pdf_content = pdf_file.read()
            pdf_text = process_pdf(pdf_content)
            response = query(pdf_text, questions)
            return render_template("index.html", response=response)
    return render_template("index.html", response=None)