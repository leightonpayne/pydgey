import React from "react";
import { Registry } from "./registry";
import type { UIElement } from "../../types";

// Helper to check visibility condition
const checkVisibility = (rule: NonNullable<UIElement["visibleWhen"]>, values: Record<string, unknown>): boolean => {
    const { field, operator, value } = rule;
    const fieldValue = values?.[field];

    switch (operator) {
        case "==": return fieldValue == value;
        case "!=": return fieldValue != value;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        case ">": return (fieldValue as any) > value;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        case "<": return (fieldValue as any) < value;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        case ">=": return (fieldValue as any) >= value;
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        case "<=": return (fieldValue as any) <= value;
        case "in": return Array.isArray(value) ? value.includes(fieldValue) : false;
        case "not in": return Array.isArray(value) ? !value.includes(fieldValue) : true;
        default: return true;
    }
};

export const RecursiveRenderer: React.FC<{ node: UIElement; model: unknown; values: Record<string, unknown> }> = ({ node, model, values }) => {
    if (!node) return null;

    // Check visibility
    if (node.visibleWhen) {
        if (!checkVisibility(node.visibleWhen, values)) {
            return null;
        }
    }

    const Component = Registry[node.type];

    if (!Component) {
        console.warn(`Unknown component type: ${node.type}`);
        return <div className="p-4 border border-red-200 bg-red-50 text-red-600 rounded">Unknown component: {node.type}</div>;
    }

    return (
        <Component {...node.props} model={model}>
            {node.children?.map((child, i) => (
                <RecursiveRenderer key={i} node={child} model={model} values={values} />
            ))}
        </Component>
    );
};
