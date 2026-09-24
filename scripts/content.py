"""Every word and number on the profile. Figures are checkable on the portfolio and in the repos."""

from dataclasses import dataclass

GITHUB = "https://github.com/Harshithpramod"
PORTFOLIO = "https://harshithpramod.vercel.app"

LINKS = {
    "portfolio": PORTFOLIO,
    "linkedin": "https://www.linkedin.com/in/harshith-pramod-m/",
    "email": "mailto:harshithpramodm@gmail.com",
    "resume": f"{PORTFOLIO}/Harshith_Pramod_Resume.pdf",
}

# (key, value) rows of the whoami card, in groups separated by a rule.
WHOAMI: tuple[tuple[tuple[str, str], ...], ...] = (
    (
        ("role", "Full-stack Developer"),
        ("focus", "Full-stack products · applied AI"),
        ("based", "Bengaluru, India · UTC+5:30"),
    ),
    (
        ("langs", "TypeScript · Python · C++ · Java · SQL"),
        ("frontend", "React · Next.js · Tailwind · Vite"),
        ("backend", "Node.js · FastAPI · Flask · REST"),
        ("data", "Supabase · PostgreSQL · RLS · Edge fns"),
        ("ai", "Gemini · tool calling · CodeQL · Semgrep"),
        ("ship", "Docker · AWS · Vercel · CF Workers"),
        ("certs", "AWS Academy ×2 · IBM Generative AI"),
    ),
    (
        ("shipped", "3 products · 2 live demos"),
        ("proof", "2nd place, PyGenic ARC Project Expo"),
    ),
)
STATUS = "final-year CSE · open to full-stack roles"


@dataclass(frozen=True)
class Project:
    slug: str
    name: str
    kind: str
    context: str
    lines: tuple[str, ...]  # tagline, pre-wrapped to fit the card
    metric: str
    metric_label: tuple[str, ...]
    stack: tuple[str, ...]
    link: str               # where the card goes: live demo, repo, or case study
    live: bool = False


PROJECTS = (
    Project(
        slug="pentestai",
        name="PentestAI",
        kind="Pentesting, verified",
        context="Personal project · 2026",
        lines=(
            "Point it at a GitHub repo. An LLM flags suspects, CodeQL",
            "traces the taint, and every high or critical finding is",
            "re-run in a locked-down sandbox before it counts.",
        ),
        metric="5",
        metric_label=("stages from clone to report: secrets,", "LLM, taint, sandbox, CVSS-tagged PDF"),
        stack=("React 19", "Supabase", "Gemini", "CodeQL", "Docker"),
        link="https://pen-ai-omega.vercel.app",
        live=True,
    ),
    Project(
        slug="adforge",
        name="AdForge.ai",
        kind="Photo in, ads out",
        context="Personal project · 2026",
        lines=(
            "One product photo and one line of copy become a finished",
            "image ad and a narrated video. Structured tool calls, and",
            "the whole video is assembled in the browser.",
        ),
        metric="3",
        metric_label=("creative variants per run, each behind", "its own retry guard"),
        stack=("React", "Gemini Vision", "Tool calling", "Web Speech"),
        link=f"{PORTFOLIO}/work/adforge",
    ),
    Project(
        slug="smartpantry",
        name="Smart Pantry",
        kind="Kitchen inventory, hands-free",
        context="PyGenic ARC Project Expo · 2nd place · 2025",
        lines=(
            "Scan a barcode, snap the bill, or just say it. Stock and",
            "expiry are tracked, the shopping list writes itself, and",
            "surplus food goes to a community marketplace.",
        ),
        metric="15%",
        metric_label=("less weekly grocery spend,", "with households walled off by RLS"),
        stack=("React", "Flask", "Supabase", "Edge fns", "OCR"),
        link="https://smart-pantry-management.vercel.app",
        live=True,
    ),
)

SOURCES = (
    ("PentestAI", f"{GITHUB}/Pen-AI"),
    ("Smart Pantry", f"{GITHUB}/smart_pantry"),
    ("AdForge case study", f"{PORTFOLIO}/work/adforge"),
)

# Three rules the work above follows, each with the evidence for it.
PRINCIPLES = (
    ("Evidence over suspicion", "PentestAI proves a hit in a sandbox first."),
    ("Lock it at the source", "Row-level security, not if-statements."),
    ("AI earns its place", "One failed model call never sinks the batch."),
)
