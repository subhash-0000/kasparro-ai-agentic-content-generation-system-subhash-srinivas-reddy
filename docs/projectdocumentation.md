# Project Documentation
## Multi-Agent Content Generation System

---

## 1. Problem Statement

**Challenge:** Design and implement a modular multi-agent automation system that transforms raw product data into structured, machine-readable content pages without manual intervention.

**Key Requirements:**
- Parse product data into clean internal models
- Automatically generate 15+ categorized user questions
- Create reusable content transformation logic
- Apply structured templates for page generation
- Generate FAQ, Product Description, and Comparison pages
- Output machine-readable JSON (not free text)
- Demonstrate true multi-agent architecture (not a monolithic GPT wrapper)

**Constraints:**
- Use ONLY provided product data (no external research)
- Must operate autonomously through agent orchestration
- Each agent must have a single, well-defined responsibility
- No hidden global state or implicit dependencies

---

## 2. Solution Overview

### High-Level Approach

The system implements a **multi-agent orchestration architecture** where specialized agents collaborate through a defined workflow to transform input data into structured output.

**Core Philosophy:**
1. **Agent Autonomy** - Each agent operates independently with clear I/O contracts
2. **Reusable Logic** - Content transformation logic is modular and composable
3. **Template-Driven** - Page structure is defined through declarative templates
4. **State Transparency** - Orchestrator manages all state explicitly
5. **Machine-Readable Output** - All outputs are validated JSON structures

### Technology Stack

- **Language:** Python 3.8+
- **Data Validation:** Pydantic (for type-safe models and validation)
- **Architecture Pattern:** Multi-Agent System with Orchestrator
- **Output Format:** JSON

---

## 3. Scopes & Assumptions

### In Scope

✅ **Data Processing**
- Parsing raw product data with validation
- Internal model transformation
- Data integrity checks

✅ **Question Generation**
- Automatic generation of 15+ questions
- Categorization across 8 categories (Informational, Usage, Safety, Skin Type, Purchase, Comparison, Results, Ingredients)
- Template-based question creation

✅ **Content Transformation**
- 7 reusable content logic blocks
- Pure functions with no side effects
- Composable transformation pipeline

✅ **Template System**
- Custom template engine
- Field definitions with validation rules
- Three template types (FAQ, Product, Comparison)

✅ **Multi-Agent Orchestration**
- 5 specialized agents with single responsibilities
- Defined workflow with state management
- Error handling and logging

✅ **Output Generation**
- Machine-readable JSON output
- Schema validation
- Structured page generation

### Out of Scope

❌ **UI/Frontend** - This is a backend system; no web interface
❌ **External Data** - No API calls or external data sources
❌ **LLM Integration** - No OpenAI/GPT calls (pure logic-based generation)
❌ **Database** - No persistent storage beyond JSON files
❌ **Authentication** - No user management
❌ **Real-time Processing** - Batch processing only

### Assumptions

1. **Input Data Quality** - Assume product data is well-formed (though validated)
2. **Single Product Context** - System processes one product at a time
3. **English Language** - All content generated in English
4. **Static Templates** - Templates are predefined, not dynamically generated
5. **Local Execution** - System runs locally, not as a web service

---

## 4. System Design

### 4.1 Architecture Overview

The system follows a **layered multi-agent architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                     Orchestrator Agent                       │
│              (Workflow Coordination & State)                 │
└───────────┬──────────────┬──────────────┬───────────────────┘
            │              │              │
    ┌───────▼───────┐ ┌───▼────────┐ ┌──▼──────────────┐
    │ DataParser    │ │ Question   │ │  Comparison     │
    │    Agent      │ │ Generator  │ │     Agent       │
    └───────┬───────┘ └─────┬──────┘ └──┬──────────────┘
            │               │            │
            ▼               ▼            ▼
        Product         QuestionSet   ComparisonData
         Model                            │
            │               │             │
            └───────┬───────┴─────────────┘
                    ▼
            ┌──────────────────┐
            │  Template Agent  │
            │  (Page Builder)  │
            └────────┬─────────┘
                     │
         ┌───────────┼──────────┐
         ▼           ▼          ▼
     faq.json   product_page   comparison
                  .json          .json
```

### 4.2 Agent Specifications

#### 4.2.1 BaseAgent (Abstract)

**Purpose:** Define standard contract for all agents

**Responsibilities:**
- Input validation
- Execution logging
- Standardized I/O wrapping

**Interface:**
```python
class BaseAgent:
    def execute(input: AgentInput) -> AgentOutput
    def validate_input(input: AgentInput) -> bool
    def log_execution(input, output)
