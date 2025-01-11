#!/usr/bin/env python3

import json
import os
import subprocess
from typing import Dict
from mcp.server.fastmcp import FastMCP, Context

# Use FastMCP instead of low-level Server
mcp = FastMCP("sequence-timer-server")

# Define tools using decorators
@mcp.tool()
def list_workouts() -> list[str]:
    """List all available workout files"""
    public_dir = os.path.join(os.getcwd(), "public")
    try:
        workouts = []
        for file in os.listdir(public_dir):
            if file.endswith(".json"):
                workouts.append(file[:-5])  # Remove .json extension
        return workouts
    except Exception as e:
        raise Exception(f"Failed to list workouts: {str(e)}")

@mcp.tool()
def read_workout(name: str) -> Dict:
    """Read a specific workout file"""
    public_dir = os.path.join(os.getcwd(), "public")
    try:
        file_path = os.path.join(public_dir, f"{name}.json")
        if not os.path.exists(file_path):
            raise Exception(f"Workout file not found: {name}")
        
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Failed to read workout: {str(e)}")

@mcp.tool()
def write_workout(name: str, content: Dict) -> str:
    """Write a new workout file
    
    Args:
        name: Name of the workout file (without .json extension)
        content: Workout content following the sequence timer format
    """
    public_dir = os.path.join(os.getcwd(), "public")
    try:
        file_path = os.path.join(public_dir, f"{name}.json")
        
        # Validate content structure
        if not isinstance(content, dict) or "name" not in content or "sequence" not in content:
            raise Exception("Invalid workout content structure")
        
        with open(file_path, "w") as f:
            json.dump(content, f, indent=2)
        
        return f"Successfully wrote workout: {name}"
    except Exception as e:
        raise Exception(f"Failed to write workout: {str(e)}")

@mcp.tool()
async def publish_workout(name: str, ctx: Context) -> str:
    """Publish a workout by running the addseq script
    
    Args:
        name: Name of the workout file to publish (without .json extension)
    """
    public_dir = os.path.join(os.getcwd(), "public")
    try:
        file_path = os.path.join(public_dir, f"{name}.json")
        if not os.path.exists(file_path):
            raise Exception(f"Workout file not found: {name}")
        
        # Report progress
        ctx.info(f"Publishing workout: {name}")
        
        # Run addseq.sh with the workout name
        result = subprocess.run(
            ["./addseq.sh", name],
            capture_output=True,
            text=True,
            check=True,
        )
        
        return f"Successfully published workout: {name}\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to publish workout: {e.stderr}")
    except Exception as e:
        raise Exception(f"Failed to publish workout: {str(e)}")

# Add resources for reading workout files
@mcp.resource("workout://{name}")
def get_workout(name: str) -> str:
    """Get a workout file as a resource"""
    public_dir = os.path.join(os.getcwd(), "public")
    file_path = os.path.join(public_dir, f"{name}.json")
    
    if not os.path.exists(file_path):
        raise Exception(f"Workout file not found: {name}")
        
    with open(file_path, "r") as f:
        return f.read()

if __name__ == "__main__":
    # Run the server
    mcp.run()
