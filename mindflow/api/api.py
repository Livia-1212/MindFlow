from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
import json
from typing import List, Dict, Optional
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Load environment variables and configure OpenAI
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

load_dotenv()

app = FastAPI(title="Workflow Creator API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

class WorkflowRequest(BaseModel):
    prompt: str
    type: str  # e.g., "business_plan", "workflow", "timeline"
    include_details: bool = True
    format: str = "json"

class Node(BaseModel):
    id: str
    label: str
    position: Dict[str, float]
    type: str
    status: Optional[str] = "Not Started"
    notes: Optional[str] = ""
    deadline: Optional[str] = None
    resources: Optional[List[str]] = []
    dependencies: Optional[List[str]] = []
    estimated_cost: Optional[float] = 0
    actual_cost: Optional[float] = 0

class Edge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = ""

class WorkflowResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    description: str
    workflow_type: str
    created_at: str
    updated_at: str

class WorkflowType(BaseModel):
    id: str
    name: str
    description: str
    template: Optional[str] = None

class WorkflowTypesResponse(BaseModel):
    workflow_types: List[WorkflowType]

@app.get("/workflow-types", response_model=WorkflowTypesResponse)
async def get_workflow_types():
    """Get available workflow types"""
    workflow_types = [
        {
            "id": "business_plan",
            "name": "Business Plan",
            "description": "Create a comprehensive business plan workflow",
            "template": "I want to create a business plan for {company_name}. The plan should include: {key_components}"
        },
        {
            "id": "project_timeline",
            "name": "Project Timeline",
            "description": "Create a project timeline workflow",
            "template": "I need a timeline for my project {project_name} with phases: {phases}"
        },
        {
            "id": "process_flow",
            "name": "Process Flow",
            "description": "Create a process flow diagram",
            "template": "Create a process flow for {process_name} with steps: {steps}"
        }
    ]
    return {"workflow_types": workflow_types}

@app.post("/generate-workflow", response_model=WorkflowResponse)
async def generate_workflow(request: WorkflowRequest):
    """Generate a workflow based on user input using AI"""
    try:
        print(f"Generating workflow for prompt: {request.prompt}")
        print(f"Workflow type: {request.type}")
        
        # Get workflow type template
        workflow_type = await get_workflow_type(request.type)
        print(f"Using workflow template: {workflow_type.template}")
        
        # Set up the system prompt
        system_prompt = """
        You are a workflow designer. Generate a workflow diagram based on the user's request.
        Return the result in JSON format with the following structure:
        {
            "nodes": [
                {
                    "id": "string",
                    "label": "string",
                    "position": {"x": number, "y": number},
                    "type": "start|task|end",
                    "status": "Not Started|In Progress|Completed|Failed",
                    "notes": "string",
                    "deadline": "YYYY-MM-DD",
                    "resources": ["string"],
                    "dependencies": ["string"],
                    "estimated_cost": number,
                    "actual_cost": number
                }
            ],
            "edges": [
                {
                    "id": "string",
                    "source": "string",
                    "target": "string",
                    "label": "string"
                }
            ],
            "description": "string"
        }
        """
        
        # Generate workflow using AI
        print("Sending request to OpenAI API...")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate a workflow diagram for: {request.prompt}. Type: {request.type}\nTemplate: {workflow_type.template}"}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        print("Received response from OpenAI API")
        
        # Parse and validate the AI response
        try:
            workflow_data = json.loads(response.choices[0].message.content)
            print("Successfully parsed AI response")
            
            # Validate required fields
            if not all(key in workflow_data for key in ["nodes", "edges", "description"]):
                raise ValueError("AI response missing required fields")
                
            # Validate nodes structure
            for node in workflow_data["nodes"]:
                if not all(key in node for key in ["id", "label", "position", "type"]):
                    raise ValueError(f"Invalid node structure: {node}")
                    
            # Validate edges structure
            for edge in workflow_data["edges"]:
                if not all(key in edge for key in ["id", "source", "target"]):
                    raise ValueError(f"Invalid edge structure: {edge}")
                    
            print("Workflow data validation successful")
            
            # Format response
            return WorkflowResponse(
                nodes=workflow_data["nodes"],
                edges=workflow_data["edges"],
                description=workflow_data["description"],
                workflow_type=request.type,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response: {str(e)}")
            print(f"Raw response: {response.choices[0].message.content}")
            raise HTTPException(
                status_code=500,
                detail="Failed to parse AI response. Please try again with a different prompt."
            )
            
        except ValueError as e:
            print(f"Validation error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Invalid workflow structure generated. Please try again with a different prompt."
            )
            
    except openai.error.APIError as e:
        print(f"OpenAI API error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API error: {str(e)}"
        )
        
    except openai.error.AuthenticationError as e:
        print(f"OpenAI Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid OpenAI API key. Please check your configuration."
        )
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate workflow: {str(e)}"
        )

@app.get("/workflow-types/{workflow_type_id}", response_model=WorkflowType)
async def get_workflow_type(workflow_type_id: str):
    """Get details about a specific workflow type"""
    workflow_types = await get_workflow_types()
    for wt in workflow_types.workflow_types:
        if wt.id == workflow_type_id:
            return wt
    raise HTTPException(status_code=404, detail="Workflow type not found")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
