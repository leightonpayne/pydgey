---
icon: lucide/layout-template
---

# Building Layouts

Pydgey provides a "React-like" Python DSL (Domain Specific Language) for building your UI. You define a hierarchy of Python objects, and Pydgey renders them as native React components in the browser.

## The Layout Structure

The root of every layout is a `Layout.Page`. Inside, you can nest containers and fields.

```python
from pydgey import Layout, Field

def define_layout(self):
    return Layout.Page([
        Layout.Section("FastQ Processing", [
            Layout.Row([
                Field.Text("sample_id", "Sample ID"),
                Field.Int("threads", "Threads", default=4)
            ]),
            Field.File("reads", "Input Reads", accept=[".fastq", ".fq.gz"])
        ])
    ])
```

## Containers

Containers organize your fields visually.

| Component | Description |
| :--- | :--- |
| `Layout.Page` | The root container. Must be the outer-most element. |
| `Layout.Section` | A collapsible section with a title. Good for grouping large steps. |
| `Layout.Card` | A distinct card with a border and shadow. Good for visually grouping related inputs. |
| `Layout.Row` | Arranges its children horizontally. Useful for compact inputs (e.g., placing "Min" and "Max" side-by-side). |
| `Layout.Tabs` | A container for tabbed content. Must contain `Layout.Tab` children. |

### Tab Example

```python
Layout.Tabs([
    Layout.Tab("Basic", [
        Field.Text("name", "Name")
    ]),
    Layout.Tab("Advanced", [
        Field.Int("memory_limit", "Memory (GB)")
    ])
])
```

## Input Fields

Fields are where the user enters data. Each field requires a unique `name` (key) and a display `label`.

| Field | Description | Key Arguments |
| :--- | :--- | :--- |
| `Field.Text` | Single line text. | `default`, `placeholder` |
| `Field.TextArea` | Multi-line text. | `rows` |
| `Field.Int` | Integer number. | `min`, `max`, `default` |
| `Field.Float` | Float number. | `min`, `max`, `step` |
| `Field.Switch` | Boolean toggle. | `default` (True/False) |
| `Field.Select` | Dropdown menu. | `options` (List[str]) |
| `Field.MultiSelect` | Select multiple items. | `options` |
| `Field.File` | Server-side file picker. | `accept`, `multiple` |

## Conditional Visibility

You can make fields or entire sections appear/disappear based on the value of other fields using the `visible_when` argument.

The format is a tuple: `("target_field_name", "operator", value)`.

Supported operators: `"=="`, `"!="`, `">"`, `"<"`, `"in"`.

```python
Layout.Page([
    # 1. The Controller Field
    Field.Select("mode", "Mode", options=["Default", "Custom"]),
    
    # 2. The Conditional Field
    # Only visible if 'mode' is 'Custom'
    Field.Int("custom_val", "Custom Value", 
              visible_when=("mode", "==", "Custom"))
])
```

This logic is evaluated dynamically in the frontend, providing instant feedback without round-tripping to Python.
