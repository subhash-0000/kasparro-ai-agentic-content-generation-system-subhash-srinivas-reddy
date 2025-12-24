"""
Template definitions for different page types.
Each template defines structure, fields, rules, and required content blocks.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class TemplateType(str, Enum):
    """Supported template types."""
    FAQ = "faq"
    PRODUCT_PAGE = "product_page"
    COMPARISON = "comparison"


class TemplateField(BaseModel):
    """Defines a single field in a template."""
    
    name: str = Field(..., description="Field name")
    field_type: str = Field(..., description="Data type (string, list, dict, etc.)")
    required: bool = Field(default=True, description="Whether field is mandatory")
    source_block: Optional[str] = Field(None, description="Content block that provides this field")
    default_value: Optional[Any] = Field(None, description="Default value if not provided")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "product_name",
                "field_type": "string",
                "required": True,
                "source_block": "product_info_block"
            }
        }


class TemplateRule(BaseModel):
    """Defines a transformation or validation rule."""
    
    rule_type: str = Field(..., description="Type of rule (transform, validate, format)")
    field: str = Field(..., description="Field to apply rule to")
    logic: str = Field(..., description="Rule logic description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Rule parameters")


class Template(BaseModel):
    """Complete template definition for a page type."""
    
    template_type: TemplateType = Field(..., description="Type of template")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="What this template generates")
    fields: List[TemplateField] = Field(..., description="All fields in the template")
    rules: List[TemplateRule] = Field(default_factory=list, description="Transformation rules")
    required_blocks: List[str] = Field(..., description="Content blocks needed for this template")
    output_schema: Dict[str, Any] = Field(..., description="Expected JSON output structure")
    
    class Config:
        schema_extra = {
            "example": {
                "template_type": "faq",
                "name": "FAQ Page Template",
                "description": "Generates FAQ page with Q&A pairs",
                "fields": [
                    {"name": "title", "field_type": "string", "required": True},
                    {"name": "questions", "field_type": "list", "required": True}
                ],
                "required_blocks": ["question_generator_block", "answer_generator_block"],
                "output_schema": {"title": "str", "faqs": "list[dict]"}
            }
        }
