import streamlit as st
import requests
import json
from graphviz import Digraph
import sys, os
from datetime import datetime
import pandas as pd

# Add parent directory to Python path to access api module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Streamlit page
st.set_page_config(
    page_title="Workflow Creator",
    page_icon="🔄",
    layout="wide",
)

# -----------------------
# 1) Initialize session state
# -----------------------
if "page" not in st.session_state:
    st.session_state.page = "workflow"  # default

if "workflow" not in st.session_state:
    st.session_state.workflow = None
    st.session_state.nodes = []
    st.session_state.edges = []
    st.session_state.description = ""
    st.session_state.current_step = 0
    st.session_state.step_details = {}
    st.session_state.node_positions = {}
    st.session_state.edge_labels = {}

# Stub data (in a real app, load from DB or file)
if "past_projects" not in st.session_state:
    st.session_state.past_projects = [
        {"id": "wf_001", "name": "T-Shirt Startup Plan", "created": "2025-05-01"},
        {"id": "wf_002", "name": "Mobile App MVP", "created": "2025-05-07"},
    ]
if "collaborators" not in st.session_state:
    st.session_state.collaborators = [
        {"username": "alice", "icon": None},
        {"username": "bob", "icon": None},
    ]

# -----------------------
# 2) Navbar
# -----------------------
def render_navbar():
    cols = st.columns([1, 1, 1, 1, 6])
    with cols[0]:
        if st.button("👤", help="Profile", key="nav_profile"):
            st.session_state.page = "profile"
    with cols[1]:
        if st.button("💼", help="Business Ideas", key="nav_business"):
            st.session_state.page = "business_ideas"
    with cols[2]:
        if st.button("🤝", help="Collaborations", key="nav_collab"):
            st.session_state.page = "collaborations"
    with cols[3]:
        if st.button("🔄", help="Workflow", key="nav_workflow"):
            st.session_state.page = "workflow"
    # cols[4] is just a spacer

# -----------------------
# 3) Page renderers
# -----------------------
def render_workflow_page():
    st.title("Workflow Visualization")

    # Sidebar form (the same “Generate Workflow” form you already had)
    with st.sidebar:
        st.title("Workflow Creator")
        with st.form("workflow_form"):
            prompt = st.text_area(
                "Describe your business plan",
                height=150,
                help="Describe your business idea, target market, and growth plan",
            )
            workflow_type = st.selectbox(
                "Workflow Type",
                ["Business Plan", "Project Timeline", "Process Flow", "Custom"],
            )
            submitted = st.form_submit_button("Generate Workflow")
            if submitted and prompt and workflow_type == "Business Plan":
                try:
                    response = requests.post(
                        "http://localhost:8000/generate-workflow",
                        json={"prompt": prompt, "type": workflow_type.lower()},
                    )
                    if response.status_code == 200:
                        wf = response.json()
                        st.session_state.nodes = wf.get("nodes", [])
                        st.session_state.edges = wf.get("edges", [])
                        st.session_state.description = wf.get("description", "")
                        # Initialize step_details if empty
                        if not st.session_state.step_details:
                            for idx, n in enumerate(st.session_state.nodes, start=1):
                                st.session_state.step_details[str(idx)] = {
                                    "name": n["label"],
                                    "status": "Not Started",
                                    "notes": "",
                                    "deadline": None,
                                    "resources": [],
                                    "estimated_cost": 0.0,
                                    "actual_cost": 0.0,
                                }
                            st.session_state.current_step = 1
                        st.session_state.workflow = True
                        st.success("Workflow generated successfully!")
                    else:
                        st.error("Failed to generate workflow")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    if st.session_state.workflow:
        dot = Digraph()
        for node in st.session_state.nodes:
            status = st.session_state.step_details[str(node["id"])]["status"]
            color = (
                "#FF0000"
                if status == "Not Started"
                else "#00FF00"
                if status == "Completed"
                else "#FFA500"
            )
            dot.node(node["id"], node["label"], style="filled", fillcolor=color)
        for edge in st.session_state.edges:
            dot.edge(edge["source"], edge["target"], label=edge.get("label", ""))

        st.subheader("Workflow Description")
        st.write(st.session_state.description)

        st.subheader("Workflow Diagram")
        st.graphviz_chart(dot.source)

        # Current step controls
        current_step = str(st.session_state.current_step)
        step_name = st.session_state.step_details[current_step]["name"]
        st.subheader(f"Current Step: {step_name}")

        c1, c2 = st.columns(2)
        with c1:
            status = st.selectbox(
                "Step Status",
                ["Not Started", "In Progress", "Completed"],
                index=[
                    "Not Started",
                    "In Progress",
                    "Completed",
                ].index(st.session_state.step_details[current_step]["status"]),
            )
            st.session_state.step_details[current_step]["status"] = status
        with c2:
            deadline = st.date_input(
                "Deadline",
                value=st.session_state.step_details[current_step]["deadline"]
                or datetime.now(),
            )
            st.session_state.step_details[current_step]["deadline"] = deadline

        st.subheader("Step Notes")
        notes = st.text_area(
            "Add notes about this step",
            value=st.session_state.step_details[current_step]["notes"],
        )
        st.session_state.step_details[current_step]["notes"] = notes

        st.subheader("Resources")
        resources = st.text_area(
            "List required resources",
            value="\n".join(st.session_state.step_details[current_step]["resources"]),
        )
        st.session_state.step_details[current_step]["resources"] = resources.split(
            "\n"
        )

        st.subheader("Cost Tracking")
        col1, col2 = st.columns(2)
        with col1:
            est = st.number_input(
                "Estimated Cost",
                value=st.session_state.step_details[current_step]["estimated_cost"],
            )
            st.session_state.step_details[current_step]["estimated_cost"] = est
        with col2:
            act = st.number_input(
                "Actual Cost",
                value=st.session_state.step_details[current_step]["actual_cost"],
            )
            st.session_state.step_details[current_step]["actual_cost"] = act

        st.subheader("Navigation")
        n1, n2 = st.columns(2)
        with n1:
            if st.button("Previous Step") and st.session_state.current_step > 1:
                st.session_state.current_step -= 1
        with n2:
            if (
                st.button("Next Step")
                and st.session_state.current_step < len(st.session_state.nodes)
            ):
                st.session_state.current_step += 1

        # Export & Save
        with st.expander("Export Options"):
            export_format = st.selectbox("Export Format", ["PNG", "SVG", "PDF"])
            if st.button("Export"):
                try:
                    dot.format = export_format.lower()
                    filename = f"workflow_{export_format.lower()}"
                    dot.render(filename, view=True)
                    st.success(f"Workflow exported as {filename}")
                except Exception as e:
                    st.error(f"Export failed: {str(e)}")

        if st.button("Save Workflow"):
            try:
                workflow_data = {
                    "nodes": st.session_state.nodes,
                    "edges": st.session_state.edges,
                    "description": st.session_state.description,
                    "step_details": st.session_state.step_details,
                }
                with open("workflow.json", "w") as f:
                    json.dump(workflow_data, f)
                st.success("Workflow saved successfully!")
            except Exception as e:
                st.error(f"Error saving workflow: {str(e)}")
    else:
        st.info("Generate a workflow first by using the sidebar form.")

