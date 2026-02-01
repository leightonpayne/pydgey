/* eslint-disable @typescript-eslint/no-explicit-any */
import React, { type ReactElement } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";

// ... (Page, Section, Row omitted for brevity, they were fine)

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

// --- Page ---
export const PageComponent: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <div className="space-y-6 w-full">
        {children}
    </div>
);

// --- Section ---
export const SectionComponent: React.FC<{ 
    title: string; 
    description?: string; 
    collapsed?: boolean; 
    children: React.ReactNode 
}> = ({ title, description, collapsed, children }) => (
    <Accordion type="single" collapsible defaultValue={collapsed ? undefined : "item-1"} className="w-full">
        <AccordionItem value="item-1" className="border-none">
            <div className="space-y-1">
                <AccordionTrigger className="hover:no-underline py-2">
                    <div className="flex flex-col">
                        <span className="text-lg font-medium">{title}</span>
                        {description && <span className="text-sm font-normal text-muted-foreground">{description}</span>}
                    </div>
                </AccordionTrigger>
                <Separator />
            </div>
            <AccordionContent className="pt-4 space-y-4">
                {children}
            </AccordionContent>
        </AccordionItem>
    </Accordion>
);

// --- Row ---
export const RowComponent: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <div className="flex flex-col md:flex-row gap-4 w-full">
        {React.Children.map(children, (child) => (
            <div className="flex-1 min-w-0">{child}</div>
        ))}
    </div>
);

// --- Tabs ---
export const TabsComponent: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    // Cast children to ReactElement to access props carefully
    const tabs = React.Children.toArray(children).filter(
        (child): child is ReactElement => React.isValidElement(child)
    );
    
    if (tabs.length === 0) return null;

    // Helper to extract label safely from either direct props or RecursiveRenderer node props
    const getLabel = (child: ReactElement, index: number): string => {
        const props = child.props as any;
        // Check if it's a RecursiveRenderer node (has 'node' prop with 'props')
        if (props.node && props.node.props && props.node.props.label) {
            return props.node.props.label;
        }
        // Fallback to direct label prop
        return props.label || `Tab ${index + 1}`;
    };

    const defaultValue = getLabel(tabs[0], 0);

    return (
        <Tabs defaultValue={defaultValue} className="w-full">
            <TabsList className="w-full justify-start flex-wrap">
                {tabs.map((tab, i) => {
                     const label = getLabel(tab, i);
                     return <TabsTrigger key={i} value={label}>{label}</TabsTrigger>;
                })}
            </TabsList>
            {tabs.map((tab, i) => {
                 const label = getLabel(tab, i);
                 return (
                    <TabsContent key={i} value={label} className="mt-4 space-y-4">
                        {/* Render the tab component (RecursiveRenderer) directly */}
                        {tab}
                    </TabsContent>
                 );
            })}
        </Tabs>
    );
};

export const TabComponent: React.FC<{ label: string; children: React.ReactNode }> = ({ children }) => (
    <>{children}</>
);

// --- Card ---
export const CardComponent: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
    <Card>
        <CardHeader>
            <CardTitle className="text-base">{title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
            {children}
        </CardContent>
    </Card>
);

// --- Text ---
export const TextComponent: React.FC<{ content: string; className?: string }> = ({ content, className }) => (
    <p className={`text-sm text-muted-foreground leading-relaxed ${className || ""}`}>
        {content}
    </p>
);

// --- HTML ---
export const HtmlComponent: React.FC<{ content: string; className?: string }> = ({ content, className }) => (
    <div 
        className={`prose prose-sm dark:prose-invert max-w-none ${className || ""}`}
        dangerouslySetInnerHTML={{ __html: content }}
    />
);
