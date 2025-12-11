# MCP Demo - Architecture Documentation

## System Architecture Overview

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                           USER INTERACTION                            │
│                                                                       │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │  Browser: http://localhost:8501                               │ │
│   │  Interface: Streamlit Web App                                 │ │
│   └───────────────────────────────────────────────────────────────┘ │
│                                  │                                    │
└──────────────────────────────────┼────────────────────────────────────┘
                                   │
                                   │ HTTP Request
                                   │ POST /chat
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                        APPLICATION TIER                               │
│                                                                       │
│   ┌────────────────────────────────────────────────────────────┐    │
│   │  Chat API Server (main.py)                                 │    │
│   │  Port: 8000                                                │    │
│   │  Framework: FastAPI                                        │    │
│   │  Role: Request orchestration and validation                │    │
│   └──────────────────────────┬─────────────────────────────────┘    │
│                              │                                       │
│   ┌──────────────────────────▼─────────────────────────────────┐    │
│   │  LLM Client (client.py)                                    │    │
│   │  • OpenAI GPT-4o-mini integration                          │    │
│   │  • Function calling orchestration                          │    │
│   │  • Conversation management                                 │    │
│   │  • Tool definition registry                                │    │
│   └──────────────────────────┬─────────────────────────────────┘    │
│                              │                                       │
└──────────────────────────────┼────────────────────────────────────────┘
                               │
                               │ HTTP Request
                               │ POST /tools/execute
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                         TOOL EXECUTION TIER                           │
│                                                                       │
│   ┌────────────────────────────────────────────────────────────┐    │
│   │  MCP Server (mcp_components/mcp_server.py)                 │    │
│   │  Port: 8001                                                │    │
│   │  Framework: FastMCP + FastAPI                              │    │
│   │  Role: Tool registration and execution                     │    │
│   │                                                            │    │
│   │  ┌──────────────────────────────────────────────────────┐ │    │
│   │  │  Tool Registry                                       │ │    │
│   │  │  ────────────────                                    │ │    │
│   │  │  • add_numbers(a: int, b: int) → int                │ │    │
│   │  │  • greet(name: str) → str                           │ │    │
│   │  │  • get_info() → dict                                │ │    │
│   │  │  • get_config() → str                               │ │    │
│   │  └──────────────────────────────────────────────────────┘ │    │
│   └────────────────────────────────────────────────────────────┘    │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘


                        EXTERNAL SERVICES
                        ─────────────────
                    ┌─────────────────────┐
                    │   OpenAI API        │
                    │   GPT-4o-mini       │
                    │   Function Calling  │
                    └─────────────────────┘
```

---

## Request-Response Flow

### Scenario: User asks "Add 15 and 27"

```
Step-by-Step Flow:
═══════════════════

1. USER INPUT
   └─> User types: "Add 15 and 27"
   └─> Streamlit captures input

2. UI → CHAT API
   └─> POST http://localhost:8000/chat
   └─> Payload: {
         "message": "Add 15 and 27",
         "conversation_history": []
       }

3. CHAT API → CLIENT
   └─> Calls: process_message(message, history)
   └─> Client builds conversation array

4. CLIENT → OPENAI
   └─> Request: chat.completions.create()
   └─> Includes:
       • messages: [{"role": "user", "content": "Add 15 and 27"}]
       • tools: [add_numbers, greet, get_info, get_config]
       • tool_choice: "auto"

5. OPENAI DECISION
   └─> LLM analyzes request
   └─> Decides to call function: add_numbers
   └─> Response:
       {
         "tool_calls": [{
           "function": {
             "name": "add_numbers",
             "arguments": "{\"a\": 15, \"b\": 27}"
           }
         }]
       }

6. CLIENT → MCP SERVER
   └─> POST http://localhost:8001/tools/execute
   └─> Payload: {
         "tool_name": "add_numbers",
         "arguments": {"a": 15, "b": 27}
       }

7. MCP EXECUTION
   └─> Finds tool in registry
   └─> Executes: add_numbers(15, 27)
   └─> Returns: {"result": 42, "status": "success"}

8. MCP SERVER → CLIENT
   └─> Returns execution result

9. CLIENT → OPENAI (Second Call)
   └─> Adds tool result to conversation
   └─> Request: chat.completions.create()
   └─> Messages now include:
       • User message
       • Assistant tool call
       • Tool result: 42

