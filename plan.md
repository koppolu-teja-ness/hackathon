# Plan: Website-Aware AI Chatbot MVP

## 1. Product Goal

Build a hackathon MVP that turns a website into an AI-powered conversational experience.

The system should:

1. Understand information published on a website.
2. Answer user questions using that website content.
3. Support at least two configured user flows for a website.
4. Execute simple service actions through approved flows.
5. Persist conversations for review.
6. Analyze flow performance and user drop-offs.
7. Provide an embeddable chat window for the website.

### Core product idea

> We don't just answer questions from a website. We understand the website's user journeys, execute those journeys conversationally, and show where those journeys are breaking.

---

# 2. MVP Scope

The MVP supports two types of websites.

## A. Information-driven website

Example: NESS-like website.

Primary capability:

- Crawl website
- Build knowledge base
- Answer questions using RAG
- Show source pages
- Track conversations

Example flows:

1. Learn about services
2. Request information / contact

## B. Service / transactional website

Example: Swiggy-like demo website.

Primary capability:

- Understand user intent
- Start a configured flow
- Collect missing information
- Call a small set of service APIs
- Ask for approval before write actions
- Complete the flow
- Record flow events

Example flows:

1. Track Order
2. Cancel Order

### Important MVP simplification

Do **not** attempt to automate arbitrary third-party website actions.

For the service demo, use a small mock backend/API that represents the website's services.

This keeps the MVP focused on the product experience instead of complex website automation.

---

# 3. High-Level Architecture

```text
                         WEBSITE
                            |
                +-----------+-----------+
                |                       |
                v                       v
        Website Content             Flow Config
                |                       |
                v                       v
               RAG                 Flow Engine
                |                       |
                +-----------+-----------+
                            |
                            v
                       CHAT AGENT
                            |
                +-----------+-----------+
                |                       |
                v                       v
             Answer                  Action
                                        |
                                   Approval
                                        |
                                     Execute
                                        |
                                        v
                                Flow Analytics
                                        |
                                        v
                                 Chat History
```

### Responsibility split

- **LLM**: understand intent, answer questions, identify missing information.
- **RAG**: provide grounded website information.
- **Flow Engine**: control the configured user journey.
- **Actions**: execute approved service operations.
- **Database**: persist conversations and analytics events.
- **UI**: configure websites/flows and review chats/analytics.

The LLM should not be responsible for inventing or controlling the entire workflow.

---

# 4. Technology Stack

Keep the stack simple.

## Frontend / UI

- Streamlit
- Python

Use Streamlit for:

- Admin dashboard
- Chat UI
- Flow configuration
- Conversation review
- Analytics

## AI

- Amazon Nova Pro through Amazon Bedrock Converse API
- Amazon Titan Embed Text v2 through Amazon Bedrock

## Knowledge Base

- FAISS
- Local persistence

## Website ingestion

- requests
- BeautifulSoup

Static HTML only.

Do not add Playwright for the MVP.

## Persistence

- SQLite for conversations, flows, sessions, and analytics
- FAISS for website knowledge

## Flow / Agent orchestration

- LangGraph
- langchain-core only where required

---

# 5. Project Structure

```text
hackathon/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── llm.py
│   ├── scraper.py
│   ├── knowledge.py
│   ├── flows.py
│   ├── agent.py
│   ├── actions.py
│   ├── analytics.py
│   └── db.py
│
├── data/
│   ├── vectorstore/
│   └── app.db
│
└── demo/
    └── service_api.py
```

---

# 6. Phase 0 — Project Setup

## Tasks

1. Create project structure.
2. Create virtual environment.
3. Add requirements.
4. Add `.gitignore`.
5. Load environment variables using `python-dotenv`.
6. Configure AWS Bedrock credentials.
7. Keep `.env` out of git.

### `.gitignore`

```text
.env
.venv/
__pycache__/
data/
*.pyc
```

### Important

Never commit AWS credentials.

If credentials have been exposed, rotate them before using the repository.

---

# 7. Phase 1 — Bedrock Foundation

Create `src/llm.py`.

## LLM

Use:

```text
Amazon Nova Pro
```

through Bedrock Converse API.

Required capability:

```text
chat(messages, system_prompt)
```

## Embeddings

Use:

```text
Amazon Titan Embed Text v2
```

Required capability:

```text
embed(text) -> vector
```

## Verification

Before building the rest of the application:

1. Test AWS authentication.
2. Test Nova Pro.
3. Test Titan embeddings.
4. Confirm the configured Bedrock region/model access.

### Success criteria

```text
AWS connection ✓
Nova Pro ✓
Titan embeddings ✓
```

---

# 8. Phase 2 — Website Crawler

