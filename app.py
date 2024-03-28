from flask import Flask, request, jsonify
import pdfplumber
from flask_cors import CORS
import re
import os 


app = Flask(__name__)
CORS(app)  

def remove_words_ignore_case(text, words):
    # Utiliser une expression régulière pour supprimer les mots spécifiés en ignorant la casse
    for word in words:
        text = re.sub(r'\b' + re.escape(word) + r'\b', '', text, flags=re.IGNORECASE)
    return text

def extract_full_name_from_pdf(filename):
    # Supprimer l'extension du fichier
    filename_without_extension = os.path.splitext(filename)[0]   
   

    # Supprimer les occurrences de ".pdf" ou d'autres extensions
    filename_without_extension_or_extension = filename_without_extension.split(".")[0]

    # Supprimer les chiffres et les parenthèses
    cleaned_name = re.sub(r'[\d()]', '', filename_without_extension_or_extension)

    # Remplacer les tirets et les traits de soulignement par des espaces
    cleaned_name = re.sub(r'[-_]', ' ', cleaned_name)
    
    # Supprimer les occurrences de "cv" ou "resume"

    words_to_remove = ["cv", "resume", "english", "français","french","anglais"]
    filename_without_words = remove_words_ignore_case(cleaned_name, words_to_remove)

    # Rechercher le nom complet dans les métadonnées du fichier
    full_name_from_metadata = extract_name_from_metadata(filename)
    
    # Si le nom complet est trouvé dans les métadonnées, le retourner
    if full_name_from_metadata:
        return full_name_from_metadata

    # Ajouter des espaces entre les majuscules suivies par des minuscules
    filename_without_words = re.sub(r'([a-z])([A-Z])', r'\1 \2', filename_without_words)

    return filename_without_words.strip()

def extract_name_from_metadata(filename):
    # Supprimer l'extension du fichier
    filename_without_extension = os.path.splitext(filename)[0]
    
    # Extraire les parties spécifiques du nom de fichier (prénom et nom de famille)
    metadata_parts = re.findall(r'(\w+):(\w+)', filename_without_extension)
    
    # Rechercher les parties du nom de fichier correspondant au prénom et au nom de famille
    first_name = None
    last_name = None
    for key, value in metadata_parts:
        if key.lower() == "firstname":
            first_name = value.capitalize()  # Mettre en majuscule la première lettre du prénom
        elif key.lower() == "lastname":
            last_name = value.capitalize()  # Mettre en majuscule la première lettre du nom de famille
    
    # Concaténer le prénom et le nom de famille si les deux ont été trouvés
    if first_name and last_name:
        full_name = first_name + " " + last_name
    else:
        full_name = None

    return full_name



def extract_text_sections(pdf,skills_list,soft_skills):
    with pdfplumber.open(pdf) as pdf:
        for page in pdf.pages:
            # Extraire le texte de la page
            text = page.extract_text()
            skills = set()

            for skill in skills_list:
                pattern = r"\b{}\b".format(re.escape(skill))
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    skills.add(skill) 


            softskills = set()

            for sfskill in soft_skills:
                pattern = r"\b{}\b".format(re.escape(sfskill))
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    softskills.add(sfskill) 


            email = None

            # Use regex pattern to find a potential email address
            pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
            match = re.search(pattern, text)
            if match:
                email = match.group()
            print(email)


            contact_number = None
            # Utiliser le motif regex pour trouver un éventuel numéro de téléphone
            pattern = r"\+?\d{1,3}[-.\s]?\(?(5[0-9]{2})\)?[-.\s]?\d{3}[-.\s]?\d{3}\b|\+212[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{3}\b|\b\d{2}[-.\s]?\d{2}[-.\s]?\d{2}[-.\s]?\d{2}[-.\s]?\d{2}\b"

            match = re.search(pattern, text)
            if match:
                contact_number = match.group()

            print(contact_number)

        langues_detectees = []
        # Parcourir chaque langue dans la liste de langues
        for langue in langues_liste:
            # Vérifier si le nom de la langue est présent dans le texte
            if langue.lower() in text.lower():
                # Ajouter le nom de la langue à la liste des langues détectées
                langues_detectees.append(langue)
    
    return list(skills),contact_number,email,list(softskills),langues_detectees