def render_profile_page():
    st.title("User Profile")
    st.write("🛠 **Work in progress**: Show user’s avatar & profile details here.")

    st.subheader("👤 Personal Info")
    st.text_input("Username", value="weiyu_li", disabled=True)
    st.text_input("Email", value="weiyu@example.com", disabled=True)
    st.text_area("Bio", value="(User bio goes here)", disabled=True)

    st.subheader("Account Settings")
    st.write("… add settings or preferences here …")

def render_business_ideas_page():
    st.title("Your Business Ideas")
    st.write(
        "Below is a table of all the workflows (past projects) you’ve generated. "
        "Type an ID below to load/edit a project."
    )

    df = pd.DataFrame(st.session_state.past_projects)
    st.dataframe(df, use_container_width=True)

    selected_id = st.text_input(
        "Enter the ID of the workflow you want to load/edit:",
        value="",
        placeholder="e.g. wf_001",
    )
    if st.button("Load Project"):
        if selected_id in [p["id"] for p in st.session_state.past_projects]:
            st.success(f"Loading workflow `{selected_id}`… (not implemented yet)")
        else:
            st.error("That ID does not exist.")

def render_collaborations_page():
    st.title("Collaborations")
    st.write("Here are your current collaborators. You can add or remove them below.")

    # Display as a 4‐column grid
    cols = st.columns(4)
    for idx, collab in enumerate(st.session_state.collaborators):
        with cols[idx % 4]:
            st.button(
                "👥",
                help=f"{collab['username']}",
                key=f"collab_icon_{idx}",
            )
            st.write(collab["username"])
            if st.button(
                "Remove",
                key=f"remove_{collab['username']}",
            ):
                st.session_state.collaborators = [
                    c
                    for c in st.session_state.collaborators
                    if c["username"] != collab["username"]
                ]
                st.experimental_rerun()

    st.markdown("---")
    st.subheader("Add a New Collaborator")
    new_username = st.text_input("Collaborator username:", "")
    if st.button("➕ Add Collaborator"):
        if new_username.strip() == "":
            st.error("Username cannot be empty.")
        elif new_username in [
            c["username"] for c in st.session_state.collaborators
        ]:
            st.warning("That collaborator already exists.")
        else:
            st.session_state.collaborators.append(
                {"username": new_username, "icon": None}
            )
            st.success(f"Added collaborator `{new_username}`!")
            st.experimental_rerun()

# -----------------------
# 4) Main “router” logic
# -----------------------
render_navbar()

if st.session_state.page == "workflow":
    render_workflow_page()
elif st.session_state.page == "profile":
    render_profile_page()
elif st.session_state.page == "business_ideas":
    render_business_ideas_page()
elif st.session_state.page == "collaborations":
    render_collaborations_page()
else:
    st.error(f"Unknown page: {st.session_state.page}")