Create `src/scraper.py`.

## Input

```text
Website URL
```

## Crawler behavior

- Start from supplied URL.
- Follow same-domain links.
- Use BFS.
- Configurable page limit.
- Configurable crawl depth.
- Static HTML only.
- Ignore scripts/styles.
- Extract useful page text.
- Store page URL and title.

Suggested defaults:

```text
max_pages = 20
max_depth = 2
```

## Text processing

For each page:

```text
HTML
 ↓
Clean text
 ↓
Chunk
 ↓
Metadata
```

Chunk metadata:

```json
{
  "source_url": "...",
  "title": "...",
  "chunk_index": 0
}
```

### Success criteria

Given a website URL:

```text
20 pages max
      ↓
clean text
      ↓
chunks
      ↓
metadata
```

---

# 9. Phase 3 — Knowledge Base / RAG

Create `src/knowledge.py`.

## Flow

```text
Website chunks
     ↓
Titan embeddings
     ↓
FAISS
     ↓
Persist locally
```

Use FAISS `IndexFlatIP` with normalized embeddings for similarity search.

## Required operations

```python
add_documents(chunks)
search(query, k=5)
save()
load()
clear()
```

## Persistence

Store:

```text
data/vectorstore/
```

The knowledge base must survive application restart.

## Chat behavior

For an information question:

```text
User question
      ↓
search knowledge base
      ↓
top relevant chunks
      ↓
Nova Pro
      ↓
grounded answer
```

The UI should show the source URL(s) used for the answer.

### Success criteria

Question:

> What services does this website provide?

Produces an answer grounded in crawled website content.

---

# 10. Phase 4 — Flow Model

Create `src/flows.py`.

Do not automatically discover complicated workflows.

For the MVP, flows are configured by the admin.

## Example

```json
{
  "id": "track_order",
  "name": "Track Order",
  "trigger": [
    "where is my order",
    "track my order",
    "order status"
  ],
  "steps": [
    {
      "type": "action",
      "action": "get_orders"
    },
    {
      "type": "user_input",
      "field": "order_id"
    },
    {
      "type": "action",
      "action": "get_order_status"
    }
  ]
}
```

Cancellation:

```json
{
  "id": "cancel_order",
  "name": "Cancel Order",
  "trigger": [
    "cancel my order",
    "I want to cancel my order"
  ],
  "steps": [
    {
      "type": "action",
      "action": "get_order"
    },
    {
      "type": "action",
      "action": "check_cancellation"
    },
    {
      "type": "approval",
      "action": "cancel_order"
    }
  ]
}
```

## Flow step types

Only support:

```text
action
user_input
approval
message
```

Keep the flow engine deterministic.

---

# 11. Phase 5 — Agent / Intent Handling

Create `src/agent.py`.

The agent has three main jobs.

## Job 1 — Information question

```text
"What services do you offer?"
        ↓
RAG
        ↓
Answer
```

## Job 2 — Flow identification

```text
"I want to cancel my order"
        ↓
intent = cancel_order
        ↓
start Cancel Order flow
```

## Job 3 — Missing information

```text
User:
Cancel my order

Bot:
Sure. Which order would you like to cancel?
```

The model should not guess missing information.

---

# 12. Phase 6 — Service Actions

Create `src/actions.py`.

Keep actions deliberately small.

## MVP action types

### Read

```text
GET /orders
GET /orders/{id}
GET /orders/{id}/status
GET /orders/{id}/cancellation
```

### Write

```text
POST /orders/{id}/cancel
```

No need for generic:

- PUT
- PATCH
- DELETE
- arbitrary HTTP requests
- login automation
- credential handling
- arbitrary HTML form submission

These are future features.

---

# 13. Phase 7 — Mock Service Backend

Create:

```text
demo/service_api.py
```

Build a tiny API representing a service website.

Example data:

```text
Users
Orders
Order status
Cancellation eligibility
```

Example endpoints:

```text
GET  /orders
GET  /orders/{id}
GET  /orders/{id}/status
GET  /orders/{id}/cancellation
POST /orders/{id}/cancel
```

Example flow:

```text
User:
Where is my order?

       ↓

Intent:
track_order

       ↓

GET /orders

       ↓

User selects order

       ↓

GET /orders/123/status

       ↓

Bot:
Your order is out for delivery.
```

Cancellation:

```text
User:
Cancel my order

       ↓

Get order

       ↓

Check eligibility

       ↓

Approval

       ↓

POST /orders/123/cancel

       ↓

Success
```

---

# 14. Phase 8 — Human Approval

Keep approval for write actions.

When a write action is ready:

```text
┌────────────────────────────────────┐
│ Action requires approval           │
│                                    │
│ Cancel Order #123                  │
│                                    │
│ POST /orders/123/cancel            │
│                                    │
│ [ Reject ]       [ Approve ]       │
└────────────────────────────────────┘
```

Only after approval:

```text
execute action
     ↓
record result
     ↓
continue flow
```

The approval step should be handled through LangGraph state/interrupts or an equivalent explicit pause/resume mechanism.

---

# 15. Phase 9 — Conversation Persistence

Create `src/db.py`.

Persist:

## Sessions

```text
id
website_id
started_at
ended_at
status
flow_id
```

## Messages

```text
id
session_id
role
content
timestamp
```

## Flow events

```text
id
session_id
flow_id
step
event
timestamp
metadata
```

Example events:

```text
FLOW_STARTED
STEP_STARTED
STEP_COMPLETED
STEP_FAILED
FLOW_COMPLETED
FLOW_ABANDONED
```

This allows both chat review and analytics.

---

# 16. Phase 10 — Analytics

Create `src/analytics.py`.

Calculate:

### Overall

```text
Total conversations
Flows started
Flows completed
Completion rate
Average duration
```

### Per flow

```text
Flow name
Started
Completed
Completion rate
Average duration
Drop-off step
```

Example:

```text
FLOW ANALYTICS

Track Order
Started:       420
Completed:     382
Completion:     91%

Cancel Order
Started:       222
Completed:     139
Completion:     63%
```

## Drop-off visualization

```text
Cancel Order

Start                 100%
  ↓
Select Order           94%
  ↓
Check Eligibility      81%
  ↓
Approval               67%
  ↓
Completed              63%
```

---

# 17. Phase 11 — AI Flow Analysis

Use Nova Pro after the basic analytics work.

Input:

- flow statistics
- drop-off points
- representative conversation samples

Ask the model to identify:

1. Largest drop-off.
2. Common user confusion.
3. Failed steps.
4. Potential UX improvement.

Example output:

> Users frequently ask about refund timing before approving cancellation.

This is an enhancement on top of deterministic analytics, not the source of the metrics.

---

# 18. Phase 12 — Streamlit Admin UI

## Screen 1 — Website

```text
WEBSITE

URL
[ https://example.com ]

Max pages
[ 20 ]

Max depth
[ 2 ]

[ Analyze Website ]
```

After crawling:

```text
18 pages discovered
32 knowledge chunks
```

---

## Screen 2 — Flows

```text
FLOWS

Track Order
4 steps

Cancel Order
4 steps

+ Add Flow
```

Allow admin to:

- create flow
- edit flow
- view steps
- enable/disable flow

---

## Screen 3 — Chat

```text
AI Assistant

User: Where is my order?

Bot: I found your recent orders.
     Which one would you like to track?

User: Order #123

Bot: Your order is out for delivery.
```

Show:

- conversation
- current flow
- current step
- tools/actions used
- source pages for RAG answers

---

## Screen 4 — Conversation Review

```text
CONVERSATIONS

#1024   Track Order       ✓
#1023   Cancel Order      ✓
#1022   Service Question  ✓
#1021   Cancel Order      ✕
```

Click a conversation to see the complete transcript and flow events.

---

## Screen 5 — Analytics

```text
ANALYTICS

Conversations       1,284
Flows Started         642
Flows Completed       521
Completion Rate        81%

Flow Performance

Track Order            91%
Cancel Order           63%

Largest Drop-off:
Cancel → Approval

AI Insight:
Users frequently ask about
refund timing before approval.
```

---

# 19. Phase 13 — Embeddable Chat Widget

Create a minimal JavaScript widget.

Target integration:

```html
<script
  src="https://yourbot.example/widget.js"
  data-bot-id="demo123">
</script>
```

The widget should open a chat window connected to the chatbot backend.

### MVP requirement

It only needs to:

1. Open/close chat.
2. Send messages.
3. Display responses.
4. Display approval requests.
5. Maintain session ID.

Do not spend significant hackathon time on widget styling.

---

# 20. Security for MVP

Because the service actions use a controlled mock backend, security is much simpler.

Still implement:

- `.env` excluded from git.
- Never expose AWS credentials to the browser.
- Server-side action execution.
- Explicit approval before write actions.
- Validate action IDs against configured flows.
- Do not allow the LLM to invent arbitrary endpoints.
- Do not accept arbitrary URLs from model tool calls.
- Request timeouts.

### Out of scope for MVP

The original plan included extensive arbitrary-site protections such as registrable-domain checks, DNS/SSRF blocking, credential isolation, and arbitrary third-party action execution. Those are appropriate if the product later performs arbitrary external-site actions, but they are not necessary for this simplified mock-API MVP.