@app.route('/extract_text', methods=['POST'])
def extract_text():
    # Vérifier si un fichier PDF est fourni
    if 'file' not in request.files:
        return jsonify({'error': 'No PDF file provided'})

    # Récupérer le fichier PDF depuis la requête
    pdf_file = request.files['file']
    filename = pdf_file.filename  # Récupérer le nom du fichier

    # Extraire le nom à partir du nom du fichier
    full_name = extract_full_name_from_pdf(filename)

    # Extraire les sections de texte du PDF
    skills,contact_number,email,softSkills,Langues = extract_text_sections(pdf_file,skills_list,soft_skills)
    # Renvoyer les sections de texte extraites
    return {'skills': skills,'contact number:':contact_number,'email':email,'soft skills':softSkills,'langues':Langues,'Name':full_name}

@app.route('/mass_extract_text', methods=['POST'])
def mass_extract_text():
    if 'files[0]' not in request.files:
        return jsonify({'error': 'No PDF files provided'})

    pdf_files = []
    for i in range(len(request.files)):
        pdf_file = request.files.get(f'files[{i}]')
        if pdf_file:
            pdf_files.append(pdf_file)

    responses = []

    for pdf_file in pdf_files:
        filename = pdf_file.filename
        full_name = extract_full_name_from_pdf(filename)
        skills, contact_number, email, softSkills, Langues = extract_text_sections(pdf_file, skills_list, soft_skills)
        responses.append({'skills': skills, 'contact number': contact_number, 'email': email, 'soft skills': softSkills, 'langues': Langues, 'Name': full_name})

    return jsonify(responses)



