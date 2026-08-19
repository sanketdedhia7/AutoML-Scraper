from typing import Dict, Any

class PromptTemplates:
    @staticmethod
    def empty_output(validator_result: Dict[str, Any]) -> str:
        """Generate prompt for empty output"""
        return (
            "The scraper returned empty results. It used to extract articles with "
            "title, author, date, and content. Please update the extraction logic "
            "to find these fields in the current page layout."
        )
    
    @staticmethod
    def missing_field(field_name: str, expected_location: str) -> str:
        """Generate prompt for missing field"""
        return (
            f"The '{field_name}' field is missing from the output. It should be "
            f"extracted from {expected_location}. Please update the extraction logic."
        )
    
    @staticmethod
    def layout_changed(old_structure: str, new_structure: str) -> str:
        """Generate prompt for layout change"""
        return (
            f"The page layout changed. Old structure: {old_structure}. "
            f"New structure: {new_structure}. Please update the extraction logic "
            "to match the new layout while keeping the same output fields."
        )

    @staticmethod
    def select_prompt(validation_result: Dict[str, Any]) -> str:
        """Dynamically select and configure a prompt template based on validator errors"""
        errors = validation_result.get("errors", [])
        if not errors:
            return "No errors detected, but self-healing was requested."
        
        # Check for empty output
        if any("Empty output" in err for err in errors):
            return PromptTemplates.empty_output(validation_result)
            
        # Check for missing required fields
        missing_fields_err = [err for err in errors if "Missing required fields" in err]
        if missing_fields_err:
            err_str = missing_fields_err[0]
            try:
                import ast
                list_str = err_str.split(":", 1)[1].strip()
                fields = ast.literal_eval(list_str)
                if isinstance(fields, list) and fields:
                    prompts = [PromptTemplates.missing_field(f, "their expected element selectors") for f in fields]
                    return " ".join(prompts)
            except Exception:
                pass
            return PromptTemplates.missing_field("required", "the page body")
            
        # Check for high missing rate
        if any("High missing rate" in err for err in errors):
            return PromptTemplates.layout_changed("original selector mapping", "new page layout containing empty or incomplete rows")
            
        # Fallback
        return f"Scraper validation failed with error: {'; '.join(errors)}. Please adjust selectors."