10. OPENAI FINAL RESPONSE
    └─> Generates natural language
    └─> Response: "The sum of 15 and 27 is 42."

11. CLIENT → CHAT API
    └─> Returns:
        {
          "response": "The sum of 15 and 27 is 42.",
          "tool_calls": [{
            "tool": "add_numbers",
            "arguments": {"a": 15, "b": 27}
          }],
          "conversation_history": [...]
        }

12. CHAT API → UI
    └─> HTTP 200 with JSON response

13. UI → USER
    └─> Displays: "The sum of 15 and 27 is 42."
    └─> Shows tool call in expandable section
    └─> Updates conversation history
```

---

## Component Details

### 1. Streamlit App (streamlit_app.py)

**Responsibilities:**
- Render chat interface
- Capture user input
- Display messages and tool calls
- Manage session state
- Monitor API connectivity

**Key Features:**
- Real-time chat interface
- Tool call visualization
- Conversation history
- Clear chat functionality
- API status indicator

**State Management:**
```python
st.session_state.messages           # UI display messages
st.session_state.conversation_history  # OpenAI conversation context
```

---

### 2. Chat API (main.py)

**Responsibilities:**
- Accept HTTP requests from UI
- Validate request data
- Orchestrate client processing
- Return formatted responses
- Error handling

**Endpoints:**
```
GET  /       → Health check
POST /chat   → Process chat message
```

**Request Flow:**
```
FastAPI Request
    ↓
Pydantic Validation (ChatRequest)
    ↓
client.process_message()
    ↓
Pydantic Response (ChatResponse)
    ↓
JSON to Streamlit
```

---

### 3. LLM Client (client.py)

**Responsibilities:**
- Integrate with OpenAI API
- Manage conversation context
- Handle function calling
- Execute tool requests via MCP
- Format responses

**Key Functions:**

```python
process_message(message, history)
├─> Build conversation
├─> Call OpenAI with tools
├─> If tool_calls:
│   ├─> Extract tool info
│   ├─> Call MCP server
│   ├─> Add result to conversation
│   └─> Get final response
└─> Return formatted result
```

**Tool Definition Example:**
```python
{
  "type": "function",
  "function": {
    "name": "add_numbers",
    "description": "Add two numbers together",
    "parameters": {
      "type": "object",
      "properties": {
        "a": {"type": "integer"},
        "b": {"type": "integer"}
      },
      "required": ["a", "b"]
    }
  }
}
```

---

### 4. MCP Server (mcp_components/mcp_server.py)

**Responsibilities:**
- Register tools with decorators
- Expose tools via REST API
- Execute tool functions
- Return results
- Handle errors

**Endpoints:**
```
GET  /              → Health check
GET  /tools/list    → List all tools
POST /tools/execute → Execute specific tool
```

**Tool Registration:**
```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Demo MCP Server")

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b
```

**Execution Flow:**
```
POST /tools/execute
    ↓
Validate tool exists
    ↓
Extract arguments
    ↓
Execute: tool.fn(**arguments)
    ↓
Return: {"result": ..., "status": "success"}
```

---

## Data Flow Diagrams

### 1. Conversation State Management

```
┌─────────────────────────────────────────────────┐
│         Streamlit Session State                 │
├─────────────────────────────────────────────────┤
│  messages: [                                    │
│    {role: "user", content: "Add 5 and 3"},     │
│    {role: "assistant", content: "8",           │
│     tool_calls: [{tool: "add_numbers"}]}       │
│  ]                                              │
│                                                 │
│  conversation_history: [                        │
│    {role: "user", content: "Add 5 and 3"},     │
│    {role: "assistant", tool_calls: [...]},     │
│    {role: "tool", content: "8"},               │
│    {role: "assistant", content: "Sum is 8"}    │
│  ]                                              │
└─────────────────────────────────────────────────┘
         │                           ▲
         │ Sent with each request    │ Updated with
         │                           │ each response
         ▼                           │
┌─────────────────────────────────────────────────┐
│            Chat API / Client                    │
└─────────────────────────────────────────────────┘
```

### 2. Tool Execution Pipeline

```
User Query
    │
    ▼
