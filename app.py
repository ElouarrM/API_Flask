from flask import Flask, request, jsonify
import pdfplumber
from flask_cors import CORS
import re



app = Flask(__name__)
CORS(app)  

skills_list = [
    # Salesforce
    "CRM",
    "Service Cloud",
    "Marketing Cloud",
    "Sales Cloud",
    "Platform Developer",
    "Administrator",
    "Integration",
    "Lightning",
    "Community Cloud",
    "Commerce Cloud",
    "Apex",
    "Visualforce",
    "DX",
    "Automation",
    "APIs",
    "SOQL",
    "SOSL",
    "Triggers",
    "Workflow Rules",
    "Process Builder",
    "Flows",
    "Reports and Dashboards",
    "Mobile Development",
    "Einstein Analytics",
    "Einstein AI",
    "Marketing Automation",
    "Pardot",
    "Community Cloud",
    "Field Service Lightning",
    "CPQ",
    "Billing",
    "Commerce Cloud",
    "Heroku",
    "AppExchange",
    "Data Migration",
    "Data Loader",
    "Change Management",
    "Security",
    "Authentication",
    "Single Sign-On",
    "Permission Sets",
    "Profiles and Roles",
    "Sandbox",
    "Deployment",
    "Release Management",
    "Customization",
    "Custom Objects",
    "Custom Fields",
    "Custom Metadata Types",
    "Validation Rules",
    "Record Types",
    "Page Layouts",
    "Translation Workbench",
    "Lightning Web Components",
    "Aura Components",
    "API Integration",
    "External Services",
    "Platform Events",
    "Connected Apps",
    "Canvas",
    "App Development",
    "Managed Packages",
    "Unmanaged Packages",
    "Trailhead",
    "Community",
    "Chatter",
    "Live Agent",
    "Omni-Channel",
    "Knowledge",
    "Einstein Discovery",
    "Data Studio",
    "Commerce Cloud",
    "Order Management",
    "Quote-to-Cash",
    "Contract Management",
    "Revenue Cloud",
    "Work.com",
    "Mulesoft",
    "Tableau CRM",
    "Einstein Voice",
    "Mobile SDK",
    "Apex REST API",
    "Apex SOAP API",
    "Bulk API",
    "Streaming API",
    "Metadata API",
    "Tooling API",
    "External Services",
    "Apex Batch Processing",
    "Apex Scheduler",
    "Apex Testing Framework",
    "DX CLI",
    "Visual Studio Code",
    "Eclipse",
    "Ant Migration Tool",
    "Continuous Integration",
    "Continuous Deployment",
    "Git Integration",
    "Jenkins Integration",
    "Travis CI Integration",
    "Code Review",
    "Code Optimization",
    "Performance Tuning",
    "Governor Limits",
    "Security Review",
    "AppExchange Publishing",
    "ISV Partner Program",
    "Trailblazer Community",
    "MVP Program",
    
    # Data
    "Data Analysis",
    "Data Science",
    "Data Engineering",
    "Data Visualization",
    "Data Warehousing",
    "Big Data",
    "Business Intelligence",
    "SQL",
    "NoSQL",
    "ETL",
    "Machine Learning",
    "Deep Learning",
    "Natural Language Processing",
    "Artificial Intelligence",
    "Predictive Analytics",
    "Statistical Analysis",
    "Data Mining",
    "Data Governance",
    "Data Quality",
    "Data Modeling",
    
    # Programmation - Langages
    "Python",
    "Java",
    "JavaScript",
    "C++",
    "C#",
    "PHP",
    "Ruby",
    "Swift",
    "Objective-C",
    "R",
    "Go",
    "Scala",
    "Kotlin",
    "TypeScript",
    "Perl",
    "Rust",
    "Shell Scripting",
    "MATLAB",
    "Html5",
    "Css3",
    
    # Programmation - Frameworks
    "Django",
    "Flask",
    "Spring Framework",
    "Node.js",
    "React.js",
    "AngularJS",
    "Vue.js",
    "Ruby on Rails",
    "Laravel",
    "ASP.NET",
    "Express.js",
    "Hibernate",
    "jQuery",
    "Bootstrap",
    "Reactjs"
    "Symfony",
    "CakePHP",
    "CodeIgniter",
    "Yii",
    "Ember.js",
    "Meteor.js",
    "Backbone.js",
    "Polymer",
    "Meteor.js",
    "Sails.js",
    "Aurelia",
    "Phoenix",
    "Play Framework",
    "Grails",
    "Spark",
    "TensorFlow",
    "PyTorch",
    "Keras",
    "Scikit-learn",
    "Pandas",
    "NumPy",
    "SciPy",
    "Matplotlib",
    "Seaborn",
    "Plotly",
    "Bokeh",
    "NLTK",
    "SpaCy",
    "Gensim",
    "Scrapy",
    "Beautiful Soup",
    "Flask-SQLAlchemy",
    "Django ORM",
    "Rails Active Record",
    "Hibernate ORM",
    "Spring Data",
    "Express.js ORM",
    "ASP.NET Entity Framework",
    "Vue.js CLI",
    "Angular CLI",
    "React Native",
    "Flutter",
    "Ionic",
    "Xamarin",
    "Cordova",
    "PhoneGap",
    "Apache Hadoop",
    "Apache Spark",
    "Hive",
    "HBase",
    "Apache Kafka",
    "Apache Flink",
    "Apache Cassandra",
    "MongoDB",
    "Couchbase",
    "Redis",
    "Elasticsearch",
    "Neo4j",
    "MariaDB",
    "PostgreSQL",
    "SQLite",
    "Oracle Database",
    "Microsoft SQL Server",
    "MySQL"
]

def extract_text_sections(pdf,skills_list):
    text_sections = []
    
    with pdfplumber.open(pdf) as pdf:
        for page in pdf.pages:
            # Extraire le texte de la page
            text = page.extract_text()
            
            skills = []

            for skill in skills_list:
                pattern = r"\b{}\b".format(re.escape(skill))
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    skills.append(skill)
            
            email = None

            # Use regex pattern to find a potential email address
            pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
            match = re.search(pattern, text)
            if match:
                email = match.group()
            print(email)



            contact_number = None

        # Utiliser le motif regex pour trouver un éventuel numéro de contact
            pattern = r"\+?\d{3}\s?\d{9}"
            match = re.search(pattern, text)
            if match:
                 contact_number = match.group()

            print(contact_number)

            


            
            # Séparer le texte en sections basées sur les sauts de ligne ou d'autres délimiteurs
            sections = text.split("\n")  # Vous pouvez utiliser d'autres délimiteurs si nécessaire

            
            # Ajouter les sections de texte de la page à la liste globale
            text_sections.extend(sections)
    
    return skills,contact_number,email

@app.route('/extract_text', methods=['POST'])
def extract_text():
    # Vérifier si un fichier PDF est fourni
    if 'file' not in request.files:
        return jsonify({'error': 'No PDF file provided'})

    # Récupérer le fichier PDF depuis la requête
    pdf_file = request.files['file']

    # Extraire les sections de texte du PDF
    skills,contact_number,email = extract_text_sections(pdf_file,skills_list)
    # Renvoyer les sections de texte extraites
    return {'skills': skills,'contact number:':contact_number,'email':email}

if __name__ == '__main__':
    app.run(debug=True)
    print('API star')