```

#### 4.2.2 DataParserAgent

**Responsibility:** Parse and validate raw product data

**Input:** 
```python
{
    "product_name": str,
    "concentration": str,
    "skin_type": str,  # comma-separated
    "key_ingredients": str,  # comma-separated
    "benefits": str,  # comma-separated
    "how_to_use": str,
    "side_effects": str,
    "price": str
}
```

**Output:** `Product` (Pydantic model)

**Transformations:**
- Split comma-separated values into lists
- Validate required fields
- Type conversion and normalization

**Dependencies:** None

---

#### 4.2.3 QuestionGeneratorAgent

**Responsibility:** Generate categorized user questions

**Input:** `Product` instance

**Output:** `QuestionSet` with 15+ questions

**Categories:**
1. Informational - Product basics
2. Usage - How to use
3. Safety - Side effects, precautions
4. Skin Type - Compatibility
5. Purchase - Price, availability
6. Comparison - vs. competitors
7. Results - Expected outcomes
8. Ingredients - Component details

**Logic:**
- Template-based question generation
- Dynamic field substitution (product name)
- Automatic categorization

**Dependencies:** Product model

---

#### 4.2.4 ComparisonAgent

**Responsibility:** Create fictional competitor and generate comparison

**Input:** `Product` instance (Product A)

**Output:** 
```python
{
    "product_a": Product,
    "product_b": Product,  # fictional
    "comparison_points": List[ComparisonItem],
    "summary": Dict,
    "recommendation": str
}
```

**Fictional Product Generation:**
- Different concentration (15% vs 10%)
- Different skin types (Normal, Dry)
- Different ingredients (adds Vitamin E, Ferulic Acid)
- Different price point (₹899 vs ₹699)

**Comparison Points (7):**
1. Price
2. Vitamin C concentration
3. Number of key ingredients
4. Suitable skin types
5. Number of benefits
6. Ingredient overlap
7. Application timing

**Dependencies:** Product model, ContentLogicBlocks

---

#### 4.2.5 TemplateAgent

**Responsibility:** Apply templates to generate structured pages

**Input:**
```python
{
    "page_type": "faq" | "product_page" | "comparison",
    "product": Product,
    "question_set": QuestionSet,  # for FAQ
    "comparison_data": Dict  # for comparison
}
```

**Output:** `FAQPage` | `ProductPage` | `ComparisonPage`

**Page Generation Logic:**

**FAQ Page:**
- Select 5 questions (distributed across categories)
- Generate answers using `answer_generator_block`
- Structure as FAQItem list

**Product Page:**
- Generate tagline and description (product_summary_block)
- Extract benefits (generate_benefits_block)
- Structure usage guide (extract_usage_block)
- Safety info (safety_info_block)
- Pricing details (pricing_info_block)

**Comparison Page:**
- Format product summaries
- Structure comparison points
- Add summary and recommendation

**Dependencies:** TemplateEngine, ContentLogicBlocks, Product, QuestionSet

---

#### 4.2.6 OrchestratorAgent

**Responsibility:** Coordinate entire workflow and manage state

**Input:** Raw product data dictionary

**Output:** Workflow summary + saved JSON files

**Workflow Steps:**
1. **Step 1:** DataParserAgent → Product
2. **Step 2:** QuestionGeneratorAgent → QuestionSet
3. **Step 3:** ComparisonAgent → ComparisonData
4. **Step 4a:** TemplateAgent (FAQ) → faq.json
5. **Step 4b:** TemplateAgent (Product) → product_page.json
6. **Step 4c:** TemplateAgent (Comparison) → comparison_page.json
7. **Step 5:** Save all JSON outputs

**State Management:**
```python
workflow_state = {
    "product": Product,
    "question_set": QuestionSet,
    "comparison_data": Dict,
    "pages": {
        "faq": FAQPage,
        "product": ProductPage,
        "comparison": ComparisonPage
    }
}
```

**Error Handling:**
- Each step validates success before proceeding
- Fails fast on errors with detailed messages
- Logs execution at each step

**Dependencies:** All other agents

---

### 4.3 Data Models

#### 4.3.1 Core Models

**Product**
```python
class Product(BaseModel):
    name: str
    concentration: str
    skin_types: List[str]
    key_ingredients: List[str]
    benefits: List[str]
    usage_instructions: str
    side_effects: Optional[str]
    price: str
```

**CategorizedQuestion**
```python
class CategorizedQuestion(BaseModel):
    category: str
    question: str
    priority: int
```

**QuestionSet**
```python
class QuestionSet(BaseModel):
    questions: List[CategorizedQuestion]
    categories: List[str]
