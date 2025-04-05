# Project Rules for Nanonets Document Processing Scripts

## Project Overview
- **Purpose**: Process and manipulate structured document data from Nanonets API
- **Primary Use Case**: Extract, transform, and enrich document data
- **Core Functionality**: Table manipulation, field extraction, data mapping, and document enrichment

## Input/Output Format

### Input Format
- Input will be a JSON array of document objects
- Each document contains metadata, predicted boxes, and table structures
- Document objects have a standard structure including:
  - `predicted_boxes`: Contains fields and tables detected in the document
  - `moderated_boxes`: Contains manually verified data (may be null)
  - `file_url`: URL to access the original document
  - Metadata fields like `id`, `page`, `size`, etc.

#### Example Input Format

```json
[
  {
    "model_id": "8a939f21-7ee3-49e0-8d76-2c08e60be226",
    "day_since_epoch": 20182,
    "is_moderated": false,
    "hour_of_day": 13,
    "id": "9966f977-1155-11f0-b589-029316520b2b",
    "url": "https://images.nanonets.com/tr:rt-0,true/uploadedfiles/8a939f21-7ee3-49e0-8d76-2c08e60be226/PredictionImages/1184000a-5406-4419-957a-787ae30167fe-1.jpeg?ik-s=15ea0462dc591cd505c31e53d827542aee267863&ik-t=1743811610",
    "predicted_boxes": [
      {
        "id": "12884f06-6fca-44f6-906c-ab06142790ae",
        "label": "doc_type",
        "xmin": 303,
        "ymin": 645,
        "xmax": 926,
        "ymax": 689,
        "score": 0.78,
        "ocr_text": "Patient Referral Form",
        "status": "correctly_predicted",
        "type": "field",
        "validation_status": "success",
        "page": 0,
        "label_id": "5133f8f1-757e-460e-b367-bd88daa0cfb6",
        "lookup_edited": false,
        "lookup_parent_box_ids": null
      },
      {
        "id": "effbaf90-118f-11f0-a878-3d31c189dec5",
        "label": "table",
        "xmin": 245,
        "ymin": 1701,
        "xmax": 623,
        "ymax": 1789,
        "score": 0,
        "ocr_text": "table",
        "status": "correctly_predicted",
        "type": "table",
        "cells": [
          {
            "id": "f80a3760-118f-11f0-a878-3d31c189dec5",
            "row": 1,
            "col": 1,
            "row_span": 1,
            "col_span": 1,
            "label": "ICD",
            "xmin": 303,
            "ymin": 1718,
            "xmax": 603,
            "ymax": 1757,
            "score": 0,
            "text": "R30.0 , N39.41",
            "row_label": "",
            "verification_status": "correctly_predicted",
            "status": "success",
            "failed_validation": "",
            "label_id": "",
            "lookup_edited": false
          }
        ],
        "grid_cells": [
          {
            "id": "f8772a00-118f-11f0-a878-3d31c189dec5",
            "row": 1,
            "col": 1,
            "row_span": 1,
            "col_span": 1,
            "label": "",
            "xmin": 245,
            "ymin": 1701,
            "xmax": 623,
            "ymax": 1789,
            "score": 0,
            "text": "",
            "row_label": "",
            "verification_status": "",
            "status": "",
            "failed_validation": "",
            "label_id": "",
            "lookup_edited": false
          }
        ],
        "page": 0,
        "label_id": "",
        "lookup_edited": false,
        "lookup_parent_box_ids": null
      }
    ],
    "moderated_boxes": null,
    "size": {
      "width": 2550,
      "height": 3300
    },
    "page": 0,
    "request_file_id": "c673573d-abce-47b8-beae-c138f61b40f2",
    "original_file_name": "John Anderson (2).pdf",
    "file_url": "https://nanonets.s3.us-west-2.amazonaws.com/uploadedfiles/8a939f21-7ee3-49e0-8d76-2c08e60be226/RawPredictions/c673573d-abce-47b8-beae-c138f61b40f2.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA5F4WPNNTLX3QHN4W%2F20250404%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20250404T200650Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&response-cache-control=no-cache&X-Amz-Signature=9449729244a902475c891d7a2c2f9f37c069a1ba5e457a394c41ad2ff4ea07b8"
  }
]
```

