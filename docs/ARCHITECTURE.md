# AI-Powered System Architecture

## LangChain + Groq LLM Multi-Agent System

```
┌───────────────────────────────────────────────────────────────────────┐
│                           USER INPUT                                   │
│                  Raw Product Data (JSON-like)                         │
└─────────────────────────────┬─────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  LANGCHAIN ORCHESTRATOR                              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  ChatGroq LLM Initialization (llama-3.1-8b-instant)           │ │
│  │  • model: "llama-3.1-8b-instant"                              │ │
│  │  • temperature: 0.7                                           │ │
│  │  • groq_api_key: from .env                                    │ │
│  └────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │           Workflow State Management                            │ │
│  │  • product: Product                                            │ │
│  │  • question_set: QuestionSet (AI-generated)                    │ │
│  │  • faq_items: List[Dict] (AI-generated answers)                │ │
│  │  • comparison_data: Dict (AI-generated competitor)             │ │
│  │  • pages: [ProductPage, FAQPage, ComparisonPage]               │ │
│  └────────────────────────────────────────────────────────────────┘ │
└───┬──────────┬───────────┬──────────────┬─────────────────────────────┘
    │          │           │              │
    │ Step 1   │ Step 2    │ Step 3       │ Steps 4-6
    │ (Parse)  │(LLM Gen)  │(LLM Batch)   │(LLM + Save)
    │          │           │              │
    ▼          ▼           ▼              ▼
┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Data    │ │Question  │ │ Answer   │ │Comparison│
│ Parser  │ │Generator │ │Generator │ │  Agent   │
│ Agent   │ │ (LLM)    │ │(LLM Batch│ │  (LLM)   │
└────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘
     │            │            │            │
     │            │            │            │
     ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────┐
│           LLM PROMPT LAYER (LangChain)          │
│ ┌─────────────────────────────────────────────┐ │
│ │ ChatPromptTemplate + JsonOutputParser       │ │
│ │ • Question prompts (category-aware)         │ │
│ │ • Answer prompts (batch mode, product ctx)  │ │
│ │ • Competitor generation prompts             │ │
│ │ • Comparison analysis prompts               │ │
│ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
     │            │            │            │
     │     API    │     API    │     API    │
     │     Call   │     Call   │     Call   │
     ▼            ▼            ▼            ▼
┌──────────────────────────────────────────────────┐
│          GROQ API (Llama 3.1 8B Instant)         │
│  • 30 requests/minute (free tier)                │
│  • 500k tokens/day                               │
│  • Fast inference (~1-2s per request)            │
└──────────────────────────────────────────────────┘
     │            │            │
     │   JSON     │   JSON     │   JSON
     │  Response  │  Response  │  Response
     ▼            ▼            ▼
┌─────────────────────────────────────────────────┐
│            DATA MODELS LAYER                    │
│ ┌─────────┐ ┌──────────┐ ┌─────────────────┐  │
│ │ Product │ │Question  │ │ComparisonData   │  │
│ │  Model  │ │   Set    │ │ (AI-Generated)  │  │
│ └─────────┘ └──────────┘ └─────────────────┘  │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│         PYDANTIC VALIDATION LAYER                │
│  ┌──────────────────────────────────────────┐   │
│  │  Output Models:                          │   │
│  │  • FAQPage (with FAQItem list)           │   │
│  │  • ProductPage (structured details)      │   │
│  │  • ComparisonPage (2 products + points)  │   │
│  │                                          │   │
│  │  Validation:                             │   │
│  │  • Type checking                         │   │
│  │  • Required fields                       │   │
│  │  • Schema compliance                     │   │
│  └──────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│         OUTPUT LAYER (JSON)                      │
│  ┌──────────────┐ ┌──────────────┐             │
│  │ faq_page     │ │ product_page │             │
│  │  .json       │ │   .json      │             │
│  │              │ │              │             │
│  │ • 22 AI Q&As │ │ • AI Desc    │             │
│  │ • Categories │ │ • Features   │             │
│  └──────────────┘ │ • Usage      │             │
│                   │ • Safety     │             │
│  ┌──────────────┐ └──────────────┘             │
│  │comparison    │                               │
│  │  _page.json  │                               │
│  │              │                               │
│  │ • Product A  │                               │
│  │ • Product B  │                               │
│  │ • 7 Points   │                               │
│  │ • Summary    │                               │
│  └──────────────┘                               │
└──────────────────────────────────────────────────┘
```