---

# 21. External Integrations — Good to Have

Only implement these if the core MVP is already working.

## Priority order

### 1. Email

Example:

```text
Flow completed
      ↓
Send confirmation email
```

### 2. Calendar

Example:

```text
Book consultation
      ↓
Check available slot
      ↓
Create calendar event
```

### 3. SMS

Example:

```text
Flow completed
      ↓
Send SMS confirmation
```

Do not build custom SMTP/SMS/calendar infrastructure. Use a simple external service/API if available.

---

# 22. End-to-End Demo

The hackathon demo should have two websites.

## Demo A — Information website

```text
Enter website URL
       ↓
Analyze
       ↓
Crawl pages
       ↓
Build knowledge base
       ↓
Open chatbot
       ↓
Ask:
"What services do you provide?"
       ↓
RAG answer
       ↓
Show source
```

Then show:

```text
Conversation saved
```

---

## Demo B — Service website

```text
Open SwiftEats demo
       ↓
Chatbot
       ↓
"I want to track my order"
       ↓
Track Order flow
       ↓
Get orders
       ↓
Select order
       ↓
Get status
       ↓
"Out for delivery"
```

Then:

```text
"I want to cancel my order"
       ↓
Cancel Order flow
       ↓
Check eligibility
       ↓
Approval card
       ↓
Approve
       ↓
POST /orders/{id}/cancel
       ↓
Success
```

Finally open analytics:

```text
Flow completion
Drop-offs
Conversation history
AI flow insight
```

---

# 23. Implementation Order

Follow this order strictly.

## Milestone 1 — AI foundation

- [ ] Project setup
- [ ] AWS configuration
- [ ] Nova Pro
- [ ] Titan embeddings
- [ ] FAISS

## Milestone 2 — Website intelligence

- [ ] URL input
- [ ] Website crawler
- [ ] Text extraction
- [ ] Chunking
- [ ] Embedding
- [ ] Search
- [ ] Persistence

## Milestone 3 — Chat

- [ ] Streamlit chat
- [ ] RAG answers
- [ ] Source display
- [ ] Conversation state

## Milestone 4 — Flows

- [ ] Flow schema
- [ ] Flow configuration
- [ ] Intent → flow mapping
- [ ] Flow state
- [ ] User input collection

## Milestone 5 — Actions

- [ ] Mock service API
- [ ] GET actions
- [ ] POST cancel action
- [ ] Approval UI
- [ ] Execute approved action

## Milestone 6 — Persistence + Analytics

- [ ] SQLite
- [ ] Chat persistence
- [ ] Flow events
- [ ] Flow metrics
- [ ] Drop-off analysis
- [ ] AI insights

## Milestone 7 — Demo polish

- [ ] Embeddable widget
- [ ] Two demo websites
- [ ] Clean UI
- [ ] README
- [ ] End-to-end demo

---

# 24. Definition of Done

The MVP is complete when the following demo works from start to finish.

### Information flow

```text
Website URL
    ↓
Crawl
    ↓
RAG
    ↓
Question
    ↓
Grounded answer + source
    ↓
Conversation persisted
```

### Service flow

```text
User
 ↓
Intent detected
 ↓
Flow started
 ↓
Information collected
 ↓
Read API
 ↓
Approval
 ↓
Write API
 ↓
Success
 ↓
Flow event recorded
```

### Analytics

```text
Conversation history
        +
Flow events
        ↓
Flow completion rate
        ↓
Drop-off analysis
        ↓
AI-generated insight
```

### Embedded experience

```text
Website
   +
One script
   ↓
Chat window
   ↓
Same AI experience
```

---

# 25. Explicitly Out of Scope

Do not add these unless the MVP is already complete:

- Playwright/browser automation
- Arbitrary third-party website actions
- Generic HTTP agent
- Automatic HTML form-to-action conversion
- Login automation
- Credential storage
- PUT/PATCH/DELETE actions
- Multi-domain action execution
- Voice
- Multi-agent architecture
- Complex authentication
- Advanced vector databases
- Kubernetes/deployment infrastructure
- Complex visual flow builder
- Advanced prompt-injection defense framework

These can become the next version.

---

# 26. Future Product Direction

After the hackathon, the architecture can evolve into:

```text
Website
   ↓
Website understanding
   ↓
Automatic flow discovery
   ↓
Visual flow builder
   ↓
Tool / API integrations
   ↓
Conversational execution
   ↓
Analytics
   ↓
AI flow optimization
```

Potential integrations:

- Email
- SMS
- Calendar
- CRM
- Ticketing
- Payments
- Internal APIs

The hackathon MVP should prove the core loop first:

> **Understand → Converse → Execute → Analyze**

