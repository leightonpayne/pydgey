/* eslint-disable @typescript-eslint/no-explicit-any */
export interface ParameterItem {
    name: string;
    label: string;
    type: "str" | "int" | "float" | "bool" | "select" | "file" | "dir" | "button" | "switch";
    def?: any;
    desc?: string;
    options?: string[];
}

export interface ParameterSchema {
    [category: string]: ParameterItem[];
}

export interface PipelineConfig {
    title?: string;
    subtitle?: string;
    category_styles?: Record<string, { bg: string; text: string }>;
}

export type StatusState = "idle" | "running" | "finished" | "error" | "aborted";

export interface LogBatchMsg {
    type: "log_batch";
    content?: string;
    status?: StatusState;
}

export interface RunFinishedMsg {
    type: "run_finished";
    logs?: string;
    status?: StatusState;
}

export type WidgetMessage = LogBatchMsg | RunFinishedMsg | { type: "custom"; [key: string]: any };

export interface Step {
    name: string;
    status: "pending" | "running" | "completed" | "failed";
    duration?: string;
}

export interface ProgressState {
    percent: number;
    current: string;
    steps: Step[];
}

export interface UIComponentProps {
    [key: string]: any;
    model?: any;
    children?: React.ReactNode;
}

export interface UIElement {
    type: string;
    props: Record<string, any>;
    children?: UIElement[];
    visibleWhen?: {
        field: string;
        operator: string;
        value: any;
    };
}