Key components in this structure:
1. Array of document objects
2. Document metadata (`model_id`, `id`, `page`, etc.)
3. `predicted_boxes` array containing:
   - Field objects (`type: "field"`)
   - Table objects (`type: "table"`)
4. Table objects contain:
   - `cells` array with individual cell data
   - `grid_cells` array with table structure information
5. Document identifiers (`file_url`, `original_file_name`)


### Output Format
- Output must maintain the same structure as the input
- Modified/enriched data should be added to the existing structure
- The function must return the entire input array with modifications

## Core Function Patterns

### Field Operations

#### Getting Field Values
Use this pattern to extract field values from documents:

```python
def get_field_value(document, field_label):
    """
    Extract a field value from a document.
    
    Args:
        document: The document object containing boxes
        field_label: The label of the field to extract
        
    Returns:
        String value of the field or empty string if not found
    """
    boxes = document.get("moderated_boxes", []) if document.get("moderated_boxes") else document.get("predicted_boxes", [])
    
    for box in boxes:
        if box.get("type") == "field" and box.get("label") == field_label:
            return box.get("ocr_text", "")
    
    return ""
```

### Table Operations

#### Finding or Creating Tables
Use this pattern to find existing tables or create new ones:

```python
def find_or_create_table(document):
    """
    Find an existing table or create a new one if none exists.
    
    Args:
        document: The document object containing boxes
        
    Returns:
        Table object
    """
    boxes = document.get("moderated_boxes", []) if document.get("moderated_boxes") else document.get("predicted_boxes", [])
    
    # First try to find an existing table
    for box in boxes:
        if box.get("type") == "table":
            return box
    
    # If no table exists, create a new one
    import time
    new_table = {
        "id": f"generated-table-{time.time()}",
        "label": "table",
        "xmin": 0,
        "ymin": 0,
        "xmax": 0,
        "ymax": 0,
        "score": 1.0,
        "ocr_text": "table",
        "status": "correctly_predicted",
        "type": "table",
        "cells": []
    }
    
    # Add the new table to the document
    if document.get("moderated_boxes"):
        document["moderated_boxes"].append(new_table)
    else:
        document["predicted_boxes"].append(new_table)
    
    return new_table
```

#### Setting Cell Values
Use this pattern to set values in table cells:

```python
def set_cell_value(document, row_idx, label, value):
    """
    Set the value of a cell with the given label in the specified row.
    If the cell doesn't exist, add it to the table using proper format.
    
    Args:
        document: The document object containing boxes
        row_idx: Row index
        label: Column label
        value: Cell value
        
    Returns:
        True if operation was successful
    """
    # Find or create the table
    table = find_or_create_table(document)
    
    # Try to find and update an existing cell
    for cell in table.get("cells", []):
        if cell.get("row") == row_idx and cell.get("label") == label:
            cell["text"] = value
            return True
    
    # If we get here, we need to add a new cell
    # Find the maximum column number in this row
    max_col = 0
    for cell in table.get("cells", []):
        if cell.get("row") == row_idx:
            max_col = max(max_col, cell.get("col", 0))
    
    # Create a new cell in the next column
    import time
    new_cell = {
        "id": f"generated-cell-{label}-{row_idx}-{time.time()}",
        "row": row_idx,
        "col": max_col + 1,
        "row_span": 0,
        "col_span": 0,
        "label": label,
        "xmin": 0,
        "ymin": 0,
        "xmax": 0,
        "ymax": 0,
        "score": 1.0,
        "text": value,
        "row_label": "",
        "verification_status": "correctly_predicted",
        "status": "",
        "failed_validation": "",
        "label_id": "",
        "lookup_edited": False
    }
    
    # Add the cell to both moderated and predicted boxes if they exist
    if document.get("moderated_boxes"):
        document["moderated_boxes"].append(new_cell)
    else:
        document["predicted_boxes"].append(new_cell)
    
    # Add the cell to the table
    if "cells" not in table:
        table["cells"] = []
    
    table["cells"].append(new_cell)
    return True
```

