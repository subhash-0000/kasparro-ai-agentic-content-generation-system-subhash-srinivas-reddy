"""
Template Engine - Custom template system for generating structured pages.
Applies templates with fields, rules, and content blocks.
"""

from typing import Dict, Any, List
from src.models.templates import Template, TemplateType, TemplateField, TemplateRule
from src.models.product import Product
from src.models.outputs import FAQPage, ProductPage, ComparisonPage


class TemplateEngine:
    """
    Custom template engine that applies structured templates to generate pages.
    """
    
    def __init__(self):
        """Initialize template engine with predefined templates."""
        self.templates: Dict[str, Template] = {}
        self._register_default_templates()
    
    def _register_default_templates(self):
        """Register default templates for FAQ, Product, and Comparison pages."""
        
        # FAQ Template
        faq_template = Template(
            template_type=TemplateType.FAQ,
            name="FAQ Page Template",
            description="Generates structured FAQ page with categorized Q&A pairs",
            fields=[
                TemplateField(name="page_type", field_type="string", required=True, default_value="faq"),
                TemplateField(name="product_name", field_type="string", required=True, source_block="product_info"),
                TemplateField(name="total_questions", field_type="integer", required=True, source_block="question_count"),
                TemplateField(name="categories", field_type="list", required=True, source_block="question_categories"),
                TemplateField(name="faqs", field_type="list", required=True, source_block="faq_items"),
            ],
            rules=[
                TemplateRule(rule_type="validate", field="faqs", logic="minimum 5 items", parameters={"min_count": 5}),
                TemplateRule(rule_type="format", field="categories", logic="unique and sorted", parameters={}),
            ],
            required_blocks=["question_generator", "answer_generator"],
            output_schema={
                "page_type": "str",
                "product_name": "str",
                "total_questions": "int",
                "categories": "List[str]",
                "faqs": "List[FAQItem]"
            }
        )
        
        # Product Page Template
        product_template = Template(
            template_type=TemplateType.PRODUCT_PAGE,
            name="Product Description Page Template",
            description="Generates comprehensive product description page",
            fields=[
                TemplateField(name="page_type", field_type="string", required=True, default_value="product_page"),
                TemplateField(name="product_name", field_type="string", required=True, source_block="product_info"),
                TemplateField(name="tagline", field_type="string", required=True, source_block="product_summary"),
                TemplateField(name="description", field_type="string", required=True, source_block="product_summary"),
                TemplateField(name="key_features", field_type="list", required=True, source_block="product_summary"),
                TemplateField(name="ingredients", field_type="dict", required=True, source_block="ingredients_detail"),
                TemplateField(name="usage_guide", field_type="dict", required=True, source_block="usage_info"),
                TemplateField(name="suitable_for", field_type="list", required=True, source_block="product_info"),
                TemplateField(name="benefits", field_type="list", required=True, source_block="benefits_detail"),
                TemplateField(name="safety_information", field_type="dict", required=True, source_block="safety_info"),
                TemplateField(name="pricing", field_type="dict", required=True, source_block="pricing_info"),
            ],
            rules=[
                TemplateRule(rule_type="validate", field="key_features", logic="minimum 3 items", parameters={"min_count": 3}),
            ],
            required_blocks=["product_summary", "benefits", "usage", "safety", "pricing"],
            output_schema={
                "page_type": "str",
                "product_name": "str",
                "tagline": "str",
                "description": "str",
                "key_features": "List[str]",
                "ingredients": "Dict[str, str]",
                "usage_guide": "Dict[str, Any]",
                "benefits": "List[str]",
                "safety_information": "Dict[str, Any]",
                "pricing": "Dict[str, str]"
            }
        )
        
        # Comparison Template
        comparison_template = Template(
            template_type=TemplateType.COMPARISON,
            name="Product Comparison Page Template",
            description="Generates side-by-side product comparison page",
            fields=[
                TemplateField(name="page_type", field_type="string", required=True, default_value="comparison"),
                TemplateField(name="product_a", field_type="dict", required=True, source_block="product_a_info"),
                TemplateField(name="product_b", field_type="dict", required=True, source_block="product_b_info"),
                TemplateField(name="comparison_points", field_type="list", required=True, source_block="comparison_logic"),
                TemplateField(name="summary", field_type="dict", required=True, source_block="comparison_summary"),
                TemplateField(name="recommendation", field_type="string", required=True, source_block="recommendation"),
            ],
            rules=[
                TemplateRule(rule_type="validate", field="comparison_points", logic="minimum 5 comparison points", parameters={"min_count": 5}),
            ],
            required_blocks=["product_comparison", "ingredient_comparison"],
            output_schema={
                "page_type": "str",
                "product_a": "Dict[str, Any]",
                "product_b": "Dict[str, Any]",
                "comparison_points": "List[ComparisonItem]",
                "summary": "Dict[str, Any]",
                "recommendation": "str"
            }
        )
        
        self.templates["faq"] = faq_template
        self.templates["product_page"] = product_template
        self.templates["comparison"] = comparison_template
    
    def get_template(self, template_type: str) -> Template:
        """
        Retrieve a template by type.
        
        Args:
            template_type: Type of template to retrieve
            
        Returns:
            Template instance
        """
        if template_type not in self.templates:
            raise ValueError(f"Template type '{template_type}' not found")
        return self.templates[template_type]
    
    def validate_data(self, template: Template, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate data against template rules.
        
        Args:
            template: Template to validate against
            data: Data to validate
            
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        # Check required fields
        for field in template.fields:
            if field.required and field.name not in data:
                errors.append(f"Required field '{field.name}' missing")
        
        # Apply validation rules
        for rule in template.rules:
            if rule.rule_type == "validate" and rule.field in data:
                if "min_count" in rule.parameters:
                    if isinstance(data[rule.field], list):
                        if len(data[rule.field]) < rule.parameters["min_count"]:
                            errors.append(f"Field '{rule.field}' must have at least {rule.parameters['min_count']} items")
        
        return len(errors) == 0, errors
    
    def apply_template(self, template_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply template to data and generate structured output.
        
        Args:
            template_type: Type of template to apply
            data: Data to populate template with
            
        Returns:
            Structured output according to template
        """
        template = self.get_template(template_type)
        
        # Validate data
        is_valid, errors = self.validate_data(template, data)
        if not is_valid:
            raise ValueError(f"Template validation failed: {', '.join(errors)}")
        
        # Build output according to template structure
        output = {}
        for field in template.fields:
            if field.name in data:
                output[field.name] = data[field.name]
            elif field.default_value is not None:
                output[field.name] = field.default_value
        
        return output
