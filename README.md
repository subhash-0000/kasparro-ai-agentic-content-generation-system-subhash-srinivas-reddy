# Multi-Agent Content Generation System

A production-grade multi-agent system for automated content generation, built with clear agent boundaries, reusable logic blocks, and structured output pipelines.

## 🎯 Overview

This system demonstrates a modular agentic architecture that transforms product data into structured, machine-readable content pages through orchestrated agent workflows.

## 🏗️ System Architecture

### Agent Design

The system follows a **multi-agent architecture** with clear responsibilities:

1. **DataParserAgent** - Parses and validates raw product data into internal models
2. **QuestionGeneratorAgent** - Generates 15+ categorized user questions automatically
3. **ComparisonAgent** - Creates fictional competing products and performs detailed comparisons
4. **TemplateAgent** - Applies templates to generate structured page content
5. **OrchestratorAgent** - Coordinates the entire workflow and manages state

### Workflow

```
Raw Data → DataParser → QuestionGenerator → ComparisonAgent → TemplateAgent → JSON Output
                ↓              ↓                    ↓
           Product Model   QuestionSet      Comparison Data
```

## 📦 Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd kasparro-ai-agentic-content-generation-system-subhash-reddy

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Usage

### Run the System

```bash
python main.py
```

This will:
1. Parse the product data
2. Generate 15+ categorized questions
3. Create a fictional competing product
4. Generate three structured pages:
   - `output/faq.json` - FAQ page with Q&A pairs
   - `output/product_page.json` - Comprehensive product description
   - `output/comparison_page.json` - Side-by-side product comparison

### Example Output

After execution, you'll find three JSON files in the `output/` directory:

- **faq.json** - 5+ FAQ items with categories
- **product_page.json** - Complete product information
- **comparison_page.json** - Detailed product comparison

## 🧩 Core Components

### 1. Data Models (`src/models/`)

- **product.py** - Product, CategorizedQuestion, QuestionSet
- **templates.py** - Template, TemplateField, TemplateRule
- **outputs.py** - FAQPage, ProductPage, ComparisonPage

### 2. Agents (`src/agents/`)

Each agent has:
- Single responsibility
- Defined input/output contracts
- Validation logic
- Execution tracking

### 3. Content Logic Blocks (`src/logic_blocks/`)

Reusable transformation functions:
- `generate_benefits_block` - Transform benefits into detailed descriptions
- `extract_usage_block` - Structure usage instructions
- `compare_ingredients_block` - Compare product ingredients
- `safety_info_block` - Generate safety information
- `pricing_info_block` - Structure pricing data
- `product_summary_block` - Create product summaries
- `answer_generator_block` - Generate Q&A answers

### 4. Template Engine (`src/template_engine/`)

Custom template system with:
- Field definitions
- Validation rules
- Output schema enforcement
- Template application logic

## 📊 Generated Content

### FAQ Page (faq.json)

```json
{
  "page_type": "faq",
  "product_name": "GlowBoost Vitamin C Serum",
  "total_questions": 5,
  "categories": ["Informational", "Usage", "Safety", "Skin Type", "Purchase"],
  "faqs": [
    {
      "question": "What is GlowBoost Vitamin C Serum?",
      "answer": "...",
      "category": "Informational"
    }
  ]
}
```

### Product Page (product_page.json)

Complete product information including:
- Tagline and description
- Key features
- Ingredient details
- Usage guide
- Benefits
- Safety information
- Pricing

### Comparison Page (comparison_page.json)

Side-by-side comparison including:
- Product A and B details
- 7+ comparison points
- Summary with strengths
- Recommendation

## 🎨 Design Principles

1. **Single Responsibility** - Each agent has one clear purpose
2. **Defined I/O Contracts** - Standard AgentInput/AgentOutput wrappers
3. **No Hidden State** - Explicit state management in orchestrator
4. **Reusable Logic** - Content blocks are pure functions
5. **Template-Driven** - Structured page generation with templates
6. **Validation at Boundaries** - Input validation before processing

## 📋 Project Structure

```
kasparro/
├── main.py                          # Entry point
├── requirements.txt                 # Dependencies
├── output/                          # Generated JSON files
│   ├── faq.json
│   ├── product_page.json
│   └── comparison_page.json
├── src/
│   ├── models/                      # Data models
│   │   ├── product.py
│   │   ├── templates.py
│   │   └── outputs.py
│   ├── agents/                      # Agent implementations
│   │   ├── base_agent.py
│   │   ├── data_parser_agent.py
│   │   ├── question_generator_agent.py
│   │   ├── comparison_agent.py
│   │   ├── template_agent.py
│   │   └── orchestrator_agent.py
│   ├── logic_blocks/                # Reusable content logic
│   │   └── content_blocks.py
│   └── template_engine/             # Template system
│       └── engine.py
└── docs/
    └── projectdocumentation.md      # System design documentation
```

## 🔧 Extensibility

### Adding New Agents

1. Extend `BaseAgent`
2. Implement `execute()` method
3. Define input validation
4. Register with orchestrator

### Adding New Templates

1. Define template in `TemplateEngine`
2. Specify fields and rules
3. Implement generation logic in `TemplateAgent`

### Adding New Content Blocks

1. Add static method to `ContentLogicBlocks`
2. Keep it pure (no side effects)
3. Document input/output clearly

## 📖 Documentation

For detailed system design, architecture diagrams, and implementation details, see [docs/projectdocumentation.md](docs/projectdocumentation.md)

## 🧪 Testing

The system validates:
- Input data integrity
- Agent output correctness
- Template compliance
- JSON output structure

## 🤝 Contributing

This is an assignment submission. Not open for contributions.

## 📄 License

This project is created for the Kasparro hiring process.

---

**Built with clarity, modularity, and production-grade engineering practices.**
