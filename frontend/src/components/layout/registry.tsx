import React from "react";
import { PageComponent, SectionComponent, RowComponent, TabsComponent, TabComponent, CardComponent, TextComponent, HtmlComponent } from "./components";
import { FieldWrapper } from "./field_wrapper";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const Registry: Record<string, React.FC<any>> = {
    "page": PageComponent,
    "section": SectionComponent,
    "row": RowComponent,
    "tabs": TabsComponent,
    "tab": TabComponent,
    "card": CardComponent,
    "field": FieldWrapper,
    "text": TextComponent,
    "html": HtmlComponent,
};
