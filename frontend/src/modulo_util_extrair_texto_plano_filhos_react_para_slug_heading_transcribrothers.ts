import type { ReactNode } from "react";
import { isValidElement } from "react";

export function extrairTextoPlanoFilhosReactTranscribrothers(children: ReactNode): string {
  if (children == null || typeof children === "boolean") return "";
  if (typeof children === "string") return children;
  if (typeof children === "number") return String(children);
  if (Array.isArray(children)) {
    return children.map(extrairTextoPlanoFilhosReactTranscribrothers).join("");
  }
  if (isValidElement(children)) {
    return extrairTextoPlanoFilhosReactTranscribrothers(children.props.children);
  }
  return "";
}
