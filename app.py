import io
import os
import re
from datetime import datetime

import streamlit as st
import pytesseract
from PIL import Image


# ============================================================
# OPTIONAL LIBRARIES
# ============================================================

try:
    import fitz
except ImportError:
    fitz = None


try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    SentenceTransformer = None
    util = None


try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import (
        ParagraphStyle,
        getSampleStyleSheet,
    )
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    REPORTLAB_AVAILABLE = True

except ImportError:
    REPORTLAB_AVAILABLE = False


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Resume Screening Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# TESSERACT OCR CONFIGURATION
# ============================================================

import shutil

TESSERACT_PATH = shutil.which("tesseract")

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    TESSERACT_AVAILABLE = True

else:
    # Windows fallback for local development
    WINDOWS_TESSERACT_PATH = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    if os.path.exists(WINDOWS_TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = (
            WINDOWS_TESSERACT_PATH
        )
        TESSERACT_AVAILABLE = True
    else:
        TESSERACT_AVAILABLE = False



# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       APPLICATION BACKGROUND
       ====================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 0%,
                rgba(59, 130, 246, 0.14),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 5%,
                rgba(168, 85, 247, 0.12),
                transparent 28%
            ),
            #080b12;
    }

    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* ======================================================
       MAIN TITLE
       ====================================================== */

    .title-card {
        text-align: center;

        padding: 32px 25px;

        margin-bottom: 30px;

        border-radius: 24px;

        border:
            1px solid rgba(
                148,
                163,
                184,
                0.18
            );

        background:
            linear-gradient(
                135deg,
                rgba(30, 58, 138, 0.95),
                rgba(76, 29, 149, 0.95)
            );

        box-shadow:
            0 18px 55px rgba(
                0,
                0,
                0,
                0.30
            );
    }

    .title-main {
        font-size: 42px;

        font-weight: 850;

        color: white;

        letter-spacing: -1px;

        margin: 0;
    }

    .title-sub {
        font-size: 16px;

        color: #dbeafe;

        margin-top: 10px;

        line-height: 1.6;
    }


    /* ======================================================
       SECTION TITLE
       ====================================================== */

    .section-title {
        font-size: 27px;

        font-weight: 750;

        color: #f8fafc;

        margin-top: 30px;

        margin-bottom: 16px;
    }


    /* ======================================================
       INPUT CARDS
       ====================================================== */

    .input-card {
        padding: 22px;

        min-height: 120px;

        border-radius: 20px;

        border:
            1px solid rgba(
                148,
                163,
                184,
                0.16
            );

        background:
            rgba(
                15,
                23,
                42,
                0.78
            );

        box-shadow:
            0 10px 35px rgba(
                0,
                0,
                0,
                0.20
            );

        margin-bottom: 12px;
    }

    .input-title {
        font-size: 21px;

        font-weight: 750;

        color: #f8fafc;
    }

    .input-description {
        color: #94a3b8;

        font-size: 14px;

        line-height: 1.6;

        margin-top: 7px;
    }


    /* ======================================================
       METRICS
       ====================================================== */

    div[data-testid="stMetric"] {

        background:
            linear-gradient(
                145deg,
                rgba(
                    30,
                    41,
                    59,
                    0.96
                ),
                rgba(
                    15,
                    23,
                    42,
                    0.90
                )
            );

        border:
            1px solid rgba(
                148,
                163,
                184,
                0.16
            );

        border-radius: 18px;

        padding: 18px 20px;

        box-shadow:
            0 12px 35px rgba(
                0,
                0,
                0,
                0.20
            );
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 800;
    }


    /* ======================================================
       SCORE CARD
       ====================================================== */

    .score-card {

        padding: 28px;

        border-radius: 22px;

        border:
            1px solid rgba(
                96,
                165,
                250,
                0.22
            );

        background:
            linear-gradient(
                135deg,
                rgba(
                    30,
                    64,
                    175,
                    0.30
                ),
                rgba(
                    88,
                    28,
                    135,
                    0.20
                ),
                rgba(
                    15,
                    23,
                    42,
                    0.90
                )
            );

        box-shadow:
            0 18px 55px rgba(
                0,
                0,
                0,
                0.25
            );

        margin-top: 12px;
    }

    .score-label {

        color: #a5b4fc;

        font-size: 14px;

        font-weight: 750;

        text-transform: uppercase;

        letter-spacing: 1px;
    }

    .score-number {

        font-size: 52px;

        font-weight: 850;

        color: white;

        margin-top: 5px;
    }

    .score-description {

        color: #94a3b8;

        font-size: 14px;
    }


    /* ======================================================
       MATCHED SKILLS
       ====================================================== */

    .matched {

        background:
            linear-gradient(
                135deg,
                rgba(
                    6,
                    78,
                    59,
                    0.94
                ),
                rgba(
                    5,
                    46,
                    38,
                    0.94
                )
            );

        border:
            1px solid rgba(
                34,
                197,
                94,
                0.28
            );

        border-left:
            4px solid #22c55e;

        padding:
            14px 17px;

        margin:
            7px 0;

        border-radius:
            12px;
    }


    /* ======================================================
       MISSING SKILLS
       ====================================================== */

    .missing {

        background:
            linear-gradient(
                135deg,
                rgba(
                    76,
                    20,
                    32,
                    0.94
                ),
                rgba(
                    52,
                    18,
                    28,
                    0.94
                )
            );

        border:
            1px solid rgba(
                239,
                68,
                68,
                0.22
            );

        border-left:
            4px solid #ef4444;

        padding:
            14px 17px;

        margin:
            7px 0;

        border-radius:
            12px;
    }


    /* ======================================================
       RECOMMENDATIONS
       ====================================================== */

    .recommendation {

        background:
            linear-gradient(
                135deg,
                rgba(
                    30,
                    58,
                    138,
                    0.58
                ),
                rgba(
                    23,
                    37,
                    84,
                    0.82
                )
            );

        border:
            1px solid rgba(
                96,
                165,
                250,
                0.18
            );

        border-left:
            4px solid #60a5fa;

        padding:
            15px 17px;

        margin:
            8px 0;

        border-radius:
            12px;
    }


    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button,
    .stDownloadButton > button {

        border-radius:
            12px;

        font-weight:
            700;

        min-height:
            46px;
    }


    /* ======================================================
       EXPANDERS
       ====================================================== */

    div[data-testid="stExpander"] {

        border:
            1px solid rgba(
                148,
                163,
                184,
                0.14
            );

        border-radius:
            14px;

        background:
            rgba(
                15,
                23,
                42,
                0.55
            );
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    section[data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #111827 0%,
                #0b1120 100%
            );

        border-right:
            1px solid rgba(
                148,
                163,
                184,
                0.12
            );
    }


    /* ======================================================
       FOOTER
       ====================================================== */

    .footer {

        text-align:
            center;

        color:
            #64748b;

        padding:
            25px 0 5px;

        font-size:
            13px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MAIN TITLE
# ============================================================

st.markdown(
    """
    <div class="title-card">

        <div class="title-main">
            🤖 AI RESUME SCREENING ASSISTANT
        </div>

        <div class="title-sub">
            AI-powered resume analysis using ATS matching,
            semantic AI, skill intelligence and recommendations
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SKILL DATABASE
# ============================================================

SKILL_ALIASES = {

    "Python": [
        "python",
        "python programming",
    ],

    "SQL": [
        "sql",
        "structured query language",
    ],

    "Excel": [
        "excel",
        "microsoft excel",
        "ms excel",
        "pivot table",
        "pivot tables",
        "vlookup",
        "xlookup",
    ],

    "Pandas": [
        "pandas",
    ],

    "NumPy": [
        "numpy",
        "num py",
    ],

    "Power BI": [
        "power bi",
        "powerbi",
        "power-bi",
    ],

    "Data Visualization": [
        "data visualization",
        "data visualisation",
        "visualization",
        "visualisation",
        "data visualization techniques",
        "data visualisation techniques",
        "charts",
        "dashboards",
        "plots",
        "plotting",
        "graphs",
        "graphing",
        "matplotlib",
        "seaborn",
        "plotly",
    ],

    "Statistics": [
        "statistics",
        "statistical analysis",
        "descriptive statistics",
        "hypothesis testing",
    ],

    "Data Cleaning": [
        "data cleaning",
        "data cleansing",
        "data preprocessing",
        "data pre-processing",
        "cleaning data",
    ],

    "Data Analysis": [
        "data analysis",
        "data analytics",
        "analyzing data",
        "analysing data",
    ],

    "Exploratory Data Analysis": [
        "eda",
        "exploratory data analysis",
        "exploratory analysis",
    ],

    "Machine Learning": [
        "machine learning",
        "machine-learning",
    ],

    "Deep Learning": [
        "deep learning",
        "deep-learning",
    ],

    "Artificial Intelligence": [
        "artificial intelligence",
        "artificial-intelligence",
    ],

    "Natural Language Processing": [
        "natural language processing",
        "nlp",
    ],

    "Communication": [
        "communication",
        "communication skills",
        "verbal communication",
        "written communication",
    ],

    "Problem Solving": [
        "problem solving",
        "problem-solving",
        "problem solving skills",
    ],

    "Tableau": [
        "tableau",
    ],

    "Matplotlib": [
        "matplotlib",
    ],

    "Seaborn": [
        "seaborn",
    ],

    "Scikit-learn": [
        "scikit-learn",
        "scikit learn",
        "sklearn",
    ],

    "Git": [
        "git",
        "git version control",
        "version control",
        "version-control",
        "source control",
        "source-control",
    ],

    "GitHub": [
        "github",
        "github repository",
        "github repositories",
        "github repo",
        "github repos",
    ],

    "Docker": [
        "docker",
    ],

    "Kubernetes": [
        "kubernetes",
        "k8s",
    ],

    "AWS": [
        "aws",
        "amazon web services",
    ],

    "Azure": [
        "azure",
        "microsoft azure",
    ],

    "Streamlit": [
        "streamlit",
        "streamlit app",
        "streamlit application",
        "streamlit applications",
        "streamlit dashboard",
        "streamlit dashboards",
    ],
}


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).lower()

    replacements = {

        "powerbi":
            "power bi",

        "power-bi":
            "power bi",

        "problem-solving":
            "problem solving",

        "version-control":
            "version control",

        "source-control":
            "source control",

        "machine-learning":
            "machine learning",

        "deep-learning":
            "deep learning",

        "artificial-intelligence":
            "artificial intelligence",

        "data-pre-processing":
            "data preprocessing",

        "data-preprocessing":
            "data preprocessing",

        "scikit learn":
            "scikit-learn",

        "num py":
            "numpy",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new,
        )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# PHRASE MATCH
# ============================================================

def phrase_present(
    text,
    phrase,
):

    text = normalize_text(text)

    phrase = normalize_text(phrase)

    if not phrase:
        return False

    pattern = (
        r"(?<!\w)"
        + re.escape(phrase)
        + r"(?!\w)"
    )

    return re.search(
        pattern,
        text,
    ) is not None


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf_text(
    uploaded_file,
):

    if fitz is None:

        return (
            "",
            "PyMuPDF is not installed. "
            "Run: pip install pymupdf",
        )

    try:

        pdf_bytes = uploaded_file.getvalue()

        document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf",
        )

        extracted_text = ""

        # ----------------------------------------------------
        # NORMAL TEXT EXTRACTION
        # ----------------------------------------------------

        for page in document:

            page_text = page.get_text(
                "text"
            )

            if page_text:

                extracted_text += (
                    page_text + "\n"
                )

        if len(
            extracted_text.strip()
        ) >= 50:

            document.close()

            return (
                extracted_text.strip(),
                "Normal PDF text extraction was used.",
            )

        # ----------------------------------------------------
        # OCR
        # ----------------------------------------------------

        if not TESSERACT_AVAILABLE:

            document.close()

            return (
                "",
                "The PDF appears to be scanned, "
                "but Tesseract OCR was not found at "
                "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
            )

        ocr_text = ""

        for page in document:

            pix = page.get_pixmap(
                matrix=fitz.Matrix(
                    2,
                    2,
                ),
                alpha=False,
            )

            image_bytes = pix.tobytes(
                "png"
            )

            image = Image.open(
                io.BytesIO(
                    image_bytes
                )
            )

            image = image.convert(
                "RGB"
            )

            page_text = (
                pytesseract.image_to_string(
                    image,
                    config="--psm 6",
                )
            )

            ocr_text += (
                page_text + "\n"
            )

        document.close()

        if ocr_text.strip():

            return (
                ocr_text.strip(),
                "OCR was used because the PDF did not contain selectable text.",
            )

        return (
            "",
            "Could not extract readable text from the scanned PDF.",
        )

    except Exception as error:

        return (
            "",
            f"PDF extraction/OCR error: {error}",
        )


# ============================================================
# DETECT SKILLS
# ============================================================

def detect_skills(text):

    detected = set()

    for skill, aliases in SKILL_ALIASES.items():

        candidates = [
            skill
        ] + aliases

        for alias in candidates:

            if phrase_present(
                text,
                alias,
            ):

                detected.add(
                    skill
                )

                break

    return sorted(
        detected
    )


# ============================================================
# MATCH SKILLS
# ============================================================

def match_skills(
    resume_skills,
    job_skills,
):

    resume_set = set(
        resume_skills
    )

    job_set = set(
        job_skills
    )

    matched = sorted(
        resume_set & job_set
    )

    missing = sorted(
        job_set - resume_set
    )

    return (
        matched,
        missing,
    )


# ============================================================
# ATS SCORE
# ============================================================

def calculate_ats_score(
    resume_skills,
    job_skills,
):

    if not job_skills:

        return 0.0

    matched, _ = match_skills(
        resume_skills,
        job_skills,
    )

    return (
        len(matched)
        /
        len(set(job_skills))
        *
        100
    )


# ============================================================
# SCORE MESSAGE
# ============================================================

def get_score_message(
    score,
):

    if score >= 80:

        return (
            "🟢 Excellent match! "
            "Your resume strongly matches "
            "the job requirements."
        )

    if score >= 60:

        return (
            "🟡 Good match! "
            "Your resume matches many "
            "of the required skills."
        )

    if score >= 40:

        return (
            "🟠 Moderate match. "
            "Consider improving your "
            "resume alignment."
        )

    return (
        "🔴 Low match. "
        "Your resume needs stronger "
        "alignment with the job description."
    )


# ============================================================
# LOAD AI MODEL
# ============================================================

@st.cache_resource
def load_ai_model():

    if SentenceTransformer is None:

        return None

    try:

        return SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    except Exception:

        return None


# ============================================================
# SEMANTIC SCORE
# ============================================================

def calculate_semantic_score(
    model,
    resume_text,
    job_description,
):

    if model is None:

        return 0.0

    try:

        resume_embedding = model.encode(
            resume_text,
            convert_to_tensor=True,
        )

        job_embedding = model.encode(
            job_description,
            convert_to_tensor=True,
        )

        similarity = util.cos_sim(
            resume_embedding,
            job_embedding,
        ).item()

        score = (
            (similarity + 1)
            /
            2
            *
            100
        )

        return max(
            0,
            min(
                100,
                score,
            ),
        )

    except Exception:

        return 0.0


# ============================================================
# SKILL RELEVANCE
# ============================================================

def calculate_skill_relevance(
    model,
    resume_text,
    job_skills,
):

    if (
        model is None
        or not job_skills
    ):

        return (
            0.0,
            {},
        )

    try:

        resume_embedding = model.encode(
            resume_text,
            convert_to_tensor=True,
        )

        relevance = {}

        for skill in job_skills:

            skill_embedding = model.encode(
                skill,
                convert_to_tensor=True,
            )

            similarity = util.cos_sim(
                resume_embedding,
                skill_embedding,
            ).item()

            score = (
                (similarity + 1)
                /
                2
                *
                100
            )

            relevance[skill] = max(
                0,
                min(
                    100,
                    score,
                ),
            )

        average = (
            sum(
                relevance.values()
            )
            /
            len(relevance)
        )

        return (
            average,
            relevance,
        )

    except Exception:

        return (
            0.0,
            {},
        )


# ============================================================
# OVERALL SCORE
# ============================================================

def calculate_overall_score(
    ats_score,
    semantic_score,
    skill_relevance,
):

    return (
        ats_score * 0.40
        +
        semantic_score * 0.30
        +
        skill_relevance * 0.30
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

RECOMMENDATIONS = {

    "Python":
        "Highlight Python projects and libraries used.",

    "SQL":
        "Mention SQL queries, joins, aggregations and database projects.",

    "Pandas":
        "Highlight Pandas usage for data cleaning and analysis.",

    "NumPy":
        "Mention NumPy usage for numerical analysis.",

    "Power BI":
        "Highlight Power BI dashboards and visualization projects.",

    "Data Visualization":
        "Mention dashboards, charts and visualization projects.",

    "Statistics":
        "Mention statistical analysis and statistical techniques.",

    "Data Cleaning":
        "Highlight data cleaning and preprocessing experience.",

    "Data Analysis":
        "Highlight practical data analysis projects and insights.",

    "Exploratory Data Analysis":
        "Mention EDA techniques and insights discovered from datasets.",

    "Machine Learning":
        "Highlight relevant machine learning projects and algorithms.",

    "Deep Learning":
        "Highlight deep learning projects if you have genuine experience.",

    "Artificial Intelligence":
        "Highlight AI projects and intelligent applications.",

    "Natural Language Processing":
        "Mention NLP projects and text-processing experience.",

    "Git":
        "Mention Git and version-control experience.",

    "GitHub":
        "Add relevant GitHub projects and repositories.",

    "Tableau":
        "Highlight Tableau dashboards and visualization projects.",

    "Streamlit":
        "Mention Streamlit applications you have built.",

    "Problem Solving":
        "Highlight problem-solving achievements through projects or coding.",

    "Communication":
        "Mention teamwork, presentations and communication experience.",
}


def generate_recommendations(
    missing_skills,
):

    recommendations = []

    for skill in missing_skills:

        if skill in RECOMMENDATIONS:

            recommendations.append(
                RECOMMENDATIONS[skill]
            )

    if not recommendations:

        recommendations.append(
            "Your resume covers the detected job requirements well."
        )

    return recommendations


# ============================================================
# AI INSIGHTS
# ============================================================

def generate_insights(
    semantic_score,
    skill_relevance,
    missing_skills,
):

    insights = []

    if semantic_score >= 70:

        insights.append(
            "🤖 Strong semantic similarity was found "
            "between the resume and job description."
        )

    elif semantic_score >= 50:

        insights.append(
            "🤖 Moderate semantic similarity was found "
            "between the resume and job description."
        )

    else:

        insights.append(
            "🤖 Low semantic similarity was found "
            "between the resume and job description."
        )

    if skill_relevance >= 70:

        insights.append(
            "🧠 The resume has strong semantic relevance "
            "to the required skills."
        )

    elif skill_relevance >= 50:

        insights.append(
            "🧠 The resume has moderate semantic relevance "
            "to the required skills."
        )

    else:

        insights.append(
            "🧠 The resume has limited semantic relevance "
            "to the required skills."
        )

    if missing_skills:

        insights.append(
            "⚠️ Missing skills should only be added "
            "if you genuinely have experience with them."
        )

    else:

        insights.append(
            "🎉 All detected job skills were found in the resume."
        )

    return insights


# ============================================================
# SKILL EVIDENCE
# ============================================================

def get_skill_evidence(
    resume_text,
    skill,
):

    evidence = []

    aliases = SKILL_ALIASES.get(
        skill,
        [skill],
    )

    for line in resume_text.splitlines():

        line = line.strip()

        if not line:
            continue

        for alias in aliases:

            if phrase_present(
                line,
                alias,
            ):

                evidence.append(
                    line[:300]
                )

                break

        if len(evidence) >= 3:

            break

    return evidence


# ============================================================
# PDF REPORT
# ============================================================

def create_pdf_report(
    resume_name,
    ats_score,
    semantic_score,
    skill_relevance,
    overall_score,
    matched_skills,
    missing_skills,
    relevance,
    recommendations,
    insights,
):

    if not REPORTLAB_AVAILABLE:

        raise RuntimeError(
            "ReportLab is not installed."
        )

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=22,
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=15,
        spaceBefore=15,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
    )

    story = []

    story.append(
        Paragraph(
            "AI Resume Screening Report",
            title_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>Resume:</b> {resume_name}",
            body_style,
        )
    )

    story.append(
        Paragraph(
            "<b>Generated:</b> "
            + datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            ),
            body_style,
        )
    )

    story.append(
        Spacer(
            1,
            15,
        )
    )

    # --------------------------------------------------------
    # SCORE TABLE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Screening Scores",
            heading_style,
        )
    )

    score_data = [
        [
            "Metric",
            "Score",
        ],
        [
            "ATS Keyword Score",
            f"{ats_score:.2f}%",
        ],
        [
            "AI Semantic Score",
            f"{semantic_score:.2f}%",
        ],
        [
            "Skill Relevance",
            f"{skill_relevance:.2f}%",
        ],
        [
            "Overall AI Score",
            f"{overall_score:.2f}%",
        ],
    ]

    score_table = Table(
        score_data,
        colWidths=[
            300,
            150,
        ],
    )

    score_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#1f2937"
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(
        score_table
    )

    # --------------------------------------------------------
    # MATCHED SKILLS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            f"Matched Skills ({len(matched_skills)})",
            heading_style,
        )
    )

    if matched_skills:

        for skill in matched_skills:

            story.append(
                Paragraph(
                    f"✓ {skill}",
                    body_style,
                )
            )

    else:

        story.append(
            Paragraph(
                "No matched skills detected.",
                body_style,
            )
        )

    # --------------------------------------------------------
    # MISSING SKILLS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            f"Missing Skills ({len(missing_skills)})",
            heading_style,
        )
    )

    if missing_skills:

        for skill in missing_skills:

            story.append(
                Paragraph(
                    f"✗ {skill}",
                    body_style,
                )
            )

    else:

        story.append(
            Paragraph(
                "No missing skills detected.",
                body_style,
            )
        )

    # --------------------------------------------------------
    # RELEVANCE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "AI Skill Relevance",
            heading_style,
        )
    )

    for skill, score in sorted(
        relevance.items(),
        key=lambda item: item[1],
        reverse=True,
    ):

        story.append(
            Paragraph(
                f"{skill}: {score:.2f}%",
                body_style,
            )
        )

    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Resume Recommendations",
            heading_style,
        )
    )

    for recommendation in recommendations:

        story.append(
            Paragraph(
                f"• {recommendation}",
                body_style,
            )
        )

    # --------------------------------------------------------
    # INSIGHTS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "AI Insights",
            heading_style,
        )
    )

    for insight in insights:

        story.append(
            Paragraph(
                insight,
                body_style,
            )
        )

    story.append(
        Spacer(
            1,
            20,
        )
    )

    story.append(
        Paragraph(
            "This report is an AI-assisted screening signal "
            "and should not be treated as an automatic hiring decision.",
            body_style,
        )
    )

    document.build(
        story
    )

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 📌 HOW IT WORKS"
    )

    st.markdown(
        """
        **1. Upload Resume**

        Upload your PDF resume.

        **2. Add Job Description**

        Paste the target job description.

        **3. Extract Text**

        Normal PDFs use direct extraction.

        Scanned PDFs use OCR.

        **4. Detect Skills**

        Skills are detected automatically.

        **5. ATS Matching**

        Resume skills are compared with job skills.

        **6. Semantic AI**

        Resume and job description meaning are compared.

        **7. Skill Relevance**

        AI calculates relevance for each job skill.

        **8. Recommendations**

        Missing skills receive suggestions.

        **9. PDF Report**

        Download the complete screening report.
        """
    )

    st.divider()

    st.success(
        "📄 PDF Extraction"
    )

    st.success(
        "📊 ATS Matching"
    )

    st.success(
        "🤖 Semantic AI"
    )

    st.success(
        "🧠 Skill Analysis"
    )

    if TESSERACT_AVAILABLE:

        st.success(
            "🔍 OCR Available"
        )

    else:

        st.error(
            "🔍 OCR Not Available"
        )


# ============================================================
# INPUT SECTION
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🚀 START RESUME SCREENING'
    '</div>',
    unsafe_allow_html=True,
)


left, right = st.columns(
    2,
    gap="large",
)


# ============================================================
# RESUME UPLOAD
# ============================================================

with left:

    st.markdown(
        """
        <div class="input-card">

            <div class="input-title">
                📄 Upload Resume
            </div>

            <div class="input-description">
                Upload your PDF resume.
                Normal PDFs use text extraction.
                Scanned PDFs use OCR.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose PDF Resume",
        type=["pdf"],
    )


# ============================================================
# JOB DESCRIPTION
# ============================================================

with right:

    st.markdown(
        """
        <div class="input-card">

            <div class="input-title">
                💼 Job Description
            </div>

            <div class="input-description">
                Paste the target job description.
                Required skills will be detected automatically.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    job_description = st.text_area(
        "Paste Job Description",
        height=190,
        placeholder=(
            "Paste the job description here..."
        ),
    )


# ============================================================
# ANALYZE BUTTON
# ============================================================

st.markdown("")

analyze = st.button(
    "🚀 ANALYZE RESUME",
    type="primary",
    use_container_width=True,
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if uploaded_file is None:

        st.error(
            "❌ Please upload a PDF resume."
        )

        st.stop()

    if not job_description.strip():

        st.error(
            "❌ Please enter a job description."
        )

        st.stop()

    # --------------------------------------------------------
    # PDF EXTRACTION
    # --------------------------------------------------------

    with st.spinner(
        "📄 Extracting resume text..."
    ):

        resume_text, extraction_message = (
            extract_pdf_text(
                uploaded_file
            )
        )

    if not resume_text:

        st.error(
            extraction_message
        )

        st.stop()

    if "OCR was used" in extraction_message:

        st.success(
            "🔍 Scanned PDF detected. "
            "Tesseract OCR successfully extracted the text."
        )

    else:

        st.success(
            "✅ Resume text extracted successfully."
        )

    # --------------------------------------------------------
    # SKILL DETECTION
    # --------------------------------------------------------

    with st.spinner(
        "🔎 Detecting skills..."
    ):

        resume_skills = detect_skills(
            resume_text
        )

        job_skills = detect_skills(
            job_description
        )

    # --------------------------------------------------------
    # MATCHING
    # --------------------------------------------------------

    matched_skills, missing_skills = (
        match_skills(
            resume_skills,
            job_skills,
        )
    )

    # --------------------------------------------------------
    # ATS SCORE
    # --------------------------------------------------------

    ats_score = calculate_ats_score(
        resume_skills,
        job_skills,
    )

    # --------------------------------------------------------
    # AI ANALYSIS
    # --------------------------------------------------------

    with st.spinner(
        "🤖 Running AI analysis..."
    ):

        model = load_ai_model()

        semantic_score = (
            calculate_semantic_score(
                model,
                resume_text,
                job_description,
            )
        )

        (
            skill_relevance,
            relevance,
        ) = calculate_skill_relevance(
            model,
            resume_text,
            job_skills,
        )

    # --------------------------------------------------------
    # OVERALL SCORE
    # --------------------------------------------------------

    overall_score = (
        calculate_overall_score(
            ats_score,
            semantic_score,
            skill_relevance,
        )
    )

    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    recommendations = (
        generate_recommendations(
            missing_skills
        )
    )

    # --------------------------------------------------------
    # INSIGHTS
    # --------------------------------------------------------

    insights = (
        generate_insights(
            semantic_score,
            skill_relevance,
            missing_skills,
        )
    )

    # ========================================================
    # RESULTS
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '📊 ANALYSIS RESULTS'
        '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(
        4
    )

    with col1:

        st.metric(
            "📈 ATS SCORE",
            f"{ats_score:.2f}%",
        )

    with col2:

        st.metric(
            "🤖 AI SEMANTIC",
            f"{semantic_score:.2f}%",
        )

    with col3:

        st.metric(
            "🧠 SKILL RELEVANCE",
            f"{skill_relevance:.2f}%",
        )

    with col4:

        st.metric(
            "🏆 OVERALL AI",
            f"{overall_score:.2f}%",
        )

    # OVERALL SCORE
# --------------------------------------------------------

st.markdown(
    f"""
<div class="score-card">

    <div class="score-label">
        🏆 OVERALL AI RESUME SCORE
    </div>

    <div class="score-number">
        {overall_score:.2f}%
    </div>

    <div class="score-description">
        40% ATS + 30% semantic similarity
        + 30% skill relevance
    </div>

</div>
""",
    unsafe_allow_html=True,
)

st.progress(
    min(
        100,
        max(
            0,
            int(overall_score),
        ),
    )
)

    # ========================================================
    # ATS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '📈 ATS KEYWORD MATCH'
        '</div>',
        unsafe_allow_html=True,
    )

    st.progress(
        min(
            100,
            max(
                0,
                int(ats_score),
            ),
        )
    )

    st.info(
        get_score_message(
            ats_score
        )
    )

    st.caption(
        f"{len(matched_skills)} matched out of "
        f"{len(job_skills)} detected job skills."
    )

    # ========================================================
    # SEMANTIC AI
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🤖 AI SEMANTIC ANALYSIS'
        '</div>',
        unsafe_allow_html=True,
    )

    st.progress(
        min(
            100,
            max(
                0,
                int(semantic_score),
            ),
        )
    )

    st.write(
        f"Semantic Similarity: "
        f"**{semantic_score:.2f}%**"
    )

    # ========================================================
    # SKILL RELEVANCE
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🧠 AI SKILL RELEVANCE'
        '</div>',
        unsafe_allow_html=True,
    )

    if relevance:

        for skill, score in sorted(
            relevance.items(),
            key=lambda item: item[1],
            reverse=True,
        ):

            st.write(
                f"**{skill}: {score:.2f}%**"
            )

            st.progress(
                min(
                    100,
                    max(
                        0,
                        int(score),
                    ),
                )
            )

    else:

        st.warning(
            "No supported skills were detected "
            "in the job description."
        )

    # ========================================================
    # MATCHED SKILLS
    # ========================================================

    st.markdown(
        f'<div class="section-title">'
        f'✅ MATCHED SKILLS ({len(matched_skills)})'
        f'</div>',
        unsafe_allow_html=True,
    )

    if matched_skills:

        columns = st.columns(
            2
        )

        for index, skill in enumerate(
            matched_skills
        ):

            with columns[
                index % 2
            ]:

                st.markdown(
                    f"""
                    <div class="matched">
                        ✓ <b>{skill}</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    else:

        st.warning(
            "No required skills matched."
        )

    # ========================================================
    # MISSING SKILLS
    # ========================================================

    st.markdown(
        f'<div class="section-title">'
        f'❌ MISSING SKILLS ({len(missing_skills)})'
        f'</div>',
        unsafe_allow_html=True,
    )

    if missing_skills:

        columns = st.columns(
            2
        )

        for index, skill in enumerate(
            missing_skills
        ):

            with columns[
                index % 2
            ]:

                st.markdown(
                    f"""
                    <div class="missing">
                        ✗ <b>{skill}</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    else:

        st.success(
            "🎉 No detected job skills are missing."
        )

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '💡 RESUME IMPROVEMENT RECOMMENDATIONS'
        '</div>',
        unsafe_allow_html=True,
    )

    for recommendation in recommendations:

        st.markdown(
            f"""
            <div class="recommendation">
                💡 {recommendation}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ========================================================
    # AI INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🤖 AI RESUME INSIGHTS'
        '</div>',
        unsafe_allow_html=True,
    )

    for insight in insights:

        st.info(
            insight
        )

    # ========================================================
    # SKILL EVIDENCE
    # ========================================================

    with st.expander(
        "🔎 VIEW SKILL MATCH EVIDENCE"
    ):

        if matched_skills:

            for skill in matched_skills:

                st.markdown(
                    f"### {skill}"
                )

                evidence = (
                    get_skill_evidence(
                        resume_text,
                        skill,
                    )
                )

                if evidence:

                    for item in evidence:

                        st.write(
                            f"• {item}"
                        )

                else:

                    st.write(
                        "No evidence line found."
                    )

                st.divider()

        else:

            st.write(
                "No matched skills."
            )

    # ========================================================
    # RESUME SKILLS
    # ========================================================

    with st.expander(
        "📚 VIEW ALL RESUME SKILLS"
    ):

        if resume_skills:

            for skill in resume_skills:

                st.write(
                    f"✓ {skill}"
                )

        else:

            st.warning(
                "No supported skills detected."
            )

    # ========================================================
    # JOB SKILLS
    # ========================================================

    with st.expander(
        "💼 VIEW ALL JOB SKILLS"
    ):

        if job_skills:

            for skill in job_skills:

                st.write(
                    f"• {skill}"
                )

        else:

            st.warning(
                "No supported skills detected."
            )

    # ========================================================
    # EXTRACTED TEXT
    # ========================================================

    with st.expander(
        "📄 VIEW EXTRACTED RESUME TEXT"
    ):

        st.text_area(
            "Extracted Resume Text",
            resume_text,
            height=400,
        )

    # ========================================================
    # PDF REPORT
    # ========================================================

    st.divider()

    st.markdown(
        '<div class="section-title">'
        '📄 DOWNLOAD SCREENING REPORT'
        '</div>',
        unsafe_allow_html=True,
    )

    if not REPORTLAB_AVAILABLE:

        st.error(
            "ReportLab is not installed."
        )

        st.code(
            "pip install reportlab",
            language="powershell",
        )

    else:

        try:

            pdf_report = create_pdf_report(
                resume_name=uploaded_file.name,
                ats_score=ats_score,
                semantic_score=semantic_score,
                skill_relevance=skill_relevance,
                overall_score=overall_score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                relevance=relevance,
                recommendations=recommendations,
                insights=insights,
            )

            st.download_button(
                label="📥 DOWNLOAD SCREENING REPORT",
                data=pdf_report,
                file_name=(
                    "AI_Resume_Screening_Report.pdf"
                ),
                mime="application/pdf",
                use_container_width=True,
            )

            st.success(
                "✅ Screening report is ready!"
            )

        except Exception as error:

            st.error(
                f"Report generation failed: {error}"
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">

        🤖 AI Resume Screening Assistant
        &nbsp;•&nbsp;
        OCR
        &nbsp;•&nbsp;
        ATS
        &nbsp;•&nbsp;
        Semantic AI
        &nbsp;•&nbsp;
        Skill Analysis
        &nbsp;•&nbsp;
        PDF Report

    </div>
    """,
    unsafe_allow_html=True,
)