langues_liste = [
    "Anglais","Français","Espagnol","Allemand","Italien","Arabe","english","french","spanish","german","arabic","italian"
]
skills_list = ["CRM","Mulesoft", "Service Cloud", "Marketing Cloud", "Sales Cloud", "Platform Developer", "Administrator", "Integration", "Lightning", "Community Cloud", "Commerce Cloud", "Apex", "Visualforce", "DX", "Automation", "APIs", "SOQL", "SOSL", "Triggers", "Workflow Rules", "Process Builder", "Flows", "Reports and Dashboards", "Mobile Development", "Einstein Analytics", "Einstein AI", "Marketing Automation", "Pardot", "Community Cloud", "Field Service Lightning", "CPQ", "Billing", "Commerce Cloud", "Heroku", "AppExchange", "Data Migration", "Data Loader", "Change Management", "Security", "Authentication", "Single Sign-On", "Permission Sets", "Profiles and Roles", "Sandbox", "Deployment", "Release Management", "Customization", "Custom Objects", "Custom Fields", "Custom Metadata Types", "Validation Rules", "Record Types", "Page Layouts", "Translation Workbench", "Lightning Web Components", "Aura Components", "API Integration", "External Services", "Platform Events", "Connected Apps", "Canvas", "App Development", "Managed Packages", "Unmanaged Packages", "Trailhead", "Community", "Chatter", "Live Agent", "Omni-Channel", "Knowledge", "Einstein Discovery", "Data Studio", "Commerce Cloud", "Order Management", "Quote-to-Cash", "Contract Management", "Revenue Cloud", "Work.com", "Mulesoft", "Tableau CRM", "Einstein Voice", "Mobile SDK", "Apex REST API", "Apex SOAP API", "Bulk API", "Streaming API", "Metadata API", "Tooling API", "External Services", "Apex Batch Processing", "Apex Scheduler", "Apex Testing Framework", "DX CLI", "Visual Studio Code", "Eclipse", "Ant Migration Tool", "Continuous Integration", "Continuous Deployment", "Git Integration", "Jenkins Integration", "Travis CI Integration", "Code Review", "Code Optimization", "Performance Tuning", "Governor Limits", "Security Review", "AppExchange Publishing", "ISV Partner Program", "Trailblazer Community", "MVP Program", "Data Analysis", "Data Science", "Data Engineering", "Data Visualization", "Data Warehousing", "Big Data", "Business Intelligence", "BI","Azure", "SQL", "NoSQL", "ETL", "Machine Learning", "Deep Learning", "Natural Language Processing", "Artificial Intelligence", "AI", "Predictive Analytics", "Statistical Analysis", "Data Mining", "Data Governance", "Data Quality", "Data Modeling", "AWS", "Python", "Java", "JavaScript", "C", "C++", "C#", "PHP", "Ruby", "Swift", "Objective-C", "R", "Go", "Scala", "Kotlin", "TypeScript", "Perl", "Rust", "Shell Scripting", "MATLAB", "Html5", "Css3", "Html", "Css", "Django", "Flask", "Spring", "Node.js", "React.js", "Reactjs", "React Native", "AngularJS", "Vue.js", "Ruby on Rails", "Laravel", "ASP.NET", ".NET", "Express.js", "Hibernate", "jQuery", "Bootstrap", "Reactjs", "Symfony", "CakePHP", "CodeIgniter", "Yii", "Ember.js", "Meteor.js", "Backbone.js", "Polymer", "Meteor.js", "Sails.js", "Aurelia", "Phoenix", "Play Framework", "Grails", "Spark", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn", "Plotly", "Bokeh", "NLTK", "SpaCy", "Gensim", "Scrapy", "Beautiful Soup", "Flask-SQLAlchemy", "Django ORM", "Rails Active Record", "Hibernate ORM", "Spring Data", "Express.js ORM", "ASP.NET Entity Framework", "Vue.js CLI", "Angular CLI", "React Native", "Flutter", "Ionic", "Xamarin", "Cordova", "PhoneGap", "Apache Hadoop", "Apache Spark", "Hive", "HBase", "Apache Kafka", "Apache Flink", "Apache Cassandra", "MongoDB", "Couchbase", "Redis", "Elasticsearch", "Neo4j", "MariaDB", "PostgreSQL", "SQLite", "Merise", "UML", "Oracle Database", "Microsoft SQL Server", "MySQL"]


soft_skills = ["Communication", "Collaboration", "Teamwork", "Leadership", "Problem Solving", "Creativity", "Adaptability", "Flexibility", "Time Management", "Organization", "Critical Thinking", "Emotional Intelligence", "Empathy", "Stress Management", "Resilience", "Conflict Resolution", "Decision Making", "Interpersonal Skills", "Presentation Skills", "Public Speaking", "Negotiation", "Active Listening", "Innovation", "Initiative", "Motivation", "Self-Discipline", "Attention to Detail", "Patience", "Open-Mindedness", "Positive Attitude", "Professionalism", "Ethics", "Integrity", "Cultural Sensitivity", "Diversity and Inclusion", "Team Building", "Feedback", "Empowerment", "Mentorship", "Coaching", "Delegation", "Time Management", "Problem Solving", "Decision Making", "Emotional Intelligence", "Adaptability", "Flexibility", "Creativity", "Innovation", "Leadership", "Teamwork", "Communication", "Active Listening", "Conflict Resolution", "Interpersonal Skills", "Networking", "Collaboration", "Critical Thinking", "Attention to Detail", "Organizational Skills", "Initiative", "Motivation", "Self-Discipline", "Resilience", "Stress Management", "Time Management", "Adaptability", "Flexibility", "Problem Solving", "Decision Making", "Creativity", "Innovation", "Leadership", "Teamwork", "Communication", "Active Listening", "Interpersonal Skills", "Presentation Skills", "Negotiation", "Conflict Resolution", "Empathy", "Emotional Intelligence", "Cultural Sensitivity", "Diversity and Inclusion", "Open-Mindedness", "Positive Attitude", "Professionalism", "Ethics", "Integrity", "Accountability", "Responsibility", "Time Management", "Organization", "Attention to Detail", "Analytical Thinking", "Critical Thinking", "Problem Solving", "Decision Making", "Initiative", "Innovation", "Adaptability", "Flexibility", "Resilience", "Stress Management", "Communication", "Interpersonal Skills", "Leadership", "Teamwork", "Collaboration", "Motivation", "Emotional Intelligence", "Empathy", "Conflict Resolution", "Negotiation", "Feedback", "Coaching", "Mentorship", "Time Management", "Prioritization", "Delegation", "Organization", "Professionalism", "Ethics", "Integrity", "Cultural Sensitivity", "Diversity and Inclusion", "Open-Mindedness", "Positive Attitude", "Creativity", "Innovation", "Problem Solving", "Analytical Skills", "Decision Making", "Risk Management", "Change Management", "Continuous Learning", "Adaptability", "Flexibility", "Resilience", "Stress Management", "Communication", "Interpersonal Skills", "Leadership", "Teamwork", "Collaboration", "Motivation", "Emotional Intelligence", "Empathy", "Conflict Resolution", "Negotiation", "Feedback", "Coaching", "Mentorship", "Time Management", "Prioritization", "Delegation", "Organization", "Professionalism", "Ethics", "Integrity", "Cultural Sensitivity", "Diversity and Inclusion", "Open-Mindedness", "Positive Attitude", "Creativity", "Innovation", "Problem Solving", "Analytical Skills", "Decision Making", "Risk Management", "Change Management", "Continuous Learning", "Adaptability", "Flexibility", "Resilience", "Stress Management", "Communication", "Interpersonal Skills", "Leadership", "Teamwork", "Collaboration", "Motivation", "Emotional Intelligence", "Empathy", "Conflict Resolution", "Negotiation", "Feedback", "Coaching", "Mentorship", "Time Management", "Prioritization", "Delegation", "Organization", "Professionalism", "Ethics", "Integrity", "Cultural Sensitivity", "Diversity and Inclusion", "Open-Mindedness", "Positive Attitude", "Creativity", "Innovation", "Problem Solving", "Analytical Skills", "Decision Making", "Risk Management", "Change Management", "Continuous Learning", "Adaptability", "Flexibility", "Resilience", "Stress Management", "Communication", "Interpersonal Skills", "Leadership", "Teamwork", "Collaboration", "Motivation", "Emotional Intelligence", "Empathy", "Conflict Resolution", "Negotiation", "Feedback", "Coaching", "Mentorship", "Time Management", "Prioritization", "Delegation", "Organization", "Professionalism", "Ethics", "Integrity", "Cultural Sensitivity", "Diversity and Inclusion", "Open-Mindedness", "Positive Attitude", "Creativity", "Innovation", "Problem Solving", "Analytical Skills", "Decision Making", "Risk Management", "Change Management", "Continuous Learning", "Adaptability", "Flexibility", "Resilience", "Stress Management", "Communication", "Interpersonal Skills", "Leadership", "Teamwork", "Collaboration", "Motivation", "Emotional Intelligence", "Empathy", "Conflict Resolution", "Negotiation", "Feedback", "Coaching", "Mentorship", "Time Management", "Prioritization", "Delegation", "Organization", "Professionalism", "Ethics", "Integrity", "Cultural Sensitivity", "Diversity and Inclusion", "Open-Mindedness", "Positive Attitude", "Creativity", "Innovation", "Problem Solving", "Analytical Skills", "Decision Making", "Risk Management", "Change Management", "Continuous Learning", "Adaptability", "Flexibility", "Resilience", "Stress Management", "Communication", "Interpersonal Skills", "Leadership", "Teamwork", "Collaboration", "Motivation", "Emotional Intelligence", "Empathy", "Conflict Resolution", "Negotiation", "Feedback", "Coaching", "Mentorship", "Time Management", "Prioritization", "Delegation", "Organization", "Professionalism", "Ethics", "Integrity", "Cultural Sensitivity", "Diversity and Inclusion", "Open-Mindedness", "Positive Attitude", "Creativity", "Innovation", "Problem Solving", "Analytical Skills", "Decision Making", "Risk Management", "Change Management", "Continuous Learning", "Adaptability", "Flexibility", "Resilience", "Stress Management", "Communication", "Interpersonal Skills", "Leadership", "Teamwork", "Collaboration", "Motivation", "Emotional Intelligence", "Empathy", "Conflict Resolution", "Negotiation", "Feedback", "Coaching", "Mentorship", "Time Management", "Prioritization", "Delegation", "Organization", "Professionalism", "Ethics", "Integrity", "Cultural", "Leaders"]


   
if __name__ == '__main__':
    app.run(debug=True)
    print('API star')