```

#### 4.3.2 Output Models

**FAQPage**
```python
class FAQPage(BaseModel):
    page_type: str = "faq"
    product_name: str
    total_questions: int
    categories: List[str]
    faqs: List[FAQItem]
    generated_by: str
```

**ProductPage**
```python
class ProductPage(BaseModel):
    page_type: str = "product_page"
    product_name: str
    tagline: str
    description: str
    key_features: List[str]
    ingredients: Dict[str, str]
    usage_guide: Dict[str, Any]
    suitable_for: List[str]
    benefits: List[str]
    safety_information: Dict[str, Any]
    pricing: Dict[str, str]
    generated_by: str
```

**ComparisonPage**
```python
class ComparisonPage(BaseModel):
    page_type: str = "comparison"
    product_a: Dict[str, Any]
    product_b: Dict[str, Any]
    comparison_points: List[ComparisonItem]
    summary: Dict[str, Any]
    recommendation: str
    generated_by: str
```

---

### 4.4 Content Logic Blocks

Reusable, pure functions for content transformation:

1. **generate_benefits_block(product)** → Detailed benefit descriptions
2. **extract_usage_block(product)** → Structured usage guide
3. **compare_ingredients_block(product_a, product_b)** → Ingredient comparison
4. **safety_info_block(product)** → Safety and precautions
5. **pricing_info_block(product)** → Structured pricing data
6. **product_summary_block(product)** → Tagline and description
7. **answer_generator_block(product, question)** → Q&A answers

**Design Principles:**
- **Pure Functions** - No side effects, deterministic output
- **Single Purpose** - Each block does one thing well
- **Composable** - Can be chained and reused
- **Type-Safe** - Strong typing with Pydantic

---

### 4.5 Template Engine

#### Template Structure

```python
class Template:
    template_type: TemplateType  # FAQ, PRODUCT_PAGE, COMPARISON
    name: str
    description: str
    fields: List[TemplateField]  # Field definitions
    rules: List[TemplateRule]    # Validation rules
    required_blocks: List[str]   # Needed content blocks
    output_schema: Dict          # Expected structure
```

#### Template Application Flow

```
Input Data → Validate Fields → Apply Rules → Generate Output → Validate Schema
```

#### Templates Defined

1. **FAQ Template**
   - Minimum 5 Q&A pairs
   - Categorized questions
   - Structured answers

2. **Product Page Template**
   - Minimum 3 key features
   - Complete ingredient details
   - Usage, safety, pricing sections

3. **Comparison Template**
   - Minimum 5 comparison points
   - Product summaries
   - Analysis and recommendation

---

### 4.6 Workflow Diagram

```
┌──────────────┐
│  Raw Data    │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  DataParserAgent     │  Step 1: Parse & Validate
└──────┬───────────────┘
       │ Product
       ▼
┌──────────────────────┐
│ QuestionGenerator    │  Step 2: Generate Questions
└──────┬───────────────┘
       │ QuestionSet
       ▼
┌──────────────────────┐
│  ComparisonAgent     │  Step 3: Create Comparison
└──────┬───────────────┘
       │ ComparisonData
       ▼
┌──────────────────────┐
│   TemplateAgent      │  Step 4a: FAQ Page
│   (FAQ Mode)         │
└──────┬───────────────┘
       │ FAQPage
       ▼
┌──────────────────────┐
│   TemplateAgent      │  Step 4b: Product Page
│  (Product Mode)      │
└──────┬───────────────┘
       │ ProductPage
       ▼
┌──────────────────────┐
│   TemplateAgent      │  Step 4c: Comparison Page
│ (Comparison Mode)    │
└──────┬───────────────┘
       │ ComparisonPage
       ▼
┌──────────────────────┐
│  Save JSON Files     │  Step 5: Output
└──────────────────────┘
       │
       ▼
   ┌───────────┐
   │ faq.json  │
   ├───────────┤
   │ product_  │
   │ page.json │
   ├───────────┤
   │comparison_│
   │ page.json │
   └───────────┘
```

---

### 4.7 Sequence Diagram

```
User            Orchestrator     DataParser   QuestionGen   Comparison   Template
 │                   │               │             │            │           │
 ├──raw data────────>│               │             │            │           │
 │                   │               │             │            │           │
 │                   ├──parse()─────>│             │            │           │
 │                   │<──Product─────┤             │            │           │
 │                   │               │             │            │           │
 │                   ├──generate()───┼────────────>│            │           │
 │                   │<──QuestionSet─┼─────────────┤            │           │
 │                   │               │             │            │           │
 │                   ├──compare()────┼─────────────┼───────────>│           │
 │                   │<──CompareData─┼─────────────┼────────────┤           │
 │                   │               │             │            │           │
 │                   ├──build(FAQ)───┼─────────────┼────────────┼──────────>│
 │                   │<──FAQPage─────┼─────────────┼────────────┼───────────┤
 │                   │               │             │            │           │
 │                   ├──build(Prod)──┼─────────────┼────────────┼──────────>│
 │                   │<──ProductPage─┼─────────────┼────────────┼───────────┤
 │                   │               │             │            │           │
 │                   ├──build(Comp)──┼─────────────┼────────────┼──────────>│
 │                   │<──CompPage────┼─────────────┼────────────┼───────────┤
 │                   │               │             │            │           │
 │                   ├──save_json()  │             │            │           │
 │<──success─────────┤               │             │            │           │
 │                   │               │             │            │           │
