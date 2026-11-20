import React from "react";

export function Seo({ data }: { data: Record<string, unknown> }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}

export function After() {
  return <p>{[1, 2].map((n) => n * 2).join(",")}</p>;
}
