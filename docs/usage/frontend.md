---
icon: lucide/monitor
---
# Frontend Architecture

While Pydgey provides a pure Python API for defining pipelines, its interactive user interface is powered by a modern, high-performance web stack.

This architecture ensures that the widget looks professional, responds instantly, and works reliably across different environments (Jupyter, Colab, VS Code).

## Technology Stack

The frontend is built as a Single Page Application (SPA) embedded within the Python package.

### React & TypeScript

- **React**: We use the latest React features for efficient rendering and state management.
- **TypeScript**: The entire frontend codebase is strongly typed, ensuring reliability and making it easier for contributors to refactor components without breaking functionality.

### Styling & Design System

- **Shadcn UI**: Pydgey uses [Shadcn UI](https://ui.shadcn.com/) for its component library. These components are accessible, customizable, and provide a premium "app-like" feel.
- **Tailwind CSS**: A utility-first CSS framework that allows for rapid styling and consistent theming.
- **Lucide Icons**: A clean, consistent icon set used throughout the interface.

### Communication Bridge

- **AnyWidget**: Pydgey relies on [anywidget](https://anywidget.dev/) to bridge the gap between Python and JavaScript. This allows bi-directional communication:
  - **Python → JS**: Pushing log updates, status changes, and progress metrics.
  - **JS → Python**: Sending form submissions and control signals (Run/Abort).

## Component Structure

The frontend code (`frontend/src`) follows a component-based architecture:

- **`widget.tsx`**: The entry point that initializes the React application.
- **`components/PipelineWidget.tsx`**: The main container that manages global state (logs, connection status) and orchestrates the view.
- **`components/layout/recursive.tsx`**: Contains `RecursiveRenderer`, a dynamic component that traverses the layout tree defined in Python and renders the corresponding React components.
- **`components/Parameters.tsx`**: Handles the rendering of form fields for user input.
- **`components/ui/`**: Reusable primitive components (Buttons, Cards, Badges) derived from Shadcn UI.

## Development Workflow

Pydgey's frontend is developed with standard modern web tools.

### Building

The widget relies on a compiled JavaScript bundle structure. To build the frontend:

```bash
pixi run build
```

This uses Vite to bundle the React application into a single file that AnyWidget can load.

### Code Quality

We enforce code quality and styling using ESLint:

```bash
pixi run lint-ui
```
