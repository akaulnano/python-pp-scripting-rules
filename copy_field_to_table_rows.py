def copy_invoice_date_to_line_items(document):
    """
    Copy the invoice_date field value to the line_item_start_date column 
    for all rows in the table.
    
    Args:
        document: The document object containing boxes
        
    Returns:
        The modified document object
    """
    try:
        # Extract invoice_date field value from document
        invoice_date = get_field_value(document, "invoice_date")
        
        if not invoice_date:
            print(f"Warning: invoice_date field not found in document")
            return document
        
        # Find or create the table
        table = find_or_create_table(document)
        
        # Group cells by row to identify all row indices
        rows = group_cells_by_row(table)
        
        # Add the invoice_date to each row's line_item_start_date column
        for row_idx in rows.keys():
            # Skip row 0 if it's a header row
            if row_idx > 0:
                set_cell_value(document, row_idx, "line_item_start_date", invoice_date)
        
        return document
    
    except Exception as e:
        print(f"Error copying invoice date to line items: {e}")
        return document

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
    
    # Add the cell to the table
    if "cells" not in table:
        table["cells"] = []
    
    table["cells"].append(new_cell)
    return True

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

def handler(input_data):
    """
    Process each document in the input data.
    
    Args:
        input_data: List of document objects
        
    Returns:
        The processed list of document objects
    """
    for document in input_data:
        copy_invoice_date_to_line_items(document)
    
    return input_data 
