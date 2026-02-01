import React from "react";
import { useModelState } from "@anywidget/react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";

import type { ParameterSchema, ParameterItem, PipelineConfig } from "../types";

/* eslint-disable @typescript-eslint/no-explicit-any */
export const Parameters: React.FC<{ model: any }> = ({ model }) => {
  const [paramsSchema] = useModelState<ParameterSchema>("params_schema");
  const [paramsValues, setParamsValues] = useModelState<Record<string, any>>("params_values");
  const [config] = useModelState<PipelineConfig>("config");
  // const model = useModelState<any>("__model__")[0]; <-- Removed

  if (!paramsSchema) return null;

  const handleChange = (name: string, value: any) => {
    setParamsValues({ ...paramsValues, [name]: value });
    model.save_changes(); 
  };
  
  const handleAction = (name: string) => {
      // Logic for action buttons
      model.set("action_requested", name);
      model.save_changes();
  };

  const categories = Object.keys(paramsSchema);

  return (
    <Accordion type="multiple" defaultValue={categories} className="w-full space-y-4">
      {categories.map((cat) => {
          const items = paramsSchema[cat];
          const style = config?.category_styles?.[cat] || { bg: "#e0e7ff", text: "#4338ca" };

          return (
            <AccordionItem key={cat} value={cat} className="border border-slate-200 rounded-lg overflow-hidden data-[state=open]:bg-slate-50/50">
              <AccordionTrigger 
                className="px-4 py-3 hover:no-underline hover:bg-slate-50 transition-colors"
                style={{ backgroundColor: style.bg + "15" }} // 10% opacity
              >
                  <div className="flex items-center gap-3">
                      <span className="text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide" style={{ backgroundColor: style.bg, color: style.text }}>
                          {cat}
                      </span>
                  </div>
              </AccordionTrigger>
              <AccordionContent className="p-4 bg-white">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {items.map((p: ParameterItem) => (
                    <div key={p.name} className="flex flex-col gap-2">
                        {p.type !== "bool" && p.type !== "switch" && p.type !== "button" && (
                            <Label htmlFor={p.name} className="font-semibold text-slate-700">{p.label}</Label>
                        )}
                        
                        {/* Description */}
                        {p.desc && p.type !== "bool" && p.type !== "switch" && (
                            <span className="text-[11px] text-slate-500 leading-tight mb-1">{p.desc}</span>
                        )}

                        {/* Controls */}
                        {p.type === "button" ? (
                            <div className="mt-4">
                                <Label className="font-semibold">{p.label}</Label>
                                <p className="text-xs text-slate-500 mb-2">{p.desc}</p>
                                <Button variant="secondary" size="sm" onClick={() => handleAction(p.name)} className="w-full">
                                    {p.label}
                                </Button>
                            </div>
                        ) : (p.type === "bool" || p.type === "switch") ? (
                            <div className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm bg-white mt-1">
                                <div className="space-y-0.5">
                                    <Label htmlFor={p.name} className="text-sm font-medium">{p.label}</Label>
                                    <p className="text-[11px] text-slate-500">{p.desc}</p>
                                </div>
                                <Switch 
                                    id={p.name}
                                    checked={paramsValues?.[p.name] ?? p.def}
                                    onCheckedChange={(checked) => handleChange(p.name, checked)}
                                />
                            </div>
                        ) : p.type === "select" ? (
                            <Select 
                                value={paramsValues?.[p.name] ?? p.def} 
                                onValueChange={(val) => handleChange(p.name, val)}
                            >
                                <SelectTrigger className="w-full bg-white">
                                    <SelectValue placeholder="Select..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {(p.options || []).map((opt: string) => (
                                        <SelectItem key={opt} value={opt}>{opt}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        ) : (
                            <Input 
                                id={p.name}
                                type={p.type === "int" || p.type === "float" ? "number" : "text"}
                                value={paramsValues?.[p.name] ?? ""}
                                placeholder={String(p.def ?? "")}
                                onChange={(e) => {
                                    let val: any = e.target.value;
                                    if (p.type === "int") val = parseInt(val) || 0; // Better NaN handling needed?
                                    if (p.type === "float") val = parseFloat(val) || 0.0;
                                    handleChange(p.name, val);
                                }}
                                className="bg-white"
                            />
                        )}
                    </div>
                  ))}
                </div>
              </AccordionContent>
            </AccordionItem>
          );
      })}
    </Accordion>
  );
};