#### Getting Cell Values
Use this pattern to extract values from table cells:

```python
def get_cell_value(table, row_idx, label):
    """
    Get the value of a cell with the given label from the specified row.
    
    Args:
        table: The table object containing cells
        row_idx: Row index
        label: Column label
        
    Returns:
        String value of the cell or empty string if not found
    """
    for cell in table.get("cells", []):
        if cell.get("row") == row_idx and cell.get("label") == label:
            return cell.get("text", "")
    
    return ""
```

#### Group Cells by Row
Use this pattern to group cells by row for easier processing:

```python
def group_cells_by_row(table):
    """
    Group table cells by row.
    
    Args:
        table: The table object containing cells
        
    Returns:
        Dictionary with row indices as keys and lists of cells as values
    """
    rows = {}
    if not table or "cells" not in table:
        return rows
    
    for cell in table.get("cells", []):
        row_idx = cell.get("row", 0)
        if row_idx not in rows:
            rows[row_idx] = []
        rows[row_idx].append(cell)
    
    return rows
```

### Debugging with Webhook

Use webhook for detailed debugging:

```python
def webhook(data):
    """Send debug data to webhook service."""
    try:
        import requests
        import json
        
        if isinstance(data, str):
            data = {"message": data}
        
        requests.post("https://webhook.site/your-webhook-id", 
                     json=data, 
                     headers={"Content-Type": "application/json"},
                     timeout=3)
    except Exception as e:
        print(f"Webhook error: {e}")
        pass  # Silently fail if webhook is unavailable
```

### Handler Function Pattern

```python
def handler(input_data):
    """
    Process each document in the input data.
    
    Args:
        input_data: List of document objects
        
    Returns:
        The processed list of document objects
    """
    webhook({"event": "handler_start", "document_count": len(input_data)})
    
    for i, document in enumerate(input_data):
        webhook({"event": "processing_document", "document_index": i, "document_id": document.get("id", "unknown")})
        # Process document
        process_document(document)
    
    webhook({"event": "handler_complete", "success": True})
    return input_data
```

## Code Organization

### File Structure
- Separate utility functions into modules in the `utils/` directory
- Main processing logic should be in the root directory
- Configuration should be in a separate module (e.g., `utils/envconfig.py`)

### Module Organization
- Import order: standard library → third-party → local modules
- Group functions by purpose:
  - Document/table extraction functions
  - Data transformation functions
  - External service integrations
  - Utility helpers
- Place handler/main functions at the bottom of the file

## Data Processing Patterns

### Document Processing
- Always handle both `predicted_boxes` and `moderated_boxes` (if present)
- Check for existing data before adding new fields
- Use helper functions to extract specific information from documents
- Create reusable patterns for common document operations

### Example: Update Table Values from Fields

```python
def update_table_values_from_field(document, field_label, target_cell_label):
    """
    Update table cells with values from a document field.
    
    Args:
        document: The document object containing boxes
        field_label: The label of the field to extract value from
        target_cell_label: The label of cells to update
        
    Returns:
        The modified document object
    """
    try:
        # Extract field value from document
        field_value = get_field_value(document, field_label)
        
        if not field_value:
            print(f"Warning: {field_label} not found in document")
            return document
        
        # Find or create the table
        table = find_or_create_table(document)
        
        # Find cells with matching label in any row
        updated_cells = 0
        for cell in table.get("cells", []):
            if cell.get("label") == target_cell_label:
                # Update the cell text with field value
                cell["text"] = field_value
                updated_cells += 1
        
        # If no matching cells were found, we'll add them to each data row
        if updated_cells == 0:
            # Identify all row indices in the table (excluding 0 in case it's a header)
            row_indices = set()
            for cell in table.get("cells", []):
                row_idx = cell.get("row", 0)
                if row_idx > 0:  # Only include data rows
                    row_indices.add(row_idx)
            
            # Add cells to each row
            for row_idx in row_indices:
                set_cell_value(document, row_idx, target_cell_label, field_value)
        
        return document
    
    except Exception as e:
        print(f"Error updating table values from field: {e}")
        return document
```

