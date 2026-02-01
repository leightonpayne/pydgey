/* eslint-disable @typescript-eslint/no-explicit-any */
import React from "react";
import { useModelState } from "@anywidget/react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";

import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"

/**
 * Simple inline markdown parser for field descriptions.
 * Supports: **bold**, *italic*, `code`, [link](url)
 */
const FormattedText: React.FC<{ text: string; className?: string }> = ({ text, className }) => {
    const parseInlineMarkdown = (input: string): React.ReactNode[] => {
        const elements: React.ReactNode[] = [];
        // Regex for patterns: **bold**, *italic*, `code`, [link](url)
        const pattern = /(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|\[(.+?)\]\((.+?)\))/g;
        let lastIndex = 0;
        let match;
        let keyIndex = 0;

        while ((match = pattern.exec(input)) !== null) {
            // Add text before the match
            if (match.index > lastIndex) {
                elements.push(input.slice(lastIndex, match.index));
            }

            if (match[2]) {
                // **bold**
                elements.push(<strong key={keyIndex++} className="font-semibold">{match[2]}</strong>);
            } else if (match[3]) {
                // *italic*
                elements.push(<em key={keyIndex++}>{match[3]}</em>);
            } else if (match[4]) {
                // `code`
                elements.push(<code key={keyIndex++} className="px-1 py-0.5 rounded bg-slate-100 text-rose-600 font-mono text-[10px]">{match[4]}</code>);
            } else if (match[5] && match[6]) {
                // [link](url)
                elements.push(
                    <a key={keyIndex++} href={match[6]} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        {match[5]}
                    </a>
                );
            }
            lastIndex = pattern.lastIndex;
        }

        // Add remaining text
        if (lastIndex < input.length) {
            elements.push(input.slice(lastIndex));
        }

        return elements.length > 0 ? elements : [input];
    };

    return <span className={className}>{parseInlineMarkdown(text)}</span>;
};

interface FieldProps {
    type: string;
    name: string;
    label: string;
    description?: string;
    default?: any;
    options?: string[];
    multiselect?: boolean;
    placeholder?: string;
    rows?: number;
    accept?: string[];
    multiple?: boolean;
    min?: number;
    max?: number;
    step?: number;
    model: any;
}

export const FieldWrapper: React.FC<FieldProps> = ({ 
    type, name, label, description, default: def, options, placeholder, rows, accept, min, max, step, model 
}) => {
    // We access the global params_values store
    const [paramsValues, setParamsValues] = useModelState<Record<string, any>>("params_values");

    const value = paramsValues?.[name] ?? def;

    const handleChange = (val: any) => {
        setParamsValues({ ...paramsValues, [name]: val });
        model.save_changes();
    };

    const handleAction = () => {
        model.set("action_requested", name);
        model.save_changes();
    };

    // Render based on type
    let control = null;

    switch (type) {
        case "text":
        case "int":
        case "float":
            control = (
                <Input
                    id={name}
                    type={type === "text" ? "text" : "number"}
                    placeholder={placeholder || String(def ?? "")}
                    value={value ?? ""}
                    min={min}
                    max={max}
                    step={step ?? (type === "float" ? "any" : undefined)}
                    onChange={(e) => {
                        let v: any = e.target.value;
                        if (type === "int") v = parseInt(v) || 0;
                        if (type === "float") v = parseFloat(v) || 0.0;
                        handleChange(v);
                    }}
                    onBlur={() => {
                        let v = value;
                        if (type === "int" || type === "float") {
                            if (v === "" || v === null || v === undefined) return;
                            if (min !== undefined && v < min) v = min;
                            if (max !== undefined && v > max) v = max;
                            if (v !== value) handleChange(v);
                        }
                    }}
                    className="bg-white"
                />
            );
            break;

        case "textarea":
            control = (
                <Textarea
                    id={name}
                    placeholder={placeholder || String(def ?? "")}
                    value={value ?? ""}
                    onChange={(e) => handleChange(e.target.value)}
                    rows={rows || 4}
                    className="bg-white"
                />
            );
            break;

        case "switch":
        case "bool":
            return (
                 <div className="flex flex-row items-center justify-between gap-4 rounded-lg border p-3 shadow-sm bg-white mt-1">
                    <div className="space-y-0.5 min-w-0">
                        <Label htmlFor={name} className="text-sm font-medium">{label}</Label>
                        {description && <FormattedText text={description} className="text-[11px] text-slate-500" />}
                    </div>
                    <Switch
                        id={name}
                        checked={!!value}
                        onCheckedChange={handleChange}
                        className="flex-shrink-0"
                    />
                </div>
            );

        case "select":
            control = (
                <Select value={value} onValueChange={handleChange}>
                    <SelectTrigger className="w-full bg-white">
                        <SelectValue placeholder="Select..." />
                    </SelectTrigger>
                    <SelectContent>
                        {(options || []).map((opt) => (
                            <SelectItem key={opt} value={opt}>{opt}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            );
            break;

        case "multiselect": {
            const currentValues = Array.isArray(value) ? value : [];
            control = (
                <div className="flex flex-wrap gap-4 mt-1">
                    {(options || []).map((opt) => {
                        const isChecked = currentValues.includes(opt);
                        return (
                            <div key={opt} className="flex items-center space-x-2">
                                <Checkbox 
                                    id={`${name}-${opt}`} 
                                    checked={isChecked}
                                    onCheckedChange={(checked) => {
                                        if (checked) {
                                            handleChange([...currentValues, opt]);
                                        } else {
                                            handleChange(currentValues.filter(v => v !== opt));
                                        }
                                    }}
                                />
                                <Label htmlFor={`${name}-${opt}`} className="text-sm font-normal cursor-pointer">
                                    {opt}
                                </Label>
                            </div>
                        );
                    })}
                </div>
            );
            break;
        }

        case "file":
            control = (
                <div className="flex flex-col gap-2">
                    <Input
                        id={name}
                        type="text"
                        placeholder={placeholder || "Enter file path..."}
                        value={value ?? ""}
                        onChange={(e) => handleChange(e.target.value)}
                        className="bg-white"
                    />
                    {accept && (
                        <p className="text-[10px] text-slate-400">Accepted: {accept.join(", ")}</p>
                    )}
                </div>
            );
            break;
            
        case "button":
            return (
                <div className="mt-4">
                    <Label className="font-semibold">{label}</Label>
                    {description && <FormattedText text={description} className="text-xs text-slate-500 mb-2 block" />}
                    <Button variant="secondary" size="sm" onClick={handleAction} className="w-full">
                        {label}
                    </Button>
                </div>
            );

        default:
            control = <div className="text-red-500 text-xs">Unknown field type: {type}</div>;
    }

    return (
        <div className="flex flex-col gap-2">
            <Label htmlFor={name} className="font-semibold text-slate-700">{label}</Label>
            {description && <FormattedText text={description} className="text-[11px] text-slate-500 leading-tight mb-1" />}
            {control}
        </div>
    );
};
