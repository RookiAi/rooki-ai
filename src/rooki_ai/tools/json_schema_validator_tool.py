import json
from typing import Dict, Any, Union 
from crewai.tools import BaseTool
from pydantic import Field 
from jsonschema import validate, ValidationError as JSONSchemaValidationError

class JSONSchemaValidatorTool(BaseTool):
    """Tool for validating JSON data against a schema.
    
    This tool validates JSON data against a provided JSON schema to ensure it conforms
    to the expected structure and data types. It's useful for ensuring that outputs
    from LLMs or other sources match the expected format before they're used in 
    downstream processes.
    """
    
    name: str = "JSONSchemaValidatorTool"
    description: str = "Validates JSON data against a schema to ensure it conforms to expected structure"
    
    schema: Dict[str, Any] = Field(
        ...,
        description="The JSON schema to validate against"
    )
    
    def _run(self, data: Union[Dict[str, Any], str], verbose: bool = False) -> Dict[str, Any]:
        """
        Validate JSON data against the schema.
        
        Args:
            data: Either a dictionary object to validate, or a JSON string to parse and validate
            verbose: If True, return detailed validation information
            
        Returns:
            Dictionary containing validation result and details:
            {
                "valid": bool,
                "errors": list (only if validation fails),
                "validated_data": dict (only if validation succeeds and verbose=True)
            }
        """
        # Convert string to dict if needed
        if isinstance(data, str):
            try:
                data_dict = json.loads(data)
            except json.JSONDecodeError as e:
                return {
                    "valid": False,
                    "errors": [f"Invalid JSON: {str(e)}"]
                }
        else:
            data_dict = data
            
        # Validate against the schema
        try:
            validate(instance=data_dict, schema=self.schema)
            
            result = {"valid": True}
            if verbose:
                result["validated_data"] = data_dict
                
            return result
            
        except JSONSchemaValidationError as e:
            # Handle validation errors
            path = ".".join(str(p) for p in e.path) if e.path else "root"
            
            return {
                "valid": False,
                "errors": [
                    {
                        "path": path,
                        "message": e.message,
                        "schema_path": ".".join(str(p) for p in e.schema_path) if hasattr(e, 'schema_path') else None
                    }
                ]
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }
    
    async def _arun(self, data: Union[Dict[str, Any], str], verbose: bool = False) -> Dict[str, Any]:
        """Async version of _run"""
        return self._run(data, verbose)
