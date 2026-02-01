---
icon: lucide/map
---
# The Whole Game

The Pydgey development process centres around four steps:

1. **Defining a Pipeline**: Create a class inheriting from `Pipeline` to manage configuration and execution.
2. **Configuring Layout**: Use the purely Pythonic API to describe your user interface.
3. **Implementing Logic**: Write the code that runs when the user clicks specific buttons.
4. **Launching**: Expose the finished tool in a notebook.

---

## The Architecture

```
📁 my_project
├── 📁 src
│   ├── 📄 __init__.py
│   └── 📄 my_pipeline.py   <-- Your Logic & Layout
└── 📄 launcher.ipynb       <-- The User's Entry Point
```

This structure keeps the notebook execution clean and repeatable. The "heavy lifting" happens in `src/`, which can be version-controlled, linted, and tested like any other software library.

---

## 1. Defining a Pipeline

In `src/my_pipeline.py`, you start by defining a class. By inheriting from `Pipeline`, your class automatically gains the ability to communicate with the frontend widget, handle state, and manage long-running processes.

```python
# src/my_pipeline.py
from pydgey import Pipeline, PipelineConfig, Layout, Field
import time

class MyPipeline(Pipeline):
    def __init__(self):
        # The configuration object defines static metadata about your tool.
        # - name: Internal ID for the pipeline.
        # - title/subtitle: Displayed prominently in the widget header.
        config = PipelineConfig(
            name="demo_pipeline",
            title="Demo Pipeline",
            subtitle="A simple Pydgey demonstration"
        )
        super().__init__(config)
```

---

## 2. Configuring Layout

Next, you need to tell Pydgey what inputs you need from the user. Instead of writing HTML or JavaScript, you define the layout declaratively in Python.

Implement the `define_layout` method to return a structure of Sections, Cards, and Fields.

```python
    def define_layout(self):
        """Define the UI structure."""
        return Layout.Page([
            # Organize fields into collapsible sections
            Layout.Section("Input parameters", [
          
                # A simple text input
                Field.Text("name", "Your Name", default="Explorer", description="Who are we greeting?"),
          
                # A numeric input with validation constraints
                Field.Int("iterations", "Count", default=3, min=1, max=10),
            ])
        ])
```

**Key Concept**: The `name` argument (e.g., `"iterations"`) is the key you will use to access this value later in your logic. Pydgey handles all the validation (checking `min`/`max`) for you before your code ever runs.

---

## 3. Implementing Logic

This is where the work happens. The `run` method is triggered when the user clicks the **Run Pipeline** button.

It receives two arguments:

* `params`: A dictionary containing all the validated values from your inputs.
* `logger`: A special logging object that streams output directly to the widget's log viewer.

```python
    def run(self, params, logger):
        """Execute the pipeline logic."""
        # 1. Unpack parameters using the keys defined in your layout
        name = params.get("name")
        count = params.get("iterations")
  
        logger.info(f"Hello, {name}!")
        logger.step("Starting process...")
  
        # 2. Perform your actual work
        # This runs in a background thread, so the UI stays responsive!
        for i in range(count):
            # Check if user requested a stop
            if self.is_stopped:
                return False

            logger.info(f"Processing item {i+1}/{count}...")
            time.sleep(0.5)  # Simulate expensive computation
      
        # 3. Report success
        logger.success("All done! 🎉")
        return True
```

---

## 4. Launching

Finally, you need to deliver this tool to your users. You do this via a standard Jupyter Notebook.

Because all the complexity is hidden in `src/`, the notebook itself is incredibly simple. This is ideal for Google Colab, where users might just want to "Run All" and get started.

```python
# launcher.ipynb

# 1. Install your package (if running in Colab)
%pip install pydgey

# 2. Import the machinery
from pydgey import create_launcher
from src.my_pipeline import MyPipeline

# 3. Launch the widget
# This renders the full interactive UI
create_launcher(MyPipeline())
```

### The User Experience

When the intended user opens the notebook:

1. **No Code Scares**: They don't see functions, imports, or logic. They see a clean interface.
2. **Safety Rails**: They can't enter invalid inputs (like negative counts) because your layout prevents it.
3. **Feedback**: When they run it, they see real-time logs and progress bars, so they know exactly what's happening.