```

---

### 4.8 Design Decisions & Rationale

#### 4.8.1 Why Multi-Agent Architecture?

**Decision:** Separate agents for parsing, question generation, comparison, and templating

**Rationale:**
- **Modularity** - Each agent can be tested and modified independently
- **Scalability** - Easy to add new agents (e.g., SEO Agent, Translation Agent)
- **Reusability** - Agents can be used in different workflows
- **Clear Boundaries** - Single responsibility prevents coupling

**Alternative Considered:** Monolithic function-based approach
- **Rejected** - Harder to test, extend, and maintain

---

#### 4.8.2 Why Pydantic for Models?

**Decision:** Use Pydantic for all data models

**Rationale:**
- **Type Safety** - Compile-time type checking
- **Validation** - Automatic data validation
- **Serialization** - Easy JSON conversion
- **Documentation** - Self-documenting schemas

**Alternative Considered:** Plain dictionaries
- **Rejected** - No validation, error-prone, harder to maintain

---

#### 4.8.3 Why Custom Template Engine?

**Decision:** Build custom template engine instead of using Jinja2/Mustache

**Rationale:**
- **Control** - Full control over validation and rules
- **Type Safety** - Integrates with Pydantic models
- **Simplicity** - No need for complex template syntax
- **Learning** - Demonstrates system design capability

**Alternative Considered:** Jinja2 templates
- **Rejected** - Overkill for JSON generation, less type-safe

---

#### 4.8.4 Why Pure Logic Blocks?

**Decision:** Make all content blocks pure functions

**Rationale:**
- **Testability** - Easy to unit test
- **Predictability** - Same input always produces same output
- **Composability** - Can be combined without side effects
- **Parallelization** - Could be parallelized in future

---

#### 4.8.5 Why State in Orchestrator?

**Decision:** Centralize state management in OrchestratorAgent

**Rationale:**
- **Transparency** - State transitions are explicit
- **Debugging** - Easy to inspect state at any point
- **Error Recovery** - Can retry from any step
- **No Hidden Dependencies** - Agents don't share state

---

### 4.9 Extensibility Points

The system is designed for easy extension:

1. **New Agents**
   - Extend `BaseAgent`
   - Register with orchestrator
   - Example: SEO optimization agent

2. **New Templates**
   - Define in `TemplateEngine`
   - Add generation logic to `TemplateAgent`
   - Example: Blog post template

3. **New Content Blocks**
   - Add to `ContentLogicBlocks`
   - Use in template generation
   - Example: Social media text block

4. **New Question Categories**
   - Add to `QuestionGeneratorAgent.QUESTION_TEMPLATES`
   - Automatically incorporated

5. **New Output Formats**
   - Currently JSON, could add XML, YAML, HTML
   - Modify save logic in orchestrator

---

### 4.10 Quality Assurance

**Validation Points:**
1. Input validation in DataParserAgent
2. Pydantic model validation at every step
3. Template rule validation
4. Output schema validation
5. File write verification

**Error Handling:**
- Each agent returns success/failure status
- Detailed error messages
- Fails fast on critical errors
- Logs all operations

**Logging:**
- Agent execution count
- Step-by-step progress
- Success/failure indicators
- Metadata tracking

---

## 5. Conclusion

This multi-agent system demonstrates production-grade engineering:

✅ **Clear Architecture** - Layered design with defined boundaries  
✅ **Agent Autonomy** - Each agent has single responsibility  
✅ **Reusable Components** - Logic blocks and templates are composable  
✅ **Type Safety** - Strong typing throughout with Pydantic  
✅ **Extensibility** - Easy to add new agents, templates, and blocks  
✅ **Machine-Readable Output** - Clean, validated JSON  
✅ **Maintainability** - Code is documented and structured  

The system is ready for production use and can easily be extended for additional content types, languages, or output formats.

---

**Document Version:** 1.0  
**Last Updated:** December 24, 2025  
**Author:** Y Subhash Srinivas Reddy  
**Assignment:** Kasparro Applied AI Engineer Challenge
