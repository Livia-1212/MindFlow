# MindFlow

**AI-Powered Workflow Creator**

MindFlow is a Streamlit-based web app that leverages OpenAI’s API to turn user-provided business ideas into instant workflow diagrams—no manual flowchart tools needed. Users can generate, visualize, and manage structured workflows (business plans, project timelines, process flows) in seconds.

---

## 🚀 Features

- **AI-Generated Workflows**  
  - Enter a free-form business idea or project description.  
  - Select a workflow type (Business Plan, Project Timeline, Process Flow, or Custom).  
  - Click “Generate Workflow” to call a FastAPI backend (OpenAI GPT) and return nodes, edges, and a description in JSON.  
  - Streamlit renders the result as a Graphviz diagram.

- **Interactive Dashboard**  
  - Color-coded nodes by status (Not Started, In Progress, Completed).  
  - Update each step’s status, deadline, notes, resources, estimated/actual cost.  
  - Navigate between steps (Previous / Next).  
  - Export diagrams as PNG, SVG, or PDF.  
  - Save workflows locally (`workflow.json`) and load them later (future enhancement).

- **Multi-Page Layout**  
  - Top‐bar icon navigation (Profile, Business Ideas, Collaborations, Workflow).  
  - **Profile Page**: Placeholder for user info (username, email, bio).  
  - **Business Ideas**: Table of saved workflows (stub data) and “Load Project” by ID.  
  - **Collaborations**: Grid of collaborator icons with add/remove functionality.

---

## 🛠️ Tech Stack

- **Back-End** (FastAPI)  
  - Python · FastAPI · Pydantic · OpenAI SDK · UVicorn  
- **Front-End** (Streamlit)  
  - Streamlit · Graphviz · Requests · Pandas  

---

## ⚙️ Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/<username>/MindFlow.git
   cd MindFlow