## External Integrations

### CSV Processing
- Use pandas for CSV operations when possible
- Handle CSV parsing errors gracefully
- Include code to inspect data structure before processing
- Implement fallback data extraction when CSV parsing fails

### Spreadsheet Integration
- Use standardized patterns for Google Sheets access
- Extract spreadsheet IDs using regex
- Convert spreadsheet data to structured format (dict/DataFrame)
- Cache spreadsheet data when appropriate

```python
def get_spreadsheet_data(sheet_url):
    """Extract data from a Google Spreadsheet."""
    pattern = r"/d/(.*?)/"
    sheet_id = re.search(pattern, sheet_url).group(1)
    sheet_name = "Sheet1"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    try:
        df = pd.read_csv(url, keep_default_na=False)
        return df.to_dict(orient="records")
    except Exception as e:
        log_error(f"Error fetching spreadsheet data: {e}")
        return []
```

### File Processing
- Use consistent file download and processing patterns
- Handle file access errors gracefully
- Process files in a temporary directory
- Clean up temporary files after processing

## Naming Conventions

### Variables and Functions
- Use snake_case for variable and function names
- Prefix functions with verbs indicating action: 
  - `get_` for data retrieval
  - `set_` for data modification
  - `process_` for data transformation
  - `extract_` for data extraction
  - `find_` for lookups
- Constants in UPPER_SNAKE_CASE (e.g., `SERVICE_SHEET_URL`)

### Table and Field Names
- Use descriptive names for table and field labels
- Use consistent naming patterns for generated fields:
  - `export_` prefix for fields added for export
  - `raw_` prefix for unprocessed data
  - `calculated_` prefix for derived values

## Error Handling

### Robust Processing
- Use try/except blocks for error-prone operations
- Log errors with detailed information
- Always include appropriate fallback behavior
- Return meaningful default values when operations fail

```python
def process_with_fallback(primary_func, fallback_func, data, default=None):
    """Process data with a fallback if the primary function fails."""
    try:
        result = primary_func(data)
        if result is not None:
            return result
    except Exception as e:
        log_error(f"Primary processing failed: {e}")
    
    try:
        return fallback_func(data)
    except Exception as e:
        log_error(f"Fallback processing failed: {e}")
        return default
```

### Data Validation
- Validate document structure before processing
- Check for required fields before accessing them
- Use default values for missing data
- Validate processed data before returning

## Debugging and Logging
- Use webhook for debugging complex operations
- Include structured data in debug messages
- Log progress at key processing points
- Include context and identifiers in log messages

## Performance Considerations
- Process documents in batches when possible
- Minimize redundant computations
- Cache frequently accessed data
- Optimize file and network operations

## Testing Standards
- Test handler function with representative input data
- Create unit tests for utility functions
- Use mock data for external services
- Test both success and failure paths

## Security Practices
- Sanitize data before sending to external services
- Use environment variables for sensitive configuration
- Validate inputs before processing
- Avoid hardcoding credentials in the code

## Document-Specific Patterns

### Address Processing
- Use consistent address parsing libraries (usaddress)
- Handle address abbreviations consistently
- Implement fuzzy matching for address comparison
- Extract zip codes and states reliably

### Date/Time Processing
- Handle timezone conversion consistently
- Account for DST when processing timestamps
- Use consistent date/time formats
- Validate date/time values before processing

## Fallback Logic
- Always implement fallback processing paths
- If CSV processing fails, fall back to table extraction
- If API calls fail, use cached or default data
- Document fallback behaviors for maintenance