## Agent Communication Flow

```
┌──────┐
│ User │
└──┬───┘
   │ Raw Data
   ▼
┌──────────────┐
│Orchestrator  │──────┐
└──┬───────────┘      │
   │                  │
   │ Parse Request    │ State: Empty
   ▼                  │
┌──────────────┐      │
│DataParser    │      │
└──┬───────────┘      │
   │ Product          │
   ▼                  │
┌──────────────┐      │
│Orchestrator  │◄─────┘
└──┬───────────┘      
   │                  │
   │ Generate Qs      │ State: product
   ▼                  │
┌──────────────┐      │
│Question Gen  │      │
└──┬───────────┘      │
   │ QuestionSet      │
   ▼                  │
┌──────────────┐      │
│Orchestrator  │◄─────┘
└──┬───────────┘      
   │                  │
   │ Compare          │ State: product, questions
   ▼                  │
┌──────────────┐      │
│Comparison    │      │
└──┬───────────┘      │
   │ CompData         │
   ▼                  │
┌──────────────┐      │
│Orchestrator  │◄─────┘
└──┬───────────┘
   │                  │
   │ Build Pages      │ State: product, questions, comparison
   ▼                  │
┌──────────────┐      │
│Template      │──────┼──► FAQ Page
│   Agent      │──────┼──► Product Page
└──────────────┘      └──► Comparison Page
   │
   │ All Pages
   ▼
┌──────────────┐
│Orchestrator  │
└──┬───────────┘
   │ Save JSON
   ▼
┌──────────────┐
│  File System │
└──────────────┘
```

## Data Flow Diagram

```
Input Product Data
       │
       ▼
   Validation
       │
       ├─────► Split comma-separated values
       ├─────► Type conversion
       └─────► Create Product model
              │
              ▼
         Product Instance
              │
              ├─────────────────┐
              │                 │
              ▼                 ▼
     Question Templates    Comparison Logic
              │                 │
              ▼                 ▼
       23 Questions        Product B Creation
              │                 │
              ▼                 ▼
     Filter Top 5          7 Comparison Points
              │                 │
              └─────┬───────────┘
                    │
                    ▼
              Content Blocks
                    │
                    ├─────► Benefits Block
                    ├─────► Usage Block
                    ├─────► Safety Block
                    ├─────► Pricing Block
                    ├─────► Summary Block
                    └─────► Answer Block
                              │
                              ▼
                      Template Engine
                              │
                    ├─────────┼─────────┐
                    ▼         ▼         ▼
                FAQ Page  Product   Comparison
                          Page       Page
                    │         │         │
                    └─────────┼─────────┘
                              │
                              ▼
                        JSON Output
```

## Component Interaction Matrix

| Agent         | Inputs             | Outputs           | Dependencies        |
|---------------|-------------------|-------------------|---------------------|
| DataParser    | Raw dict          | Product           | Pydantic           |
| QuestionGen   | Product           | QuestionSet       | Product model      |
| Comparison    | Product           | ComparisonData    | ContentBlocks      |
| Template      | Product+Context   | Page (JSON)       | TemplateEngine     |
| Orchestrator  | Raw dict          | Workflow summary  | All agents         |

## Module Dependency Graph

```
main.py
  └─► orchestrator_agent
       ├─► data_parser_agent
       │    └─► product (model)
       │
       ├─► question_generator_agent
       │    ├─► product (model)
       │    └─► outputs (model)
       │
       ├─► comparison_agent
       │    ├─► product (model)
       │    ├─► content_blocks
       │    └─► outputs (model)
       │
       └─► template_agent
            ├─► product (model)
            ├─► outputs (model)
            ├─► content_blocks
            └─► template_engine
                 └─► templates (model)
```
