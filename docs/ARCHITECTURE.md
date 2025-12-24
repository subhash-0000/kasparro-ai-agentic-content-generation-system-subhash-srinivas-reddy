# System Architecture Diagram

## Multi-Agent Content Generation System

```
┌───────────────────────────────────────────────────────────────────────┐
│                           USER INPUT                                   │
│                  Raw Product Data (JSON-like)                         │
└─────────────────────────────┬─────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR AGENT                              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │           Workflow State Management                            │ │
│  │  • product: Product                                            │ │
│  │  • question_set: QuestionSet                                   │ │
│  │  • comparison_data: Dict                                       │ │
│  │  • pages: {faq, product, comparison}                           │ │
│  └────────────────────────────────────────────────────────────────┘ │
└───┬──────────┬───────────┬───────────┬──────────────────────────────┘
    │          │           │           │
    │ Step 1   │ Step 2    │ Step 3    │ Steps 4a-c
    │          │           │           │
    ▼          ▼           ▼           ▼
┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Data    │ │Question  │ │Comparison│ │Template  │
│ Parser  │ │Generator │ │  Agent   │ │  Agent   │
│ Agent   │ │  Agent   │ │          │ │          │
└────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘
     │            │            │            │
     │            │            │            │
     ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────┐
│            DATA MODELS LAYER                    │
│ ┌─────────┐ ┌──────────┐ ┌─────────────────┐  │
│ │ Product │ │Question  │ │ComparisonData   │  │
│ │  Model  │ │   Set    │ │                 │  │
│ └─────────┘ └──────────┘ └─────────────────┘  │
└─────────────────────────────────────────────────┘
     │            │            │
     │            │            │
     ▼            ▼            ▼
┌──────────────────────────────────────────────────┐
│       CONTENT LOGIC BLOCKS LAYER                 │
│  ┌──────────────────────────────────────────┐   │
│  │ • generate_benefits_block                │   │
│  │ • extract_usage_block                    │   │
│  │ • compare_ingredients_block              │   │
│  │ • safety_info_block                      │   │
│  │ • pricing_info_block                     │   │
│  │ • product_summary_block                  │   │
│  │ • answer_generator_block                 │   │
│  └──────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│         TEMPLATE ENGINE LAYER                    │
│  ┌──────────────────────────────────────────┐   │
│  │  Template Definitions:                   │   │
│  │  • FAQ Template                          │   │
│  │  • Product Page Template                 │   │
│  │  • Comparison Template                   │   │
│  │                                          │   │
│  │  Template Application:                   │   │
│  │  • Field validation                      │   │
│  │  • Rule enforcement                      │   │
│  │  • Schema compliance                     │   │
│  └──────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│         OUTPUT LAYER (JSON)                      │
│  ┌──────────────┐ ┌──────────────┐             │
│  │  faq.json    │ │ product_page │             │
│  │              │ │   .json      │             │
│  │ • 5+ Q&As    │ │ • Description│             │
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
