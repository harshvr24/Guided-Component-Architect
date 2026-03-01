import React from "react";
import { ComponentOutput } from "./types";

interface Props {
  component: ComponentOutput | null;
}

export default function PreviewFrame({ component }: Props) {
  if (!component) return null;

  const srcDoc = `
    <html>
      <head>
        <style>
          ${component.css}
        </style>
      </head>
      <body>
        ${component.html}
      </body>
    </html>
  `;

  return (
    <iframe
      sandbox="allow-scripts"
      srcDoc={srcDoc}
      style={{
        width: "100%",
        height: "600px",
        border: "1px solid #ddd",
        borderRadius: "8px"
      }}
    />
  );
}