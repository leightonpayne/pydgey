import { createRender } from "@anywidget/react";
import React from "react";
import { PipelineWidget } from "./components/PipelineWidget";
import "./index.css";

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean, error: Error | null }> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 20, border: '2px solid red', color: 'red', background: '#fff0f0' }}>
          <h3>Widget Crushed 💥</h3>
          <pre>{this.state.error?.toString()}</pre>
          <pre>{this.state.error?.stack}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

export const render = createRender(() => {
  // const { model } = props;
  
  return (
    <div className="flex justify-center w-full bg-transparent p-4">
      <ErrorBoundary>
        <PipelineWidget />
      </ErrorBoundary>
    </div>
  );
});