┌──────────────────┐
│  LLM Analysis    │  ← OpenAI decides if tool needed
└────────┬─────────┘
         │
         ├─────── No Tool ──────► Direct Response
         │
         └─────── Tool Needed
                  │
                  ▼
         ┌────────────────────┐
         │  Extract Tool Info │
         │  • name            │
         │  • arguments       │
         └─────────┬──────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │   HTTP POST to MCP  │
         └─────────┬───────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  Tool Execution     │
         └─────────┬───────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  Result to Context  │
         └─────────┬───────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  LLM Final Response │
         └─────────┬───────────┘
                   │
                   ▼
              User sees result
```

---

## Port Configuration

```
Component          Port    Protocol    Purpose
─────────────────  ──────  ──────────  ────────────────────────
Streamlit UI       8501    HTTP        User interface
Chat API           8000    HTTP        Request orchestration
MCP Server         8001    HTTP        Tool execution
OpenAI API         443     HTTPS       LLM processing (external)
```

---

## Security Considerations

### 1. API Key Management
```
.env file (not in git)
├─> OPENAI_API_KEY=sk-...
└─> Loaded via python-dotenv
```

### 2. Request Validation
```
Pydantic Models
├─> ChatRequest
├─> ChatResponse
└─> ToolCallRequest
```

### 3. Error Handling
```
Try-Catch at every layer
├─> UI: Display user-friendly errors
├─> API: HTTP status codes
└─> Client: Exception handling
```

### 4. Tool Isolation
- Tools execute in separate server
- No direct access to application state
- Sandboxed execution environment

---

## Performance Characteristics

### Response Times (Typical)

```
Component                  Latency
─────────────────────────  ────────────
Streamlit → Chat API       < 10ms
Chat API → Client          < 5ms
Client → OpenAI (1st)      500-2000ms  (LLM processing)
Client → MCP Server        < 50ms
MCP Tool Execution         < 10ms
Client → OpenAI (2nd)      500-1500ms  (Response generation)
Total (with tool)          1-4 seconds
Total (without tool)       500-2000ms
```

### Bottlenecks
1. **OpenAI API calls** - Primary latency source
2. **Network I/O** - Between components
3. **Tool complexity** - Some tools may take longer

### Optimization Opportunities
- Cache OpenAI responses for repeated queries
- Implement request batching
- Use async/await for concurrent requests
- Add response streaming

---

## Scalability Considerations

### Horizontal Scaling

```
Load Balancer
      │
      ├──► Chat API Instance 1
      ├──► Chat API Instance 2
      └──► Chat API Instance N
              │
              ▼
      ┌──────────────┐
      │  MCP Cluster │
      │  Instance 1  │
      │  Instance 2  │
      │  Instance N  │
      └──────────────┘
```

### Vertical Scaling
- Increase server resources
- Optimize tool execution
- Add caching layers

---

## Error Handling Strategy

### Error Propagation

```
MCP Server Error
    │
    ├─> HTTP 404/500
    │
    ▼
Client catches exception
    │
    ├─> Logs error
    ├─> Returns error response
    │
    ▼
Chat API receives error
    │
    ├─> HTTP 500 with details
    │
    ▼
Streamlit displays
    │
    └─> st.error("Connection error: ...")
```

### Error Types

1. **Connection Errors**
   - MCP server down
   - Chat API unavailable
   - Network issues

2. **Validation Errors**
   - Invalid tool name
   - Missing arguments
   - Type mismatches

3. **Execution Errors**
   - Tool runtime errors
   - OpenAI API errors
   - Timeout errors

---

## Monitoring & Observability

### Logging Points

```
1. Streamlit:  User actions, API calls
2. Chat API:   Requests, responses, errors
3. Client:     OpenAI calls, tool executions
4. MCP Server: Tool executions, results
```

### Metrics to Track

- Request count per endpoint
- Response times
- Error rates
- Tool usage statistics
- OpenAI API costs

---

## Development Workflow

```
1. Add Tool Definition
   └─> mcp_components/mcp_server.py (@mcp.tool decorator)

2. Register with Client
   └─> client.py (tools array)

3. Restart Servers
   ├─> MCP Server (Terminal 1)
   └─> Chat API (Terminal 2)

4. Test in Streamlit
   └─> Terminal 3

5. Verify
   └─> Check tool calls in UI expandable section
```

---

**Document Version:** 1.0.0
**Last Updated:** December 11, 2024
