import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import { exec } from 'child_process';
import fs from 'fs/promises';
import path from 'path';
import { promisify } from 'util';

const execAsync = promisify(exec);

const server = new Server(
  {
    name: "sequence-timer-server",
    version: "0.1.0",
  },
  {
    capabilities: {
      resources: {},
      tools: {},
      logging: {},
    },
  }
);

const LIST_WORKOUTS = {
  name: "list_workouts",
  description: "List all available workout files",
  inputSchema: {
    type: "object",
    properties: {},
    required: [],
  },
};

const READ_WORKOUT = {
  name: "read_workout",
  description: "Read a specific workout file",
  inputSchema: {
    type: "object",
    properties: {
      name: {
        type: "string",
        description: "Name of the workout file (without .json extension)",
      },
    },
    required: ["name"],
  },
};

const WRITE_WORKOUT = {
  name: "write_workout",
  description: "Write a new workout file",
  inputSchema: {
    type: "object",
    properties: {
      name: {
        type: "string",
        description: "Name of the workout file (without .json extension)",
      },
      content: {
        type: "object",
        description: "Workout content following the sequence timer format",
        properties: {
          name: {
            type: "string",
            description: "Display name of the workout"
          },
          sequence: {
            type: "array",
            items: {
              type: "object",
              properties: {
                name: {
                  type: "string",
                  description: "Name of the exercise"
                },
                duration: {
                  type: "integer",
                  description: "Duration in seconds"
                }
              },
              required: ["name", "duration"]
            }
          }
        },
        required: ["name", "sequence"]
      }
    },
    required: ["name", "content"],
  },
};

const PUBLISH_WORKOUT = {
  name: "publish_workout",
  description: "Publish a workout by running the addseq script",
  inputSchema: {
    type: "object",
    properties: {
      name: {
        type: "string",
        description: "Name of the workout file to publish (without .json extension)",
      },
    },
    required: ["name"],
  },
};

const GET_EQUIPMENT = {
  name: "get_equipment",
  description: "List all available workout equipment",
  inputSchema: {
    type: "object",
    properties: {},
    required: [],
  },
};

const GET_INJURIES = {
  name: "get_injuries",
  description: "List all recorded injuries",
  inputSchema: {
    type: "object",
    properties: {},
    required: [],
  },
};

const GET_CURRENT_DATE = {
  name: "get_current_date",
  description: "Get current date in ISO format",
  inputSchema: {
    type: "object",
    properties: {},
    required: [],
  },
};

const PUBLIC_DIR = '/Users/matt/code/sequence-timer-web/public';

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [LIST_WORKOUTS, READ_WORKOUT, WRITE_WORKOUT, PUBLISH_WORKOUT, GET_EQUIPMENT, GET_INJURIES, GET_CURRENT_DATE],
}));

async function doListWorkouts() {
  try {
    const files = await fs.readdir(PUBLIC_DIR);
    const workouts = files
      .filter(file => file.endsWith('.json'))
      .map(file => file.slice(0, -5));
    
    return {
      content: [{ type: "text", text: JSON.stringify(workouts) }],
    };
  } catch (e) {
    throw new Error(`Failed to list workouts: ${e.message}`);
  }
}

async function doReadWorkout(name) {
  try {
    const filePath = path.join(PUBLIC_DIR, `${name}.json`);
    const content = await fs.readFile(filePath, 'utf-8');
    return {
      content: [{ type: "text", text: content }],
    };
  } catch (e) {
    throw new Error(`Failed to read workout: ${e.message}`);
  }
}

async function doWriteWorkout(name, content) {
  try {
    const filePath = path.join(PUBLIC_DIR, `${name}.json`);

    if (!content.name || !content.sequence) {
      throw new Error("Invalid workout content structure");
    }

    await fs.writeFile(filePath, JSON.stringify(content, null, 2));
    return {
      content: [{ type: "text", text: `Successfully wrote workout: ${name}` }],
    };
  } catch (e) {
    throw new Error(`Failed to write workout: ${e.message}`);
  }
}

async function doPublishWorkout(name) {
  try {
    const filePath = path.join(PUBLIC_DIR, `${name}.json`);
    await fs.access(filePath);
    const { stdout } = await execAsync(`cd /Users/matt/code/sequence-timer-web && ./addseq.sh public/${name}.json`);
    const url = `https://sequence-timer-web.web.app/${name}`;
    return {
      content: [{ 
        type: "text", 
        text: `Successfully published workout: ${name}\n${stdout}\nWorkout URL: ${url}` 
      }],
    };
  } catch (e) {
    throw new Error(`Failed to publish workout: ${e.message}`);
  }
}

async function doGetEquipment() {
  try {
    const content = await fs.readFile('/Users/matt/code/sequence-timer-web/mcp_server/equipment.txt', 'utf-8');
    return {
      content: [{ type: "text", text: content }],
    };
  } catch (e) {
    throw new Error(`Failed to get equipment: ${e.message}`);
  }
}

async function doGetInjuries() {
  try {
    const content = await fs.readFile('/Users/matt/code/sequence-timer-web/mcp_server/injuries.txt', 'utf-8');
    const currentDate = new Date().toISOString().split('T')[0];
    return {
      content: [{ type: "text", text: `Current date: ${currentDate}\n\n${content}` }],
    };
  } catch (e) {
    throw new Error(`Failed to get injuries: ${e.message}`);
  }
}

async function doGetCurrentDate() {
  const currentDate = new Date().toISOString().split('T')[0];
  return {
    content: [{ type: "text", text: currentDate }],
  };
}

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  switch (request.params.name) {
    case "list_workouts":
      return doListWorkouts();
    
    case "read_workout":
      const { name } = request.params.arguments;
      return doReadWorkout(name);
    
    case "write_workout":
      const { name: writeName, content } = request.params.arguments;
      return doWriteWorkout(writeName, content);
    
    case "publish_workout":
      const { name: publishName } = request.params.arguments;
      return doPublishWorkout(publishName);
    
    case "get_equipment":
      return doGetEquipment();
    
    case "get_injuries":
      return doGetInjuries();
    
    case "get_current_date":
      return doGetCurrentDate();
    
    default:
      throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${request.params.name}`);
  }
});

// Error handler
server.onerror = (error) => {
  console.error(error);
};

// Handle SIGINT
process.on("SIGINT", async () => {
  await server.close();
  process.exit(0);
});

// Run the server
async function runServer() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Sequence Timer MCP Server running on stdio");
}

runServer().catch((error) => {
  console.error("Fatal error running server:", error);
  process.exit(1);
});